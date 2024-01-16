from qgis.PyQt.QtWidgets import QMenu

from tianditu_tools.utils import PluginDir, load_yaml, PluginConfig
from tianditu_tools.widgets.icons import icons
from .utils import add_raster_layer, get_map_uri

conf = PluginConfig()


def add_extra_map(mapdata):
    name = mapdata["name"]
    uri = get_map_uri(
        mapdata["url"], mapdata["zmin"], mapdata["zmax"], mapdata.get("referer", "")
    )
    add_raster_layer(uri, name)


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


def add_extra_map_menu(parent_menu: QMenu):
    extra = load_yaml(PluginDir.joinpath("maps/extra.yml"))
    extra_maps = extra["maps"]
    extra_root = parent_menu.addAction(icons["other"], "其他地图")
    extra_root_menu = QMenu()
    maps = extra_maps.keys()
    extra_maps_status = conf.get_extra_maps_status()
    for map_name in maps:
        if (
            map_name in extra_maps_status["tianditu_province"]
            or map_name in extra_maps_status["extra"]
        ):
            map_data = extra_maps[map_name]
            sub_menu = extra_root_menu.addAction(icons["other"], map_name)
            sub_sub_menu = QMenu()
            for sub_map in map_data:
                sub_sub_menu.addAction(
                    icons["other"],
                    sub_map["name"],
                    lambda m_=sub_map: add_extra_map(m_),
                )
            sub_menu.setMenu(sub_sub_menu)
    extra_root.setMenu(extra_root_menu)
