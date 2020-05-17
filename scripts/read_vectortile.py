import vector_tile_base
import matplotlib.pyplot as plt
import numpy as np
import json
from utils import tile2pole, pole2tile, pole2ratio, _download
import requests
import pandas as pd
import cv2

def fetch_tile(z, x, y):
    url = "https://cyberjapandata.gsi.go.jp/xyz/dem/{z}/{x}/{y}.txt".format(z=z, x=x, y=y)
    df =  pd.read_csv(url, header=None).replace("e", 0)
    return df.values

def _altitude(x, y, alti_tile):
    x = int(x)
    y = int(y)
    if x < 0:
        x = 0
    if y < 0:
        y = 0
    if x > 255:
        x = 255
    if y > 255:
        y = 255
    return alti_tile[x, y]

def _get_altitude(lat, lon, alti_tile, tile_coord):
    h, w = alti_tile.shape

    # lat = 34.98971451951239
    # lon = 135.79079031944275
    tile_lat, tile_lon = pole2tile(lat, lon, tile_coord[0])

    tile_lat = tile_lat-tile_coord[2]
    tile_lon = tile_lon-tile_coord[1]
    return float(_altitude(tile_lat*w, tile_lon*h, alti_tile))
    