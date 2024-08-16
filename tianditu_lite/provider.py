from qgis.PyQt.QtGui import QIcon
from qgis.core import (
    QgsDataItemProvider,
    QgsDataProvider,
    QgsDataCollectionItem,
    QgsDataItem,
    QgsMimeDataUtils,
)

from .utils import (
    PluginDir,
    add_tianditu_basemap,
    tianditu_map_info,
    create_tianditu_raster_layer,
)

icon = QIcon(str(PluginDir.joinpath("./images/tianditu_lite.svg")))


class TiandituProvider(QgsDataItemProvider):
    def __init__(self, iface):
        self.iface = iface
        QgsDataItemProvider.__init__(self)

    def name(self):
        return "Tianditu"

    def capabilities(self):
        return QgsDataProvider.Net

    def dataProviderKey(self):
        return "Tianditu"

    def createDataItem(self, path, parentItem):
        return RootCollection(self.iface, parent=parentItem)


class TiandituMapItem(QgsDataItem):
    def __init__(self, parent, name, path, index):
        super().__init__(QgsDataItem.Custom, parent, name, path)
        self.setIcon(icon)
        self.setSortKey(index)  # 给他排序
        self.populate()  # set to treat Item as not-folder-like 取消展开
        self.map_key = self.path().split("Tianditu/")[1]

    def handleDoubleClick(self):
        add_tianditu_basemap(self.map_key)
        return True

    def mimeUris(self):
        layer = create_tianditu_raster_layer(self.map_key)
        uri = QgsMimeDataUtils.Uri(layer)
        return [uri]

    def hasDragEnabled(self):
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
