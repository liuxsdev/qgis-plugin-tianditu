from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QThread, pyqtSignal
from .configSetting import ConfigFile, CONFIG_FILE_PATH
from .ui.setting import Ui_SettingDialog
from .utils import tianditu_map_url, check_url_status, check_subdomains

cfg = ConfigFile(CONFIG_FILE_PATH)


class CheckThread(QThread):
    check_finished = pyqtSignal(str)

    def run(self):
        url = tianditu_map_url('vec', self.key, 't0')
        tile_url = url.format(x=0, y=0, z=0)
        check_msg = check_url_status(tile_url)
        if check_msg['code'] == 0:
            self.check_finished.emit('正常')
            cfg.setValue('Tianditu', 'keyisvalid', 'True')
        else:
            error_msg = f"{check_msg['msg']}: {check_msg['resolve']}"
            self.check_finished.emit(error_msg)
            cfg.setValue('Tianditu', 'keyisvalid', 'False')


class PingUrlThread(QThread):
    ping_finished = pyqtSignal(list)

    def __init__(self, key):
        super().__init__()
        self.key = key

    def run(self):
        # url = tianditu_map_url('vec', self.key)
        subdomain_list = ['t0', 't1', 't2', 't3', 't4', 't5', 't6', 't7']
        urls = [tianditu_map_url('vec', self.key, subdomain) for subdomain in subdomain_list]
        status = check_subdomains(urls)
        self.ping_finished.emit(status)
    # TODO 勾选随机时不进行测速与选择 重构天地图url，增加{s}表示子域名


class SettingDialog(QtWidgets.QDialog, Ui_SettingDialog):
    def __init__(self, extra_map_action, parent=None):
        super(SettingDialog, self).__init__(parent)
        self.ping_thread = None
        self.check_thread = None
        self.extra_map_action = extra_map_action
        # 读取配置
        self.key = cfg.getValue('Tianditu', 'key')
        self.keyisvalid = cfg.getValueBoolean('Tianditu', 'keyisvalid')
        self.extramap_enabled = cfg.getValueBoolean('Other', 'extramap')
        self.random_enabled = cfg.getValueBoolean('Tianditu', 'random')
        self.subdomain = cfg.getValue('Tianditu', 'subdomain')
        if self.subdomain == '':
            cfg.setValue('Tianditu', 'subdomain', 't0')
            self.subdomain = cfg.getValue('Tianditu', 'subdomain')
        self.setupUi(self)
        self.mLineEdit_key.setText(self.key)
        if self.keyisvalid:
            self.label_keystatus.setText('正常')
        else:
            self.label_keystatus.setText('无效')
        self.pushButton.clicked.connect(self.check)
        self.checkBox.setChecked(self.extramap_enabled)
        self.checkBox.stateChanged.connect(self.enable_extramap)
        self.checkBox_2.setChecked(self.random_enabled)
        self.checkBox_2.stateChanged.connect(self.enable_random)
        self.subdomain_list = ['t0', 't1', 't2', 't3', 't4', 't5', 't6', 't7']
        self.comboBox.addItems(self.subdomain_list)
        self.comboBox.setCurrentIndex(self.subdomain_list.index(self.subdomain))
        self.comboBox.setEnabled(not self.random_enabled)
        self.comboBox.currentIndexChanged.connect(self.handle_comboBox_index_changed)
        if not self.random_enabled:
            self.ping_thread = PingUrlThread(self.key)
            self.ping_thread.ping_finished.connect(lambda data: self.handle_ping_finished(data))
            self.ping_thread.start()

    def handle_ping_finished(self, status):
        min_time = min(status)
        min_index = status.index(min_time)
        for i in range(8):
            self.comboBox.setItemText(i, f't{i} {status[i]}')
        self.comboBox.setItemText(min_index, f't{min_index} {status[min_index]}*')

    def check(self):
        # save
        cfg.setValue('Tianditu', 'key', self.mLineEdit_key.text())
        self.label_keystatus.setText('检查中...')
        self.check_thread = CheckThread()
        self.check_thread.key = self.mLineEdit_key.text()
        self.check_thread.check_finished.connect(self.label_keystatus.setText)
        self.check_thread.start()

    def enable_extramap(self):
        if self.checkBox.isChecked():
            cfg.setValue('Other', 'extramap', 'True')
            self.extra_map_action.setEnabled(True)
        else:
            cfg.setValue('Other', 'extramap', 'False')
            self.extra_map_action.setEnabled(False)

    def handle_comboBox_index_changed(self):
        selected_index = self.comboBox.currentIndex()
        selected_domain = self.subdomain_list[selected_index]
        cfg.setValue('Tianditu', 'subdomain', selected_domain)

    def enable_random(self):
        if self.checkBox_2.isChecked():
            cfg.setValue('Tianditu', 'random', 'True')
            self.comboBox.setEnabled(False)
        else:
            cfg.setValue('Tianditu', 'random', 'False')
            self.comboBox.setEnabled(True)
            self.ping_thread = PingUrlThread(self.key)
            self.ping_thread.ping_finished.connect(lambda data: self.handle_ping_finished(data))
            self.ping_thread.start()
