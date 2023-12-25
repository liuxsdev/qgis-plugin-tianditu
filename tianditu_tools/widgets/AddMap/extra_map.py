from qgis.PyQt.QtWidgets import QMenu

from tianditu_tools.utils import PluginDir, load_yaml, PluginConfig
from tianditu_tools.widgets.icons import icons
from .utils import add_raster_layer

conf = PluginConfig()


def add_tianditu_province_menu(parent_menu: QMenu):
    tianditu_province_path = PluginDir.joinpath("maps/tianditu_province.yml")
    tianditu_province = load_yaml(tianditu_province_path)["maps"]
    maps = tianditu_province.keys()
    extra_maps_status = conf.get_extra_maps_status()
    for map_name in maps:
        # 一级菜单 省份名称
        if map_name in extra_maps_status["tianditu_province"]:
            add_map_action = parent_menu.addAction(icons["map"], map_name)
            map_data = tianditu_province[map_name]
            sub_menu = QMenu()
            for m in map_data:
                sub_menu.addAction(
                    icons["map"],
                    m["name"],
                    lambda m_=m: add_raster_layer(
                        m_["uri"], m_["name"], m_.get("type", "wms")
                    ),
                )
            add_map_action.setMenu(sub_menu)
    parent_menu.addSeparator()
