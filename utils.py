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


def api_search_v2(keyword, token, specify=None):
    # 天地图地名搜索API说明：http://lbs.tianditu.gov.cn/server/search2.html
    data = {
        "keyWord": keyword,  # 搜索的关键字
        "mapBound": "-180,-90,180,90",  # 查询的地图范围(minx,miny,maxx,maxy) | -180,-90至180,90。(似乎不起作用，specify指定行政区有效)
        "level": 18,  # 目前查询的级别 | 1-18级
        "queryType": 1,  # 搜索类型 | 1:普通搜索（含地铁公交） 7：地名搜索
        "start": 0,  # 返回结果起始位（用于分页和缓存）默认0 | 0-300，表示返回结果的起始位置。
        "count": 10,  # 返回的结果数量（用于分页和缓存）| 1-300，返回结果的条数。
        "show": 1,  # 返回poi结果信息类别 | 取值为1，则返回基本poi信息;取值为2，则返回详细poi信息
    }
    if specify:
        data['specify'] = specify
    payload = {'postStr': str(data), 'type': 'query', 'tk': token}
    r = requests.get('http://api.tianditu.gov.cn/v2/search', headers=HEADER, params=payload)
    return r.json() if r.ok else {'status': {'cndesc': '服务异常:', 'infocode': 0}}


def api_geocoder(keyword, token):
    # 天地图地理编码接口API说明：http://lbs.tianditu.gov.cn/server/geocodinginterface.html
    data = {
        "keyWord": keyword,  # 搜索的关键字
    }
    payload = {'ds': str(data), 'tk': token}
    r = requests.get('http://api.tianditu.gov.cn/geocoder', headers=HEADER, params=payload)
    return r.json() if r.ok else {'status': {'cndesc': '服务异常:', 'infocode': 0}}


def api_regeocoder(lon, lat, token):
    data = {
        "lon": lon,
        "lat": lat,
        "ver": 1
    }
    payload = {'postStr': str(data), 'type': 'geocode', 'tk': token}
    r = requests.get('http://api.tianditu.gov.cn/geocoder', headers=HEADER, params=payload)
    return r.json() if r.ok else {'status': {'cndesc': '服务异常:', 'infocode': 0}}


class TiandituAPI:
    def __init__(self, token: str):
        self.token = token
        self.header = {
            'User-Agent': 'Mozilla/5.0 QGIS/32400/Windows 10 Version 2009',
            'Referer': 'https://www.tianditu.gov.cn/'
        }
