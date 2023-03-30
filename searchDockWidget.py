import os
from qgis.core import QgsProject, QgsVectorLayer, QgsGeometry, QgsFeature, QgsPointXY
from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import QStringListModel, Qt
from qgis.PyQt.QtWidgets import QMessageBox
from .utils import PluginDir, api_search_v2
from .configSetting import ConfigFile, CONFIG_FILE_PATH

FORM_CLASS, _ = uic.loadUiType(os.path.join(PluginDir, './ui/search.ui'))


def add_numbers_to_items(items):
    a = []
    for i, data in enumerate(items):
        item = f'{i + 1}. {data}'
        a.append(item)
    return a


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
    # TODO：画布缩放到点/样式


def on_item_double_clicked(index, r):
    text = index.data(Qt.DisplayRole).split('. ')[1]
    pois = r['pois']
    current = [x for x in pois if x['name'] == text][0]
    # print([x for x in pois if x['name'] == text])
    # TODO 有bug
    # print(current)
    lonlat = current['lonlat']
    lon = float(lonlat.split(',')[0])
    lat = float(lonlat.split(',')[1])
    addPoint(current['name'], lon, lat)


class SearchDockWidget(QtWidgets.QDockWidget, FORM_CLASS):
    def __init__(self, parent=None):
        super(SearchDockWidget, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.search)

    def search(self):
        # 读取token
        cfg = ConfigFile(CONFIG_FILE_PATH)
        token = cfg.getValue('Tianditu', 'key')
        keyisvalid = cfg.getValueBoolean('Tianditu', 'keyisvalid')
        if token == '' or keyisvalid is False:
            QMessageBox.warning(self.toolbar, '错误', '天地图Key未设置或Key无效', QMessageBox.Yes, QMessageBox.Yes)
        else:
            keyword = self.lineEdit.text()
            r = api_search_v2(keyword, token)
            if r['resultType'] == 1:
                pois = r['pois']
                names = [x['name'] for x in pois]
                model = QStringListModel()
                model.setStringList(add_numbers_to_items(names))
                self.listView.setModel(model)
                self.listView.doubleClicked.connect(lambda index: on_item_double_clicked(index, r))
