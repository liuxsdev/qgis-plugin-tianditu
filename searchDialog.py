import os

from qgis.PyQt import QtWidgets

from .configSetting import ConfigFile, CONFIG_FILE_PATH
from .ui.setting import Ui_Form
from .utils import tianditu_map_url, check_url_status

plugin_dir = os.path.dirname(__file__)

cfg = ConfigFile(CONFIG_FILE_PATH)


class SearchDialog(QtWidgets.QDockWidget, Ui_Form):
    def __init__(self, parent=None):
        super(SettingDialog, self).__init__(parent)
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
        self.label_keystatus.setText('检查中')
        url = tianditu_map_url('vec', self.mLineEdit_key.text())
        tile_url = url.format(x=0, y=0, z=0)
        status = check_url_status(tile_url)
        if status:
            self.label_keystatus.setText('正常')
            cfg.setValue('Tianditu', 'keyisvalid', 'True')
        else:
            self.label_keystatus.setText('异常,请检查key是否正确！')
            cfg.setValue('Tianditu', 'keyisvalid', 'False')
