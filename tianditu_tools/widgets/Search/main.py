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
        self.iface = iface
        self.setIcon(icons["search"])
        self.setText("搜索")
        self.searchdockwidget = None
        self.triggered.connect(self.openSearch)

    def openSearch(self):
        # TODO: search 窗口可以关闭
        key = conf.get_key()
        keyisvalid = conf.get_bool_value("Tianditu/keyisvalid")
        if key == "" or keyisvalid is False:
            QMessageBox.warning(
                self.toolbar, "错误", "天地图Key未设置或Key无效", QMessageBox.Yes, QMessageBox.Yes
            )
        else:
            if self.searchdockwidget is None:
                self.searchdockwidget = SearchDockWidget(self.iface)
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.searchdockwidget)
            self.searchdockwidget.show()
