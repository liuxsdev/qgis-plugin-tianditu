TianMapInfo = {
    'vec': '天地图-矢量底图',
    'cva': '天地图-矢量注记',
    'img': '天地图-影像底图',
    'cia': '天地图-影像注记',
    'ter': '天地图-地形晕染',
    'cta': '天地图-地形注记',
    'eva': '天地图-英文矢量注记',
    'eia': '天地图-英文影像注记',
    'ibo': '天地图-全球境界'
}

extra_map = {
    'Google Map - Satellite': {
        'name': 'Google Map - Satellite',
        'url': 'http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        'zmin': 0,
        'zmax': 21,
        'referer': ''
    },
    'Google Map - Satellite(国内)': {
        'name': 'Google Map - Satellite',
        'url': 'https://gac-geo.googlecnapps.cn/maps/vt?lyrs=s&x={x}&y={y}&z={z}',
        'zmin': 0,
        'zmax': 21,
        'referer': ''
    },
    'Openstreetmap': {
        'name': 'Openstreetmap',
        'url': 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        'zmin': 0,
        'zmax': 21,
        'referer': ''
    },
    '高德地图(有偏移)': {
        'name': '高德地图',
        'url': 'http://webrd03.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
        'zmin': 0,
        'zmax': 21,
        'referer': ''
    }
}
