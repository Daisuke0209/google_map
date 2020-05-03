# モジュールのインポート
import pandas as pd
import urllib
import urllib.error
import urllib.request

# Google API モジュール
from pygeocoder import Geocoder
import googlemaps



googleapikey = 'AIzaSyAiNWxoEEoz4cD4dpXaNrpi0Df8nsKPDoA'
output_path = '../data'
pixel = '640x480'
scale = '18'

location = ["国会議事堂", "วัดพระแก้ว", "New York City", "Государственный Эрмитаж", "مكة المكرمة"]

gmaps = googlemaps.Client(key=googleapikey)
address = u'国会議事堂'
result = gmaps.geocode(address)
print(result[0]["geometry"])