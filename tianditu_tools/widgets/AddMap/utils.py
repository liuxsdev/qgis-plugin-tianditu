from urllib.parse import quote

from qgis.core import Qgis
from qgis.core import QgsProject, QgsRasterLayer


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


def add_raster_layer(uri: str, name: str, provider_type: str = "wms") -> None:
    """QGIS 添加栅格图层

    Args:
        uri (str): 栅格图层uri
        name (str): 栅格图层名称
        provider_type(str): 栅格图层类型(wms,arcgismapserver)
    Reference: https://qgis.org/pyqgis/3.32/core/QgsRasterLayer.html
    """
    raster_layer = QgsRasterLayer(uri, name, provider_type)
    if raster_layer.isValid():
        QgsProject.instance().addMapLayer(raster_layer)
    else:
        print("add layer field")


def get_xyz_uri(url: str, zmin: int = 0, zmax: int = 18, referer: str = "") -> str:
    """返回 XYZ Tile 地图 uri

    Args:
        url (str): 瓦片地图 url
        zmin (int, optional): z 最小值. Defaults to 0.
        zmax (int, optional): z 最大值 Defaults to 18.
        referer (str, optional): Referer. Defaults to "".

    Returns:
        str: 瓦片地图uri
    """
    # "?" 进行 URL 编码后, 在 3.34 版本上无法加载地图
    # "&" 是必须要进行 url 编码的
    url = quote(url, safe=":/?=")
    parsed_referer = parse_referer(referer)
    uri = f"type=xyz&url={url}&zmin={zmin}&zmax={zmax}{parsed_referer}"
    return uri


def get_wmts_uri(uri, referer=""):
    parsed_referer = parse_referer(referer)
    return uri + parsed_referer
