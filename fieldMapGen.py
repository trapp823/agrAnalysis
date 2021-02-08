'''
Created Jan 29, 2021

Thomas Rapp

Summary: to create field layout csv to correspond with plot layout in actual field
'''

import argparse
import pandas as pd
import csv

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--sourceFile", required=True,
                help="source field plot file")
ap.add_argument("-t", "--tgtPath", required=True,
                help="target folder to save to")

args = ap.parse_args()
source = args.sourceFile
target = args.tgtPath

colNames = ["Plot_ID", "Range", "Row", "Rep"]
plotidsRaw = pd.read_csv(source, header=0, names=colNames)
plotids = plotidsRaw.Plot_ID.to_list()
plotids.reverse()

fieldRanges = 61

field = [plotids[i:i+fieldRanges] for i in range(0, len(plotids), fieldRanges)]

finalFile = open(target + "\\fieldMap.csv", "wt")
try:
    writer = csv.writer(finalFile, delimiter=',', lineterminator='\n')
    writer.writerows(field)
finally:
    finalFile.close()