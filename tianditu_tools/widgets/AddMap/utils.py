import requests
from qgis.core import Qgis
from qgis.core import QgsProject, QgsRasterLayer


def add_raster_layer(uri: str, name: str, provider_type: str = "wms") -> None:
    """QGIS 添加栅格图层

    Args:
        uri (str): 栅格图层uri
        name (str): 栅格图层名称
        provider_type(str): 栅格图层类型(wms,arcgismapserver)
    Reference: https://qgis.org/pyqgis/3.32/core/QgsRasterLayer.html
    """
    raster_layer = QgsRasterLayer(uri, name, provider_type)
    QgsProject.instance().addMapLayer(raster_layer)


def get_map_uri(url: str, zmin: int = 0, zmax: int = 18, referer: str = "") -> str:
    """返回瓦片地图uri

    Args:
        url (str): 瓦片地图url
        zmin (int, optional): z 最小值. Defaults to 0.
        zmax (int, optional): z 最大值 Defaults to 18.
        referer (str, optional): Referer. Defaults to "".

    Returns:
        str: 瓦片地图uri
    """
    # "?" 进行 URL 编码后, 在 3.34 版本上无法加载地图
    # "&"是必须要进行 url 编码的
    current_qgis_version = Qgis.QGIS_VERSION_INT
    url_quote = requests.utils.quote(url, safe=":/?=")
    uri = f"type=xyz&url={url_quote}&zmin={zmin}&zmax={zmax}"
    if referer != "":
        if current_qgis_version >= 32600:
            uri += f"&http-header:referer={referer}"
        else:
            uri += f"&referer={referer}"
    return uri
