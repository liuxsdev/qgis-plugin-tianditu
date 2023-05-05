import random

import requests
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu, QToolButton, QMessageBox
from qgis.core import Qgis, QgsRasterLayer, QgsProject, QgsSettings

from .searchDockWidget import SearchDockWidget
from .settingDialog import SettingDialog
from .tiandituConfig import TianMapInfo, extra_maps, tdt
from .utils import tianditu_map_url, TianDiTuHomeURL, PluginDir

current_qgis_version = Qgis.versionInt()


def add_xyz_layer(uri, name):
    raster_layer = QgsRasterLayer(uri, name, 'wms')
    QgsProject.instance().addMapLayer(raster_layer)


def get_map_uri(url, zmin=0, zmax=18, referer=''):
    url_quote = requests.utils.quote(url, safe=':/')
    uri = f'type=xyz&url={url_quote}&zmin={zmin}&zmax={zmax}'
    if referer != '':
        if current_qgis_version >= 32600:
            uri += f'&http-header:referer={referer}'
        else:
            uri += f'&referer={referer}'
    return uri


def add_extra_map(map_data):
    name = map_data['name']
    uri = get_map_uri(map_data['url'], map_data['zmin'], map_data['zmax'], map_data['referer'])
    add_xyz_layer(uri, name)


def get_extra_map_icon(map_data):
    icon_home_path = PluginDir + "/images/map_icons/"
    if 'icon' in map_data:
        icon = QIcon(icon_home_path + map_data['icon'])
    else:
        icon = QIcon(icon_home_path + "default.svg")
    return icon


