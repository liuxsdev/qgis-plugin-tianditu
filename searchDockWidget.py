import os

from qgis.core import QgsProject, QgsVectorLayer, QgsGeometry, QgsFeature, QgsPointXY
from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QThread, pyqtSignal
from qgis.PyQt.QtWidgets import QTreeWidget, QTreeWidgetItem
from .utils import PluginDir, TiandituAPI
from .ui.search import Ui_SearchDockWidget
from .configSetting import ConfigFile, CONFIG_FILE_PATH


class SearchRequestThread(QThread):
    request_finished = pyqtSignal(dict)

    def __init__(self, search_type, api, data):
        super().__init__()
        self.search_type = search_type  # 搜索类型
        self.data = data  # 搜索参数
        self.api = api

    def run(self):
        if self.search_type == 'api_search_v2':
            keyword = self.data['keyword']
            r = self.api.api_search_v2(keyword)
            if r['code'] == 1:
                data = r['data']
                if data['status']['infocode'] != 0:
                    # 直接返回POI的情况
                    if data['resultType'] == 1:
                        pois = data['pois']
                        # 获取当前搜索结果所在的行政区,作为根节点
                        if 'prompt' in data:  # prompt不一定存在
                            admins = data['prompt'][0]['admins'][0]['adminName']
                        else:
                            admins = '全国'
                        self.request_finished.emit(
                            {
                                'type': 'api_search_v2:1',
                                'admins': admins,
                                'pois': pois
                            }
                        )
                    # 返回统计集合的情况
                    elif data['resultType'] == 2:
                        all_admins = (data['statistics']['allAdmins'])
                        first = all_admins[0]
                        if not first['isleaf']:
                            # 地点不精确的时候，返回的统计集合为省级。不往下继续搜索了
                            self.request_finished.emit({
                                'type': 'no_result',
                                'message': '请输入更为详细的地名'
                            })
                        else:
                            self.request_finished.emit({'type': 'api_search_v2:2', 'all_admins': all_admins})
                    else:
                        self.request_finished.emit({
                            'type': 'no_result',
                            'message': '无结果'
                        })
            else:
                self.request_finished.emit({
                    'type': 'error',
                    'message': r['message']
                })
        elif self.search_type == 'api_search_v2_admincode':
            keyword = self.data['keyword']
            admin_code = self.data['admin_code']
            r = self.api.api_search_v2(keyword, specify=admin_code)
            if r['code'] == 1:
                data = r['data']
                if data['resultType'] == 1:
                    pois = data['pois']
                    self.request_finished.emit({
                        'type': 'api_search_v2_admincode',
                        'pois': pois
                    })
        elif self.search_type == 'api_geocoder':
            keyword = self.data['keyword']
            r = self.api.api_geocoder(keyword)
            if r['code'] == 1:
                data = r['data']
                if data['msg'] == 'ok':
                    location = data['location']
                    level = location['level']
                    score = location['score']
                    lon = round(location['lon'], 6)
                    lat = round(location['lat'], 6)
                    t = f"关键词: {location['keyWord']}\n\nScore:{score}\n\n类别名称: {level}\n\n经纬度: {lon},{lat}  [添加到地图中](#)"
                else:
                    t = '请求失败'
                    self.request_finished.emit({'text': "请求失败！"})
            else:
                t = f"请求失败！{r['message']}"
            self.request_finished.emit({
                'type': 'api_geocoder',
                'text': t
            })
        elif self.search_type == 'api_regeocoder':
            lon = self.data['lon']
            lat = self.data['lat']
            r = self.api.api_regeocoder(lon, lat)
            if r['code'] == 1:
                data = r['data']
                if data['status'] == '0':
                    result = data['result']
                    formatted_address = result['formatted_address']
                    if formatted_address != '':
                        text = formatted_address
                    else:
                        text = '无结果'
                else:
                    text = '请求失败'
            else:
                text = f"请求失败！{r['message']}"
            self.request_finished.emit({
                'type': 'api_regeocoder',
                'text': text
            })


