from pathlib import Path

import requests
import yaml
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QTreeWidget, QTreeWidgetItem

from tianditu_tools.utils import load_yaml


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

    def load_map_summary(self):
        summary_path = self.map_folder.joinpath("summary.yml")
        if not summary_path.exists():
            print("本地文件丢失")
        summary = load_yaml(summary_path)
        for key, value in summary.items():
            update_btn = QPushButton("更新")
            update_btn.setStyleSheet("QPushButton{margin:2px 20px;}")
            update_btn.setEnabled(False)
            item = QTreeWidgetItem(self, [value["name"], value["lastUpdated"], "/"])

            item.setSizeHint(0, QSize(160, 28))
            item.setTextAlignment(1, Qt.AlignCenter)
            item.setTextAlignment(2, Qt.AlignCenter)
            self.setItemWidget(item, 3, update_btn)
            map_detail = self.load_map_detail(value["id"])["maps"]
            for map_name in map_detail.keys():
                child_item = QTreeWidgetItem(item)
                child_item.setText(0, map_name)
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