class TianDiTu:
    def __init__(self, iface):
        self.iface = iface
        # 设置工具栏
        self.toolbar = self.iface.addToolBar('TianDiTu Toolbar')
        self.toolbar.setObjectName('TianDiTuToolbar')
        self.toolbar.setToolTip('天地图工具栏')
        self.plugin_dir = PluginDir
        # 定义实例变量
        self.addTiandituToolbar = None
        self.addTiandituButton = None
        self.extra_map_action = None
        self.action_setting = None
        self.action_search = None
        self.searchdockwidget = None
        self.tdt_jiangsu_action = None
        # 配置文件
        self.qset = QgsSettings()
        if not self.qset.contains("tianditu-tools/Tianditu/key"):
            # 初始化
            self.qset.setValue("tianditu-tools/Tianditu/key", '')
            self.qset.setValue("tianditu-tools/Tianditu/keyisvalid", False)
            self.qset.setValue("tianditu-tools/Tianditu/random", True)
            self.qset.setValue("tianditu-tools/Tianditu/subdomain", 't0')
            self.qset.setValue("tianditu-tools/Other/extramap", False)

    def initGui(self):
        # 图标
        icon_setting = QIcon(self.plugin_dir + "/images/setting.svg")
        icon_add = QIcon(self.plugin_dir + "/images/add_map.svg")
        icon_map = QIcon(self.plugin_dir + "/images/map_tianditu.svg")
        icon_other = QIcon(self.plugin_dir + "/images/earth.svg")
        icon_search = QIcon(self.plugin_dir + "/images/search.svg")
        # 天地图添加 Action
        menu = QMenu()
        menu.setObjectName('TianDiTuAddMap')
        for maptype in TianMapInfo:
            menu.addAction(icon_map, TianMapInfo[maptype], lambda maptype_=maptype: self.add_tianditu_basemap(maptype_))
        menu.addSeparator()
        # 天地图省级节点
        self.tdt_jiangsu_action = menu.addAction(icon_map, '天地图·江苏')
        tdt_jiangsu_menu = QMenu()
        tianditu_jiangsu = tdt['天地图-江苏']
        for mapdata in tianditu_jiangsu:
            tdt_jiangsu_menu.addAction(icon_map, mapdata['name'], lambda m=mapdata: add_xyz_layer(m['uri'], m['name']))
        self.tdt_jiangsu_action.setMenu(tdt_jiangsu_menu)
        menu.addSeparator()
        # 其他图源
        self.extra_map_action = menu.addAction(icon_other, '其他图源')
        extra_map_menu = QMenu()
        for map_data in extra_maps:
            if map_data['name'] != 'Separator':
                icon = get_extra_map_icon(map_data)
                extra_map_menu.addAction(
                    icon,
                    map_data['name'],
                    lambda map_data_=map_data: add_extra_map(map_data_)
                )
            else:
                extra_map_menu.addSeparator()
            # TODO:增加备注tooltip
        self.extra_map_action.setMenu(extra_map_menu)
        extramap_enabled = self.qset.value("tianditu-tools/Other/extramap", type=bool)
        if not extramap_enabled:
            self.extra_map_action.setEnabled(False)

        self.addTiandituButton = QToolButton()
        self.addTiandituButton.setMenu(menu)
        self.addTiandituButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.addTiandituButton.setText('添加底图')
        self.addTiandituButton.setIcon(icon_add)
        self.addTiandituButton.setToolTip('添加底图')
        self.addTiandituToolbar = self.toolbar.addWidget(self.addTiandituButton)

        # 设置 Action
        self.action_setting = QAction(icon_setting, "设置", self.iface.mainWindow())
        self.action_setting.triggered.connect(self.show_setting_dialog)
        self.toolbar.addAction(self.action_setting)

        # 查询 Action
        self.action_search = QAction(icon_search, "查询", self.iface.mainWindow())
        self.action_search.triggered.connect(self.openSearch)
        self.toolbar.addAction(self.action_search)

    def show_setting_dialog(self):
        dlg = SettingDialog(self.extra_map_action)
        dlg.exec_()

    def add_tianditu_basemap(self, maptype):
        key = self.qset.value('tianditu-tools/Tianditu/key')
        keyisvalid = self.qset.value('tianditu-tools/Tianditu/keyisvalid', type=bool)
        random_enabled = self.qset.value('tianditu-tools/Tianditu/random', type=bool)
        subdomain = self.qset.value('tianditu-tools/Tianditu/subdomain')
        if key == '' or keyisvalid is False:
            QMessageBox.warning(self.toolbar, '错误', '天地图Key未设置或Key无效', QMessageBox.Yes, QMessageBox.Yes)
        else:
            if random_enabled:
                subdomain = random.choice(['t0', 't1', 't2', 't3', 't4', 't5', 't6', 't7'])
                uri = get_map_uri(tianditu_map_url(maptype, key, subdomain), zmin=1, referer=TianDiTuHomeURL)
            else:
                uri = get_map_uri(tianditu_map_url(maptype, key, subdomain), zmin=1, referer=TianDiTuHomeURL)
            add_xyz_layer(uri, TianMapInfo[maptype])

    def openSearch(self):
        key = self.qset.value('tianditu-tools/Tianditu/key')
        keyisvalid = self.qset.value('tianditu-tools/Tianditu/keyisvalid', type=bool)
        if key == '' or keyisvalid is False:
            QMessageBox.warning(self.toolbar, '错误', '天地图Key未设置或Key无效', QMessageBox.Yes, QMessageBox.Yes)
        else:
            if self.searchdockwidget is None:
                self.searchdockwidget = SearchDockWidget(self.iface)
            self.iface.addDockWidget(Qt.LeftDockWidgetArea, self.searchdockwidget)
            self.searchdockwidget.show()

    def unload(self):
        """Unload from the QGIS interface"""
        self.addTiandituButton.setMenu(None)
        self.iface.removeToolBarIcon(self.action_setting)
        self.iface.removeToolBarIcon(self.action_search)
        self.iface.removeToolBarIcon(self.addTiandituToolbar)
        if self.searchdockwidget:
            self.iface.removeDockWidget(self.searchdockwidget)
