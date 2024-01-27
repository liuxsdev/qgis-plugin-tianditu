from qgis.PyQt.QtGui import QIcon

from ..utils import PluginDir

icon_dict = {
    "setting": "./images/setting.svg",
    "add": "./images/add_map.svg",
    "map": "./images/map_tianditu.svg",
    "other": "./images/earth.svg",
    "search": "./images/search.svg",
    "fitzoom": "./images/fitzoom.svg",
}

icons = {key: QIcon(str(PluginDir.joinpath(value))) for key, value in icon_dict.items()}

map_icon_folder = PluginDir.joinpath("./images/map_icons")


def get_extra_map_icon(name: str):
    if map_icon_folder.joinpath(name).exists():
        return QIcon(str(map_icon_folder.joinpath(name)))
    return QIcon(str(map_icon_folder.joinpath("default.svg")))
