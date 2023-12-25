from pathlib import Path

import requests
import yaml
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QTreeWidget, QTreeWidgetItem

from tianditu_tools.utils import load_yaml, PluginConfig


class MapManager(QTreeWidget):
    """
    地图管理
    """

    def __init__(
            self,
            map_folder: Path,
            parent=None,
    ):
        super().__init__(parent)
        self.map_folder = map_folder
        self.font = QFont()
        self.font.setFamily("微软雅黑")
        self.font.setPointSize(8)
        self.setFont(self.font)
        self.update_url = "https://maps-tan-phi.vercel.app/dist/summary.yml"
        self.conf = PluginConfig()
        # self.check_update()
        self.setupUI()

    def setupUI(self):
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
        """
        通过地图名称获取id
        """
        summary = self.get_summary()
        for key, item in summary.items():
            if item["name"] == name:
                return item["id"]
        return None

    def load_map_summary(self):
        summary = self.get_summary()
        for key, value in summary.items():
            update_btn = QPushButton("更新")
            update_btn.setStyleSheet("QPushButton{margin:2px 20px;}")
            update_btn.setEnabled(False)
            item = QTreeWidgetItem(self, [value["name"], value["lastUpdated"], "/"])

            item.setSizeHint(0, QSize(160, 28))
            item.setTextAlignment(1, Qt.AlignCenter)
            item.setTextAlignment(2, Qt.AlignCenter)
            self.setItemWidget(item, 3, update_btn)
            extra_maps_status = self.conf.get_extra_maps_status()
            map_detail = self.load_map_detail(value["id"])["maps"]
            section_maps_status = extra_maps_status[value["id"]]
            for map_name in map_detail.keys():
                child_item = QTreeWidgetItem(item)
                child_item.setText(0, map_name)
                # 是否启用
                if map_name in section_maps_status:
                    child_item.setCheckState(0, Qt.Checked)
                else:
                    child_item.setCheckState(0, Qt.Unchecked)

            self.addTopLevelItem(item)

    def check_update(self):
        r = requests.get(self.update_url, timeout=8)
        update_summary = yaml.safe_load(r.text)
        for _, map_sum in update_summary.items():
            print(map_sum)
            name = map_sum["name"]
            item = self.findItems(name, Qt.MatchExactly)[0]
            item.setText(2, map_sum["lastUpdated"])

    def update_map_enable_state(self):
        top_level_item_count = self.topLevelItemCount()
        checked_item = []
        current_status = {}
        for i in range(top_level_item_count):
            top_level_item = self.topLevelItem(i)
            map_name = top_level_item.text(0)
            map_id = self.get_map_id_by_name(map_name)
            # 获取子项的数量
            child_count = top_level_item.childCount()
            # 遍历子项
            for j in range(child_count):
                child_item = top_level_item.child(j)
                if child_item.checkState(0) == 2:
                    checked_item.append(child_item.text(0))
            current_status[map_id] = checked_item
        # 保存状态
        self.conf.set_extra_maps_status(current_status)
