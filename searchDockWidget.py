import os
from qgis.core import QgsProject, QgsVectorLayer, QgsGeometry, QgsFeature, QgsPointXY
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QStringListModel, Qt
from qgis.PyQt.QtWidgets import QMessageBox
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
    # TODO：画布缩放到点/样式


def on_item_double_clicked(index, r):
    text = index.data(Qt.DisplayRole).split('. ')[1]
    pois = r['pois']
    current = next((x for x in pois if x['name'] == text), None)
    if current:
        lonlat = current['lonlat']
        lon, lat = map(float, lonlat.split(','))
        addPoint(current['name'], lon, lat)
    # print([x for x in pois if x['name'] == text])
    # TODO 有bug
    # print(current)


class SearchDockWidget(QtWidgets.QDockWidget, Ui_SearchDockWidget):
    def __init__(self, parent=None):
        super(SearchDockWidget, self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.search)

    def search(self):
        # 读取token
        cfg = ConfigFile(CONFIG_FILE_PATH)
        token = cfg.getValue('Tianditu', 'key')
        keyisvalid = cfg.getValueBoolean('Tianditu', 'keyisvalid')
        if not token or not keyisvalid:
            QMessageBox.warning(self.toolbar, '错误', '天地图Key未设置或Key无效', QMessageBox.Yes, QMessageBox.Yes)
        else:
            keyword = self.lineEdit.text()
            r = api_search_v2(keyword, token)
            print(r)
            if r['status']['infocode'] !=0:
                if r['resultType'] == 1:
                    pois = r['pois']
                    names = [f"{i + 1}. {data['name']}" for i, data in enumerate(pois)]
                    model = QStringListModel()
                    model.setStringList(names)
                    self.listView.setModel(model)
                    self.listView.doubleClicked.connect(lambda index: on_item_double_clicked(index, r))
