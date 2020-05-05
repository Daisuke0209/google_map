"""
Traveling Salesman Problem
https://qiita.com/panchovie/items/6509fb54e3d53f4766aa
http://www.nct9.ne.jp/m_hiroi/light/pulp04.html
"""

import sys, math, time

import numpy as np
import pulp 
import matplotlib.pyplot as plt
from matplotlib.patches import ArrowStyle

def solve_tsp(ws):
    """巡回セールスマン問題を解く

    :param ws: 隣接行列
    :type ws: np.ndarray (nodes_num, nodes_num)
    :return: 巡回ルート
    :rtype: np.ndarray (nodes_num, )

    :Example:
    >>> import numpy as np
    >>> import tsp
    >>> l = [[0, 6, 3, 5, 2, 10],
    >>>     [3, 0, 5, 1, 2, 5],
    >>>     [2, 1, 0, 3, 3, 5],
    >>>     [3, 4, 2, 0, 1, 6],
    >>>     [1, 3, 4, 5, 0, 2],
    >>>     [4, 5, 7, 2, 2, 0]]
    >>> print(tsp.solve_tsp(np.array()))
    [0 4 5 3 2 1]
    """
    # ws:隣接行列
    size = ws.shape[0]

    prob = pulp.LpProblem('tsp', pulp.LpMinimize)

    # 変数の生成
    xs = []
    for i in range(size):
        # xs1 = [pulp.LpVariable('x{}_{}'.format(i, j), cat='Binary') for j in range(size)]
        xs1 = [pulp.LpVariable('x{}_{}'.format(i, j), 0, 1, cat='Integer') for j in range(size)]
        xs.append(xs1)
    us = [pulp.LpVariable('u{}'.format(i), cat='Integer', lowBound=0, upBound=size-1) for i in range(size)]

   # 目的関数
    prob += pulp.lpSum([pulp.lpDot(w, x) for w, x in zip(ws, xs)])

    # 制約条件
    for i in range(size):
        prob += pulp.lpSum(xs[j][i] for j in range(size) if i != j) == 1
        prob += pulp.lpSum(xs[i][j] for j in range(size) if i != j) == 1
    
    # 自分自身への辺は選択しない
    for i in range(size):
        prob += xs[i][i] == 0

    # 頂点に対応する変数の制約
    BigM = 9999
    for i in range(size):
        for j in range(1, size):
            if i == j: continue
            # prob += us[i] + 1 - (size - 1) * (1 - xs[i][j]) <= us[j]
            prob += us[i] + 1 - BigM * (1 - xs[i][j]) <= us[j]
    
    # スタート
    prob += us[0] == 0
    # 全ノードを回る（この制約は不要？）    
    prob += pulp.lpSum(us[i] for i in range(size)) == size*(size-1)/2

    # 解く
    status = prob.solve()

    # 巡回ルート
    route = []
    for i in range(len(us)):
        route.append(pulp.value(us[i]))
    route = np.argsort(np.array(route))
    
    # デバッグ用
    xs_array = np.zeros((len(xs), len(xs)))
    for i in range(len(xs)):
        for j in range(len(xs[i])):
            xs_array[i, j] = pulp.value(xs[i][j])
    # print(xs)

    # print(prob)

    print("")
    print("計算結果")
    print("*" * 8)
    print(f"最適性 = {pulp.LpStatus[status]}")
    print(f"目的関数値 = {pulp.value(prob.objective)}")
    print("解(巡回ルート)")
    print(route)
    print("*" * 8)

    return route

def draw_tsp_route(c, csr, route, start):
    """巡回ルートの描画

    :param c: ノード座標
    :type c: np.ndarray (nodes_num, 2)
    :param csr: 隣接行列
    :type csr: np.ndarray (nodes_num, nodes_num)
    :param route: 巡回ルート
    :type route: np.ndarray (nodes_num, )
    :param start: スタートかつゴールのノード番号(c, csrの行インデックス)
    :type start: int
    
    :return: None
    """
    # draw nodes
    plt.scatter(c[:, 0], c[:, 1], marker='o', s=200)
    for i in range(c.shape[0]):
        plt.text(c[i, 0]+0.1, c[i, 1]+0.1, i, size=20)

    # start node -> red
    plt.scatter(c[start, 0], c[start, 1], marker='o', s=200, color='red')

    # draw route
    route = np.append(route, 0)
    for i in range(len(route)-1):
            plt.annotate('', xy=(c[route[i], 0],c[route[i], 1]), xytext=(c[route[i+1], 0], c[route[i+1], 1]),
                            arrowprops=dict(arrowstyle=ArrowStyle('<|-', head_length=1, head_width=0.5)))
            plt.text((c[route[i], 0]+c[route[i+1], 0])/2, (c[route[i], 1]+c[route[i+1], 1])/2,
                        csr[ route[i], route[i+1]], color='k', size=15)

    plt.grid(which='major',color='gray',linestyle='-')
    plt.show()

def main():
    from spp import draw_graph

    c = [[0, 4],
        [0, 3],
        [2, 4],
        [1, 2],
        [3, 1],
        [4, 3]]

    l = [[0, 6, 3, 5, 2, 10],
        [3, 0, 5, 1, 2, 5],
        [2, 1, 0, 3, 3, 5],
        [3, 4, 2, 0, 1, 6],
        [1, 3, 4, 5, 0, 2],
        [4, 5, 7, 2, 2, 0]]
    
    c = np.array(c)
    l = np.array(l).astype(np.int)

    draw_graph(c, l)

    route = solve_tsp(l)

    start = 4
    print("start node:", start)

    draw_tsp_route(c, l, route, start)
    
    return

if __name__ == '__main__':
    main()