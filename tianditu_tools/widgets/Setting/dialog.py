from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QThread, pyqtSignal

from tianditu_tools.ui.setting import Ui_SettingDialog
from tianditu_tools.utils import (
    tianditu_map_url,
    check_url_status,
    check_subdomains,
    check_key_format,
    PluginConfig,
)


class CheckThread(QThread):
    check_finished = pyqtSignal(str)

    def __init__(self, conf):
        super().__init__()
        self.conf = conf
        self.key = ""

    def run(self):
        url = tianditu_map_url("vec", self.key, "t0")
        tile_url = url.format(x=0, y=0, z=0)
        check_msg = check_url_status(tile_url)
        if check_msg["code"] == 0:
            self.check_finished.emit("正常")
            self.conf.set_value("Tianditu/keyisvalid", True)
        else:
            error_msg = f"{check_msg['msg']}: {check_msg['resolve']}"
            self.check_finished.emit(error_msg)
            self.conf.set_value("Tianditu/keyisvalid", False)


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
        self.conf = PluginConfig()
        # 设置界面
        self.setupUi(self)
        self.mLineEdit_key.setText(self.conf.get_key())
        if len(self.mLineEdit_key.text()) == 0:
            self.pushButton.setEnabled(False)
        self.mLineEdit_key.textChanged.connect(self.on_key_LineEdit_changed)
        keyisvalid = self.conf.get_bool_value("Tianditu/keyisvalid")
        if keyisvalid:
            self.label_keystatus.setText("正常")
        else:
            self.label_keystatus.setText("无效")
        self.pushButton.clicked.connect(self.check)
        self.checkBox.setChecked(self.conf.get_bool_value("Other/extramap"))
        self.checkBox.stateChanged.connect(self.enable_extramap)
        self.checkBox_2.setChecked(self.conf.get_bool_value("Tianditu/random"))
        self.checkBox_2.stateChanged.connect(self.enable_random)
        # subdomian 设置
        self.subdomain_list = ["t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7"]
        self.comboBox.addItems(self.subdomain_list)
        self.comboBox.setCurrentIndex(
            self.subdomain_list.index(self.conf.get_value("Tianditu/subdomain"))
        )
        self.comboBox.setEnabled(not self.conf.get_value("Tianditu/random"))
        self.comboBox.currentIndexChanged.connect(self.handle_comboBox_index_changed)
        if not self.conf.get_bool_value("Tianditu/random") and self.conf.get_bool_value(
            "Tianditu/keyisvalid"
        ):
            self.ping_thread = PingUrlThread(self.conf.get_key())
            self.ping_thread.ping_finished.connect(self.handle_ping_finished)
            self.ping_thread.start()

    def handle_ping_finished(self, status):
        min_time = min(status)
        min_index = status.index(min_time)
        for i in range(8):
            self.comboBox.setItemText(i, f"t{i} {status[i]}")
        self.comboBox.setItemText(min_index, f"t{min_index} {status[min_index]}*")

    def on_key_LineEdit_changed(self):
        # self.pushButton.setEnabled(True)
        current_text = self.mLineEdit_key.text()
        # 删除key中的空格以及非打印字符
        filtered_text = "".join(
            [c for c in current_text if c.isprintable() and not c.isspace()]
        )
        if filtered_text != current_text:
            self.mLineEdit_key.setText(filtered_text)
        # 检查key格式
        key_format = check_key_format(self.mLineEdit_key.text())
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
        self.conf.set_value("Tianditu/key", self.mLineEdit_key.text())
        self.label_keystatus.setText("检查中...")
        self.check_thread = CheckThread(self.conf)
        self.check_thread.key = self.mLineEdit_key.text()
        self.check_thread.check_finished.connect(self.label_keystatus.setText)
        self.check_thread.start()

    def enable_extramap(self):
        if self.checkBox.isChecked():
            self.conf.set_value("Other/extramap", True)
            self.extra_map_action.setEnabled(True)
        else:
            self.conf.set_value("Other/extramap", False)
            self.extra_map_action.setEnabled(False)

    def handle_comboBox_index_changed(self):
        selected_index = self.comboBox.currentIndex()
        selected_domain = self.subdomain_list[selected_index]
        self.conf.set_value("Tianditu/subdomain", selected_domain)

    def enable_random(self):
        if self.checkBox_2.isChecked():
            self.conf.set_value("Tianditu/random", True)
            self.comboBox.setEnabled(False)
        else:
            self.conf.set_value("Tianditu/random", False)
            self.comboBox.setEnabled(True)
            if self.conf.get_bool_value("Tianditu/keyisvalid"):
                self.ping_thread = PingUrlThread(self.conf.get_key())
                self.ping_thread.ping_finished.connect(self.handle_ping_finished)
                self.ping_thread.start()
