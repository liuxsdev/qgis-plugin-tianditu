import os
import requests
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu, QToolButton
from qgis.core import Qgis, QgsRasterLayer, QgsProject
from .tiandituConfig import TianMapInfo, extra_map
from .settingDialog import SettingDialog

current_qgis_version = Qgis.versionInt()


def run():
    print("running")
    dlg = SettingDialog()
    dlg.show()
    dlg.exec_()


def add_xyz_layer(uri, name):
    raster_layer = QgsRasterLayer(uri, name, 'wms')
    QgsProject.instance().addMapLayer(raster_layer)


def tianditu_map_url(maptype, token):
    url = 'https://t2.tianditu.gov.cn/'
    url += f'{maptype}_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER={maptype}'
    url += '&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TileCol={x}&TileRow={y}&TileMatrix={z}'
    url += f'&tk={token}'
    return url


def get_map_uri(url, zmin=0, zmax=18, referer=''):
    url_quote = requests.utils.quote(url, safe=':/')
    if referer == '':
        uri = f'type=xyz&url={url_quote}&zmin={zmin}&zmax={zmax}'
    elif current_qgis_version >= 32600:
        uri = f'type=xyz&url={url_quote}&zmin={zmin}&zmax={zmax}&http-header:referer={referer}'
    else:
        uri = f'type=xyz&url={url_quote}&zmin={zmin}&zmax={zmax}&referer={referer}'
    return uri


def add_tianditu_basemap(maptype):
    # TODO Token save to config file
    token = 'cfcbc282308686d26782fcb4e11b32a4'
    uri = get_map_uri(tianditu_map_url(maptype, token), zmin=1, referer='https://www.tianditu.gov.cn/')
    add_xyz_layer(uri, TianMapInfo[maptype])


def add_extra_map(name):
    map_data = extra_map[name]
    name = map_data['name']
    uri = get_map_uri(map_data['url'], map_data['zmin'], map_data['zmax'], map_data['referer'])
    add_xyz_layer(uri, name)


class TianDiTu:
    def __init__(self, iface):
        self.iface = iface
        # 设置工具栏
        self.toolbar = self.iface.addToolBar('TianDiTu Toolbar')
        self.toolbar.setObjectName('TianDiTuToolbar')
        self.toolbar.setToolTip('天地图工具栏')
        self.plugin_dir = os.path.dirname(__file__)
        # 定义实例变量,摆脱烦人的Pylint警报
        self.addTiandituToolbar = None
        self.addTiandituButton = None
        self.action_setting = None

    def initGui(self):
        # 图标
        icon_setting = QIcon(self.plugin_dir + "/images/setting.svg")
        icon_logo = QIcon(self.plugin_dir + "/images/logo.svg")
        icon_add = QIcon(self.plugin_dir + "/images/Add.svg")
        icon_map = QIcon(self.plugin_dir + "/images/logo_map.svg")
        icon_googlemap_sat = QIcon(self.plugin_dir + "/images/googlemap_satellite.png")

        # 底图添加 Action
        menu = QMenu()
        menu.setObjectName('TianDiTuAddMap')
        menu.addAction(icon_map, TianMapInfo['vec'], lambda: add_tianditu_basemap('vec'))
        menu.addAction(icon_map, TianMapInfo['cva'], lambda: add_tianditu_basemap('cva'))
        menu.addAction(icon_map, TianMapInfo['img'], lambda: add_tianditu_basemap('img'))
        menu.addAction(icon_map, TianMapInfo['cia'], lambda: add_tianditu_basemap('cia'))
        menu.addAction(icon_map, TianMapInfo['ter'], lambda: add_tianditu_basemap('ter'))
        menu.addAction(icon_map, TianMapInfo['cta'], lambda: add_tianditu_basemap('cta'))
        menu.addAction(icon_map, TianMapInfo['eva'], lambda: add_tianditu_basemap('eva'))
        menu.addAction(icon_map, TianMapInfo['eia'], lambda: add_tianditu_basemap('eia'))
        menu.addAction(icon_map, TianMapInfo['ibo'], lambda: add_tianditu_basemap('ibo'))
        menu.addSeparator()
        extra_map_action = menu.addAction(icon_map, '其他图源')
        extra_map_menu = QMenu()
        extra_map_menu.addAction(icon_googlemap_sat, 'Google Map - Satellite',
                                 lambda: add_extra_map('Google Map - Satellite'))
        extra_map_action.setMenu(extra_map_menu)

        self.addTiandituButton = QToolButton()
        self.addTiandituButton.setMenu(menu)
        self.addTiandituButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.addTiandituButton.setText('添加底图')
        self.addTiandituButton.setIcon(icon_add)
        self.addTiandituButton.setToolTip('添加底图')
        self.addTiandituToolbar = self.toolbar.addWidget(self.addTiandituButton)

        # 设置 Action
        self.action_setting = QAction(icon_setting, "设置", self.iface.mainWindow())
        self.action_setting.triggered.connect(run)
        self.toolbar.addAction(self.action_setting)

    def unload(self):
        self.iface.removeToolBarIcon(self.action_setting)
        self.iface.removeToolBarIcon(self.addTiandituToolbar)
