from pathlib import Path
from random import choice
from urllib.parse import quote

from qgis.core import (
    Qgis,
    QgsProject,
    QgsRasterLayer,
)

PluginDir = Path(__file__).parent

tianditu_map_info = {
    "vec": "天地图-矢量地图",
    "cva": "天地图-矢量注记",
    "img": "天地图-影像地图",
    "cia": "天地图-影像注记",
    "ter": "天地图-地形晕染",
    "cta": "天地图-地形注记",
    "ibo": "天地图-全球境界",
}


def parse_referer(referer):
    current_qgis_version = Qgis.QGIS_VERSION_INT
    referer_string = ""
    if referer == "":
        return referer_string
    if current_qgis_version >= 32600:
        referer_string = f"&http-header:referer={referer}"
    else:
        referer_string = f"&referer={referer}"
    return referer_string


def add_raster_layer(raster_layer: QgsRasterLayer) -> None:
    if raster_layer.isValid():
        QgsProject.instance().addMapLayer(raster_layer)
    else:
        print("add layer field")


def create_raster_layer(
    uri: str, name: str, provider_type: str = "wms"
) -> QgsRasterLayer:
    return QgsRasterLayer(uri, name, provider_type)


def tianditu_map_url(maptype: str, token: str, subdomain: str) -> str:
    url = f"https://{subdomain}.tianditu.gov.cn/"
    url += (
        f"{maptype}_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER={maptype}"
    )
    url += "&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TileCol={x}&TileRow={y}&TileMatrix={z}"
    url += f"&tk={token}"
    return url


def get_xyz_uri(url: str, zmin: int = 0, zmax: int = 18, referer: str = "") -> str:
    url = quote(url, safe=":/?=")
    parsed_referer = parse_referer(referer)
    uri = f"type=xyz&url={url}&zmin={zmin}&zmax={zmax}{parsed_referer}"
    return uri


def create_tianditu_raster_layer(maptype: str, key: str = "您的密钥") -> QgsRasterLayer:
    subdomain = choice([f"t{i}" for i in range(8)])
    map_url = tianditu_map_url(maptype, key, subdomain)
    uri = get_xyz_uri(map_url, 1, 18, "http://lbs.tianditu.gov.cn/")
    return create_raster_layer(uri, tianditu_map_info[maptype])


def add_tianditu_basemap(maptype):
    tianditu_layer = create_tianditu_raster_layer(maptype)
    add_raster_layer(tianditu_layer)
