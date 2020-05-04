"""
Shortest Path Problem
https://note.nkmk.me/python-scipy-shortest-path/
"""

import numpy as np
from scipy.sparse.csgraph import shortest_path, floyd_warshall, dijkstra, bellman_ford, johnson
from scipy.sparse import csr_matrix

import matplotlib.pyplot as plt
from matplotlib.patches import ArrowStyle

def draw_graph(c, csr):
    # draw nodes
    plt.scatter(c[:, 0], c[:, 1], marker='o', s=200)
    for i in range(c.shape[0]):
        plt.text(c[i, 0]+0.1, c[i, 1]+0.1, i, size=10)
    # draw links
    for i in range(csr.shape[0]):
        for j in range(csr.shape[1]):
            weight = csr[i, j]
            if weight>0:
                plt.annotate('', xy=(c[i, 0],c[i, 1]), xytext=(c[j, 0], c[j, 1]),
                            arrowprops=dict(arrowstyle=ArrowStyle('<|-', head_length=1, head_width=0.5)))
                plt.text((c[i, 0]+c[j, 0]*0.2)/1.2, (c[i, 1]+c[j, 1]*0.2)/1.2,
                            csr[i, j], color='red', size=10)

    plt.grid(which='major',color='gray',linestyle='-')
    # plt.xlim(-0.5, 5.5)
    # plt.ylim(-0.5, 5.5)
    plt.show()

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

def draw_route(c, csr, route):
    # draw nodes
    plt.scatter(c[:, 0], c[:, 1], marker='o', s=200)
    for i in range(c.shape[0]):
        plt.text(c[i, 0]+0.1, c[i, 1]+0.1, i, size=20)
    # draw route
    for i in range(len(route)-1):
            # plt.plot([c[route[i], 0], c[route[i+1], 0]], [c[route[i], 1], c[route[i+1], 1]], c='red')
            plt.annotate('', xy=(c[route[i], 0],c[route[i], 1]), xytext=(c[route[i+1], 0], c[route[i+1], 1]),
                            arrowprops=dict(arrowstyle=ArrowStyle('<|-', head_length=1, head_width=0.5)))
            plt.text((c[route[i], 0]+c[route[i+1], 0])/2, (c[route[i], 1]+c[route[i+1], 1])/2,
                        csr[ route[i], route[i+1]], color='k', size=15)

    plt.grid(which='major',color='gray',linestyle='-')
    # plt.xlim(-0.5, 5.5)
    # plt.ylim(-0.5, 5.5)
    plt.show()


#----------------------------------
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
    # d, p = shortest_path(csr, return_predecessors=True)
    # d, p = shortest_path(csr, return_predecessors=True, indices=0)
    # print(d)
    # print(p)

    start = 4
    end = 0
    d, p = shortest_path(csr, return_predecessors=True, indices=start)
    route = get_path_row(start, end, p)
    print(d[end])
    print(route)
    # [0, 2, 1, 3, 4]

    draw_graph(c, csr)
    draw_route(c, route)


    #----------------------------------
    x_size = 6
    y_size = 5
    c = np.zeros((x_size*y_size, 2))
    for i in range(x_size):
        for j in range(y_size):
            c[i*y_size+j, 0] = i
            c[i*y_size+j, 1] = j

    l = np.zeros((x_size*y_size, x_size*y_size)).astype(np.int)
    for i in range(l.shape[0]):
        for j in range(l.shape[1]):
            if abs(c[i, 0]-c[j, 0])+abs(c[i, 1]-c[j, 1])==1:
                l[i, j] = np.random.randint(1, 10)
    l = np.tril(l) + np.tril(l).T

    c = np.array(c)
    csr = csr_matrix(l)
    print(c)
    print(l)

    start = 0
    end = 29
    d, p = shortest_path(csr, return_predecessors=True, indices=start)
    route = get_path_row(start, end, p)
    print(d[end])
    print(route)

    draw_graph(c, csr)
    draw_route(c, route)