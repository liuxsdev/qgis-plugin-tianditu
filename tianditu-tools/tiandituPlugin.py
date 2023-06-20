import random

import requests
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu, QToolButton, QMessageBox
from qgis.core import Qgis, QgsRasterLayer, QgsProject, QgsSettings

from .searchDockWidget import SearchDockWidget
from .settingDialog import SettingDialog
from .tiandituConfig import TianMapInfo, extra_maps, tianditu_province
from .utils import tianditu_map_url, TIANDITU_HOME_URL, PluginDir

current_qgis_version = Qgis.versionInt()


def add_xyz_layer(uri: str, name: str) -> None:
    """QGIS 添加xyz图层

    Args:
        uri (str): 图层uri
        name (str): 图层名称
    """
    raster_layer = QgsRasterLayer(uri, name, "wms")
    QgsProject.instance().addMapLayer(raster_layer)


def get_map_uri(url: str, zmin: int = 0, zmax: int = 18, referer: str = "") -> str:
    """返回瓦片地图uri

    Args:
        url (str): 瓦片地图url
        zmin (int, optional): z 最小值. Defaults to 0.
        zmax (int, optional): z 最大值 Defaults to 18.
        referer (str, optional): Referer. Defaults to "".

    Returns:
        str: 瓦片地图uri
    """
    url_quote = requests.utils.quote(url, safe=":/")
    uri = f"type=xyz&url={url_quote}&zmin={zmin}&zmax={zmax}"
    if referer != "":
        if current_qgis_version >= 32600:
            uri += f"&http-header:referer={referer}"
        else:
            uri += f"&referer={referer}"
    return uri


def add_extra_map(map_data: object) -> None:
    """添加额外的地图

    Args:
        map_data (object): 地图信息
    """
    name = map_data["name"]
    uri = get_map_uri(
        map_data["url"], map_data["zmin"], map_data["zmax"], map_data["referer"]
    )
    add_xyz_layer(uri, name)


def get_extra_map_icon(map_data: object) -> QIcon:
    """获取额外地图的图标

    Args:
        map_data (object): 地图信息

    Returns:
        QIcon: 图标
    """
    icon_home_path = PluginDir + "/images/map_icons/"
    if "icon" in map_data:
        icon = QIcon(icon_home_path + map_data["icon"])
    else:
        icon = QIcon(icon_home_path + "default.svg")
    return icon


