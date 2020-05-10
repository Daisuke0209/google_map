import sqlite3
import json
import random
from utils import Plot_route_db
import matplotlib.pyplot as plt
import os
from tqdm import tqdm
import matplotlib.cm as cm
from matplotlib.patches import ArrowStyle
import matplotlib.animation as animation
import numpy as np
from PIL import Image

class Indivisual():
    def __init__(self):
        self.diagnosis = []
        self.age = 0
        self.sex = "Male"
        self.route = []
        self.route_coord = []


def indiv_route(cur, table_name, node_ini = 0, time = 10):
    route = []
    node_id = node_ini

    for i in range(time):
        route.append(node_id)
        table_name_sub = table_name + '_' + str(node_id)
        cur.execute(f"SELECT neighbors FROM {table_name_sub}")
        neighbors = cur.fetchall()
        dest_node_index = random.randint(0, len(neighbors)-1)
        node_id = neighbors[dest_node_index][0]

    return route

if __name__ == '__main__':
    conn = sqlite3.connect('../data/vectortile.db')
    cur = conn.cursor()

    with open('../config.json') as f:
        config = json.load(f)

    tile_coord = (config["coord"]["zoom"], config["coord"]["t_lon"], config["coord"]["t_lat"])

    table_name = f'table_{tile_coord[0]}_{tile_coord[1]}_{tile_coord[2]}'

    img = Image.open('../data/img.png')
    h, w = img.size
    ratio = 1/30*2
    img = img.crop((-w*ratio, -w*ratio, w+w*ratio, h+h*ratio))

    cur.execute(f"SELECT * FROM {table_name}") 
    nodes = cur.fetchall()
    w, h = img.size
    lats = []
    lons = []
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(1, 1, 1)

    for i, node in enumerate(nodes):
        lats.append(node[6])
        lons.append(node[7])
    ax.scatter(lons, lats, s = 1)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    ax.imshow(img, extent=[*xlim, *ylim], alpha=0.6)
    # plt.show()

    #初期化

    class Updater():
        def __init__(self, cur, table_name, n_samples = 10, time = 10):
            self.n_samples = n_samples
            self.time = time

            indivisuals = []
            for i in tqdm(range(self.n_samples)):
                indi = Indivisual()
                indi.route = indiv_route(cur, table_name, node_ini = random.randint(0,5000), time = self.time)
                indi.diagnosis.append(random.randint(0,1))

                for node in indi.route:
                    cur.execute(f"SELECT * FROM {table_name} where id = {str(node)}") 
                    node_data = cur.fetchone()
                    indi.route_coord.append([node_data[6], node_data[7]])
                indivisuals.append(indi)

            self.indivisuals = indivisuals

        def _get_routes(self):
            routes = []
            for i in range(self.n_samples):
                routes.append(self.indivisuals[i].route)
            return np.array(routes)

        def _get(self):
            routes = self._get_routes()
            infections_index = []
            for i, indi in enumerate(self.indivisuals):
                if indi.diagnosis[0] == 1:
                    infections_index.append(i)

            for t in tqdm(range(self.time)):
                infectinos = routes[infections_index,t]
                for i, indi in enumerate(self.indivisuals):
                    if indi.route[t] in infectinos:
                        indi.diagnosis.append(1)
                        if i not in infections_index:
                            infections_index.append(i)
                    else:
                        indi.diagnosis.append(0)


    time = 1000
    n_samples = 100
    updater = Updater(cur, table_name, n_samples = n_samples, time = time)
    updater._get()

    individuals = updater.indivisuals


    def plot_scatter(t, individuals):
        y = np.zeros(len(individuals))
        lats, lons = [], []
        num_infections = 0
        for i, indi in enumerate(individuals):
            lats.append(indi.route_coord[t][0])
            lons.append(indi.route_coord[t][1])
            num_infections = num_infections + indi.diagnosis[t]
            if indi.diagnosis[t] == 1:
                y[i] = 1
            
        title = ax.text(0.5, 1.01, f'time = {t}, infectinos = {num_infections}',
                     ha='center', va='bottom',
                     transform=ax.transAxes, fontsize='large')
        im = [ax.scatter(lons, lats, c=y, cmap=cm.bwr)]+[title]
        return im
        
    ims = []

    for t in range(time):
        ims.append(plot_scatter(t, individuals))

    ani = animation.ArtistAnimation(fig, ims, interval = 250)
    plt.show()

