import os
from qgis.core import QgsProject, QgsVectorLayer, QgsGeometry, QgsFeature, QgsPointXY
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QStringListModel, Qt
from qgis.PyQt.QtWidgets import QMessageBox, QTreeWidget, QTreeWidgetItem
from .utils import PluginDir, api_search_v2
from .ui.search import Ui_SearchDockWidget
from .configSetting import ConfigFile, CONFIG_FILE_PATH


def addPoint(name, x, y):
    # 定义图层
    layer = QgsVectorLayer('point?crs=epsg:4326&field=Name:string', name, 'memory')
    pr = layer.dataProvider()
    # 定义要素
    geom = QgsGeometry.fromPointXY(QgsPointXY(x, y))
    point = QgsFeature()
    point.setGeometry(geom)
    point.setAttributes([name])
    # 添加要素到图层
    pr.addFeature(point)
    # 加载图层样式
    layer.loadNamedStyle(os.path.join(PluginDir, "PointStyle.qml"))
    layer.updateExtents()
    QgsProject.instance().addMapLayer(layer)
    # TODO：画布缩放到点


def on_treeWidget_item_double_clicked(item, _, search_result):
    # _表示column,指点击的第几列，这里用不到
    # 只有子节点响应双击事件
    if item.childCount() == 0:
        print(item.text(0), item.text(1))
        num = int(item.text(0)) - 1
        current = search_result['pois'][num]
        print(current)
        lonlat = current['lonlat']
        lon, lat = map(float, lonlat.split(','))
        addPoint(current['name'], lon, lat)


class SearchDockWidget(QtWidgets.QDockWidget, Ui_SearchDockWidget):
    def __init__(self, parent=None):
        super(SearchDockWidget, self).__init__(parent)
        self.setupUi(self)
        # 读取token
        self.cfg = ConfigFile(CONFIG_FILE_PATH)
        self.token = self.cfg.getValue('Tianditu', 'key')
        self.keyisvalid = self.cfg.getValueBoolean('Tianditu', 'keyisvalid')
        if not self.token or not self.keyisvalid:
            QMessageBox.warning(self.toolbar, '错误', '天地图Key未设置或Key无效', QMessageBox.Yes, QMessageBox.Yes)

        self.pushButton.clicked.connect(self.search)
        self.treeWidget = QTreeWidget(self.tab)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.setColumnCount(3)
        self.treeWidget.setHeaderLabels(['行政区', '地点', 'lonlat'])
        # self.treeWidget.setColumnHidden(2, True)
        self.treeWidget.setAlternatingRowColors(True)
        self.verticalLayout_2.addWidget(self.treeWidget)

    def on_treeWidget_root_item_double_clicked(self, item, _, search_result):
        all_admins = search_result['statistics']['allAdmins']
        admin_index = int(item.text(0).split(' ')[0])
        # 没有子节点的根节点,根据根节点的行政区划进行搜索
        if item.childCount() == 0 and item.parent() is None:
            print(item.text(0), item.text(1))
            admin_code = all_admins[admin_index - 1]['adminCode']
            keyword = self.lineEdit.text()
            r = api_search_v2(keyword, self.token, specify=admin_code)
            if r['resultType'] == 1:
                pois = r['pois']
                # names = [x['name'] for x in pois]
                for index, poi in enumerate(pois):
                    child = QTreeWidgetItem(item)
                    child.setText(0, str(index + 1))
                    child.setText(1, poi['name'])
                    child.setText(2, poi['lonlat'])
        if item.childCount() == 0 and item.parent() is not None:
            print("点击了子节点,", item.text(0), item.text(1))
            poi_index = int(item.text(0)) - 1
            current = r['pois'][poi_index]
            lonlat = current['lonlat']
            lon, lat = map(float, lonlat.split(','))
            addPoint(current['name'], lon, lat)

    def search(self):
        keyword = self.lineEdit.text()
        # 清除treeview
        self.treeWidget.clear()
        # 搜索
        r = api_search_v2(keyword, self.token)
        print(r)
        if r['status']['infocode'] != 0:
            # 直接返回POI的情况
            if r['resultType'] == 1:
                pois = r['pois']
                names = [x['name'] for x in pois]
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
                # model = self.treeWidget.model()
                # print("count", self.treeWidget.topLevelItemCount())
                # for i in range(self.treeWidget.topLevelItemCount()):
                #     item = self.treeWidget.topLevelItem(i)
                #     for j in range(self.treeWidget.columnCount()):
                #         index = model.index(i, j)
                #         value = model.data(index)
                #         print(value)
                # item双击信号
                self.treeWidget.itemDoubleClicked.connect(
                    lambda item, _: on_treeWidget_item_double_clicked(item, _, r))
            # 返回统计集合的情况
            elif r['resultType'] == 2:
                all_admins = r['statistics']['allAdmins']
                for index, admins in enumerate(all_admins):
                    print(admins)
                    root = QTreeWidgetItem(self.treeWidget)
                    root.setText(0, f"{index + 1} {admins['adminName']}")
                    root.setText(1, f"{admins['count']}个结果")
                self.treeWidget.itemDoubleClicked.connect(
                    lambda item, _: self.on_treeWidget_root_item_double_clicked(item, _, r))
