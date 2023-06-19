from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QThread, pyqtSignal
from qgis.core import QgsSettings

from .ui.setting import Ui_SettingDialog
from .utils import (
    tianditu_map_url,
    check_url_status,
    check_subdomains,
    check_key_format,
    get_qset_name,
    PluginConfig,
)


class CheckThread(QThread):
    check_finished = pyqtSignal(str)

    def __init__(self, qset):
        super().__init__()
        self.qset = qset
        self.key = ""

    def run(self):
        url = tianditu_map_url("vec", self.key, "t0")
        tile_url = url.format(x=0, y=0, z=0)
        check_msg = check_url_status(tile_url)
        if check_msg["code"] == 0:
            self.check_finished.emit("正常")
            self.qset.setValue("tianditu-tools/Tianditu/keyisvalid", True)
        else:
            error_msg = f"{check_msg['msg']}: {check_msg['resolve']}"
            self.check_finished.emit(error_msg)
            self.qset.setValue("tianditu-tools/Tianditu/keyisvalid", False)


class PingUrlThread(QThread):
    ping_finished = pyqtSignal(list)

    def __init__(self, key):
        super().__init__()
        self.key = key

    def run(self):
        subdomain_list = ["t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7"]
        urls = [
            tianditu_map_url("vec", self.key, subdomain) for subdomain in subdomain_list
        ]
        status = check_subdomains(urls)
        self.ping_finished.emit(status)


class SettingDialog(QtWidgets.QDialog, Ui_SettingDialog):
    def __init__(self, extra_map_action):
        super().__init__()
        self.ping_thread = None
        self.check_thread = None
        self.extra_map_action = extra_map_action
        # 读取配置
        self.qset = QgsSettings()
        self.config = PluginConfig(
            key=self.qset.value(get_qset_name("key")),
            random_enabled=self.qset.value(get_qset_name("random"), type=bool),
            keyisvalid=self.qset.value(get_qset_name("keyisvalid"), type=bool),
            subdomain=self.qset.value(get_qset_name("subdomain")),
            extramap_enabled=self.qset.value(get_qset_name("extramap"), type=bool),
        )
        # 设置界面
        self.setupUi(self)
        self.mLineEdit_key.setText(self.config.key)
        self.mLineEdit_key.textChanged.connect(self.on_key_LineEdit_changed)
        if self.config.keyisvalid:
            self.label_keystatus.setText("正常")
        else:
            self.label_keystatus.setText("无效")
        self.pushButton.clicked.connect(self.check)
        self.checkBox.setChecked(self.config.extramap_enabled)
        self.checkBox.stateChanged.connect(self.enable_extramap)
        self.checkBox_2.setChecked(self.config.random_enabled)
        self.checkBox_2.stateChanged.connect(self.enable_random)
        self.subdomain_list = ["t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7"]
        self.comboBox.addItems(self.subdomain_list)
        self.comboBox.setCurrentIndex(self.subdomain_list.index(self.config.subdomain))
        self.comboBox.setEnabled(not self.config.random_enabled)
        self.comboBox.currentIndexChanged.connect(self.handle_comboBox_index_changed)
        if not self.config.random_enabled and self.config.keyisvalid:
            self.ping_thread = PingUrlThread(self.config.key)
            self.ping_thread.ping_finished.connect(self.handle_ping_finished)
            self.ping_thread.start()

    def handle_ping_finished(self, status):
        min_time = min(status)
        min_index = status.index(min_time)
        for i in range(8):
            self.comboBox.setItemText(i, f"t{i} {status[i]}")
        self.comboBox.setItemText(min_index, f"t{min_index} {status[min_index]}*")

    def on_key_LineEdit_changed(self):
        current_text = self.mLineEdit_key.text()
        # 删除key中的空格以及非打印字符
        filtered_text = "".join(
            [c for c in current_text if c.isprintable() and not c.isspace()]
        )
        if filtered_text != current_text:
            self.mLineEdit_key.setText(filtered_text)
        # 检查key格式
        key_format = check_key_format(current_text)
        if key_format["key_length_error"]:
            self.label_keystatus.setText("无效key: 格式错误(长度不对)")
            self.pushButton.setEnabled(False)
        elif key_format["has_special_character"]:
            self.label_keystatus.setText("无效key: 含非常规字符")
            self.pushButton.setEnabled(False)
        else:
            self.label_keystatus.setText("未知")
            self.pushButton.setEnabled(True)

    def check(self):
        """检查key是否有效"""
        self.qset.setValue("tianditu-tools/Tianditu/key", self.mLineEdit_key.text())
        self.label_keystatus.setText("检查中...")
        self.check_thread = CheckThread(self.qset)
        self.check_thread.key = self.mLineEdit_key.text()
        self.check_thread.check_finished.connect(self.label_keystatus.setText)
        self.check_thread.start()

    def enable_extramap(self):
        if self.checkBox.isChecked():
            self.qset.setValue("tianditu-tools/Other/extramap", True)
            self.extra_map_action.setEnabled(True)
        else:
            self.qset.setValue("tianditu-tools/Other/extramap", False)
            self.extra_map_action.setEnabled(False)

    def handle_comboBox_index_changed(self):
        selected_index = self.comboBox.currentIndex()
        selected_domain = self.subdomain_list[selected_index]
        self.qset.setValue("tianditu-tools/Tianditu/subdomain", selected_domain)

    def enable_random(self):
        if self.checkBox_2.isChecked():
            self.qset.setValue("tianditu-tools/Tianditu/random", True)
            self.comboBox.setEnabled(False)
        else:
            self.qset.setValue("tianditu-tools/Tianditu/random", False)
            self.comboBox.setEnabled(True)
            if self.config.keyisvalid:
                self.ping_thread = PingUrlThread(self.config.key)
                self.ping_thread.ping_finished.connect(self.handle_ping_finished)
                self.ping_thread.start()
