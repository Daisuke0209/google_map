import vector_tile_base
import matplotlib.pyplot as plt
import numpy as np
import json

def _distance(coords):
    N = len(coords)
    L = 0
    for n in range(N):
        if n != 0:
            dx = coords[n-1][0] - coords[n][0]
            dy = coords[n-1][1] - coords[n][1]
            dl = np.sqrt(dx**2+dy**2)
            L = L + dl
    return L

def _neighbors(cursors, cursor):
    neighbors = np.where(cursors == str(cursor))[0]
    return neighbors

def _get_nodes(layer_map):
    layer = layer_map['road']
    edges = []
    for i, f in enumerate(layer.features):
        coords = f.get_geometry()[0]
        edges.append(str(coords[0]))
        edges.append(str(coords[-1]))
    return np.unique(edges)

def _edges(layer_map):
    layer = layer_map['road']
    s_edges = []
    e_edges = []
    distances = []
    for i, f in enumerate(layer.features):
        coords = f.get_geometry()[0]
        s_edges.append(str(coords[0]))
        e_edges.append(str(coords[-1]))
        distances.append(_distance(coords))  
    return np.array(s_edges), np.array(e_edges), distances

def _dic(nodes, s_edges, e_edges, distances):
    dic = {}
    for i, node in enumerate(nodes):
        s_indexes = np.where(node == np.array(s_edges))[0]
        e_indexes = np.where(node == np.array(e_edges))[0]
        neighbors_coord = []
        neighbors_index = []
        neighbors_distances = []
        if len(e_indexes) != 0:
            for index in e_indexes:
                coord = s_edges[index]
                node_index = np.where(nodes == coord)[0]
                if len(node_index) != 0:
                    neighbors_coord.append(coord)
                    neighbors_index.append(str(node_index[0]))
                    neighbors_distances.append(distances[index])
                    
        if len(s_indexes) != 0:
            for index in s_indexes:
                coord = e_edges[index]
                node_index = np.where(nodes == coord)[0]
                if len(node_index) != 0:
                    neighbors_coord.append(coord)
                    neighbors_index.append(str(node_index[0]))
                    neighbors_distances.append(distances[index])

    
        dic[i] = {
            'coord': [int(node.split(',')[1][:-1]), int(node.split(',')[0][1:])],
            'neighbors': neighbors_index,
            'neighbors_coords': neighbors_coord,
            'distances': neighbors_distances
        }
    return dic


def _show_plots(layer_map):
    layer = layer_map['road']
    for i, f in enumerate(layer.features):
        if i > 254 and i < 258:
            coords = f.get_geometry()[0]
            cursor = f.cursor
            xs, ys = [], []
            for coord in coords:
                xs.append(coord[1])
                ys.append(coord[0])
            plt.plot(xs, ys)
            plt.plot(coords[0][1], coords[0][0], marker='s', markersize=3)
            plt.plot(coords[-1][1], coords[-1][0], marker='s', markersize=3)
    plt.savefig('../data/plots.png')

if __name__ == '__main__':
    with open(r'../data/test.pbf', 'rb') as f:
        data = f.read()
        vt = vector_tile_base.VectorTile(data)

    layer_map = {l.name : l for l in vt.layers}
    nodes = _get_nodes(layer_map)
    s_edges, e_edges, distances = _edges(layer_map)
    # _show_plots(layer_map)
    dic = _dic(nodes, s_edges, e_edges, distances)
    with open('../data/nodes.json', 'w') as f:
        json.dump(dic, f, indent=4)

    L = len(dic)
    link_matrix = []
    coord_matrix = []
    # To do: fix 
    for key in dic.keys():
        coord_matrix.append(dic[key]['coord'])
        vec = np.zeros(L)
        for i, neighbor in enumerate(dic[key]['neighbors']):
            vec[int(neighbor)] = dic[key]['distances'][i]
        link_matrix.append(vec)

    link_matrix = np.array(link_matrix)
    coord_matrix = np.array(coord_matrix)
    print(coord_matrix.shape)
    print(link_matrix.shape)
        