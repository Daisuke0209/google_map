from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path
from read_vectortile import _matrix
from spp import get_path_row
from utils import Plot_route, _nearest_node, _get_latlon_byname, Plot_route_db
import json
from spp import shortest_route, make_adjacency_matrix, _linkmatrix, shortest_route_db
import sqlite3
import numpy as np

if __name__ == '__main__':
    conn = sqlite3.connect('../data/vectortile.db')
    cur = conn.cursor()

    with open('../data/nodes.json') as f:
        dic = json.load(f)

    with open('../config.json') as f:
        config = json.load(f)

    tile_coord = (config["coord"]["zoom"], config["coord"]["t_lon"], config["coord"]["t_lat"])

    table_name = f'table_{tile_coord[0]}_{tile_coord[1]}_{tile_coord[2]}'
    link_matrix,coord_matrix = _linkmatrix(cur, table_name)

    csr_link_matrix = csr_matrix(link_matrix)

    route, weight = shortest_route_db('西院駅', '野洲駅', csr_link_matrix, cur, table_name)

    
    plotter = Plot_route_db(config)
    plotter.draw_route(cur, table_name, route)

    # adj_matrix = make_adjacency_matrix(['金閣寺', '清水寺', '伏見稲荷'], csr_link_matrix, dic)