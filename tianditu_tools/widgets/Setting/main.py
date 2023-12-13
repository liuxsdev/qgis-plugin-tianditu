from qgis.PyQt.QtWidgets import QAction

from tianditu_tools.widgets.icons import icons
from .dialog import SettingDialog


class SettingAction(QAction):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(icons["setting"])
        self.setText("设置")
        self.triggered.connect(self.show_setting_dialog)

    def show_setting_dialog(self):
        dlg = SettingDialog(self)
        dlg.exec_()
