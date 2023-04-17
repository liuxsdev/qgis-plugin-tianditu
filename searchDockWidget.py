import os

from qgis.core import QgsProject, QgsVectorLayer, QgsGeometry, QgsFeature, QgsPointXY
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QThread, pyqtSignal
from qgis.PyQt.QtWidgets import QMessageBox, QTreeWidget, QTreeWidgetItem
from .utils import PluginDir, api_search_v2, api_geocoder, api_regeocoder
from .ui.search import Ui_SearchDockWidget
from .configSetting import ConfigFile, CONFIG_FILE_PATH


class RegeocoderRequestThread(QThread):
    request_finished = pyqtSignal(str)

    def run(self):
        r = api_regeocoder(self.lon, self.lat, self.token)
        if r['status'] == '0':
            result = r['result']
            formatted_address = result['formatted_address']
            if formatted_address != '':
                self.request_finished.emit(formatted_address)
            else:
                self.request_finished.emit("无结果")
        else:
            self.request_finished.emit("请求失败！")


class GeocoderRequestThread(QThread):
    request_finished = pyqtSignal(str)

    def run(self):
        r = api_geocoder(self.keyword, self.token)
        if r['msg'] == 'ok':
            location = r['location']
            level = location['level']
            score = location['score']
            lon = round(location['lon'], 6)
            lat = round(location['lat'], 6)
            t = f"关键词: {location['keyWord']}\n\nScore:{score}\n\n类别名称: {level}\n\n经纬度: {lon},{lat}  [添加到地图中](#)"
            self.request_finished.emit(t)
        else:
            self.request_finished.emit("请求失败！")


class SearchWithAdminCodeThread(QThread):
    search_complete = pyqtSignal(list)

    def __init__(self, keyword, token, admin_code):
        super().__init__()
        self.keyword = keyword
        self.token = token
        self.admin_code = admin_code

    def run(self):
        r = api_search_v2(self.keyword, self.token, specify=self.admin_code)
        if r['resultType'] == 1:
            pois = r['pois']
            self.search_complete.emit(pois)


def do_nothing():
    pass


def handle_search_complete(item, pois):
    """添加搜索结果至item"""
    for index, poi in enumerate(pois):
        child = QTreeWidgetItem(item)
        child.setText(0, str(index + 1))
        child.setText(1, poi['name'])
        child.setText(2, poi['lonlat'])
    item.removeChild(item.child(0))


