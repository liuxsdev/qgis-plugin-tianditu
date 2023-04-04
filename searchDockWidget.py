import os
from qgis.core import QgsProject, QgsVectorLayer, QgsGeometry, QgsFeature, QgsPointXY
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtWidgets import QMessageBox, QTreeWidget, QTreeWidgetItem, QLabel
from .utils import PluginDir, api_search_v2, api_geocoder
from .ui.search import Ui_SearchDockWidget
from .configSetting import ConfigFile, CONFIG_FILE_PATH


class SearchDockWidget(QtWidgets.QDockWidget, Ui_SearchDockWidget):
    def __init__(self, iface, parent=None):
        super(SearchDockWidget, self).__init__(parent)
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
        self.geocoder_result_label = QLabel(self.tab_2)
        self.verticalLayout_3.addWidget(self.geocoder_result_label)
        self.pushButton_2.clicked.connect(self.geocoder)
        self.label_2.linkActivated.connect(self.addtest)

    def on_treeWidget_item_double_clicked(self, item, _):
        # 没有子节点的根节点,根据根节点的行政区划进行搜索
        if item.childCount() == 0:
            if item.parent() is None:
                admin_code = item.text(3)
                keyword = self.lineEdit.text()
                r = api_search_v2(keyword, self.token, specify=admin_code)
                if r['resultType'] == 1:
                    pois = r['pois']
                    for index, poi in enumerate(pois):
                        child = QTreeWidgetItem(item)
                        child.setText(0, str(index + 1))
                        child.setText(1, poi['name'])
                        child.setText(2, poi['lonlat'])
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
        # 画布缩放到点 TODO：Bug 只能缩放到经纬度坐标，其他坐标系需要转成对应的坐标
        rect = layer.extent()
        # print(rect)
        self.iface.mapCanvas().setExtent(rect)
        self.iface.mapCanvas().refresh()

    def search(self):
        keyword = self.lineEdit.text()
        # 清除treeview数据
        self.treeWidget.clear()
        # TODO 加载中 使用 QThread, pyqtSignal
        # 搜索
        r = api_search_v2(keyword, self.token)
        print(r)
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
                print()
                all_admins = r['statistics']['allAdmins']
                for index, admins in enumerate(all_admins):
                    print(admins)
                    root = QTreeWidgetItem(self.treeWidget)
                    root.setText(0, f"{index + 1} {admins['adminName']}")
                    root.setText(1, f"{admins['count']}个结果")
                    root.setText(3, f"{admins['adminCode']}")
                self.treeWidget.itemDoubleClicked.connect(self.on_treeWidget_item_double_clicked)
            else:
                root = QTreeWidgetItem(self.treeWidget)
                root.setText(0, f"无结果")
        else:
            root = QTreeWidgetItem(self.treeWidget)
            root.setText(0, f"服务异常，无结果")

    def geocoder(self):
        self.geocoder_result_label.setText('')
        keyword = self.lineEdit_2.text()
        r = api_geocoder(keyword, self.token)
        print(r)
        if r['msg'] == 'ok':
            location = r['location']
            level = location['level']
            lon = round(location['lon'], 6)
            lat = round(location['lat'], 6)
            t = f"关键词：{location['keyWord']}\n\n类别名称：{level}\n\n经纬度：{lon}, {lat}  [添加到地图中]()"
            self.label_2.setText(t)

    def addtest(self):
        print(self.label_2.text())
