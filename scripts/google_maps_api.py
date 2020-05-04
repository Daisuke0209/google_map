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
address = u'山科駅'
result = gmaps.geocode(address)
lat = result[0]['geometry']['location']['lat']
lng = result[0]['geometry']['location']['lng']

import requests

print(lat)
print(lng)
lat = lat  # 緯度
lon = lng # 経度

url = "http://cyberjapandata2.gsi.go.jp/general/dem/scripts/getelevation.php" \
       "?lon=%s&lat=%s&outtype=%s" %(lon, lat, "JSON")

resp = requests.get(url, timeout=10)
data = resp.json()

print(data["elevation"])