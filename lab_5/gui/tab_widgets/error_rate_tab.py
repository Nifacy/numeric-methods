from typing import Callable
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QSlider, QVBoxLayout, QWidget)
from common.typing import Matrix

import domain


class ErrorRateTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._U = None
        self._U2 = None
        self._grid = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Создание графика
        self.canvas = FigureCanvas(Figure())
        self.ax = self.canvas.figure.subplots()
        (self._plot,) = self.ax.plot([0], [0])

        self.ax.set_xlabel("Время (t)")
        self.ax.set_ylabel("Погрешность")

        # Ползунок для изменения графика
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(
            self._update_graph
        )  # Привязка к обновлению графика

        # Добавление ползунка и графика в layout
        layout.addWidget(self.canvas)
        layout.addWidget(self.slider)
        self.setLayout(layout)

    def update_content(self, grid: domain.Grid, U: Callable[[float, float], float], U2: Matrix):
        self._grid = grid
        self._U = U
        self._U2 = U2
        self.slider.setValue(0)
        self.slider.setMaximum(self._grid.N)
        self._update_graph()

    def _update_graph(self):
        index = self.slider.value()
        h = self._grid.L / self._grid.N
        t_values = np.linspace(0.0, self._grid.T, self._grid.M + 1)

        if self._grid is not None:
            self.ax.set_xlim(0.0, self._grid.L)

        if self._U2 is not None and self._U is not None:
            # считаем модуль разности между эталонным и полученным решениями
            y_values = [
                abs(self._U2[i, index] - self._U(index * h, t))
                for i, t in enumerate(t_values)
            ]

            self._plot.set_data(t_values, y_values)
            self.ax.set_ylim(0.0, max(y_values))

        self.canvas.draw()
