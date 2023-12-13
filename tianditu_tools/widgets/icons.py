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