class SearchDockWidget(QtWidgets.QDockWidget, Ui_SearchDockWidget):
    def __init__(self, iface, parent=None):
        super(SearchDockWidget, self).__init__(parent)
        self.thread_request_search2 = None
        self.setupUi(self)
        self.iface = iface
        # 读取token
        self.cfg = ConfigFile(CONFIG_FILE_PATH)
        self.token = self.cfg.getValue('Tianditu', 'key')
        self.keyisvalid = self.cfg.getValueBoolean('Tianditu', 'keyisvalid')
        if not self.token or not self.keyisvalid:
            self.iface.messageBar().pushMessage("天地图Key未设置或Key无效")
            QMessageBox.warning(self.iface.mainWindow(), '错误', '天地图Key未设置或Key无效', QMessageBox.Yes,
                                QMessageBox.Yes)

        self.pushButton.clicked.connect(self.search)
        self.treeWidget = QTreeWidget(self.tab)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.setColumnCount(4)
        self.treeWidget.setHeaderLabels(['行政区', '地点', 'lonlat', 'admin_code'])
        self.treeWidget.setColumnHidden(2, True)
        self.treeWidget.setColumnHidden(3, True)
        self.treeWidget.setAlternatingRowColors(True)
        self.verticalLayout_2.addWidget(self.treeWidget)
        # 地理编码查询
        self.pushButton_2.clicked.connect(self.geocoder)
        self.label_2.linkActivated.connect(self.geocoder_result_link_clicked)
        self.request_geocoder = None
        # 逆地理编码查询
        self.request_regeocoder = None
        self.pushButton_3.clicked.connect(self.regeocoder)

    def on_treeWidget_item_double_clicked(self, item, _):
        # 没有子节点的根节点,根据根节点的行政区划进行搜索,行政区划代码在第4列(index=3)
        if item.childCount() == 0:
            if item.parent() is None:
                admin_code = item.text(3)
                keyword = self.lineEdit.text()
                search_progress_tip_item = QTreeWidgetItem(item)
                search_progress_tip_item.setText(1, "搜索中...")
                self.thread_request_search2 = SearchWithAdminCodeThread(keyword, self.token, admin_code)
                self.thread_request_search2.search_complete.connect(lambda pois: handle_search_complete(item, pois))
                self.thread_request_search2.start()
            else:
                name = item.text(1)
                lonlat = item.text(2)
                lon, lat = map(float, lonlat.split(','))
                self.addPoint(name, lon, lat)

    def addPoint(self, name, x, y):
        # 创建一个图层组，用于存放地名搜索结果
        root = QgsProject.instance().layerTreeRoot()
        group_name = '地名搜索结果'
        group = root.findGroup(group_name)
        if group is None:
            group = root.addGroup(group_name)
        # 定义图层
        layer = QgsVectorLayer('point?crs=epsg:4326&field=Name:string', name, 'memory')
        pr = layer.dataProvider()
        # 定义要素
        geom = QgsGeometry.fromPointXY(QgsPointXY(x, y))
        point = QgsFeature()
        point.setGeometry(geom)
        point.setAttributes([name])
        # 添加要素到图层
        group.addLayer(layer)
        pr.addFeature(point)
        # 加载图层样式
        layer.loadNamedStyle(os.path.join(PluginDir, "PointStyle.qml"))
        layer.updateExtents()
        QgsProject.instance().addMapLayer(layer, False)
        # 画布缩放到点 TODO：Bug 只能缩放到经纬度坐标，其他坐标系需要转成对应坐标系下的坐标
        # rect = layer.extent()
        # self.iface.mapCanvas().setExtent(rect)
        self.iface.mapCanvas().refresh()

    def search(self):
        keyword = self.lineEdit.text()
        # 清除treeview数据
        self.treeWidget.clear()
        # 检查信号是否已经连接,连接的话就断开
        if self.treeWidget.receivers(self.treeWidget.itemDoubleClicked) > 0:
            self.treeWidget.itemDoubleClicked.disconnect(self.on_treeWidget_item_double_clicked)
        # TODO 加载中 使用 QThread, pyqtSignal
        # 搜索
        r = api_search_v2(keyword, self.token)
        if r['status']['infocode'] != 0:
            # 直接返回POI的情况
            if r['resultType'] == 1:
                pois = r['pois']
                # 获取当前搜索结果所在的行政区,作为根节点
                admins = r['prompt'][0]['admins'][0]['adminName']
                root = QTreeWidgetItem(self.treeWidget)
                root.setText(0, admins)
                # 向根节点填充数据
                for index, poi in enumerate(pois):
                    child = QTreeWidgetItem(root)
                    child.setText(0, str(index + 1))
                    child.setText(1, poi['name'])
                    child.setText(2, poi['lonlat'])
                # 展开所有节点
                self.treeWidget.expandAll()
                # item双击信号
                self.treeWidget.itemDoubleClicked.connect(self.on_treeWidget_item_double_clicked)
            # 返回统计集合的情况
            elif r['resultType'] == 2:
                all_admins = r['statistics']['allAdmins']
                for index, admins in enumerate(all_admins):
                    root = QTreeWidgetItem(self.treeWidget)
                    root.setText(0, f"{index + 1} {admins['adminName']}")
                    root.setText(1, f"{admins['count']}个结果")
                    root.setText(3, f"{admins['adminCode']}")
                self.treeWidget.itemDoubleClicked.connect(self.on_treeWidget_item_double_clicked)
            # TODO 返回行政区的情况
            else:
                root = QTreeWidgetItem(self.treeWidget)
                root.setText(0, f"无结果")
        else:
            root = QTreeWidgetItem(self.treeWidget)
            root.setText(0, f"服务异常，无结果")

    def geocoder(self):
        self.label_2.setText('搜索中...')
        keyword = self.lineEdit_2.text()
        self.request_geocoder = GeocoderRequestThread()
        self.request_geocoder.keyword = keyword
        self.request_geocoder.token = self.token
        self.request_geocoder.request_finished.connect(self.label_2.setText)
        self.request_geocoder.start()

    def geocoder_result_link_clicked(self):
        text = self.label_2.text()
        a_ = text.split('Score:')[0]
        name = a_.split('关键词: ')[1].strip()
        b_ = text.split('经纬度: ')[1]
        lonlat = b_.split('  [添加到地图中](#)')[0]
        lon, lat = map(float, lonlat.split(','))
        self.addPoint(name, lon, lat)

    def regeocoder(self):
        lonlat = self.lineEdit_3.text()
        try:
            lon, lat = map(float, lonlat.split(','))
            self.label_4.setText("搜索中...")
            self.request_regeocoder = RegeocoderRequestThread()
            self.request_regeocoder.token = self.token
            self.request_regeocoder.lon = lon
            self.request_regeocoder.lat = lat
            self.request_regeocoder.request_finished.connect(self.label_4.setText)
            self.request_regeocoder.start()
        except Exception as e:
            QMessageBox.warning(self.iface.mainWindow(), '错误', '经纬度输入有误', QMessageBox.Yes, QMessageBox.Yes)
            print(e)
