from math import sin
import sys
from typing import Any, Callable, Mapping
import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtCore import QTimer
from lab_2.plot_widget.widget import PlotWidget, add_grid
from lab_2.plot_widget.controllers import RangeSelectionController, RectSelectionController, ResizeController
from lab_2.plot_widget.widget import PlotUpdateEvent

from lab_2.task_2 import domain

from lab_2.plot_widget.objects import Curve, OneArgFunction, Coords, RangeSelection, RectArea, VerticalLine, Point

from PyQt5.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QComboBox, QDoubleSpinBox, QSpinBox

from math import *
from sympy import symbols, sympify, lambdify


def _expr_to_func(expr: str) -> Callable[[float, float], float]:
    x_1, x_2 = symbols('x_1 x_2')
    func = lambdify([x_1, x_2], sympify(expr), 'numpy')
    return func


class Task2Window(QWidget):
    DEFAULT_FUNCTIONS = ('x_1 ** 2 + x_2 ** 2 - 2 ** 2', 'x_1 - exp(x_2) + 2')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(self._init_objects())


    def _init_plot_widget(self):
        self._plot_widget = PlotWidget(self, 20.0)
        self._func_1_graphic = Curve(
            plot_widget=self._plot_widget,
            f=_expr_to_func(self.DEFAULT_FUNCTIONS[0]),
            styles={
                'colors': ['red'],
                'linewidths': [1],
            }
        )
        self._func_2_graphic = Curve(
            plot_widget=self._plot_widget,
            f=_expr_to_func(self.DEFAULT_FUNCTIONS[1]),
            styles={
                'colors': ['blue'],
                'linewidths': [1],
            }
        )
        self._rect_area = RectArea(
            plot_widget=self._plot_widget,
            s1=(0, 0),
            s2=(0, 0),
            styles={
                'color': 'blue',
                'alpha': 0.2,
                'linewidth': 2,
            },
        )
        self._answer_point = Point(
            plot_widget=self._plot_widget,
            pos=(0, 0),
            styles={
                'color': 'orange',
                'linewidth': 2,
            },
        )

        self._resize_controller = ResizeController(self._plot_widget)
        self._range_contoller = RectSelectionController(self._plot_widget, self._rect_area)

        add_grid(self._plot_widget)
        self._answer_point.hide()

        return self._plot_widget


    def _init_function_1_input(self):
        self._function_1_layout = QHBoxLayout()
        self._function_1_prefix = QLabel('f_1(x_1, x_2) = ')
        self._function_1_editor = QLineEdit(self)

        self._function_1_editor.setText(self.DEFAULT_FUNCTIONS[0])

        self._function_1_layout.addWidget(self._function_1_prefix)
        self._function_1_layout.addWidget(self._function_1_editor)

        return self._function_1_layout


    def _init_function_2_input(self):
        self._function_2_layout = QHBoxLayout()
        self._function_2_prefix = QLabel('f_2(x_1, x_2) = ')
        self._function_2_editor = QLineEdit(self)

        self._function_2_editor.setText(self.DEFAULT_FUNCTIONS[1])

        self._function_2_layout.addWidget(self._function_2_prefix)
        self._function_2_layout.addWidget(self._function_2_editor)

        return self._function_2_layout


    def _init_method_input(self):
        self._method_layout = QHBoxLayout()
        self._method_preifx = QLabel('Метод: ')
        self._method_combo_box = QComboBox()
        
        self._method_combo_box.addItems(['Итераций', 'Ньютона'])
        
        self._method_layout.addWidget(self._method_preifx)
        self._method_layout.addWidget(self._method_combo_box, 1)
        
        return self._method_layout


    def _init_error_label(self):
        self._error_label = QLabel('Ошибка: Функция введена неверно')
        self._error_label.setStyleSheet('color: red')
        self._error_label.hide()

        return self._error_label


    def _init_epsilon_input(self):
        self._epsilon_layout = QHBoxLayout()
        self._epsilon_label = QLabel('eps = ')
        self._epsilon_input = QDoubleSpinBox()

        self._epsilon_input.setDecimals(10)
        self._epsilon_input.setValue(0.01)
        self._epsilon_input.setSingleStep(0.01)
        self._epsilon_input.setRange(10 ** (-10), 1.0)

        self._epsilon_layout.addWidget(self._epsilon_label)
        self._epsilon_layout.addWidget(self._epsilon_input, 1)

        return self._epsilon_layout


    def _init_iteration_input(self):
        self._iteration_layout = QHBoxLayout()
        self._iteration_label = QLabel('Кол-во итераций: ')
        self._iteration_input = QSpinBox()

        self._iteration_input.setMinimum(1)

        self._iteration_layout.addWidget(self._iteration_label)
        self._iteration_layout.addWidget(self._iteration_input, 1)

        return self._iteration_layout


    def _init_answer_layout(self):
        self._answer_layout = QVBoxLayout()
        self._answer_label = QLabel('Ответ: x = (0.0000, 0.0000)')
        self._answer_iterations_label = QLabel('Кол-во итераций: 0')

        self._answer_label.hide()
        self._answer_iterations_label.hide()

        self._answer_layout.addWidget(self._answer_label)
        self._answer_layout.addWidget(self._answer_iterations_label)

        return self._answer_layout


    def _update_range_label(self):
        (x1, y1), (x2, y2) = self._rect_area.coords
        self._range_label.setText(f'Область: [{x1:.5f}, {x2:.5f}] x [{y1:.5f}, {y2:.5f}]')


    def _update_function(self, editor, visualizer):
        def _handler():
            formula = editor.text()
            try:
                new_function = _expr_to_func(formula)
                new_function(0, 0)
            except:
                self._error_label.show()
            else:
                visualizer.function = new_function
        return _handler


    def _run_solution(self):
        choosed_method = self._method_combo_box.currentText()

        if choosed_method == 'Итераций':
            method = domain.iteration_method
        else:
            method = domain.newton_method

        s1, s2 = map(np.array, self._rect_area.coords)
        eps = self._epsilon_input.value()
        iterations = self._iteration_input.value()
        f1 = self._func_1_graphic.function
        f2 = self._func_2_graphic.function
        f = domain.VectorFunction([
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


    def _init_objects(self):
        self._start_button = QPushButton('Start')
        self._range_label = QLabel('Область: [0, 0] x [0, 0]')

        self._main_layout = QVBoxLayout()
        self._main_layout.addWidget(self._init_plot_widget(), 1)
        self._main_layout.addLayout(self._init_function_1_input())
        self._main_layout.addLayout(self._init_function_2_input())
        self._main_layout.addWidget(self._init_error_label())
        self._main_layout.addLayout(self._init_epsilon_input())
        self._main_layout.addLayout(self._init_iteration_input())
        self._main_layout.addWidget(self._range_label)
        self._main_layout.addLayout(self._init_method_input())
        self._main_layout.addWidget(self._start_button)
        self._main_layout.addLayout(self._init_answer_layout())

        # bindings

        self._plot_widget.mpl_connect('draw_event', lambda _: self._update_range_label())
        self._function_1_editor.textChanged.connect(self._error_label.hide)
        self._function_2_editor.textChanged.connect(self._error_label.hide)
        self._function_1_editor.editingFinished.connect(self._update_function(self._function_1_editor, self._func_1_graphic))
        self._function_2_editor.editingFinished.connect(self._update_function(self._function_2_editor, self._func_2_graphic))
        self._start_button.clicked.connect(self._run_solution)

        return self._main_layout


app = QtWidgets.QApplication(sys.argv)
w = Task2Window()
w.resize(600, 700)
w.show()
app.exec_()
