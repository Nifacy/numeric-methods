from math import sin
import sys
from typing import Any, Callable, Mapping
import numpy as np
from PyQt5 import QtWidgets
from plot_widget import PlotWidget, add_grid, ResizeController
from plot_widget.controller import RangeSelectionController
from plot_widget.plot_widget import PlotUpdateEvent

import task_1

from PyQt5.QtCore import QTimer

import matplotlib.pyplot as plt

from plot_widget.visualizers import FunctionVisualizer, RangeSelectionVisualizer

from PyQt5.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QComboBox


from math import *


def function_from_formula(formula: str) -> Callable[[float], float]:
    def _f(x: float) -> float:
        return eval(formula.replace('x', f'({x})'))
    return _f


class Winow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(self._init_objects())

    def _init_objects(self):
        self._plot_widget = PlotWidget(self)
        add_grid(self._plot_widget)
        self._function_visualizer = FunctionVisualizer(function_from_formula('x ** 2 - 2'), self._plot_widget, {
            'color': 'red',
            'linewidth': 1,
        })
        self._range_visualizer = RangeSelectionVisualizer((0, 0), self._plot_widget, {
            'color': 'blue',
            'alpha': 0.2,
            'linewidth': 2,
        })
        self._resize_controller = ResizeController(self._plot_widget)
        self._range_contoller = RangeSelectionController(self._plot_widget, self._range_visualizer)

        self._function_prefix = QLabel('f(x) = ')
        self._function_editor = QLineEdit(self)
        self._start_button = QPushButton('Start')
        self._range_label = QLabel('Область: [0, 0]')
        self._method_combo_box = QComboBox()
        self._method_combo_box.addItems(['Итераций', 'Ньютона'])
        self._method_preifx = QLabel('Метод: ')
        self._answer_label = QLabel('Ответ: x = 0.00000')

        self._function_layout = QHBoxLayout()
        self._function_layout.addWidget(self._function_prefix)
        self._function_layout.addWidget(self._function_editor)

        self._method_layout = QHBoxLayout()
        self._method_layout.addWidget(self._method_preifx)
        self._method_layout.addWidget(self._method_combo_box, 1)

        self._main_layout = QVBoxLayout()
        self._main_layout.addWidget(self._plot_widget, 1)
        self._main_layout.addLayout(self._function_layout)
        self._main_layout.addWidget(self._range_label)
        self._main_layout.addLayout(self._method_layout)
        self._main_layout.addWidget(self._start_button)
        self._main_layout.addWidget(self._answer_label)

        # bindings
        def f1(_):
            a, b = self._range_visualizer.borders
            self._range_label.setText(f'Область: [{a:.5f}, {b:.5f}]')
        
        def f2():
            formula = self._function_editor.text()
            self._function_visualizer.function = function_from_formula(formula)
        
        def f3():
            choosed_method = self._method_combo_box.currentText()
            if choosed_method == 'Итераций':
                method = task_1.iterations_method
            else:
                method = task_1.newton_method

            a, b = self._range_visualizer.borders
            eps = 0.0001
            iterations = 100
            f = self._function_visualizer.function
            ans = method(f, a, b, eps, iterations)

            self._answer_label.setText(f'Ответ: x = {ans:.5f}')

        self._plot_widget.mpl_connect('draw_event', f1)
        self._function_editor.editingFinished.connect(f2)
        self._start_button.clicked.connect(f3)

        return self._main_layout



# class MainWindow(QtWidgets.QMainWindow):
#     def __init__(self, *args, **kwargs):
#         super(MainWindow, self).__init__(*args, **kwargs)
#         self.resize(400, 400)
#         self._init_plot_widget()
#         self.setCentralWidget(self._plot_widget)
#         self.show()

#     def _init_plot_widget(self):
#         self._plot_widget = PlotWidget(self, scale=50.0)
#         self._controller = ResizeController(self._plot_widget)
#         add_grid(self._plot_widget)

#         self._v2 = RangeSelectionVisualizer((0.0, 1.0), self._plot_widget, {
#             'color': 'blue',
#             'alpha': 0.2,
#             'linewidth': 4,
#         })

#         self._a = RangeSelectionController(self._plot_widget, self._v2)

#         self._v = FunctionVisualizer(lambda x: sin(x), self._plot_widget, {'color': 'red'})
#         self._plot_widget.on_update.connect(self._v._on_update)


app = QtWidgets.QApplication(sys.argv)
w = Winow()
w.resize(600, 700)
w.show()
app.exec_()
