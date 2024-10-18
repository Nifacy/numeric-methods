from typing import Callable
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QSlider, QVBoxLayout, QWidget)

import domain
from common.typing import Matrix


class SolutionTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._U = None
        self._U2 = None
        self._grid = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Создание графика
        self._canvas = FigureCanvas(Figure())
        self._ax = self._canvas.figure.subplots()
        (self._plot_approx,) = self._ax.plot([0], [0], label="Аппроксимация U'")
        (self._plot_etalone,) = self._ax.plot(
            [0], [0],
            label="Эталонное решение U",
            linestyle="--",
        )

        self._ax.set_xlabel("Координата x")
        self._ax.set_ylabel("Значение U(x, t)")

        self._ax.set_ylim(-1.0, 1.0)
        self._ax.legend()

        # Ползунок для изменения графика
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setMinimum(1)
        self._slider.setMaximum(100)
        self._slider.setValue(50)
        self._slider.valueChanged.connect(
            self._update_graph
        )  # Привязка к обновлению графика

        # Добавление ползунка и графика в layout
        layout.addWidget(self._canvas)
        layout.addWidget(self._slider)
        self.setLayout(layout)

    def update_content(
        self,
        grid: domain.Grid,
        U: Callable[[float, float], float],
        U2: Matrix
    ):
        self._grid = grid
        self._U = U
        self._U2 = U2
        self._slider.setValue(0)
        self._slider.setMaximum(self._grid.M)
        self._update_graph()

    def _update_graph(self):
        index = self._slider.value()
        tau = self._grid.T / self._grid.M
        tau = self._grid.T / self._grid.M
        x_values = np.linspace(0.0, self._grid.L, self._grid.N + 1)

        if self._grid is not None:
            self._ax.set_xlim(0.0, self._grid.L)

        if self._U2 is not None:
            self._plot_approx.set_data(x_values, self._U2[index, :])

        if self._U is not None:
            self._plot_etalone.set_data(x_values, self._U(x_values, index * tau))

        self._canvas.draw()
