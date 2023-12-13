from .plugin import TianDiTu


def classFactory(iface):
    """QGIS Plugin"""
    return TianDiTu(iface)
