import os

from qgis.PyQt import QtWidgets
from qgis.PyQt import uic

from .configSetting import ConfigFile, CONFIG_FILE_PATH

plugin_dir = os.path.dirname(__file__)
FORM_CLASS, _ = uic.loadUiType(os.path.join(plugin_dir, 'ui/setting.ui'))


def check_key():
    print('key')


cfg = ConfigFile(CONFIG_FILE_PATH)
print(cfg.sections)
print(cfg.cfg['Tianditu']['key'])


class SettingDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(SettingDialog, self).__init__(parent)
        self.setupUi(self)
        self.lineEdit.setText(cfg.getValue('Tianditu', 'key'))
        self.pushButton.clicked.connect(self.check)

    def check(self):
        cfg.setValue('Tianditu', 'key', self.lineEdit.text())
