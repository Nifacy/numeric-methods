from math import sin
import sys
from typing import Any, Callable, Mapping
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from .plot_widget import PlotWidget, add_grid, ResizeController
from .plot_widget.controller import RangeSelectionController, RectSelectionController
from .plot_widget.plot_widget import PlotUpdateEvent

import lab_2.task_2 as task_2

from .plot_widget.visualizers import CurveVisualizer, FunctionVisualizer, PointVisualizer, RangeSelectionVisualizer, RectAreaVisualizer, VLineVisualizer

from PyQt5.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QComboBox, QDoubleSpinBox, QSpinBox

from math import *
from sympy import symbols, sympify, lambdify


def function_from_formula(formula: str) -> Callable[[float], float]:
    x_1, x_2 = symbols('x_1 x_2')
    expression = sympify(formula)
    func = lambdify([x_1, x_2], expression, 'numpy')
    return func


class Window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(self._init_objects())

    def _init_objects(self):
        self._plot_widget = PlotWidget(self, 20)
        add_grid(self._plot_widget)
        self._function_1_visualizer = CurveVisualizer(function_from_formula('x_1 + x_2'), self._plot_widget, {
            'colors': ['red'],
            'linewidths': [1],
        })
        self._function_2_visualizer = CurveVisualizer(function_from_formula('x_1 - x_2'), self._plot_widget, {
            'colors': ['blue'],
            'linewidths': [1],
        })

        self._rect_area = RectAreaVisualizer(self._plot_widget, (0, 0), (0, 0), {
            'color': 'blue',
            'alpha': 0.2,
            'linewidth': 2,
        })
        self._resize_controller = ResizeController(self._plot_widget)
        self._range_contoller = RectSelectionController(self._plot_widget, self._rect_area)

        self._answer_point = PointVisualizer(self._plot_widget, (0, 0), {'color': 'orange', 'linewidth': 2})
        self._answer_point.hide()

        self._function_1_prefix = QLabel('f_1(x_1, x_2) = ')
        self._function_1_editor = QLineEdit(self)
        self._function_1_editor.setText('x_1 + x_2')

        self._function_2_prefix = QLabel('f_2(x_1, x_2) = ')
        self._function_2_editor = QLineEdit(self)
        self._function_2_editor.setText('x_1 - x_2')

        self._start_button = QPushButton('Start')
        self._range_label = QLabel('Область: [0, 0] x [0, 0]')
        self._method_combo_box = QComboBox()
        self._method_combo_box.addItems(['Итераций', 'Ньютона'])
        self._method_preifx = QLabel('Метод: ')
        self._answer_label = QLabel('Ответ: x = (0.0000, 0.0000)')
        self._answer_iterations_label = QLabel('Кол-во итераций: 0')

        self._error_label = QLabel('Ошибка: Функция введена неверно')
        self._error_label.setStyleSheet('color: red')
        self._error_label.hide()

        self._epsilon_label = QLabel('eps = ')
        self._epsilon_input = QDoubleSpinBox()
        self._epsilon_input.setDecimals(10)
        self._epsilon_input.setValue(0.01)
        self._epsilon_input.setSingleStep(0.01)
        self._epsilon_input.setRange(10 ** (-10), 1.0)

        self._iteration_label = QLabel('Кол-во итераций: ')
        self._iteration_input = QSpinBox()
        self._iteration_input.setMinimum(1)

        self._function_1_layout = QHBoxLayout()
        self._function_1_layout.addWidget(self._function_1_prefix)
        self._function_1_layout.addWidget(self._function_1_editor)

        self._function_2_layout = QHBoxLayout()
        self._function_2_layout.addWidget(self._function_2_prefix)
        self._function_2_layout.addWidget(self._function_2_editor)

        self._method_layout = QHBoxLayout()
        self._method_layout.addWidget(self._method_preifx)
        self._method_layout.addWidget(self._method_combo_box, 1)

        self._epsilon_layout = QHBoxLayout()
        self._epsilon_layout.addWidget(self._epsilon_label)
        self._epsilon_layout.addWidget(self._epsilon_input, 1)

        self._iteration_layout = QHBoxLayout()
        self._iteration_layout.addWidget(self._iteration_label)
        self._iteration_layout.addWidget(self._iteration_input, 1)

        self._answer_layout = QVBoxLayout()
        self._answer_layout.addWidget(self._answer_label)
        self._answer_layout.addWidget(self._answer_iterations_label)
        self._answer_label.hide()
        self._answer_iterations_label.hide()

        self._main_layout = QVBoxLayout()
        self._main_layout.addWidget(self._plot_widget, 1)
        self._main_layout.addLayout(self._function_1_layout)
        self._main_layout.addLayout(self._function_2_layout)
        self._main_layout.addWidget(self._error_label)
        self._main_layout.addLayout(self._epsilon_layout)
        self._main_layout.addLayout(self._iteration_layout)
        self._main_layout.addWidget(self._range_label)
        self._main_layout.addLayout(self._method_layout)
        self._main_layout.addWidget(self._start_button)
        self._main_layout.addLayout(self._answer_layout)

        # bindings
        def f1(_):
            (x1, y1), (x2, y2) = self._rect_area.coords
            self._range_label.setText(f'Область: [{x1:.5f}, {x2:.5f}] x [{y1:.5f}, {y2:.5f}]')

        def update_function(editor, visualizer):
            def _handler():
                formula = editor.text()
                try:
                    new_function = function_from_formula(formula)
                    new_function(0, 0)
                except:
                    self._error_label.show()
                else:
                    visualizer.function = new_function
            return _handler

        def f3():
            choosed_method = self._method_combo_box.currentText()
            if choosed_method == 'Итераций':
                method = task_2.iteration_method
            else:
                method = task_2.newton_method

            s1, s2 = map(np.array, self._rect_area.coords)
            eps = self._epsilon_input.value()
            iterations = self._iteration_input.value()
            f1 = self._function_1_visualizer.function
            f2 = self._function_2_visualizer.function
            f = task_2.VectorFunction([
                lambda x: f1(x[0], x[1]),
                lambda x: f2(x[0], x[1]),
            ])

            ans, iterations = method(f, s1, s2, eps, iterations)

            self._answer_label.setText(f'Ответ: x = ({ans[0]:.5f}, {ans[1]:.5f})')
            self._answer_iterations_label.setText(f'Кол-во итераций: {iterations}')
            self._answer_label.show()
            self._answer_iterations_label.show()
            self._answer_point.position = (ans[0], ans[1])
            self._answer_point.show()

        self._plot_widget.mpl_connect('draw_event', f1)
        self._function_1_editor.textChanged.connect(self._error_label.hide)
        self._function_2_editor.textChanged.connect(self._error_label.hide)
        self._function_1_editor.editingFinished.connect(update_function(self._function_1_editor, self._function_1_visualizer))
        self._function_2_editor.editingFinished.connect(update_function(self._function_2_editor, self._function_2_visualizer))
        self._start_button.clicked.connect(f3)

        return self._main_layout


app = QtWidgets.QApplication(sys.argv)
w = Window()
w.resize(600, 700)
w.show()
app.exec_()
