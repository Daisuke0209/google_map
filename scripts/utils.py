import numpy as np
from math import pi
from math import e
from math import atan

def sec(x):
    return 1/np.cos(x)

def pole2tile(lat, lon, zoom):
    n = 2**zoom
    tile_lon = (n * (lon + 180))/360
    lat_rad = lat * pi / 180
    tile_lat = (n * (1 - np.log(np.tan(lat_rad) + sec(lat_rad)) / pi)) / 2
    return tile_lat,tile_lon

def tile2pole(tile_lat, tile_lon, zoom):
	lon = (tile_lon / 2.0**zoom) * 360 - 180 # 経度（東経）
	mapy = (tile_lat / 2.0**zoom) * 2 * pi - pi
	lat = 2 * atan(e ** (- mapy)) * 180 / pi - 90 # 緯度（北緯）
	return lat, lon


tile_lat, tile_lon = pole2tile(34.992668, 135.816928, 13)
# print(tile_lat,tile_lon)
lat, lon = tile2pole(tile_lat, tile_lon, 13)
# print(lat,lon)
