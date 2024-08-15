from pathlib import Path
from random import choice
from urllib.parse import quote

from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsDataItemProvider,
    QgsDataProvider,
    QgsDataCollectionItem,
    QgsDataItem,
    QgsApplication,
    QgsProject,
    QgsRasterLayer,
    Qgis,
)

PluginDir = Path(__file__).parent
icon = QIcon(str(PluginDir.joinpath("./images/tianditu_lite.svg")))

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


def add_raster_layer(uri: str, name: str, provider_type: str = "wms") -> None:
    raster_layer = QgsRasterLayer(uri, name, provider_type)
    if raster_layer.isValid():
        QgsProject.instance().addMapLayer(raster_layer)
    else:
        print("add layer field")


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


def add_tianditu_basemap(maptype):
    key = "您的密钥"
    subdomain = choice([f"t{i}" for i in range(8)])
    map_url = tianditu_map_url(maptype, key, subdomain)
    uri = get_xyz_uri(map_url, 1, 18, "http://lbs.tianditu.gov.cn/")
    add_raster_layer(uri, tianditu_map_info[maptype])


class TiandituMapItem(QgsDataItem):
    def __init__(self, parent, name, path, index):
        super().__init__(QgsDataItem.Custom, parent, name, path)
        self.setIcon(icon)
        self.setSortKey(index)  # 给他排序
        self.populate()  # set to treat Item as not-folder-like 取消展开

    def handleDoubleClick(self):
        map_key = self.path().split("Tianditu/")[1]
        add_tianditu_basemap(map_key)
        return True


class RootCollection(QgsDataCollectionItem):
    def __init__(self, iface, parent):
        self.iface = iface
        QgsDataCollectionItem.__init__(self, parent, "天地图", "/Tianditu")
        self.setIcon(icon)
        self.setSortKey("Tianditu")

    def createChildren(self):
        children = []
        for index, map_key in enumerate(tianditu_map_info):
            name = tianditu_map_info[map_key]
            item = TiandituMapItem(self, name, f"/Tianditu/{map_key}", index)
            children.append(item)
        return children


class TiandituProvider(QgsDataItemProvider):
    def __init__(self, iface):
        self.iface = iface
        self.root = None
        QgsDataItemProvider.__init__(self)

    def name(self):
        return "Tianditu"

    def capabilities(self):
        return QgsDataProvider.Net

    def createDataItem(self, path, parentItem):
        self.root = RootCollection(self.iface, parent=parentItem)
        return self.root


class TianDiTuLite:
    def __init__(self, iface):
        self.iface = iface
        self.initGui()

    def initGui(self):
        self.registProvider()

    def registProvider(self):
        """注册自定义的 QgsDataItemProvider"""
        self.removeProvider()
        t = TiandituProvider(self.iface)
        QgsApplication.instance().dataItemProviderRegistry().addProvider(t)

    def removeProvider(self):
        p = QgsApplication.instance().dataItemProviderRegistry().provider("Tianditu")
        if p:
            QgsApplication.instance().dataItemProviderRegistry().removeProvider(p)

    def unload(self):
        """Unload from the QGIS interface"""
        self.removeProvider()
