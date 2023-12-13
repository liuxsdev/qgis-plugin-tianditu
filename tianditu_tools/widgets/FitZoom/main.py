from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsCoordinateReferenceSystem

from tianditu_tools.widgets.icons import icons


def find_nearest_number_index(numbers_list, target):
    min_difference = float("inf")
    nearest_index = None

    for i, number in enumerate(numbers_list):
        difference = abs(number - target)
        if difference < min_difference:
            min_difference = difference
            nearest_index = i

    return nearest_index


class FitZoomAction(QAction):
    def __init__(self, iface, parent=None):
        self.iface = iface
        super().__init__(parent)
        self.setIcon(icons["fitzoom"])
        self.setText("调整缩放比例")
        self.triggered.connect(
            self.fit_zoom_level
        )  # how to fix pycharm: 'pyqtSignal | pyqtSignal' 中找不到引用 'connect'
        self.iface.mapCanvas().destinationCrsChanged.connect(self.check_crs)
        self.iface.mapCanvas().layersChanged.connect(self.check_crs)

    def fit_zoom_level(self):
        crs = self.iface.mapCanvas().mapSettings().destinationCrs()
        if crs == QgsCoordinateReferenceSystem("EPSG:3857"):
            max_zoom_level = 23
            mpp_3857 = [40075016.685 / (2**i * 256) for i in range(max_zoom_level)]
            current_mpp = self.iface.mapCanvas().mapUnitsPerPixel()
            nearest_level = find_nearest_number_index(mpp_3857, current_mpp)
            zoom_factor = mpp_3857[nearest_level] / current_mpp
            if not abs(1 - zoom_factor) < 1e-5:
                self.iface.mapCanvas().zoomByFactor(zoom_factor)

    def check_crs(self):
        crs = self.iface.mapCanvas().mapSettings().destinationCrs()
        layers_number = self.iface.mapCanvas().layerCount()
        if crs == QgsCoordinateReferenceSystem("EPSG:3857") and layers_number > 0:
            self.setEnabled(True)
        else:
            self.setText("调整缩放比例不可用")
            self.setEnabled(False)
