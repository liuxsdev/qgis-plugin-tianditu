import os
import requests
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QMenu, QToolButton
from qgis.core import Qgis, QgsRasterLayer, QgsProject
from .tiandituConfig import TianMapInfo

current_qgis_version = Qgis.versionInt()


def run():
    print("running")


def add_xyz_layer(uri, name):
    raster_layer = QgsRasterLayer(uri, name, 'wms')
    QgsProject.instance().addMapLayer(raster_layer)


def tianditu_map_url(maptype, token):
    url = 'https://t2.tianditu.gov.cn/'
    url += f'{maptype}_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER={maptype}'
    url += '&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TileCol={x}&TileRow={y}&TileMatrix={z}'
    url += f'&tk={token}'
    return url


def get_map_uri(url, zmin=0, zmax=18, referer='https://www.tianditu.gov.cn/'):
    url_quote = requests.utils.quote(url, safe=':/')
    if current_qgis_version >= 32600:
        uri = f'type=xyz&url={url_quote}&zmin={zmin}&zmax={zmax}&http-header:referer={referer}'
    else:
        uri = f'type=xyz&url={url_quote}&zmin={zmin}&zmax={zmax}&referer={referer}'
    return uri


def add_tianditu_basemap(maptype):
    token = 'cfcbc282308686d26782fcb4e11b32a4'
    uri = get_map_uri(tianditu_map_url(maptype, token))
    add_xyz_layer(uri, TianMapInfo[maptype])


class TianDiTu:
    def __init__(self, iface):
        self.iface = iface
        # 设置工具栏
        self.toolbar = self.iface.addToolBar('TianDiTu Toolbar')
        self.toolbar.setObjectName('TianDiTuToolbar')
        self.toolbar.setToolTip('天地图工具栏')

    def initGui(self):
        # 图标
        icon_setting = QIcon(os.path.dirname(__file__) + "/images/setting.svg")
        icon_logo = QIcon(os.path.dirname(__file__) + "/images/logo.svg")

        # 底图添加 Action
        menu = QMenu()
        menu.setObjectName('TianDiTuAddMap')
        self.action_addTianditu_vec = menu.addAction(icon_logo, TianMapInfo['vec'],
                                                     lambda: add_tianditu_basemap('vec'))
        self.action_addTianditu_cva = menu.addAction(icon_logo, TianMapInfo['cva'],
                                                     lambda: add_tianditu_basemap('cva'))
        self.action_addTianditu_img = menu.addAction(icon_logo, TianMapInfo['img'],
                                                     lambda: add_tianditu_basemap('img'))
        self.action_addTianditu_cia = menu.addAction(icon_logo, TianMapInfo['cia'],
                                                     lambda: add_tianditu_basemap('cia'))
        self.action_addTianditu_ter = menu.addAction(icon_logo, TianMapInfo['ter'],
                                                     lambda: add_tianditu_basemap('ter'))
        self.action_addTianditu_cta = menu.addAction(icon_logo, TianMapInfo['cta'],
                                                     lambda: add_tianditu_basemap('cta'))
        self.action_addTianditu_eva = menu.addAction(icon_logo, TianMapInfo['eva'],
                                                     lambda: add_tianditu_basemap('eva'))
        self.action_addTianditu_eia = menu.addAction(icon_logo, TianMapInfo['eia'],
                                                     lambda: add_tianditu_basemap('eia'))
        self.action_addTianditu_ibo = menu.addAction(icon_logo, TianMapInfo['ibo'],
                                                     lambda: add_tianditu_basemap('ibo'))
        self.action_addTiandutu = QAction(icon_setting, '添加底图', self.iface.mainWindow())
        self.action_addTiandutu.setMenu(menu)

        self.addTiandituButton = QToolButton()
        self.addTiandituButton.setMenu(menu)
        self.addTiandituButton.setDefaultAction(self.action_addTianditu_vec)
        self.addTiandituButton.setPopupMode(QToolButton.MenuButtonPopup)
        self.addTiandituToolbar = self.toolbar.addWidget(self.addTiandituButton)
        # 设置 Action
        self.action_setting = QAction(icon_setting, "设置", self.iface.mainWindow())
        self.action_setting.triggered.connect(run)
        self.toolbar.addAction(self.action_setting)

    def unload(self):
        self.iface.removeToolBarIcon(self.action_setting)
        self.iface.removeToolBarIcon(self.addTiandituToolbar)
