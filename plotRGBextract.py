'''
author: Thomas Rapp @ KresovichLab Clemson Univ
        tsrapp@clemson.edu
assistance from: Kevin (Xu) Wang @ Kansas State Univ
                 Sirjan Sapkota @ Clemson Univ

Created Feb 8, 2021

Summary: Use shapefile created in QGIS using HTP Geoprocessor plugin to extract
         plot-by-plot raster data from drone imaging of agricultural research field.
'''

import argparse
import fiona
import rasterio
from rasterio.mask import mask
import numpy as np
import csv
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-shp", "--shapefile", required=True,
                help="source shapefile")
ap.add_argument("-s", "--sourceImage", required=True,
                help="source GeoTiff Image File")
ap.add_argument("-t", "--targetFolder", required=True,
                help="target folder")

args = ap.parse_args()
plotShape = args.shapefile
srcImage = args.sourceImage
tgtFolder = args.targetFolder

bufferString = (plotShape.split("\\")[5] + "_buffer" + plotShape.split("_")[3]
                + "_" + plotShape.split("_")[4]).strip(".shp")
print(bufferString)

with fiona.open(plotShape) as shapes:
    coords = [poly['geometry']['coordinates'] for poly in shapes.values()]
    geoms = [feature["geometry"] for feature in shapes]
    plotIDs = [feature["properties"] for feature in shapes]

allData = []
#imgGrey = cv2.imread(srcImage, 0)
#nzPixels = []
progressCount = 0
for i in range(len(plotIDs)):
    progressCount = progressCount + 1
    print("working on " + str(progressCount) + "/" + str(len(plotIDs)))
    plotID = str(plotIDs[i]).split("'")[3]
    with rasterio.open(srcImage) as src:
        rawNpPixels, out_transform = mask(src, [geoms[i]], crop=True)
    out_meta = src.meta.copy()
    out_meta.update({"driver": "GTiff",
                     "height": rawNpPixels.shape[1], "width": rawNpPixels.shape[2],
                     "transform": out_transform})

    #with rasterio.open(tgtFolder+"\\"+plotID+".tif", "w", **out_meta) as dest:
       #dest.write(rawNpPixels)

    npRed = rawNpPixels[0]
    npRed[npRed < 0] = 0
    npGreen = rawNpPixels[1]
    npGreen[npGreen < 0] = 0
    npBlue = rawNpPixels[2]
    npBlue[npBlue < 0] = 0

    for x in range(len(npRed)):
        for y in range(len(npRed[x])):
            if (npBlue[x][y] == 0 | npGreen[x][y] == 0):
                thisBGI = 0
            else:
                thisBGI = npBlue[x][y] / npGreen[x][y]
            if(thisBGI > 0.65):
                #rawNpPixels[0][x][y] = 0
                npRed[x][y] = 0
                #rawNpPixels[1][x][y] = 0
                npGreen[x][y] = 0
                #rawNpPixels[2][x][y] = 0
                npBlue[x][y] = 0

    # plot RGB extraction
    if np.count_nonzero(npRed) > 0:
        nzRed = npRed[np.nonzero(npRed)]
        redMean = np.mean(nzRed)  # /(256*256)
        redStdDev = np.std(nzRed)

    if np.count_nonzero(npGreen) > 0:
        nzGreen = npGreen[np.nonzero(npGreen)]
        greenMean = np.mean(nzGreen)  # /(256*256)
        greenStdDev = np.std(nzGreen)

    if np.count_nonzero(npBlue) > 0:
        nzBlue = npBlue[np.nonzero(npBlue)]
        blueMean = np.mean(nzBlue)  # /(256*256)
        blueStdDev = np.std(nzBlue)

    #with rasterio.open(tgtFolder+"\\"+plotID+"noSoil.tif", "w", **out_meta) as dest:
       #dest.write(rawNpPixels)

    # vegetation indices calculations using mean RGB values
    # brightness index (vegetation cover)
    BI = np.sqrt((pow(redMean, 2) + pow(greenMean, 2) + pow(blueMean, 2) / 3))

    # soil color index
    SCI = (redMean - greenMean) / (redMean + greenMean)

    # green leaf index (chlorophyll)
    GLI = (2 * greenMean - redMean - blueMean) / (2 * greenMean + redMean + blueMean)

    # normalized green red difference index (chlorophyll, biomass, water content)
    NGRDI = (greenMean - redMean) / (greenMean + redMean)

    # spectral slope saturation index (soil color)
    SI = (redMean - blueMean) / (redMean + blueMean)

    # primary colors hue index (soil color)
    HI = (2 * redMean - greenMean - blueMean) / (greenMean - blueMean)

    # visible atmospherically resistant index (canopy, biomass, chlorophyll)
    VARI = (greenMean - redMean) / (greenMean + redMean - blueMean)

    # overall hue index (soil color)
    HUE = np.arctan(2 * (blueMean - greenMean - redMean) / 30.5 * (greenMean - redMean))

    # blue green pigment index (chlorophyll, leaf area index)
    BGI = blueMean / greenMean

    csvRow = [plotID, coords[i][0][0][0], coords[i][0][0][1],
              coords[i][0][1][0], coords[i][0][1][1],
              coords[i][0][2][0], coords[i][0][2][1],
              coords[i][0][3][0], coords[i][0][3][1],
              redMean, greenMean, blueMean,
              redStdDev, greenStdDev, blueStdDev,
              BI, SCI, GLI, NGRDI, SI, HI, VARI, HUE, BGI]

    allData.append(csvRow)

finalFile = open(tgtFolder + "\\PlotPixelAnalysis_" + bufferString + ".csv", "wt")
try:
    writer = csv.writer(finalFile, delimiter=',', lineterminator='\n')
    csvHeader = ["Plot_ID", "X1", "Y1", "X2", "Y2", "X3", "Y3", "X4", "Y4",
                 "Red_Mean", "Green_Mean", "Blue_Mean",
                 "Red_StdDev", "Green_StdDev", "Blue_StdDev",
                 "brightness", "soil color", "green leaf",
                 "normalized green-red diff", "spectral slope saturation",
                 "primary colors hue", "visible atmospherically resistant",
                 "overall hue", "blue-green"]
    writer.writerow(csvHeader)
    writer.writerows(allData)
finally:
    finalFile.close()
