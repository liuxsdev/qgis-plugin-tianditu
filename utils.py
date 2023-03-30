import os

import requests

TianDiTuHomeURL = 'https://www.tianditu.gov.cn/'
PluginDir = os.path.dirname(__file__)
HEADER = {'User-Agent': 'Mozilla/5.0 QGIS/32400/Windows 10 Version 2009', 'Referer': 'https://www.tianditu.gov.cn/'}


def tianditu_map_url(maptype, token):
    url = 'https://t2.tianditu.gov.cn/'
    url += f'{maptype}_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER={maptype}'
    url += '&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TileCol={x}&TileRow={y}&TileMatrix={z}'
    url += f'&tk={token}'
    return url


def check_url_status(url):
    r = requests.get(url, headers=HEADER)
    return r.ok


def api_search_v2(keyword, token):
    # 天地图地名搜索API说明：http://lbs.tianditu.gov.cn/server/search2.html
    data = {
        "keyWord": keyword,
        "level": 18,
        "mapBound": "-180,-90,180,90",
        "queryType": 1,
        "start": 0,
        "count": 10,
        "show": 1,
    }
    payload = {'postStr': str(data), 'type': 'query', 'tk': token}
    r = requests.get('http://api.tianditu.gov.cn/v2/search', headers=HEADER, params=payload)
    return r.json() if r.ok else {'status': {'cndesc': '服务异常:', 'infocode': 0}}
