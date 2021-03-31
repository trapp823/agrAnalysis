'''
Created Feb 09, 2021

Thomas Rapp
tsrapp@g.clemson.edu

Summary: buffer original plots in shapefile by a user defined percentage and store as new csv coordinates
'''

import argparse
import pandas as pd
import csv

ap = argparse.ArgumentParser()
ap.add_argument("-src", "--sourceCoord", required=True,
                help="source coordinate file")
ap.add_argument("-l", "--length", required=True,
                help="percentage to buffer length by")
ap.add_argument("-w", "--width", required=True,
                help="percentage to buffer width by")
ap.add_argument("-t", "--targetFolder", required=True,
                help="target folder to save new coordinate file")

args = ap.parse_args()
srcFile = args.sourceCoord
length = float(args.length)
width = float(args.width)
tgt = args.targetFolder

colNames = ["Plot_ID", "X1", "Y1", "X2", "Y2", "X3", "Y3", "X4", "Y4"]
ogCoordsRaw = pd.read_csv(srcFile, header=0, names=colNames)
plotIds = ogCoordsRaw.Plot_ID.to_list()
ogX1 = ogCoordsRaw.X1.to_list()
ogY1 = ogCoordsRaw.Y1.to_list()
ogX2 = ogCoordsRaw.X2.to_list()
ogY2 = ogCoordsRaw.Y2.to_list()
ogX3 = ogCoordsRaw.X3.to_list()
ogY3 = ogCoordsRaw.Y3.to_list()
ogX4 = ogCoordsRaw.X4.to_list()
ogY4 = ogCoordsRaw.Y4.to_list()
#print(ogX1[0])

coord1 = [0.0] * 8
coord2 = [0.0] * 8
newFile = open(tgt + "\\bufferPlotCoordinates_" + str(length) + "_"
               + str(width) + ".csv", "wt")
writer = csv.writer(newFile, delimiter=',', lineterminator='\n')
writer.writerow(('Plot_ID', 'X1', 'Y1', 'X2', 'Y2', 'X3', 'Y3', 'X4', 'Y4'))
for i in range(len(ogX1)):
        coord1[0] = ogX1[i] + (ogX2[i] - ogX1[i]) * 0.005 * length
        coord1[1] = ogY1[i] + (ogY2[i] - ogY1[i]) * 0.005 * length
        coord1[2] = ogX2[i] + (ogX1[i] - ogX2[i]) * 0.005 * length
        coord1[3] = ogY2[i] + (ogY1[i] - ogY2[i]) * 0.005 * length
        coord1[4] = ogX3[i] + (ogX4[i] - ogX3[i]) * 0.005 * length
        coord1[5] = ogY3[i] + (ogY4[i] - ogY3[i]) * 0.005 * length
        coord1[6] = ogX4[i] + (ogX3[i] - ogX4[i]) * 0.005 * length
        coord1[7] = ogY4[i] + (ogY3[i] - ogY4[i]) * 0.005 * length

        coord2[0] = coord1[0] + (coord1[6] - coord1[0]) * 0.005 * width
        coord2[1] = coord1[1] + (coord1[7] - coord1[1]) * 0.005 * width
        coord2[2] = coord1[2] + (coord1[4] - coord1[2]) * 0.005 * width
        coord2[3] = coord1[3] + (coord1[5] - coord1[3]) * 0.005 * width
        coord2[4] = coord1[4] + (coord1[2] - coord1[4]) * 0.005 * width
        coord2[5] = coord1[5] + (coord1[3] - coord1[5]) * 0.005 * width
        coord2[6] = coord1[6] + (coord1[0] - coord1[6]) * 0.005 * width
        coord2[7] = coord1[7] + (coord1[1] - coord1[7]) * 0.005 * width

        writer.writerow((plotIds[i], coord2[0], coord2[1], coord2[2],
                        coord2[3], coord2[4], coord2[5],
                        coord2[6], coord2[7]))
