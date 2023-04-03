from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import QThread, pyqtSignal
from .configSetting import ConfigFile, CONFIG_FILE_PATH
from .ui.setting import Ui_SettingDialog
from .utils import tianditu_map_url, check_url_status

cfg = ConfigFile(CONFIG_FILE_PATH)


class CheckThread(QThread):
    check_finished = pyqtSignal(str)

    def run(self):
        url = tianditu_map_url('vec', self.key)
        tile_url = url.format(x=0, y=0, z=0)
        status = check_url_status(tile_url)
        if status:
            self.check_finished.emit('正常')
            cfg.setValue('Tianditu', 'keyisvalid', 'True')
        else:
            self.check_finished.emit('异常,请检查key是否正确！')
            cfg.setValue('Tianditu', 'keyisvalid', 'False')


class SettingDialog(QtWidgets.QDialog, Ui_SettingDialog):
    def __init__(self, parent=None):
        super(SettingDialog, self).__init__(parent)
        self.check_thread = None
        self.key = cfg.getValue('Tianditu', 'key')
        self.keyisvalid = cfg.getValueBoolean('Tianditu', 'keyisvalid')
        self.setupUi(self)
        self.mLineEdit_key.setText(self.key)
        if self.keyisvalid:
            self.label_keystatus.setText('正常')
        self.pushButton.clicked.connect(self.check)

    def check(self):
        # save
        cfg.setValue('Tianditu', 'key', self.mLineEdit_key.text())
        self.label_keystatus.setText('检查中...')
        self.check_thread = CheckThread()
        self.check_thread.key = self.mLineEdit_key.text()
        self.check_thread.check_finished.connect(self.label_keystatus.setText)
        self.check_thread.start()
