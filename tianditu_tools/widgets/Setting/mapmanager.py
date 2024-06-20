from functools import partial
from pathlib import Path

import yaml
from PyQt5.QtCore import QSize, Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtNetwork import QNetworkReply
from PyQt5.QtWidgets import QPushButton, QTreeWidget, QTreeWidgetItem
from qgis.core import QgsNetworkAccessManager

from ...utils import load_yaml, PluginConfig, make_request, HEADER

ui_font = QFont()
ui_font.setFamily("微软雅黑")
ui_font.setPointSize(8)


class MapManager(QTreeWidget):
    """
    地图管理
    """

    def __init__(
        self, map_folder: Path, parent=None, update_btn=None, status_label=None
    ):
        super().__init__(parent)
        self.map_folder = map_folder
        self.update_btn = update_btn
        self.status_label = status_label
        self.setFont(ui_font)
        self.update_host = "https://maps.liuxs.pro/dist/"
        self.update_url = f"{self.update_host}summary.yml"
        self.conf = PluginConfig()
        # self.check_update()
        # 设置 status label 的定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.clear_status_label)
        self.setupUI()

    def setupUI(self):
        self.clear()
        self.setColumnCount(3)  # 设置列
        self.setHeaderLabels(["名称", "Local", "LastUpdated", "操作"])
        self.header().setDefaultAlignment(Qt.AlignCenter)
        self.setUniformRowHeights(True)
        # 设置宽度
        self.setColumnWidth(0, 190)
        self.setColumnWidth(1, 125)
        self.setColumnWidth(2, 125)
        self.setColumnWidth(3, 90)
        self.load_map_summary()
        self.expandAll()

    def load_map_detail(self, map_id):
        mapfile_path = self.map_folder.joinpath(f"{map_id}.yml")
        data = load_yaml(mapfile_path)
        return data

    def get_summary(self):
        summary_path = self.map_folder.joinpath("summary.yml")
        return load_yaml(summary_path)

    def get_map_id_by_name(self, name):
        """通过地图名称获取 id"""
        summary = self.get_summary()
        for item in summary.values():
            if item["name"] == name:
                return item["id"]
        return None

    def load_map_summary(self):
        summary = self.get_summary()
        for value in summary.values():
            update_btn = QPushButton("更新")
            update_btn.setStyleSheet("QPushButton{margin:2px 20px;}")
            update_btn.clicked.connect(self.update_btn_clicked)
            update_btn.setEnabled(False)
            item = QTreeWidgetItem(self, [value["name"], value["lastUpdated"], "/"])
            item.setSizeHint(0, QSize(160, 28))
            item.setTextAlignment(1, Qt.AlignCenter)
            item.setTextAlignment(2, Qt.AlignCenter)
            self.setItemWidget(item, 3, update_btn)
            extra_maps_status = self.conf.get_extra_maps_status()
            map_detail = self.load_map_detail(value["id"])["maps"]
            section_maps_status = extra_maps_status[value["id"]]
            # 添加地图item
            for map_name in map_detail.keys():
                child_item = QTreeWidgetItem(item)
                child_item.setText(0, map_name)
                # 是否启用
                if map_name in section_maps_status:
                    child_item.setCheckState(0, Qt.Checked)
                else:
                    child_item.setCheckState(0, Qt.Unchecked)

            self.addTopLevelItem(item)

    def update_btn_clicked(self):
        """
        更新地图配置文件
        """
        sender_btn = self.sender()  # 获取发出信号的按钮
        if sender_btn:
            item = self.itemFromIndex(
                self.indexAt(sender_btn.pos())
            )  # 获取包含按钮的项
            if item:
                map_id = self.get_map_id_by_name(item.text(0))
                self.download_map_conf(map_id)
                # 重新禁用按钮
                update_btn = self.itemWidget(item, 3)
                update_btn.setEnabled(False)
                # 重绘UI
                self.setupUI()

    def download_map_conf(self, map_id):
        download_url = f"{self.update_host}{map_id}.yml"
        mapfile_path = self.map_folder.joinpath(f"{map_id}.yml")
        # 更新 summary
        network_manager = QgsNetworkAccessManager.instance()
        request = make_request(self.update_url)
        reply = network_manager.blockingGet(request)
        if reply.error() == QNetworkReply.NoError:
            with open(self.map_folder.joinpath("summary.yml"), "wb") as f:
                f.write(reply.content())
        request = make_request(download_url)
        reply = network_manager.blockingGet(request)
        if reply.error() == QNetworkReply.NoError:
            with open(mapfile_path, "wb") as f:
                f.write(reply.content())

    def handle_check_update_response(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NoError:
            response_data = str(reply.readAll(), "utf-8", "ignore")
            self.set_status_label("检查更新成功")
            self.update_btn.setEnabled(True)
            # print("response_data:", response_data)
            update_summary = yaml.safe_load(response_data)
            for _, map_sum in update_summary.items():
                name = map_sum["name"]
                item = self.findItems(name, Qt.MatchExactly)[0]
                item.setText(2, map_sum["lastUpdated"])
                if item.text(1) != item.text(2):
                    # 将按钮设置为启用状态
                    update_btn = self.itemWidget(item, 3)
                    update_btn.setEnabled(True)
        else:
            self.set_status_label("检查更新失败，请稍后重试...")
            # print(f"错误: {reply.errorString()},{reply.readAll()}")
            self.update_btn.setEnabled(True)
        reply.deleteLater()

    def set_status_label(self, text: str):
        self.status_label.setText(text)
        self.timer.start(2000)

    def clear_status_label(self):
        self.status_label.clear()
        self.timer.stop()

    def check_update(self):
        self.status_label.setText("检查更新中...")
        self.update_btn.setEnabled(False)
        network_manager = QgsNetworkAccessManager.instance()
        request = make_request(self.update_url, HEADER["Referer"])
        reply = network_manager.get(request)
        reply.finished.connect(partial(self.handle_check_update_response, reply))

    def update_map_enable_state(self):
        top_level_item_count = self.topLevelItemCount()
        current_status = {}
        for i in range(top_level_item_count):
            top_level_item = self.topLevelItem(i)
            map_name = top_level_item.text(0)
            map_id = self.get_map_id_by_name(map_name)
            # 获取子项的数量
            child_count = top_level_item.childCount()
            # 遍历子项
            checked_item = []
            for j in range(child_count):
                child_item = top_level_item.child(j)
                if child_item.checkState(0) == 2:
                    checked_item.append(child_item.text(0))
            current_status[map_id] = checked_item
        # 保存状态
        self.conf.set_extra_maps_status(current_status)
