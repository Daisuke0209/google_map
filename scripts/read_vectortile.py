import vector_tile_base
import matplotlib.pyplot as plt
import numpy as np
import json
from .utils import tile2pole, pole2tile, pole2ratio, _download
import requests
import pandas as pd
import cv2

def _distance(coords, extent):
    N = len(coords)
    L = 0
    for n in range(N):
        if n != 0:
            dx = coords[n-1][0]/extent - coords[n][0]/extent
            dy = coords[n-1][1]/extent - coords[n][1]/extent
            dl = np.sqrt(dx**2+dy**2)
            L = L + dl
    return L

def _diff_altitude(coords, tile_coord, extent, alti_tile):
    s_edge = coords[0]
    e_edge = coords[-1]
    s_lat, s_lon = tile2pole(float(s_edge[0]/extent)+tile_coord[2], float(s_edge[1]/extent)+tile_coord[1], tile_coord[0])
    e_lat, e_lon = tile2pole(float(e_edge[0]/extent)+tile_coord[2], float(e_edge[1]/extent)+tile_coord[1], tile_coord[0])
    s_alti = _get_altitude(s_lat, s_lon, alti_tile, tile_coord)
    e_alti = _get_altitude(e_lat, e_lon, alti_tile, tile_coord)
    return e_alti-s_alti

def fetch_tile(z, x, y):
    url = "https://cyberjapandata.gsi.go.jp/xyz/dem/{z}/{x}/{y}.txt".format(z=z, x=x, y=y)
    df =  pd.read_csv(url, header=None).replace("e", 0)
    return df.values

def _neighbors(cursors, cursor):
    neighbors = np.where(cursors == str(cursor))[0]
    return neighbors

def _nodes(layer_map, tile_coord, alti_tile):
    layer = layer_map['road']
    s_edges = []
    e_edges = []
    edges = []
    distances = []
    for i, f in enumerate(layer.features):
        coords = f.get_geometry()[0]
        s_edges.append(str([coords[0][0]/layer.extent, coords[0][1]/layer.extent]))
        e_edges.append(str([coords[-1][0]/layer.extent, coords[-1][1]/layer.extent]))
        edges.append(str([coords[0][0]/layer.extent, coords[0][1]/layer.extent]))
        edges.append(str([coords[-1][0]/layer.extent, coords[-1][1]/layer.extent]))
        distances.append(_distance(coords, layer.extent))  
    return np.unique(edges), np.array(s_edges), np.array(e_edges), distances

def _dic(nodes, s_edges, e_edges, distances, alti_tile, tile_coord):
    dic = {}
    for i, node in enumerate(nodes):
        s_indexes = np.where(node == np.array(s_edges))[0]
        e_indexes = np.where(node == np.array(e_edges))[0]
        neighbors_coord = []
        neighbors_index = []
        neighbors_distances = []
        if len(e_indexes) != 0:
            for index in e_indexes:
                str_coord = s_edges[index]
                node_index = np.where(nodes == str_coord)[0]
                if len(node_index) != 0:
                    coord = [tile2pole(float(str_coord.split(',')[1][:-1])+tile_coord[2], float(str_coord.split(',')[0][1:])+tile_coord[1],tile_coord[0])]
                    neighbors_coord.append(coord)
                    neighbors_index.append(str(node_index[0]))
                    neighbors_distances.append(distances[index])
                    
        if len(s_indexes) != 0:
            for index in s_indexes:
                str_coord = e_edges[index]
                node_index = np.where(nodes == str_coord)[0]
                if len(node_index) != 0:
                    coord = [tile2pole(float(str_coord.split(',')[1][:-1])+tile_coord[2], float(str_coord.split(',')[0][1:])+tile_coord[1],tile_coord[0])]
                    neighbors_coord.append(coord)
                    neighbors_index.append(str(node_index[0]))
                    neighbors_distances.append(distances[index])
    
        lat, lon = tile2pole(float(node.split(',')[1][:-1])+tile_coord[2], float(node.split(',')[0][1:])+tile_coord[1], tile_coord[0])

        dic[i] = {
            'coord': [lat, lon],
            'neighbors': neighbors_index,
            'neighbors_coords': neighbors_coord,
            'distances': neighbors_distances,
            'altitude': _get_altitude(lat, lon,alti_tile, tile_coord),
        }
    return dic

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

def _matrix(dic):
    L = len(dic)
    link_matrix = []
    coord_matrix = []
    # To do: fix 
    for key in dic.keys():
        coord_matrix.append([dic[key]['coord'][1], dic[key]['coord'][0]])
        vec = np.zeros(L)
        for i, neighbor in enumerate(dic[key]['neighbors']):
            if dic[key]['neighbor_altitude'][i]<0:
                vec[int(neighbor)] = dic[key]['distances'][i]*1
            else:
                vec[int(neighbor)] = dic[key]['distances'][i]*100
        link_matrix.append(vec)

    link_matrix = np.array(link_matrix)
    coord_matrix = np.array(coord_matrix)
    return link_matrix, coord_matrix

def _modify_dic(dic, tile_coord):
    for key in dic.keys():
        # add neighbor altitude
        neighbors = dic[key]['neighbors']
        alti = dic[key]['altitude']
        diff_altis = []
        for neighbor in neighbors:
            diff_altis.append((dic[int(neighbor)]['altitude'])-alti)
        dic[key]['neighbor_altitude'] = diff_altis

        # add ratio coord
        ratio_lon, ratio_lat = pole2ratio(dic[key]["coord"][0], dic[key]["coord"][1], tile_coord)
        dic[key]['ratio_coord'] = [ratio_lon, ratio_lat]
    return dic


if __name__ == '__main__':
    with open('../config.json') as f:
        config = json.load(f)

    tile_coord = (config["coord"]["zoom"], config["coord"]["t_lon"], config["coord"]["t_lat"])

    _download(tile_lon = tile_coord[1], tile_lat = tile_coord[2], zoom = tile_coord[0])

    # Open the pbf data
    with open(r'../data/test.pbf', 'rb') as f:
        data = f.read()
        vt = vector_tile_base.VectorTile(data)
    layer_map = {l.name : l for l in vt.layers}

    alti_tile = fetch_tile(*tile_coord)

    # Get all nodes and edges from .pbf
    nodes, s_edges, e_edges, distances = _nodes(layer_map, tile_coord, alti_tile)

    # _show_plots(layer_map, nabewari_tile)
    
    dic = _dic(nodes, s_edges, e_edges, distances, alti_tile, tile_coord)
    dic = _modify_dic(dic, tile_coord)
    with open('../data/nodes.json', 'w') as f:
        json.dump(dic, f, indent=4)

    

    link_matrix, coord_matrix = _matrix(dic)