import os

from qgis.PyQt import QtWidgets, uic
from .utils import PluginDir

FORM_CLASS, _ = uic.loadUiType(os.path.join(PluginDir, './ui/search.ui'))


class SearchDialogWidget(QtWidgets.QDockWidget, FORM_CLASS):
    def __init__(self, parent=None):
        super(SearchDialogWidget, self).__init__(parent)
        self.setupUi(self)
