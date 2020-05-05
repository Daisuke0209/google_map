from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path
from read_vectortile import _matrix
from spp import get_path_row, draw_graph, draw_route
from utils import Plot_route, _nearest_node, _get_latlon_byname
import json
from spp import shortest_route, make_adjacency_matrix

if __name__ == '__main__':
    with open('../data/nodes.json') as f:
        dic = json.load(f)

    with open('../config.json') as f:
        config = json.load(f)

    link_matrix, coord_matrix = _matrix(dic)

    csr_link_matrix = csr_matrix(link_matrix)

    route, weight = shortest_route('金閣寺', '伏見稲荷', csr_link_matrix, dic)

    plotter = Plot_route(config)
    plotter.draw_lines(dic)
    plotter.draw_route(dic, route)

    adj_matrix = make_adjacency_matrix(['金閣寺', '清水寺', '伏見稲荷'], csr_link_matrix, dic)