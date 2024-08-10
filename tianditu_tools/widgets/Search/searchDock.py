import json
import re

from qgis.PyQt import QtWidgets
from qgis.PyQt.QtNetwork import QNetworkReply
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
    QgsNetworkAccessManager,
)

from ...ui.search import Ui_SearchDockWidget
from ...utils import PluginDir, make_request, HEADER


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
        self.nwm = QgsNetworkAccessManager.instance()
        self.qset = QgsSettings()
        # 读取 token
        self.token = self.qset.value("tianditu-tools/Tianditu/key")
        # 初始化 treeWidget
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
                network_manager = QgsNetworkAccessManager.instance()
                data = {
                    "keyWord": keyword,  # 搜索的关键字
                    "mapBound": "-180,-90,180,90",  # 查询的地图范围(minx,miny,maxx,maxy) | -180,-90至180,90
                    "level": 18,  # 目前查询的级别 | 1-18级
                    "queryType": 1,  # 搜索类型 | 1:普通搜索（含地铁公交） 7：地名搜索
                    "start": 0,  # 返回结果起始位（用于分页和缓存）默认0 | 0-300，表示返回结果的起始位置。
                    "count": 10,  # 返回的结果数量（用于分页和缓存）| 1-300，返回结果的条数。
                    "show": 1,  # 返回poi结果信息类别 | 取值为1，则返回基本poi信息;取值为2，则返回详细poi信息
                    "specify": admin_code,  # 在指定的行政区内搜索
                }
                payload = {"postStr": str(data), "type": "query", "tk": self.token}
                url = "http://api.tianditu.gov.cn/v2/search"
                request = make_request(url, referer=HEADER["Referer"], params=payload)
                reply = network_manager.get(request)
                reply.finished.connect(lambda: self.onAdminSearchFinished(reply, item))

            else:
                name = item.text(1)
                if name == "无结果,请换关键词重试":
                    return
                lonlat = item.text(2)
                lon, lat = map(float, lonlat.split(","))
                self.addPoint(name, lon, lat)

    @staticmethod
    def onAdminSearchFinished(reply: QNetworkReply, item):
        item.removeChild(item.child(0))  # 移除搜索中
        if reply.error() == QNetworkReply.NoError:
            response_data = json.loads(str(reply.readAll(), "utf-8", "ignore"))
            pois = response_data.get("pois", None)
            if pois is None:
                # 即使普通搜索已经返回某行政区内有 n 个结果,但是继续在行政区搜索时,可能出现没有结果的情况
                # 如搜索 北京大 ,继续在河南省搜索结果为 0
                child = QTreeWidgetItem(item)
                child.setText(1, "无结果,请换关键词重试")
                return
            for index, poi in enumerate(pois):
                child = QTreeWidgetItem(item)
                child.setText(0, str(index + 1))
                child.setText(1, poi["name"])
                child.setText(2, poi["lonlat"])
        else:
            child = QTreeWidgetItem(item)
            child.setText(0, f"搜索失败{reply.errorString()}")
        reply.deleteLater()

    def addPoint(self, name, x, y):
        # 创建一个图层组，用于存放地名搜索结果
        root = QgsProject.instance().layerTreeRoot()
        group_name = "地名搜索结果"
        group = root.findGroup(group_name)
        if group is None:
            group = root.addGroup(group_name)
        # 确保图层组在第一位置
        if group:
            group_index = root.children().index(group)
            if group_index != 0:
                root.insertChildNode(0, group.clone())
                root.removeChildNode(group)
        group = root.findGroup(group_name)  # 重新拿到 group
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

    def onSearchRequestFinished(self, reply: QNetworkReply):
        self.treeWidget.takeTopLevelItem(0)  # 移除"搜索中..."
        if reply.error() == QNetworkReply.NoError:
            response_data = json.loads(str(reply.readAll(), "utf-8", "ignore"))
        else:
            root = QTreeWidgetItem(self.treeWidget)
            root.setText(0, "错误")
            root.setText(1, f"{reply.errorString()}")
            return

        if response_data["resultType"] == 1:
            # 获取当前搜索结果所在的行政区,作为根节点
            if "prompt" in response_data:  # prompt不一定存在
                admins = response_data["prompt"][0]["admins"][0]["adminName"]
            else:
                admins = "全国"
            pois = response_data.get("pois", None)  # POI 可能不存在
            root = QTreeWidgetItem(self.treeWidget)
            if pois is None:
                root.setText(0, "无结果")
                return
            root.setText(0, f"{admins}")
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
        elif response_data["resultType"] == 2:
            # 有多个搜索结果, 返回统计集合的情况
            # 行政区+结果数,双击item在当前行政区搜索
            all_admins = response_data["statistics"]["allAdmins"]
            for index, admins in enumerate(all_admins):
                root = QTreeWidgetItem(self.treeWidget)
                root.setText(0, f"{index + 1} {admins['adminName']}")
                root.setText(1, f"{admins['count']}个结果")
                root.setText(3, f"{admins['adminCode']}")
            self.treeWidget.itemDoubleClicked.connect(
                self.on_treeWidget_item_double_clicked
            )
        elif response_data.get("resultType") == 3:
            # 行政区划类型
            # 返回的是行政区划政府所在点
            area_data = response_data["area"]
            root = QTreeWidgetItem(self.treeWidget)
            root.setText(0, "行政区")

            child = QTreeWidgetItem(root)
            child.setText(0, "1")
            child.setText(1, area_data["name"])
            child.setText(2, area_data["lonlat"])

            self.treeWidget.expandAll()
            self.treeWidget.itemDoubleClicked.connect(
                self.on_treeWidget_item_double_clicked
            )
        else:
            root = QTreeWidgetItem(self.treeWidget)
            root.setText(0, "未知类型")
            print(response_data)
        reply.deleteLater()

    def search(self):
        """
        天地图地名搜索V2.0 http://lbs.tianditu.gov.cn/server/search2.html
        暂时只实现了 普通搜索服务
        """
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
        data = {
            "keyWord": keyword,  # 搜索的关键字
            "mapBound": "-180,-90,180,90",  # 查询的地图范围(minx,miny,maxx,maxy) | -180,-90至180,90
            "level": 18,  # 目前查询的级别 | 1-18级
            "queryType": 1,  # 搜索类型 | 1:普通搜索（含地铁公交） 7：地名搜索
            "start": 0,  # 返回结果起始位（用于分页和缓存）默认0 | 0-300，表示返回结果的起始位置。
            "count": 10,  # 返回的结果数量（用于分页和缓存）| 1-300，返回结果的条数。
            "show": 1,  # 返回poi结果信息类别 | 取值为1，则返回基本poi信息;取值为2，则返回详细poi信息
        }
        payload = {"postStr": str(data), "type": "query", "tk": self.token}
        url = "http://api.tianditu.gov.cn/v2/search"
        request = make_request(url, referer=HEADER["Referer"], params=payload)
        reply = self.nwm.get(request)
        reply.finished.connect(lambda: self.onSearchRequestFinished(reply))

    def onGeocoderRequestFinished(self, reply: QNetworkReply):
        """
        天地图地理编码接口
        API说明: http://lbs.tianditu.gov.cn/server/geocodinginterface.html
        返回结果示例
        {'msg': '无结果', 'searchVersion': '6.4.9V', 'status': '404'}
        {'msg': 'ok', 'location': {...}, 'searchVersion': '6.4.9V', 'status': '0'}
        """
        t = "请求失败"
        if reply.error() == QNetworkReply.NoError:
            response_data = json.loads(str(reply.readAll(), "utf-8", "ignore"))
            if response_data["msg"] == "ok":
                location = response_data["location"]
                level = location["level"]
                score = location["score"]
                lon = round(float(location["lon"]), 6)
                lat = round(float(location["lat"]), 6)
                style = (
                    "<style>p { margin: 0; padding: 5px 0;} span {color:blue}</style>"
                )
                t = f"{style}<p><span>关键词</span>: {location['keyWord']}"
                t += f"<p><span>Score</span>:{score}</p>"
                t += f"<p><span>类别名称</span>: {level}</p>"
                _link = '<a href="#">添加到地图中</a>'
                t += f"<span>经纬度</span>: {lon},{lat} {_link} "
            elif response_data["msg"] == "无结果":
                t = "无结果"
        self.label_2.setText(t)
        reply.deleteLater()

    def geocoder(self):
        keyword = self.lineEdit_2.text()
        if len(keyword) == 0:
            return
        self.label_2.setText("搜索中...")
        url = "http://api.tianditu.gov.cn/geocoder"
        data = {"keyWord": keyword}
        payload = {"ds": str(data), "tk": self.token}
        request = make_request(url, referer=HEADER["Referer"], params=payload)
        reply = self.nwm.get(request)
        reply.finished.connect(lambda: self.onGeocoderRequestFinished(reply))

    def geocoder_result_link_clicked(self):
        text = self.label_2.text()
        name = text.split("<span>关键词</span>:")[1].split("<")[0].strip()
        pattern = r"经纬度</span>: ([\d\.]+),([\d\.]+)"
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

    def onRegeocoderRequestFinished(self, reply: QNetworkReply):
        """
        天地图逆地理编码接口
        API说明: http://lbs.tianditu.gov.cn/server/geocoding.html
        """
        text = "请求失败"
        if reply.error() == QNetworkReply.NoError:
            response_data = json.loads(str(reply.readAll(), "utf-8", "ignore"))
            if response_data["status"] == "0":
                result = response_data["result"]
                formatted_address = result["formatted_address"]
                if formatted_address != "":
                    text = formatted_address
                else:
                    text = "无结果"
        self.label_4.setText(text)
        reply.deleteLater()

    def regeocoder(self):
        lonlat = self.lineEdit_3.text()
        if len(lonlat) == 0:
            return
        try:
            lon, lat = map(float, lonlat.split(","))
            self.label_4.setText("搜索中...")
            url = "http://api.tianditu.gov.cn/geocoder"
            data = {"lon": lon, "lat": lat, "ver": 1}
            payload = {"postStr": str(data), "type": "geocode", "tk": self.token}
            request = make_request(url, referer=HEADER["Referer"], params=payload)
            reply = self.nwm.get(request)
            reply.finished.connect(lambda: self.onRegeocoderRequestFinished(reply))
        except ValueError as e:
            self.iface.messageBar().pushWarning(
                title="天地图API - Error: 经纬度输入有误", message=str(e)
            )
