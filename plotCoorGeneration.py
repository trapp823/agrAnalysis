'''
Created on Oct 22, 2020

@author: Xu
'''
'''
Originally Created on Jun 27, 2020

@author: Xu
'''
import pandas as pd
import argparse

# ------------------------------------------------------------------------
ap = argparse.ArgumentParser()
ap.add_argument("-cp", "--srcCorner", required=True,
                help="source field corner point file")
ap.add_argument("-sh", "--srcField", required=True,
                help="source field layout file")
ap.add_argument("-t", "--tgtPath", required=True,
                help="target folder for saving")
# ==============
args = ap.parse_args()
cpFile = args.srcCorner
fieldFile = args.srcField
targetPath = args.tgtPath

## Cross points generation
originalPoints = pd.read_csv(cpFile, header=0, usecols=[0, 1, 2])
# print(originalPoints)
x1 = originalPoints.iloc[0][0]
y1 = originalPoints.iloc[0][1]
x2 = originalPoints.iloc[1][0]
y2 = originalPoints.iloc[1][1]
x3 = originalPoints.iloc[2][0]
y3 = originalPoints.iloc[2][1]
x4 = originalPoints.iloc[3][0]
y4 = originalPoints.iloc[3][1]
# print(x4)
# print(y4)

# 1     2
#
#
# 4     3
fieldmap = pd.read_csv(fieldFile, header=None)
fieldmap.iloc[0][0]

rowNum, colNum = fieldmap.shape

import numpy as np


# k,b
def cal_kb(a1, b1, a2, b2):
    if a1 != a2:
        k = (b2 - b1) / (a2 - a1)
        b = (a2 * b1 - a1 * b2) / (a2 - a1)
    else:
        k = np.nan
        b = np.nan
    return k, b


# cross point
def cal_cp(k1, b1, k2, b2):
    if k1 != k2:
        x = (b2 - b1) / (k1 - k2)
        y = (k2 * b1 - k1 * b2) / (k2 - k1)
    else:
        x = np.nan
        y = np.nan
    return x, y


# Line 1-2
# k1 = cal_k(x1,y1,x2,y2)
# b1 = cal_b(x1,y1,x2,y2)
l1x = []
l1y = []
intv_x = (x2 - x1) / colNum
intv_y = (y2 - y1) / colNum
l1x.append(x1)
l1y.append(y1)
for i in range(colNum - 1):
    xc = x1 + (i + 1) * intv_x
    yc = y1 + (i + 1) * intv_y
    l1x.append(xc)
    l1y.append(yc)
l1x.append(x2)
l1y.append(y2)
# print(l1x)
# print(l1y)
# Line 4-3
# k3 = cal_k(x4,y4,x3,y3)
# b3 = cal_b(x4,y4,x3,y3)
l3x = []
l3y = []
intv_x = (x3 - x4) / colNum
intv_y = (y3 - y4) / colNum
l3x.append(x4)
l3y.append(y4)
for i in range(colNum - 1):
    xc = x4 + (i + 1) * intv_x
    yc = y4 + (i + 1) * intv_y
    l3x.append(xc)
    l3y.append(yc)
l3x.append(x3)
l3y.append(y3)
# print(l3x)
# print(l3y)
# Line 2-3
# k2 = cal_k(x2,y2,x3,y3)
# b2 = cal_b(x2,y2,x3,y3)
l2x = []
l2y = []
intv_x = (x3 - x2) / rowNum
intv_y = (y3 - y2) / rowNum
l2x.append(x2)
l2y.append(y2)
for i in range(rowNum - 1):
    xc = x2 + (i + 1) * intv_x
    yc = y2 + (i + 1) * intv_y
    l2x.append(xc)
    l2y.append(yc)
l2x.append(x3)
l2y.append(y3)
# print(len(l2x))
# print(len(l2y))
# Line 1-4
# k4 = cal_k(x1,y1,x4,y4)
# b4 = cal_b(x1,y1,x4,y4)
l4x = []
l4y = []
intv_x = (x4 - x1) / rowNum
intv_y = (y4 - y1) / rowNum
l4x.append(x1)
l4y.append(y1)
for i in range(rowNum - 1):
    xc = x1 + (i + 1) * intv_x
    yc = y1 + (i + 1) * intv_y
    l4x.append(xc)
    l4y.append(yc)
l4x.append(x4)
l4y.append(y4)
# print(len(l4x))
# print(len(l4y))
xp = []
yp = []
xp.extend(l1x)
yp.extend(l1y)
xp.extend(l2x)
yp.extend(l2y)
xp.extend(l3x)
yp.extend(l3y)
xp.extend(l4x)
yp.extend(l4y)
print(len(xp))
cp_tuples = list(zip(xp, yp))
# print(cp_tuples)
df_cp = pd.DataFrame(cp_tuples, columns=['Longitude', 'Latitude'])
# df_cp
cpsx = np.zeros((rowNum + 1, colNum + 1))
cpsy = np.zeros((rowNum + 1, colNum + 1))
# cps
for i in range(rowNum + 1):
    xl4 = l4x[i]
    yl4 = l4y[i]
    xl2 = l2x[i]
    yl2 = l2y[i]
    k1, b1 = cal_kb(xl4, yl4, xl2, yl2)
    for j in range(colNum + 1):
        xl1 = l1x[j]
        yl1 = l1y[j]
        xl3 = l3x[j]
        yl3 = l3y[j]
        k2, b2 = cal_kb(xl1, yl1, xl3, yl3)
        cpsx[i, j], cpsy[i, j] = cal_cp(k1, b1, k2, b2)
# print(cpsx[0,0])
# print(cpsx[0,1])
# cpsy
import csv

finalFile = open(targetPath + "\\plotCoord.csv", 'wt')
try:
    writer = csv.writer(finalFile, delimiter=',', lineterminator='\n')
    writer.writerow(('Plot_ID', 'X1', 'Y1', 'X2', 'Y2', 'X3', 'Y3', 'X4', 'Y4'))
    for i in range(rowNum):
        for j in range(colNum):
            writer.writerow((fieldmap.iloc[i][j], cpsx[i, j], cpsy[i, j], cpsx[i + 1, j], cpsy[i + 1, j],
                             cpsx[i + 1, j + 1], cpsy[i + 1, j + 1], cpsx[i, j + 1], cpsy[i, j + 1]))
finally:
    finalFile.close()
