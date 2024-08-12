import json

from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QTimer
from qgis.PyQt.QtGui import QClipboard
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest
from qgis.PyQt.QtWidgets import QApplication
from qgis.core import QgsNetworkAccessManager

from .mapmanager import MapManager
from ...ui.setting import Ui_SettingDialog
from ...utils import (
    tianditu_map_url,
    PluginConfig,
    PluginDir,
    make_request,
    HEADER,
)


def check_key_format(key: str) -> object:
    """检查key格式

    Args:
        key (str): 天地图key

    Returns:
        object:
            "key_length_error": key的长度有误,
            "has_special_character": 含有除字母数字外的其他字符
    """
    correct_length = 32
    key_length = len(key)
    key_length_error = False
    if key_length != correct_length:
        key_length_error = True
    return {
        "key_length_error": key_length_error,
        "has_special_character": not key.isalnum(),
    }


class SettingDialog(QtWidgets.QDialog, Ui_SettingDialog):
    def __init__(self, toolbar):
        super().__init__()
        self.check_thread = None
        self.mapm = None
        self.toolbar = toolbar
        # 读取配置
        self.conf = PluginConfig()
        self.subdomain_list = [f"t{i}" for i in range(8)]
        # 设置 status label 的定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.clear_status_label)
        # 设置界面
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.init_keyCombo()
        # 如果key输入框是空白的，则禁用保存按钮
        if len(self.mLineEdit_key.text()) == 0:
            self.saveButton.setEnabled(False)
        # 给控件添加事件
        self.mLineEdit_key.textChanged.connect(self.on_key_LineEdit_changed)
        self.saveButton.clicked.connect(self.save_key)
        self.pushButton_copy.clicked.connect(self.copy_key)
        self.pushButton_delete.clicked.connect(self.del_key)
        self.keyComboBox.currentIndexChanged.connect(self.select_key)
        # 是否启用key随机
        if self.conf.get_bool_value("Tianditu/random_key"):
            self.checkBox_key_rand.setChecked(True)
            self.keyComboBox.setEnabled(False)
            self.pushButton_copy.setEnabled(False)
            self.pushButton_delete.setEnabled(False)
        self.checkBox_key_rand.stateChanged.connect(self.enable_key_random)
        # subdomain 选择
        self.checkBox_domain_rand.setChecked(
            self.conf.get_bool_value("Tianditu/random")
        )
        self.checkBox_domain_rand.stateChanged.connect(self.enable_random)
        # subdomian 设置
        self.subdomainComboBox.addItems(self.subdomain_list)
        self.subdomainComboBox.setCurrentIndex(
            self.subdomain_list.index(self.conf.get_value("Tianditu/subdomain"))
        )
        self.subdomainComboBox.setEnabled(not self.conf.get_value("Tianditu/random"))
        self.subdomainComboBox.currentIndexChanged.connect(self.select_subdomain)
        # init map manager
        map_folder = PluginDir.joinpath("maps")
        self.mapm = MapManager(
            map_folder=map_folder,
            parent=self.tab_map,
            update_btn=self.btn_checkupdate,
            status_label=self.label_checkstatus,
        )
        self.verticalLayout_6.addWidget(self.mapm)
        self.btn_checkupdate.clicked.connect(self.mapm.check_update)
        #
        self.tabWidget.currentChanged.connect(self.adjust_tab_height)

    def adjust_tab_height(self):
        current_index = self.tabWidget.currentIndex()
        if current_index == 0:
            self.setFixedHeight(312)
        else:
            self.setFixedHeight(500)  # 根据内容计算高度

    def set_status_label(self, text: str):
        """
        创建提示
        """
        self.info_status.setText(text)
        self.timer.start(2000)

    def clear_status_label(self):
        self.info_status.clear()
        self.timer.stop()

    def get_key_by_masked(self, masked):
        key_list = self.conf.get_key_list()
        filtered_items = [key for key in key_list if key.startswith(masked[:8])]
        if len(filtered_items) > 0:
            return filtered_items[0]
        return ""

    def init_keyCombo(self):
        self.keyComboBox.clear()  # 先清除
        # 如果 key 列表中没有值, keyComboBox 添加提示
        key_list = self.conf.get_key_list()
        if len(key_list) == 0:
            self.keyComboBox.addItem("请添加 key")
            self.pushButton_delete.setEnabled(False)
            self.pushButton_copy.setEnabled(False)
        else:
            self.keyComboBox.addItems([f"{key[:8]}****" for key in key_list])
            # 将 keyComboBox 的当前值改为当前选用的 key
            current_key = self.conf.get_key()
            index = key_list.index(current_key)
            self.keyComboBox.setCurrentIndex(index)
            self.pushButton_delete.setEnabled(True)
            self.pushButton_copy.setEnabled(True)

    def copy_key(self):
        current_key = self.keyComboBox.currentText()
        full_key = self.get_key_by_masked(current_key)
        clipboard = QApplication.clipboard()
        clipboard.setText(full_key, QClipboard.Clipboard)
        self.set_status_label(f"已复制{current_key}到剪贴板")

    def handle_key_check(self, reply, key):
        key_list = self.conf.get_key_list()
        # 获取状态码
        status_code = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
        if reply.error() == QNetworkReply.NoError:
            response_data = reply.readAll()
            png_signature = b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A"
            if response_data[:8] == png_signature:
                if self.keyComboBox.itemText(0) == "请添加 key":
                    self.keyComboBox.removeItem(0)
                self.mLineEdit_key.setText("")
                key_list.append(key)
                self.conf.save_key_list(key_list)
                self.saveButton.setEnabled(False)
                self.set_status_label("保存成功")
                self.init_keyCombo()
        else:
            if status_code == 403:
                # 当期 2024-06-09 似乎不需要设置 Referer 也能正常访问
                # {'msg': '非法Key', 'resolve': '请到API控制台重新申请Key', 'code': 1}
                # {'msg': '域名不匹配', 'resolve': '请到API控制台查看域名配置并修改', 'code': 7}
                # {'msg': '权限类型错误', 'resolve': 'Key权限类型为:服务端，请使用服务端访问！', 'code': 12}
                # {'msg': '权限类型错误', 'resolve': '不支持的key类型！', 'code': 18}
                response_data = str(reply.readAll(), "utf-8", "ignore")
                json_data = json.loads(response_data)
                self.set_status_label(
                    f"错误: {json_data.get('msg')} {json_data.get('resolve')}"
                )
            elif status_code == 418:
                self.set_status_label("错误: 疑似攻击")
            else:
                self.set_status_label("未知错误")

    def save_key(self):
        key = self.mLineEdit_key.text()
        key_list = self.conf.get_key_list()
        if key in key_list:
            self.set_status_label("key 已存在")
            return
        url = tianditu_map_url("vec", key, "t0")
        tile_url = url.format(x=0, y=0, z=0)
        network_manager = QgsNetworkAccessManager.instance()
        request = make_request(tile_url, HEADER.get("Referer"))
        reply = network_manager.get(request)
        # reply.finished.connect(partial(self.handle_key_check, reply, key))
        reply.finished.connect(lambda: self.handle_key_check(reply, key))

    def select_key(self):
        if self.keyComboBox.count() > 0:
            masked_key = self.keyComboBox.currentText()
            key = self.get_key_by_masked(masked_key)
            self.conf.set_key(key)
            self.set_status_label(f"设置当前 key 为{masked_key}")

    def del_key(self):
        current_index = self.keyComboBox.currentIndex()
        key_list = self.conf.get_key_list()
        del key_list[current_index]
        self.conf.save_key_list(key_list)
        self.set_status_label("已删除")
        self.init_keyCombo()

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
        if len(self.mLineEdit_key.text()) > 0:
            key_format = check_key_format(self.mLineEdit_key.text())
            if key_format["key_length_error"]:
                self.info_status.setText("无效key: 格式错误(长度不对)")
                self.saveButton.setEnabled(False)
            elif key_format["has_special_character"]:
                self.info_status.setText("无效key: 含非常规字符")
                self.saveButton.setEnabled(False)
            else:
                self.info_status.setText("点击保存")
                self.saveButton.setEnabled(True)
        else:
            self.info_status.clear()

    def select_subdomain(self):
        selected_index = self.subdomainComboBox.currentIndex()
        selected_domain = self.subdomain_list[selected_index]
        self.conf.set_value("Tianditu/subdomain", selected_domain)
        self.set_status_label(f"设置 subdomain 为 {selected_domain}")

    def enable_random(self):
        if self.checkBox_domain_rand.isChecked():
            self.conf.set_value("Tianditu/random", True)
            self.subdomainComboBox.setEnabled(False)
            self.set_status_label("设置 subdomain 为 随机")
        else:
            self.conf.set_value("Tianditu/random", False)
            self.subdomainComboBox.setEnabled(True)

    def enable_key_random(self):
        if self.checkBox_key_rand.isChecked():
            self.conf.set_value("Tianditu/random_key", True)
            self.keyComboBox.setEnabled(False)
            self.pushButton_copy.setEnabled(False)
            self.pushButton_delete.setEnabled(False)
            self.set_status_label("设置 key 为 随机")
        else:
            self.conf.set_value("Tianditu/random_key", False)
            self.keyComboBox.setEnabled(True)
            self.pushButton_copy.setEnabled(True)
            self.pushButton_delete.setEnabled(True)

    def closeEvent(self, event):
        # 在对话框关闭时触发的事件
        self.mapm.update_map_enable_state()
        self.toolbar.add_button.setup_action()
        event.accept()  # 接受关闭事件，关闭对话框
