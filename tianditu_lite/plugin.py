from qgis.core import QgsApplication

from .provider import TiandituProvider


class TianDiTuLite:
    def __init__(self, iface):
        self.iface = iface
        self.initGui()

    def initGui(self):
        self.registProvider()

    def registProvider(self):
        """注册自定义的 QgsDataItemProvider"""
        self.removeProvider()
        t = TiandituProvider(self.iface)
        QgsApplication.instance().dataItemProviderRegistry().addProvider(t)

    def removeProvider(self):
        p = QgsApplication.instance().dataItemProviderRegistry().provider("Tianditu")
        if p:
            QgsApplication.instance().dataItemProviderRegistry().removeProvider(p)

    def unload(self):
        """Unload from the QGIS interface"""
        self.removeProvider()
