from qgis.PyQt.QtWidgets import QToolBar

from tianditu_tools.utils import PluginConfig
from tianditu_tools.widgets.AddMap import AddMapBtn
from tianditu_tools.widgets.FitZoom import FitZoomAction
from tianditu_tools.widgets.Search import SearchAction
from tianditu_tools.widgets.Setting import SettingAction
from .icons import icons


class TiandituToolbar(QToolBar):
    def __init__(self, iface, parent=None) -> None:
        super().__init__(parent)
        self.iface = iface
        self.icons = icons
        self.conf = PluginConfig()
        self.setToolTip("天地图 Tools 工具栏")
        self.add_button = None
        self.actions = []

        self.init_config()
        self.setup_action()

    def setup_action(self):
        self.add_button = AddMapBtn(self)
        self.addWidget(self.add_button)
        # 添加 Action
        action_setting = SettingAction(self)
        action_search = SearchAction(iface=self.iface, parent=self)
        action_fitzoom = FitZoomAction(iface=self.iface, parent=self)

        self.actions.extend([action_setting, action_search, action_fitzoom])
        self.addActions(self.actions)

    def init_config(self):
        self.conf.init_config()

    def remove_dock(self):
        dock = self.actions[1]
        dock.unload()
