from flask import render_template, request, send_file, make_response
from main import app
from io import BytesIO
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt
import numpy as np
import urllib
import sqlite3
import json
from PIL import Image
import sys
import os
sys.path.append('../')
print(os.getcwd())
from scripts.utils import Plot_route_db
from scripts.spp import _linkmatrix, shortest_route_db
from scipy.sparse import csr_matrix

@app.route('/',methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route("/plot/<func>/<func2>")
def plot_graph(func='sin', func2 = '野洲駅'):

    # fig = Figure()
    # ax = fig.add_subplot(111)
    # xs = np.linspace(-np.pi, np.pi, 100)
    # if func == 'sin':
    #     ys = np.sin(xs)
    # elif func == 'cos':
    #     ys = np.cos(xs)
    # elif func == 'tan':
    #     ys = np.tan(xs)
    # else:
    #     ys = xs
    # ax.plot(xs, ys)

    # img = Image.open('../data/img.png')
    # ratio = 1/30*2
    # w, h = img.size
    # img = img.crop((-w*ratio, -w*ratio, w+w*ratio, h+h*ratio))
    conn = sqlite3.connect('../data/vectortile.db')
    cur = conn.cursor()

    with open('../config.json') as f:
        config = json.load(f)

    tile_coord = (config["coord"]["zoom"], config["coord"]["t_lon"], config["coord"]["t_lat"])
    table_name = f'table_{tile_coord[0]}_{tile_coord[1]}_{tile_coord[2]}'

    link_matrix,coord_matrix = _linkmatrix(cur, table_name)

    csr_link_matrix = csr_matrix(link_matrix)

    route, weight = shortest_route_db(func, func2, csr_link_matrix, cur, table_name)

    plotter = Plot_route_db(config)
    fig = plotter.draw_route(cur, table_name, route)

    canvas = FigureCanvasAgg(fig)
    png_output = BytesIO()
    canvas.print_png(png_output)
    img_data = urllib.parse.quote(png_output.getvalue())
    return img_data