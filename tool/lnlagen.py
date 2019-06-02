import xlrd
from datetime import date,datetime
import numpy as np
# from pandas import Series, DataFrame
import pandas as pd
import datetime
import dateutil
from math import *
from dateutil import parser

PI = 3.141592654
EARTH_RADIUS = 6378137  

df1 = pd.DataFrame(pd.read_excel(r'input_alldata.xlsx'))
df2 = pd.DataFrame(pd.read_excel(r'input_alldata2.xlsx'))
df = df1.append(df2)
df = df.set_index("ID", drop=False)


def get_distance(lat1, lng1, lat2, lng2):
	radLat1 = lat1 * PI / 180.0   #角度1˚ = π / 180
	radLat2 = lat2 * PI / 180.0   #角度1˚ = π / 180
	a = radLat1 - radLat2#纬度之差
	b = lng1 * PI / 180.0 - lng2* PI / 180.0  #经度之差
	dst = 2 * asin((sqrt(pow(sin(a / 2), 2) + cos(radLat1) * cos(radLat2)*pow(sin(b / 2), 2))))
	dst = dst * EARTH_RADIUS
	dst = round(dst * 10000) / 10000
	return dst

def get_angle(lat1, lng1, lat2, lng2):
	x = lat1 - lat2#t d
	y = lng1 - lng2#z y
	angle=-1
	if (y == 0 & x > 0): angle = 0
	if (y == 0 & x < 0): angle = 180
	if(x ==0 & y > 0): angle = 90
	if(x == 0 & y < 0): angle = 270
	if (angle == -1):
		dislat = get_distance(lat1, lng2, lat2, lng2)
		dislng = get_distance(lat2, lng1, lat2, lng2)
		if (x > 0 & y > 0): angle = atan2(dislng, dislat) / PI * 180
		if (x < 0 & y > 0): angle = atan2(dislat, dislng) / PI * 180+90
		if (x < 0 & y < 0): angle = atan2(dislng, dislat) / PI * 180 + 180
		if (x > 0 & y < 0): angle = atan2(dislat, dislng) / PI * 180 + 270
	return angle

def sortedlistgen():
    n = 1000
    angle = {}
    for i in range(1,n):
        angle['angle_%d' % i]  = get_angle(df.loc[['0'],['lat']], df.loc[['0'],['lng']], df.loc[['i'],['lat']], df.loc[['i']['lng']])
    sorted_angle = list(dict.keys(sorted(angle,key=angle.__getitem__)))
    return sorted_angle