class SearchDockWidget(QtWidgets.QDockWidget, Ui_SearchDockWidget):
    def __init__(self, iface, parent=None):
        super(SearchDockWidget, self).__init__(parent)
        self.search_request_thread = None
        self.setupUi(self)
        self.iface = iface
        # 读取token
        self.cfg = ConfigFile(CONFIG_FILE_PATH)
        self.token = self.cfg.getValue('Tianditu', 'key')
        self.api = TiandituAPI(self.token)
        # 初始化treeWidget
        self.treeWidget = QTreeWidget(self.tab)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.setColumnCount(4)
        self.treeWidget.setHeaderLabels(['行政区', '地点', 'lonlat', 'admin_code'])
        self.treeWidget.setColumnHidden(2, True)
        self.treeWidget.setColumnHidden(3, True)
        self.treeWidget.setAlternatingRowColors(True)
        self.verticalLayout_2.addWidget(self.treeWidget)
        # 地名搜索
        self.pushButton.clicked.connect(self.search)
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
                self.search_request_thread = SearchRequestThread(
                    search_type="api_search_v2_admincode",
                    api=self.api,
                    data={'keyword': keyword, 'admin_code': admin_code}
                )
                self.search_request_thread.request_finished.connect(lambda data: self.on_search_complate(data, item))
                self.search_request_thread.start()
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

    def on_search_complate(self, data, item=None):
        search_type = data['type']
        if search_type == "api_search_v2:1":
            self.treeWidget.takeTopLevelItem(0)  # 移除"搜索中..."
            admins = data['admins']
            pois = data['pois']
            root = QTreeWidgetItem(self.treeWidget)
            root.setText(0, admins)
            for index, poi in enumerate(pois):
                child = QTreeWidgetItem(root)
                child.setText(0, f"{index + 1}")
                child.setText(1, poi['name'])
                child.setText(2, poi['lonlat'])
            # 展开所有节点
            self.treeWidget.expandAll()
            # item双击信号
            self.treeWidget.itemDoubleClicked.connect(self.on_treeWidget_item_double_clicked)
        elif search_type == "api_search_v2:2":
            self.treeWidget.takeTopLevelItem(0)  # 移除"搜索中..."
            all_admins = data['all_admins']
            for index, admins in enumerate(all_admins):
                root = QTreeWidgetItem(self.treeWidget)
                root.setText(0, f"{index + 1} {admins['adminName']}")
                root.setText(1, f"{admins['count']}个结果")
                root.setText(3, f"{admins['adminCode']}")
            self.treeWidget.itemDoubleClicked.connect(self.on_treeWidget_item_double_clicked)
        elif search_type == "api_search_v2_admincode":
            pois = data['pois']
            for index, poi in enumerate(pois):
                child = QTreeWidgetItem(item)
                child.setText(0, str(index + 1))
                child.setText(1, poi['name'])
                child.setText(2, poi['lonlat'])
            item.removeChild(item.child(0))
        elif search_type == 'api_geocoder':
            text = data['text']
            self.label_2.setText(text)
        elif search_type == 'api_regeocoder':
            text = data['text']
            self.label_4.setText(text)
        elif search_type == "no_result":
            self.treeWidget.takeTopLevelItem(0)  # 移除"搜索中..."
            root = QTreeWidgetItem(self.treeWidget)
            root.setText(1, data['message'])
        elif search_type == "error":
            self.treeWidget.takeTopLevelItem(0)  # 移除"搜索中..."
            root = QTreeWidgetItem(self.treeWidget)
            root.setText(1, data['message'])
            self.iface.messageBar().pushWarning(title="天地图API - Error", message=data['message'])
        else:
            self.treeWidget.takeTopLevelItem(0)  # 移除"搜索中..."
            root = QTreeWidgetItem(self.treeWidget)
            root.setText(0, f"无结果")

    def search(self):
        keyword = self.lineEdit.text()
        if len(keyword) == 0:
            return
        # 清除treeWidget数据
        self.treeWidget.clear()
        # 检查信号是否已经连接,连接的话就断开
        if self.treeWidget.receivers(self.treeWidget.itemDoubleClicked) > 0:
            self.treeWidget.itemDoubleClicked.disconnect(self.on_treeWidget_item_double_clicked)
        # 搜索
        search_progress_tip = QTreeWidgetItem(self.treeWidget)
        search_progress_tip.setText(1, '搜索中...')
        self.search_request_thread = SearchRequestThread(search_type="api_search_v2", api=self.api,
                                                         data={'keyword': keyword})
        self.search_request_thread.request_finished.connect(lambda data: self.on_search_complate(data))
        self.search_request_thread.start()

    def geocoder(self):
        keyword = self.lineEdit_2.text()
        if len(keyword) == 0:
            return
        self.label_2.setText('搜索中...')
        self.search_request_thread = SearchRequestThread(
            search_type='api_geocoder', api=self.api, data={'keyword': keyword}
        )
        self.search_request_thread.request_finished.connect(lambda data: self.on_search_complate(data))
        self.search_request_thread.start()

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
        if len(lonlat) == 0:
            return
        try:
            lon, lat = map(float, lonlat.split(','))
            self.label_4.setText("搜索中...")
            self.search_request_thread = SearchRequestThread(
                search_type='api_regeocoder', api=self.api, data={'lon': lon, 'lat': lat}
            )
            self.search_request_thread.request_finished.connect(lambda data: self.on_search_complate(data))
            self.search_request_thread.start()
        except Exception as e:
            self.iface.messageBar().pushWarning(title="天地图API - Error：经纬度输入有误", message=str(e))
