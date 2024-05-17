import re

from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QThread, pyqtSignal
from qgis.PyQt.QtWidgets import QTreeWidget, QTreeWidgetItem
from qgis.core import Qgis
from qgis.core import (
    QgsFeature,
    QgsProject,
    QgsSettings,
    QgsVectorLayer,
    QgsPointXY,
    QgsGeometry,
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
)

from ...ui.search import Ui_SearchDockWidget
from ...utils import PluginDir, TiandituAPI


class SearchRequestThread(QThread):
    request_finished = pyqtSignal(dict)

    def __init__(self, search_type, api, data):
        super().__init__()
        self.search_type = search_type  # 搜索类型
        self.data = data  # 搜索参数
        self.api = api

    def handle_response_api_search_v2(self, response):
        if response["code"] == 1:
            data = response["data"]
            if data["status"]["infocode"] != 0:
                # 直接返回POI的情况
                if data["resultType"] == 1:
                    pois = data["pois"]
                    # 获取当前搜索结果所在的行政区,作为根节点
                    if "prompt" in data:  # prompt不一定存在
                        admins = data["prompt"][0]["admins"][0]["adminName"]
                    else:
                        admins = "全国"
                    self.request_finished.emit(
                        {"type": "api_search_v2:1", "admins": admins, "pois": pois}
                    )
                # 返回统计集合的情况
                elif data["resultType"] == 2:
                    all_admins = data["statistics"]["allAdmins"]
                    first = all_admins[0]
                    if not first["isleaf"]:
                        # 地点不精确的时候，返回的统计集合为省级。不往下继续搜索了
                        self.request_finished.emit(
                            {"type": "no_result", "message": "请输入更为详细的地名"}
                        )
                    else:
                        self.request_finished.emit(
                            {"type": "api_search_v2:2", "all_admins": all_admins}
                        )
                else:
                    self.request_finished.emit(
                        {"type": "no_result", "message": "无结果"}
                    )
        else:
            self.request_finished.emit(
                {"type": "error", "message": response["message"]}
            )

    def handle_response_api_search_v2_admincode(self, response):
        if response["code"] == 1:
            data = response["data"]
            if data["resultType"] == 1:
                pois = data["pois"]
                self.request_finished.emit(
                    {"type": "api_search_v2_admincode", "pois": pois}
                )

    def handle_response_api_geocoder(self, response):
        if response["code"] == 1:
            data = response["data"]
            if data["msg"] == "ok":
                location = data["location"]
                level = location["level"]
                score = location["score"]
                lon = round(float(location["lon"]), 6)
                lat = round(float(location["lat"]), 6)
                t = f"<p>关键词: {location['keyWord']}</p><p>Score:{score}</p><p>类别名称: {level}</p>"
                _link = '<a href="#">添加到地图中</a>'
                t += f"经纬度: {lon},{lat} {_link} "
            else:
                t = "请求失败"
                self.request_finished.emit({"text": "请求失败！"})
        else:
            t = f"请求失败！{response['message']}"
        self.request_finished.emit({"type": "api_geocoder", "text": t})

    def handle_response_api_regeocoder(self, response):
        if response["code"] == 1:
            data = response["data"]
            if data["status"] == "0":
                result = data["result"]
                formatted_address = result["formatted_address"]
                if formatted_address != "":
                    text = formatted_address
                else:
                    text = "无结果"
            else:
                text = "请求失败"
        else:
            text = f"请求失败！{response['message']}"
        self.request_finished.emit({"type": "api_regeocoder", "text": text})

    def run(self):
        if self.search_type == "api_search_v2":
            keyword = self.data["keyword"]
            r = self.api.api_search_v2(keyword)
            self.handle_response_api_search_v2(r)
        elif self.search_type == "api_search_v2_admincode":
            keyword = self.data["keyword"]
            admin_code = self.data["admin_code"]
            r = self.api.api_search_v2(keyword, specify=admin_code)
            self.handle_response_api_search_v2_admincode(r)
        elif self.search_type == "api_geocoder":
            keyword = self.data["keyword"]
            r = self.api.api_geocoder(keyword)
            self.handle_response_api_geocoder(r)
        elif self.search_type == "api_regeocoder":
            lon = self.data["lon"]
            lat = self.data["lat"]
            r = self.api.api_regeocoder(lon, lat)
            self.handle_response_api_regeocoder(r)


