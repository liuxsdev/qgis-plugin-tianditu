from qgis.core import QgsProject, QgsRasterLayer


def add_raster_layer(uri: str, name: str, provider_type: str = "wms") -> None:
    """QGIS 添加栅格图层

    Args:
        uri (str): 栅格图层uri
        name (str): 栅格图层名称
        provider_type(str): 栅格图层类型(wms,arcgismapserver)
    Reference: https://qgis.org/pyqgis/3.32/core/QgsRasterLayer.html
    """
    raster_layer = QgsRasterLayer(uri, name, provider_type)
    QgsProject.instance().addMapLayer(raster_layer)
