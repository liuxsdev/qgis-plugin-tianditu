from .plugin import TianDiTuLite


def classFactory(iface):
    """QGIS Plugin"""
    return TianDiTuLite(iface)
