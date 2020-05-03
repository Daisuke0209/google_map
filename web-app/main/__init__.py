from flask import Flask
from flask_googlemaps import GoogleMaps

app = Flask(__name__)
GoogleMaps(app, key="AIzaSyAiNWxoEEoz4cD4dpXaNrpi0Df8nsKPDoA")

import main.views