import json

from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtNetwork import QNetworkReply
from qgis.PyQt.QtWidgets import QAction, QTreeWidgetItem, QListWidgetItem
from qgis.core import QgsNetworkAccessManager

from .utils import add_raster_layer
from ..icons import icons
from ...ui.sd import Ui_SdDockWidget
from ...utils import PluginConfig, make_request


class SdDock(QtWidgets.QDockWidget, Ui_SdDockWidget):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton_search.clicked.connect(self.get_his_maps)
        self.init_tree_widget()
        self.conf = PluginConfig()
        self.tk = None
        self.pushButton_save.clicked.connect(self.save_tk)
        self.sd_tile_data = {
            "山东省影像注记": "sdrasterpubmapdj",
            "山东省电子地图": "sdpubmap",
            "山东省影像地图": "sdrasterpubmap",
        }
        self.sd_tile_LayerId = {
            "sdrasterpubmapdj": "SDRasterPubMapDJ",
            "sdpubmap": "SDPubMap",
            "sdrasterpubmap": "SDRasterPubMap",
        }
        self.init_tk()
        self.init_list_widget()

    def init_tk(self):
        self.tk = self.conf.get_value("Other/sd_tk")
        if self.tk is None:
            self.pushButton_search.setEnabled(False)
            self.listWidget.setEnabled(False)
        else:
            self.mLineEdit_sdtk.setText(self.tk)

    def init_tree_widget(self):
        self.treeWidget.setColumnWidth(0, 160)
        self.treeWidget.setColumnWidth(1, 100)
        self.treeWidget.setColumnWidth(2, 60)
        # 连接双击事件
        self.treeWidget.itemDoubleClicked.connect(self.on_item_double_clicked)
        # 启用排序功能
        self.treeWidget.setSortingEnabled(True)
        # 隐藏 url 和 el 列
        self.treeWidget.header().hideSection(3)
        self.treeWidget.header().hideSection(4)

    def save_tk(self):
        tk = self.mLineEdit_sdtk.text()
        if tk != "":
            self.conf.set_value("Other/sd_tk", tk)
            self.init_tk()
            self.pushButton_search.setEnabled(True)
            self.listWidget.setEnabled(True)

    def init_list_widget(self):
        self.listWidget.adjustSize()
        self.listWidget.itemDoubleClicked.connect(self.on_listitem_double_clicked)

        for name in self.sd_tile_data:
            item = QListWidgetItem(name)
            self.listWidget.addItem(item)

    def on_listitem_double_clicked(self, item):
        item_name = item.text()
        t_id = self.sd_tile_data[item_name]
        cap_url = f"https://service.sdmap.gov.cn/tileservice/{t_id}?tk%3D{self.tk}"
        cap_url += "%26Service%3DWMTS%26Request%3DGetCapabilities"

        uri = f"crs=EPSG:4490&dpiMode=7&format=image/jpeg&layers={self.sd_tile_LayerId[t_id]}"
        uri += f"&styles=default&tileMatrixSet=raster&tilePixelRatio=0&url={cap_url}"

        add_raster_layer(uri, item_name)

    def get_his_maps(self):
        # 获取画布中心坐标

        # 获取 Zoom Level

        # 构建查询
        network_manager = QgsNetworkAccessManager.instance()

        url = f"https://service.sdmap.gov.cn/imgmeta?wktpoint=POINT(117.7 36)&level=7&tk={self.tk}"
        request = make_request(url)
        reply = network_manager.blockingGet(request)
        if reply.error() == QNetworkReply.NoError:
            raw_data = json.loads(reply.content().data())
            # 筛选出历史影像
            # tileservice/sdrasterpubmap 添加方式不同
            his_data = [d for d in raw_data if "hisimage" in d["url"]]
            sorted_data = sorted(his_data, key=lambda x: x["st"])
            self.add_item(sorted_data)
        # 默认按照时间降序排序
        self.treeWidget.sortByColumn(1, 1)

    def add_item(self, map_data):
        self.treeWidget.clear()  # 先清空 item
        for m in map_data:
            item = QTreeWidgetItem(self.treeWidget)
            item.setText(0, m.get("name", ""))
            item.setText(1, str(m["st"]))
            item.setText(2, str(m["reso"]))
            item.setText(3, m["url"])
            item.setText(4, str(m["el"]))
            item.setTextAlignment(0, Qt.AlignCenter)
            item.setTextAlignment(1, Qt.AlignCenter)
            item.setTextAlignment(2, Qt.AlignCenter)

    @staticmethod
    def on_item_double_clicked(item):
        """
        处理双击事件
        :param item: 被双击的 QTreeWidgetItem
        """
        name = f"山东 - {item.text(0)}"
        url = item.text(3)
        el = item.text(4)

        mapid = url.split("/")[-1]
        # 为山东天地图历史影像写了一个简单的 WMTS Capabilities 生成服务
        # 源代码见 https://github.com/liuxspro/maps/tree/sd/wmts
        # 部署在 Deno Deploy
        his_wmts_server = "https://wmts.deno.dev/"
        cap_url = (
            f"{his_wmts_server}sdhis/{mapid}/{el}?tk%3Dee5c67bbafffd91385530796fb58d0f6"
        )
        uri = f"crs=EPSG:4490&format=image/png&layers={mapid}"
        uri += f"&styles=default&tileMatrixSet=default028mm&url={cap_url}"

        add_raster_layer(uri, name)


class SdAction(QAction):
    def __init__(self, iface, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.iface = iface
        self.dock = SdDock()
        self.setIcon(icons["map"])
        self.setText("天地图·山东")
        self.triggered.connect(self.open_dock)

    def open_dock(self):
        # https://qgis.org/pyqgis/master/gui/QgisInterface.html#qgis.gui.QgisInterface.addTabifiedDockWidget
        self.iface.addTabifiedDockWidget(
            Qt.RightDockWidgetArea, self.dock, ["sd"], raiseTab=True
        )
