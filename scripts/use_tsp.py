from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path
from read_vectortile import _matrix
from spp import get_path_row
from utils import Plot_route, _nearest_node, _get_latlon_byname, Plot_route_db
import json
from spp import _linkmatrix, shortest_route_db, make_adjacency_matrix_db
import sqlite3
import numpy as np
from tsp import solve_tsp

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

    adj_matrix, route_matrix = make_adjacency_matrix_db(['京都駅', '野洲駅', '西院駅', '堅田駅'], csr_link_matrix, cur, table_name)

    paths = solve_tsp(adj_matrix)

    routes = []
    L = len(paths)
    for l in range(L):
        if l != 0:
            routes.append(route_matrix[l][l-1])

    plotter = Plot_route_db(config)
    plotter.draw_routes(cur, table_name, routes)