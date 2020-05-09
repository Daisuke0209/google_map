import urllib.request
import cv2
import json
from utils import pole2tile
import numpy as np
import vector_tile_base

def _show_plots(layer_map, img):
    layer = layer_map['road']

    h, w, c = img.shape
    colors = [50,100,150,200,250]
    for j, f in enumerate(layer.features):
        coords = f.get_geometry()[0]
        for i, coord in enumerate(coords):
            if i > 0:
                y1, x1 = (np.array(coords[i-1]))/layer.extent
                y2, x2 = (np.array(coords[i]))/layer.extent
                x1 = int(x1*h)
                y1 = int(y1*w)
                x2 = int(x2*h)
                y2 = int(y2*w)
                cv2.line(img, (x1, h-y1), (x2, h-y2), (colors[j%5], 0, colors[j%5]), thickness=1, lineType=cv2.LINE_4)

    cv2.imwrite('../data/plots.png', img)

def _show_alti(dic, img, tile_coord):
    h, w, c = img.shape
    for key in dic.keys():
        y = dic[key]['coord'][0]
        x = dic[key]['coord'][1]
        y,x = pole2tile(y, x, tile_coord[0])
        y = int((y - tile_coord[2])*h)
        x = int((x - tile_coord[1])*w)
        alti=int(dic[key]['altitude'])
        cv2.circle(img, (y, h-x), 1, (alti, 0, alti), thickness=-1)
    cv2.imwrite('../data/plots_alti.png', img)

if __name__ == '__main__':

    with open('../data/nodes.json') as f:
        dic = json.load(f)

    with open('../config.json') as f:
        config = json.load(f)

    tile_coord = (config["coord"]["zoom"], config["coord"]["t_lon"], config["coord"]["t_lat"])

    img = cv2.imread('../data/img.png')
    img = np.rot90(img)
    cv2.imwrite('../data/img_r.png', img)
    img = cv2.imread('../data/img_r.png')

    with open(r'../data/test.pbf', 'rb') as f:
        data = f.read()
        vt = vector_tile_base.VectorTile(data)

    layer_map = {l.name : l for l in vt.layers}

    _show_plots(layer_map, img)
    img = cv2.imread('../data/img_r.png')
    _show_alti(dic, img, tile_coord)