class TianDiTu:
    def __init__(self, iface):
        self.iface = iface
        # 设置工具栏
        self.toolbar = self.iface.addToolBar("TianDiTu Toolbar")
        self.toolbar.setObjectName("TianDiTuToolbar")
        self.toolbar.setToolTip("天地图工具栏")
        # 定义实例变量
        self.addTiandituToolbar = None
        self.addTiandituButton = None
        self.searchdockwidget = None
        self.actions = {"search": None, "setting": None, "extra_map_action": None}
        # 配置文件
        self.qset = QgsSettings()
        if not self.qset.contains("tianditu-tools/Tianditu/key"):
            # 初始化
            self.qset.setValue("tianditu-tools/Tianditu/key", "")
            self.qset.setValue("tianditu-tools/Tianditu/keyisvalid", False)
            self.qset.setValue("tianditu-tools/Tianditu/random", True)
            self.qset.setValue("tianditu-tools/Tianditu/subdomain", "t0")
            self.qset.setValue("tianditu-tools/Other/extramap", False)

    def initGui(self):
        # 图标
        icons = {
            "setting": QIcon(PluginDir + "/images/setting.svg"),
            "add": QIcon(PluginDir + "/images/add_map.svg"),
            "map": QIcon(PluginDir + "/images/map_tianditu.svg"),
            "other": QIcon(PluginDir + "/images/earth.svg"),
            "search": QIcon(PluginDir + "/images/search.svg"),
        }
        # 天地图添加 Action
        menu = QMenu()
        menu.setObjectName("TianDiTuAddMap")
        for map_type, map_name in TianMapInfo.items():
            menu.addAction(
                icons["map"],
                map_name,
                lambda maptype_=map_type: self.add_tianditu_basemap(maptype_),
            )
        menu.addSeparator()
        # 天地图省级节点
        keys = tianditu_province.keys()
        for key in keys:
            province_action = menu.addAction(icons["map"], key)
            map_data = tianditu_province[key]
            province_menu = QMenu()
            for m in map_data:
                province_menu.addAction(
                    icons["map"],
                    m["name"],
                    lambda m_=m: add_xyz_layer(m_["uri"], m_["name"]),
                )
            province_action.setMenu(province_menu)
        menu.addSeparator()
        # 添加其他图源 Action
        self.actions["extra_map_action"] = menu.addAction(icons["other"], "其他图源")
        extra_map_menu = QMenu()
        for map_data in extra_maps:
            if map_data["name"] != "Separator":
                icon = get_extra_map_icon(map_data)
                extra_map_menu.addAction(
                    icon,
                    map_data["name"],
                    lambda map_data_=map_data: add_extra_map(map_data_),
                )
            else:
                extra_map_menu.addSeparator()
        self.actions["extra_map_action"].setMenu(extra_map_menu)
        extramap_enabled = self.qset.value("tianditu-tools/Other/extramap", type=bool)
        if not extramap_enabled:
            self.actions["extra_map_action"].setEnabled(False)

        self.addTiandituButton = QToolButton()
        self.addTiandituButton.setMenu(menu)
        self.addTiandituButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.addTiandituButton.setText("添加底图")
        self.addTiandituButton.setIcon(icons["add"])
        self.addTiandituButton.setToolTip("添加底图")
        self.addTiandituToolbar = self.toolbar.addWidget(self.addTiandituButton)

        # 设置 Action
        self.actions["setting"] = QAction(
            icons["setting"], "设置", self.iface.mainWindow()
        )
        self.actions["setting"].triggered.connect(self.show_setting_dialog)
        self.toolbar.addAction(self.actions["setting"])

        # 查询 Action
        self.actions["search"] = QAction(icons["search"], "查询", self.iface.mainWindow())
        self.actions["search"].triggered.connect(self.openSearch)
        self.toolbar.addAction(self.actions["search"])

    def show_setting_dialog(self):
        dlg = SettingDialog(self.actions["extra_map_action"])
        dlg.exec_()

    def add_tianditu_basemap(self, maptype):
        key = self.qset.value("tianditu-tools/Tianditu/key")
        keyisvalid = self.qset.value("tianditu-tools/Tianditu/keyisvalid", type=bool)
        random_enabled = self.qset.value("tianditu-tools/Tianditu/random", type=bool)
        subdomain = self.qset.value("tianditu-tools/Tianditu/subdomain")
        if key == "" or keyisvalid is False:
            QMessageBox.warning(
                self.toolbar, "错误", "天地图Key未设置或Key无效", QMessageBox.Yes, QMessageBox.Yes
            )
        else:
            if random_enabled:
                subdomain = random.choice(
                    ["t0", "t1", "t2", "t3", "t4", "t5", "t6", "t7"]
                )
                uri = get_map_uri(
                    tianditu_map_url(maptype, key, subdomain),
                    zmin=1,
                    referer=TIANDITU_HOME_URL,
                )
            else:
                uri = get_map_uri(
                    tianditu_map_url(maptype, key, subdomain),
                    zmin=1,
                    referer=TIANDITU_HOME_URL,
                )
            add_xyz_layer(uri, TianMapInfo[maptype])

    def openSearch(self):
        key = self.qset.value("tianditu-tools/Tianditu/key")
        keyisvalid = self.qset.value("tianditu-tools/Tianditu/keyisvalid", type=bool)
        if key == "" or keyisvalid is False:
            QMessageBox.warning(
                self.toolbar, "错误", "天地图Key未设置或Key无效", QMessageBox.Yes, QMessageBox.Yes
            )
        else:
            if self.searchdockwidget is None:
                self.searchdockwidget = SearchDockWidget(self.iface)
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.searchdockwidget)
            self.searchdockwidget.show()

    def unload(self):
        """Unload from the QGIS interface"""
        self.addTiandituButton.setMenu(None)
        self.iface.removeToolBarIcon(self.actions["setting"])
        self.iface.removeToolBarIcon(self.actions["search"])
        self.iface.removeToolBarIcon(self.addTiandituToolbar)
        if self.searchdockwidget:
            self.iface.removeDockWidget(self.searchdockwidget)
