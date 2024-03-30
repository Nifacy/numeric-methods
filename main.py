from math import sin
import sys
from typing import Any, Callable, Mapping
import numpy as np
from PyQt5 import QtWidgets
from plot_widget import PlotWidget, add_grid, ResizeController
from plot_widget.controller import RangeSelectionController
from plot_widget.plot_widget import PlotUpdateEvent

import matplotlib.pyplot as plt

from plot_widget.visualizers import FunctionVisualizer, RangeSelectionVisualizer





class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.resize(400, 400)
        self._init_plot_widget()
        self.setCentralWidget(self._plot_widget)
        self.show()
    
    def _init_plot_widget(self):
        self._plot_widget = PlotWidget(self, scale=50.0)
        self._controller = ResizeController(self._plot_widget)
        self._a = RangeSelectionController(self._plot_widget)
        add_grid(self._plot_widget)

        self._v2 = RangeSelectionVisualizer((0.0, 1.0), self._plot_widget)

        self._v = FunctionVisualizer(lambda x: sin(x), self._plot_widget, {'color': 'red'})
        self._plot_widget.on_update.connect(self._v._on_update)


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()
