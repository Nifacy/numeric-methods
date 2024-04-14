from dataclasses import dataclass
import sys
from math import *
from typing import Callable, Iterable
import numpy as np

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QSpacerItem,
    QSizePolicy
)
from PyQt5.QtCore import pyqtSignal
from sympy import lambdify, symbols, sympify

from common.plot_widget.controllers import PointDragController, ResizeController
from common.plot_widget.objects import OneArgFunction, Point
from common.plot_widget.widget import PlotWidget, add_grid
from lab_3.task_3 import domain


class Window(QWidget):
    DEFAULT_COORDINATES: list[tuple[float, float]] = [(0, 0), (1, 1), (2, 3), (3, 2)]

    @dataclass(frozen=True, slots=True)
    class NodesChanged:
        nodes: tuple[tuple[float, float], ...]

    on_nodes_changed = pyqtSignal(NodesChanged)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._node_points = []
        self.setLayout(self._init_objects())

        self.on_nodes_changed.connect(self._update_graphic)
        self.on_nodes_changed.connect(self._update_points_info)
        self.on_nodes_changed.connect(self._update_value_layout)
        self._argument_input.valueChanged.connect(self._update_value_layout)
        self._push_nodes_changed_event()
    
    def _init_objects(self):
        self._main_layout = QHBoxLayout()
        self._main_layout.addWidget(self._init_plot_widget())

        self._panel = QVBoxLayout()
        self._panel.addLayout(self._init_info_layout())
        self._panel.addLayout(self._init_value_layout())

        self._main_layout.addLayout(self._panel)

        for node_coords in self.DEFAULT_COORDINATES:
            self._create_node_point(node_coords)

        return self._main_layout

    def _init_plot_widget(self):
        self._plot_widget = PlotWidget(self, 30)
        self._func_graphic = OneArgFunction(
            plot_widget=self._plot_widget,
            f=lambda _: 0.0,
            styles={
                "color": "red",
                "linewidth": 1,
            },
        )

        self._resize_controller = ResizeController(self._plot_widget)
        add_grid(self._plot_widget)

        return self._plot_widget

    def _update_graphic(self, event: NodesChanged) -> None:
        nodes = list(event.nodes)
        nodes.sort(key=lambda p: p[0])

        try:
            p = domain.MinimalSquareInterpolation(2, nodes)
            self._func_graphic.function = p
        except:
            pass

    def _update_points_info(self, event: NodesChanged) -> None:
        for label, (x, y) in zip(self._point_coords_labels, event.nodes):
            label.setText(f'X = {x:.5f}, Y = {y:.5f}')

    def _push_nodes_changed_event(self) -> None:
        self.on_nodes_changed.emit(
            self.NodesChanged(
                nodes=tuple(
                    point.position
                    for (point, _) in self._node_points
                ),
            ),
        )

    def _create_node_point(self, coords: tuple[float, float]) -> None:
        node_point = Point(
            plot_widget=self._plot_widget,
            pos=coords,
            styles={
                "color": "red",
                "linewidth": 5,
            }
        )

        controller = PointDragController(
            plot_widget=self._plot_widget,
            point=node_point,
        )

        controller.on_update.connect(self._push_nodes_changed_event)
        self._node_points.append((node_point, controller))
    
    def _init_info_layout(self) -> QVBoxLayout:
        self._point_coords_labels = [
            QLabel(parent=self) for _ in self.DEFAULT_COORDINATES
        ]

        self._info_layout = QVBoxLayout()
        for point_label in self._point_coords_labels:
            self._info_layout.addWidget(point_label)

        return self._info_layout
    
    def _init_value_layout(self) -> QHBoxLayout:
        self._argument_input_label = QLabel(text='X* = ')

        self._argument_input = QDoubleSpinBox()
        self._argument_input.setDecimals(3)
        self._argument_input.setValue(0.001)
        self._argument_input.setSingleStep(0.001)

        self._value_label = QLabel(text='f(X*) = 0.0')

        self._value_layout = QHBoxLayout()
        self._value_layout.addWidget(self._argument_input_label)
        self._value_layout.addWidget(self._argument_input)
        self._value_layout.addWidget(self._value_label)

        return self._value_layout
    
    def _update_value_layout(self):
        argument = self._argument_input.value()
        f = self._func_graphic.function
        value = f(argument)
        self._value_label.setText(f'f(X*) = {value:.5f}')



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Window()
    w.resize(800, 500)
    w.show()
    app.exec_()
