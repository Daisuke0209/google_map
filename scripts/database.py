import sqlite3
import vector_tile_base
import json
from utils import tile2pole, pole2tile, pole2ratio, _download
from read_vectortile import _get_altitude, fetch_tile
import numpy as np

def make_tbl(cur, table_name):
    cur.execute(f"drop table {table_name};")
    cur.execute(f'''CREATE TABLE IF NOT EXISTS {table_name}(
        id integer, 
        line_id integer, 
        tile_lat integer, 
        tile_lon integer,
        ratio_lat integer,
        ratio_lon integer,
        lat integer,
        lon integer,
        alti integer,
        edge integer,
        t_lat integer,
        t_lon integer
        )
        ''')
    with open(r'../data/test.pbf', 'rb') as f:
        data = f.read()

    vt = vector_tile_base.VectorTile(data)
    layer_map = {l.name : l for l in vt.layers}
    layer = layer_map['road']
    alti_tile = fetch_tile(*tile_coord)

    n = 0
    for i, f in enumerate(layer.features):
        coords = f.get_geometry()[0]
        L = len(coords)
        for l in range(L):
            tile_lat = coords[l][1]
            tile_lon = coords[l][0]
            ratio_lat = tile_lat/layer.extent
            ratio_lon = tile_lon/layer.extent
            t_lat = ratio_lat+(tile_coord[2])
            t_lon = ratio_lon+(tile_coord[1])
            lat, lon = tile2pole(t_lat, t_lon, tile_coord[0])
            alti = _get_altitude(lat, lon, alti_tile, tile_coord)
            
            if l > 0 and l < L-1:
                table_name_sub = table_name + '_' + str(n)
                cur.execute(f"drop table {table_name_sub};")
                cur.execute(f'''CREATE TABLE IF NOT EXISTS {table_name_sub}(id integer, neighbors integer)''')
                cur.execute(f"INSERT INTO {table_name_sub} VALUES ({n}, {n-1})")
                cur.execute(f"INSERT INTO {table_name_sub} VALUES ({n}, {n+1})")
                cur.execute(f"INSERT INTO {table_name} VALUES ({n}, {i}, {tile_lat}, {tile_lon}, {ratio_lat}, {ratio_lon}, {lat}, {lon}, {alti}, {0}, {t_lat}, {t_lon})")
            elif l == 0:
                cur.execute(f"INSERT INTO {table_name} VALUES ({n}, {i}, {tile_lat}, {tile_lon}, {ratio_lat}, {ratio_lon}, {lat}, {lon}, {alti}, {1}, {t_lat}, {t_lon})")
            else:
                cur.execute(f"INSERT INTO {table_name} VALUES ({n}, {i}, {tile_lat}, {tile_lon}, {ratio_lat}, {ratio_lon}, {lat}, {lon}, {alti}, {-1}, {t_lat}, {t_lon})")
            n = n + 1

def add_neighbor_tbl(cur, table_name):
    cur.execute(f"SELECT * FROM {table_name} WHERE edge IN(-1,1)")
    targets = cur.fetchall()
    for target in targets:
        n = target[0]
        target_lat = target[2]
        target_lon = target[3]
        cur.execute(f"SELECT * FROM {table_name} WHERE tile_lat = {target_lat} and tile_lon = {target_lon} and id != {n} and edge IN(-1,1)") 
        # nodes: targetと同じ物理的位置を持つノード
        nodes = cur.fetchall()
        table_name_sub = table_name + '_' + str(n)
        cur.execute(f"drop table {table_name_sub};")
        cur.execute(f'''CREATE TABLE IF NOT EXISTS {table_name_sub}(id integer, neighbors integer)''')
        for node in nodes:
            line_id = node[1]
            edge = node[9]
            node_id = node[0]
            if edge == 1:
                cur.execute(f"INSERT INTO {table_name_sub} VALUES ({n}, {node_id+1})")
            else:
                cur.execute(f"INSERT INTO {table_name_sub} VALUES ({n}, {node_id-1})")

def show_tbl(cur, table_name):
    for row in cur.execute(f'SELECT * FROM {table_name}'):
        print(row)

def _distances(cur, table_name, s_node, e_node):
    cur.execute(f"SELECT * FROM {table_name} WHERE id = {s_node}") 
    node = cur.fetchone()
    s_lat = node[6]
    s_lon = node[7]
    cur.execute(f"SELECT * FROM {table_name} WHERE id = {e_node}") 
    node = cur.fetchone()
    e_lat = node[6]
    e_lon = node[7]
    dis = ((s_lat-e_lat)**2+(s_lon-e_lon)**2)
    return dis

def _height(cur, table_name, s_node, e_node):
    '''
        input: 
            s_node: スタートノード番号
            e_ndoe: 行き先ノード番号
        output: e_nodeの高さ-s_nodeの高さ
    '''
    cur.execute(f"SELECT * FROM {table_name} WHERE id = {s_node}") 
    node = cur.fetchone()
    s_alti = node[8]
    cur.execute(f"SELECT * FROM {table_name} WHERE id = {e_node}") 
    node = cur.fetchone()
    e_alti = node[8]
    return e_alti-s_alti


if __name__ == '__main__':
    # make database
    conn = sqlite3.connect('../data/vectortile.db')
    cur = conn.cursor()

    with open('../config.json') as f:
        config = json.load(f)

    tile_coord = (config["coord"]["zoom"], config["coord"]["t_lon"], config["coord"]["t_lat"])

    _download(tile_lon = tile_coord[1], tile_lat = tile_coord[2], zoom = tile_coord[0])

    # make table
    table_name = f'table_{tile_coord[0]}_{tile_coord[1]}_{tile_coord[2]}'
    make_tbl(cur, table_name)
    # add neighbor relations
    add_neighbor_tbl(cur, table_name)
    conn.commit()
    conn.close()

    
    
