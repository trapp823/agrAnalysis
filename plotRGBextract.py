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

with fiona.open(plotShape) as shapes:
    coords = [poly['geometry']['coordinates'] for poly in shapes.values()]
    geoms = [feature["geometry"] for feature in shapes]
    plotIDs = [feature["properties"] for feature in shapes]

allData = []
for i in range(len(plotIDs)):
    plotID = str(plotIDs[i]).split("'")[3]
    with rasterio.open(srcImage) as src:
        rawNpPixels, out_transform = mask(src, [geoms[i]], crop=True)
    out_meta = src.meta.copy()
    out_meta.update({"driver": "GTiff",
                     "height": rawNpPixels.shape[1], "width": rawNpPixels.shape[2],
                     "transform": out_transform})

#    with rasterio.open(tgtFolder+"\\"+plotID+".tif", "w", **out_meta) as dest:
#       dest.write(rawNpPixels)

    npRed = rawNpPixels[0]
    npRed[npRed < 0] = 0
    npGreen = rawNpPixels[1]
    npGreen[npGreen < 0] = 0
    npBlue = rawNpPixels[2]
    npBlue[npBlue < 0] = 0

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

    csvRow = [plotID, coords[i][0][0][0], coords[i][0][0][1],
              coords[i][0][1][0], coords[i][0][1][1],
              coords[i][0][2][0], coords[i][0][2][1],
              coords[i][0][3][0], coords[i][0][3][1],
              redMean, greenMean, blueMean,
              redStdDev, greenStdDev, blueStdDev]

    allData.append(csvRow)

finalFile = open(tgtFolder + "\\PlotPixelAnalysis.csv", "wt")
try:
    writer = csv.writer(finalFile, delimiter=',', lineterminator='\n')
    csvHeader = ["Plot_ID", "X1", "Y1", "X2", "Y2", "X3", "Y3", "X4", "Y4",
                 "Red_Mean", "Green_Mean", "Blue_Mean",
                 "Red_StdDev", "Green_StdDev", "Blue_StdDev"]
    writer.writerow(csvHeader)
    writer.writerows(allData)
finally:
    finalFile.close()
