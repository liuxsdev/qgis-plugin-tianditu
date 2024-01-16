from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QAction, QMessageBox

from tianditu_tools.utils import PluginConfig
from tianditu_tools.widgets.icons import icons
from .searchDock import SearchDockWidget

conf = PluginConfig()


class SearchAction(QAction):
    def __init__(
        self,
        iface,
        parent=None,
    ):
        super().__init__(parent)
        self.parent = parent
        self.iface = iface
        self.setIcon(icons["search"])
        self.setText("搜索")
        self.searchdockwidget = SearchDockWidget(self.iface)
        self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.searchdockwidget)
        self.searchdockwidget.hide()
        self.setCheckable(True)
        self.triggered.connect(self.openSearch)

    def openSearch(self):
        key = conf.get_key()
        if key == "":
            QMessageBox.warning(
                self.parent, "错误", "天地图Key未设置或Key无效", QMessageBox.Yes, QMessageBox.Yes
            )
        else:
            if self.searchdockwidget.isHidden():
                self.searchdockwidget.show()
                self.setChecked(True)
            else:
                self.setChecked(False)
                self.searchdockwidget.hide()

    def unload(self):
        self.iface.removeDockWidget(self.searchdockwidget)
