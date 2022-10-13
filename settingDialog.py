import os

from qgis.PyQt import QtWidgets
from qgis.PyQt import uic

from .configSetting import ConfigFile, CONFIG_FILE_PATH
from .utils import tianditu_map_url, check_url_status

plugin_dir = os.path.dirname(__file__)
FORM_CLASS, _ = uic.loadUiType(os.path.join(plugin_dir, 'ui/setting.ui'))


def check_key():
    print('key')


cfg = ConfigFile(CONFIG_FILE_PATH)


class SettingDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        super(SettingDialog, self).__init__(parent)
        self.setupUi(self)
        self.lineEdit.setText(cfg.getValue('Tianditu', 'key'))
        self.pushButton.clicked.connect(self.check)

    def check(self):
        self.label_3.setText('检查中')  #
        # # cfg.setValue('Tianditu', 'key', self.lineEdit.text())
        url = tianditu_map_url('vec', self.lineEdit.text())
        tile_url = url.format(x=0, y=0, z=0)
        status = check_url_status(tile_url)
        if status:
            self.label_3.setText('正常')
        else:
            self.label_3.setText('异常,请检查key是否正确！')
        self.pushButton.setEnabled(True)
