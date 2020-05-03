import numpy as np

def sec(x):
    return 1/np.cos(x)

def get_tile_coord(lat_deg, lon_deg, zoom):
    n = 2**zoom
    x = (n * (lon_deg + 180))//360
    lat_rad = lat_deg * np.pi / 180
    y = (n * (1 - np.log(np.tan(lat_rad) + sec(lat_rad)) / np.pi)) // 2
    return x,y

print(get_tile_coord(34.992668, 135.816928, 13))