def create_point_layer(name: str, point: QgsPointXY, crs: str):
    layer = QgsVectorLayer(f"Point?crs={crs}&field=Name:string", name, "memory")
    pr = layer.dataProvider()
    point_feature = QgsFeature()
    point_feature.setGeometry(QgsGeometry.fromPointXY(point))
    point_feature.setAttributes([name])
    pr.addFeature(point_feature)
    return layer


class SearchDockWidget(QtWidgets.QDockWidget, Ui_SearchDockWidget):
    def __init__(self, iface):
        super().__init__()
        self.search_request_thread = None
        self.setupUi(self)
        self.iface = iface
        self.qset = QgsSettings()
        # 读取token
        self.token = self.qset.value("tianditu-tools/Tianditu/key")
        self.api = TiandituAPI(self.token)
        # 初始化treeWidget
        self.treeWidget = QTreeWidget(self.tab)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.setColumnCount(4)
        self.treeWidget.setHeaderLabels(["行政区", "地点", "lonlat", "admin_code"])
        self.treeWidget.setColumnHidden(2, True)
        self.treeWidget.setColumnHidden(3, True)
        self.treeWidget.setAlternatingRowColors(True)
        self.verticalLayout_2.addWidget(self.treeWidget)
        # 地名搜索
        self.pushButton.clicked.connect(self.search)
        # 地理编码查询
        self.pushButton_2.clicked.connect(self.geocoder)
        self.label_2.linkActivated.connect(self.geocoder_result_link_clicked)
        # 逆地理编码查询
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
                    data={"keyword": keyword, "admin_code": admin_code},
                )
                self.search_request_thread.request_finished.connect(
                    lambda data: self.on_search_complete(data, item)
                )
                self.search_request_thread.start()
            else:
                name = item.text(1)
                lonlat = item.text(2)
                lon, lat = map(float, lonlat.split(","))
                self.addPoint(name, lon, lat)

    def addPoint(self, name, x, y):
        # 创建一个图层组，用于存放地名搜索结果
        root = QgsProject.instance().layerTreeRoot()
        group_name = "地名搜索结果"
        group = root.findGroup(group_name)
        if group is None:
            group = root.addGroup(group_name)
        # 确保图层组在第一位置
        if group:
            group_index = root.Children().index(group)
            if group_index != 0:
                root.insertChildNode(0, group.clone())
                root.removeChildNode(group)
        # 定义图层
        raw_point = QgsPointXY(x, y)
        # 当前工程坐标系
        current_project_crs = QgsProject.instance().crs()
        # 定义坐标转换
        coord_trans = QgsCoordinateTransform(
            QgsCoordinateReferenceSystem("EPSG:4326"),
            current_project_crs,
            QgsProject.instance(),
        )
        projected_point = coord_trans.transform(raw_point)
        raw_layer = create_point_layer(name, raw_point, "EPSG:4326")
        # 此图层用于缩放到点
        layer = create_point_layer(name, projected_point, current_project_crs.authid())
        group.addLayer(raw_layer)
        # 加载图层样式
        # 根据QGIS版本设置不同的样式
        current_qgis_version = Qgis.QGIS_VERSION_INT
        if current_qgis_version <= 31616:
            raw_layer.loadNamedStyle(
                str(PluginDir.joinpath("./Styles/PointStyle_316.qml"))
            )
        else:
            raw_layer.loadNamedStyle(str(PluginDir.joinpath("./Styles/PointStyle.qml")))
        raw_layer.updateExtents()
        QgsProject.instance().addMapLayer(raw_layer, False)
        # 画布缩放到点
        rect = layer.extent()
        self.iface.mapCanvas().setExtent(rect)
        self.iface.mapCanvas().zoomScale(18056)  # 设置缩放等级, setExtent的缩放等级太大
        self.iface.mapCanvas().refresh()

    def on_search_complete(self, data, item=None):
        search_type = data["type"]
        if search_type == "api_search_v2:1":
            self.treeWidget.takeTopLevelItem(0)  # 移除"搜索中..."
            admins = data["admins"]
            pois = data["pois"]
            root = QTreeWidgetItem(self.treeWidget)
            root.setText(0, admins)
            for index, poi in enumerate(pois):
                child = QTreeWidgetItem(root)
                child.setText(0, f"{index + 1}")
                child.setText(1, poi["name"])
                child.setText(2, poi["lonlat"])
            # 展开所有节点
            self.treeWidget.expandAll()
            # item双击信号
            self.treeWidget.itemDoubleClicked.connect(
                self.on_treeWidget_item_double_clicked
            )
        elif search_type == "api_search_v2:2":
            self.treeWidget.takeTopLevelItem(0)  # 移除"搜索中..."
            all_admins = data["all_admins"]
            for index, admins in enumerate(all_admins):
                root = QTreeWidgetItem(self.treeWidget)
                root.setText(0, f"{index + 1} {admins['adminName']}")
                root.setText(1, f"{admins['count']}个结果")
                root.setText(3, f"{admins['adminCode']}")
            self.treeWidget.itemDoubleClicked.connect(
                self.on_treeWidget_item_double_clicked
            )
        elif search_type == "api_search_v2_admincode":
            pois = data["pois"]
            for index, poi in enumerate(pois):
                child = QTreeWidgetItem(item)
                child.setText(0, str(index + 1))
                child.setText(1, poi["name"])
                child.setText(2, poi["lonlat"])
            item.removeChild(item.child(0))
        elif search_type == "api_geocoder":
            text = data["text"]
            self.label_2.setText(text)
        elif search_type == "api_regeocoder":
            text = data["text"]
            self.label_4.setText(text)
        elif search_type == "no_result":
            self.treeWidget.takeTopLevelItem(0)  # 移除"搜索中..."
            root = QTreeWidgetItem(self.treeWidget)
            root.setText(1, data["message"])
        elif search_type == "error":
            self.treeWidget.takeTopLevelItem(0)  # 移除"搜索中..."
            root = QTreeWidgetItem(self.treeWidget)
            root.setText(1, data["message"])
            self.iface.messageBar().pushWarning(
                title="天地图API - Error", message=data["message"]
            )
        else:
            self.treeWidget.takeTopLevelItem(0)  # 移除"搜索中..."
            root = QTreeWidgetItem(self.treeWidget)
            root.setText(0, "无结果")

    def search(self):
        keyword = self.lineEdit.text()
        if len(keyword) == 0:
            return
        # 清除treeWidget数据
        self.treeWidget.clear()
        # 检查信号是否已经连接,连接的话就断开
        if self.treeWidget.receivers(self.treeWidget.itemDoubleClicked) > 0:
            self.treeWidget.itemDoubleClicked.disconnect(
                self.on_treeWidget_item_double_clicked
            )
        # 搜索
        search_progress_tip = QTreeWidgetItem(self.treeWidget)
        search_progress_tip.setText(1, "搜索中...")
        self.search_request_thread = SearchRequestThread(
            search_type="api_search_v2", api=self.api, data={"keyword": keyword}
        )
        self.search_request_thread.request_finished.connect(self.on_search_complete)
        self.search_request_thread.start()

    def geocoder(self):
        keyword = self.lineEdit_2.text()
        if len(keyword) == 0:
            return
        self.label_2.setText("搜索中...")
        self.search_request_thread = SearchRequestThread(
            search_type="api_geocoder", api=self.api, data={"keyword": keyword}
        )
        self.search_request_thread.request_finished.connect(self.on_search_complete)
        self.search_request_thread.start()

    def geocoder_result_link_clicked(self):
        text = self.label_2.text()
        name = text.split("关键词:")[1].split("<")[0].strip()
        pattern = r"经纬度: ([\d\.]+),([\d\.]+)"
        match = re.search(pattern, text)
        # 如果匹配成功，则提取经纬度信息
        if match:
            longitude = float(match.group(1))
            latitude = float(match.group(2))
            self.addPoint(name, longitude, latitude)
        else:
            self.iface.messageBar().pushWarning(
                title="天地图API - Error: ", message="添加地图点失败"
            )

    def regeocoder(self):
        lonlat = self.lineEdit_3.text()
        if len(lonlat) == 0:
            return
        try:
            lon, lat = map(float, lonlat.split(","))
            self.label_4.setText("搜索中...")
            self.search_request_thread = SearchRequestThread(
                search_type="api_regeocoder",
                api=self.api,
                data={"lon": lon, "lat": lat},
            )
            self.search_request_thread.request_finished.connect(self.on_search_complete)
            self.search_request_thread.start()
        except ValueError as e:
            self.iface.messageBar().pushWarning(
                title="天地图API - Error: 经纬度输入有误", message=str(e)
            )
