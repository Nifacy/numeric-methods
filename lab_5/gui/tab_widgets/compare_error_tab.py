import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QVBoxLayout, QWidget)

import domain


class CompareErrorRateTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._U = None
        self._Ux = None
        self._Ut = None
        self._grid = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Создание графика
        self._canvas = FigureCanvas(Figure())
        self._ax1, self._ax2 = self._canvas.figure.subplots(1, 2)

        self._ax1.set_xlabel("Время (t)")
        self._ax1.set_ylabel("Погрешность")

        self._ax2.set_xlabel("Координата (x)")
        self._ax2.set_ylabel("Погрешность")

        layout.addWidget(self._canvas)
        self.setLayout(layout)

    def update_content(self, grid: domain.Grid, U, Ux, Ut):
        self._grid = grid
        self._U = U
        self._Ux = Ux
        self._Ut = Ut
        self._update_graph()

    def _update_graph(self):
        self._ax1.clear()
        self._ax2.clear()

        i = 1
        h = self._grid.L / self._grid.N
        self._ax1.set_xlim(0.0, self._grid.L)

        for k, U2 in zip((3, 2, 1), self._Ut):
            t_values = np.linspace(0.0, self._grid.T, self._grid.M + 1)
            y_values = [
                abs(U2[index, i] - self._U(i * h, t))
                for index, t in enumerate(t_values)
            ]
            self._ax1.plot(t_values, y_values, label=f"N = {self._grid.N * k}")
        self._ax1.legend()

        j = 1
        tau = self._grid.T / self._grid.M
        x_values = np.linspace(0.0, self._grid.L, self._grid.N + 1)
        self._ax1.set_xlim(0.0, self._grid.T)

        for k, U2 in zip((3, 2, 1), self._Ux):
            y_values = [
                abs(U2[j, index] - self._U(x, j * tau))
                for index, x in enumerate(x_values)
            ]
            self._ax2.plot(x_values, y_values, label=f"M = {self._grid.M * k}")
        self._ax2.legend()

        self._canvas.draw()
