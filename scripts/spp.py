"""
Shortest Path Problem
https://note.nkmk.me/python-scipy-shortest-path/
"""

import numpy as np
from scipy.sparse.csgraph import shortest_path, floyd_warshall, dijkstra, bellman_ford, johnson
from scipy.sparse import csr_matrix
import matplotlib.pyplot as plt
from matplotlib.patches import ArrowStyle
from read_vectortile import _download
import cv2
from utils import _get_latlon_byname, _nearest_node, _weight, _nearest_node_db
from database import _distances, _height
from tqdm import tqdm

def get_path(start, goal, pred):
    return get_path_row(start, goal, pred[start])

def get_path_row(start, goal, pred_row):
    path = []
    i = goal
    while i != start and i >= 0:
        path.append(i)
        i = pred_row[i]
    if i < 0:
        return []
    path.append(i)
    return path[::-1]

def shortest_route(s_pos, e_pos, csr_link_matrix, dic):
    s_lat, s_lon = _get_latlon_byname(s_pos)
    start = _nearest_node(dic, s_lat, s_lon)

    e_lat, e_lon = _get_latlon_byname(e_pos)
    end = _nearest_node(dic, e_lat, e_lon)

    d, p = shortest_path(csr_link_matrix, return_predecessors=True, indices=start)
    route = get_path_row(start, end, p)
    weight = _weight(route, csr_link_matrix)

    return route, weight

def shortest_route_db(s_pos, e_pos, csr_link_matrix, cur, table_name):
    s_lat, s_lon = _get_latlon_byname(s_pos)
    start = _nearest_node_db(cur, table_name, s_lat, s_lon)

    e_lat, e_lon = _get_latlon_byname(e_pos)
    end = _nearest_node_db(cur, table_name, e_lat, e_lon)

    print(f"start: {start}")
    print(f"end: {end}")

    d, p = shortest_path(csr_link_matrix, return_predecessors=True, indices=start)

    route = get_path_row(start, end, p)
    
    weight = _weight(route, csr_link_matrix)

    return route, weight

def make_adjacency_matrix(nodes_list, csr_link_matrix, dic):
    N = len(nodes_list)

    adj_matrix = np.zeros((N, N))

    for i in range(N):
        for j in range(N):
            if i == j: continue
            route, cost = shortest_route(nodes_list[i], nodes_list[j], csr_link_matrix, dic)
            adj_matrix[i, j] = cost
    
    return adj_matrix

def make_adjacency_matrix_db(nodes_list, csr_link_matrix, cur, table_name):
    N = len(nodes_list)

    adj_matrix = np.zeros((N, N))
    route_matrix = []

    for i in range(N):
        route_vector = []
        for j in range(N):
            if i == j: continue
            route, cost = shortest_route_db(nodes_list[i], nodes_list[j], csr_link_matrix, cur, table_name)
            adj_matrix[i, j] = cost
            route_vector.append(route)
        route_matrix.append(route_vector)

    return adj_matrix, route_matrix

def _linkmatrix(cur, table_name):
    cur.execute(f"SELECT * FROM {table_name}")
    nodes = cur.fetchall()
    L = len(nodes)
    link_matrix = []
    coord_matrix = []
    for node in tqdm(nodes):
        vec = np.zeros(L)
        node_id = node[0]
        coord_matrix.append([node[7], node[6]])
        table_name_sub = table_name + '_' + str(node_id)
        cur.execute(f"SELECT * FROM {table_name_sub}")
        neighbors = cur.fetchall()
        for neighbor in neighbors:
            neighbor_id = neighbor[1]
            dis = _distances(cur, table_name, node_id, neighbor_id)
            alti = _height(cur, table_name, node_id, neighbor_id)
            if alti < 0:
                vec[neighbor_id] = dis*10
            else:
                vec[neighbor_id] = dis/10
        link_matrix.append(vec)

    return np.array(link_matrix), np.array(coord_matrix)

if __name__ == '__main__':
    c = [[0, 4],
        [2, 4],
        [1, 2],
        [3, 1],
        [4, 3]]

    l = [[0, 6, 3, 0, 0],
        [0, 0, 0, 1, 2],
        [2, 1, 0, 3, 0],
        [0, 0, 2, 0, 1],
        [0, 3, 0, 0, 0]]

    c = np.array(c)
    csr = csr_matrix(l)

    start = 4
    end = 0
    d, p = shortest_path(csr, return_predecessors=True, indices=start)
    route = get_path_row(start, end, p)
    print(d[end])
    print(route)