import os

import requests

TianDiTuHomeURL = 'https://www.tianditu.gov.cn/'
PluginDir = os.path.dirname(__file__)


def tianditu_map_url(maptype, token):
    url = 'https://t2.tianditu.gov.cn/'
    url += f'{maptype}_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER={maptype}'
    url += '&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TileCol={x}&TileRow={y}&TileMatrix={z}'
    url += f'&tk={token}'
    return url


def check_url_status(url):
    headers = {'User-Agent': 'Mozilla/5.0 QGIS/32400/Windows 10 Version 2009',
               'Referer': 'https://www.tianditu.gov.cn/'}
    r = requests.get(url, headers=headers)
    return r.ok
