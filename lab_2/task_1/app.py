import sys
from math import *

from common.plot_widget.controllers import RangeSelectionController
from common.plot_widget.controllers import ResizeController
from common.plot_widget.objects import OneArgFunction
from common.plot_widget.objects import RangeSelection
from common.plot_widget.objects import VerticalLine
from common.plot_widget.widget import PlotWidget
from common.plot_widget.widget import add_grid
from common.typing import Function
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
from sympy import lambdify
from sympy import symbols
from sympy import sympify

from lab_2.task_1 import domain


def _expr_to_func(expr: str) -> Function:
    x = symbols("x")
    func = lambdify([x], sympify(expr), "numpy")
    return func


class Task1Window(QWidget):
    DEFAULT_FUNCTION = "2 ** x + x ** 2 - 2.0"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(self._init_objects())

    def _init_plot_widget(self):
        self._plot_widget = PlotWidget(self, 30)
        self._answer_line = VerticalLine(
            plot_widget=self._plot_widget,
            x=1.0,
            styles={
                "color": "orange",
                "linewidth": 2,
            },
        )
        self._func_graphic = OneArgFunction(
            plot_widget=self._plot_widget,
            f=_expr_to_func(self.DEFAULT_FUNCTION),
            styles={
                "color": "red",
                "linewidth": 1,
            },
        )
        self._selection = RangeSelection(
            plot_widget=self._plot_widget,
            borders=(0, 0),
            styles={
                "color": "blue",
                "alpha": 0.2,
                "linewidth": 2,
            },
        )

        self._resize_controller = ResizeController(self._plot_widget)
        self._selection_controller = RangeSelectionController(
            plot_widget=self._plot_widget,
            range_obj=self._selection,
        )

        add_grid(self._plot_widget)
        self._answer_line.hide()

        return self._plot_widget

    def _init_function_input(self):
        self._function_layout = QHBoxLayout()
        self._function_prefix = QLabel("f(x) = ")
        self._function_input = QLineEdit(self)

        self._function_input.setText(self.DEFAULT_FUNCTION)

        self._function_layout.addWidget(self._function_prefix)
        self._function_layout.addWidget(self._function_input)

        return self._function_layout

    def _init_method_input(self):
        self._method_layout = QHBoxLayout()
        self._method_preifx = QLabel("Метод: ")
        self._method_combo_box = QComboBox()

        self._method_combo_box.addItems(["Итераций", "Ньютона"])

        self._method_layout.addWidget(self._method_preifx)
        self._method_layout.addWidget(self._method_combo_box, 1)

        return self._method_layout

    def _init_iterations_input(self):
        self._iteration_layout = QHBoxLayout()
        self._iteration_label = QLabel("Кол-во итераций: ")
        self._iteration_input = QSpinBox()

        self._iteration_input.setMinimum(1)

        self._iteration_layout.addWidget(self._iteration_label)
        self._iteration_layout.addWidget(self._iteration_input, 1)

        return self._iteration_layout

    def _init_epsilon_input(self):
        self._epsilon_layout = QHBoxLayout()
        self._epsilon_label = QLabel("eps = ")
        self._epsilon_input = QDoubleSpinBox()

        self._epsilon_input.setDecimals(10)
        self._epsilon_input.setValue(0.01)
        self._epsilon_input.setSingleStep(0.01)
        self._epsilon_input.setRange(10 ** (-10), 1.0)

        self._epsilon_layout.addWidget(self._epsilon_label)
        self._epsilon_layout.addWidget(self._epsilon_input, 1)

        return self._epsilon_layout

    def _init_answer(self):
        self._answer_layout = QVBoxLayout()
        self._answer_iterations_label = QLabel("Кол-во итераций: 0")
        self._answer_label = QLabel("Ответ: x = 0.00000")

        self._answer_label.hide()
        self._answer_iterations_label.hide()

        self._answer_layout.addWidget(self._answer_label)
        self._answer_layout.addWidget(self._answer_iterations_label)

        return self._answer_layout

    def _init_error_label(self):
        self._error_label = QLabel("Ошибка: Функция введена неверно")
        self._error_label.setStyleSheet("color: red")
        self._error_label.hide()

        return self._error_label

    def _update_range_label(self):
        a, b = self._selection.borders
        self._range_label.setText(f"Область: [{a:.5f}, {b:.5f}]")

    def _update_function(self):
        expr = self._function_input.text()

        try:
            new_function = _expr_to_func(expr)
            assert isinstance(new_function(0), (float, int))
        except:
            self._error_label.show()
        else:
            self._func_graphic.function = new_function

    def _run_solution(self):
        chosen_method = self._method_combo_box.currentText()

        if chosen_method == "Итераций":
            method = domain.iterations_method
        else:
            method = domain.newton_method

        a, b = self._selection.borders
        eps = self._epsilon_input.value()
        iterations = self._iteration_input.value()
        f = self._func_graphic.function
        ans, iters = method(f, a, b, eps, iterations)

        self._answer_label.setText(f"Ответ: x = {ans:.5f}")
        self._answer_iterations_label.setText(f"Кол-во итераций: {iters}")
        self._answer_label.show()
        self._answer_iterations_label.show()
        self._answer_line.position = ans
        self._answer_line.show()

    def _init_objects(self):
        self._start_button = QPushButton("Start")
        self._range_label = QLabel("Область: [0, 0]")

        self._main_layout = QVBoxLayout()
        self._main_layout.addWidget(self._init_plot_widget(), 1)
        self._main_layout.addLayout(self._init_function_input())
        self._main_layout.addWidget(self._init_error_label())
        self._main_layout.addWidget(self._range_label)
        self._main_layout.addLayout(self._init_epsilon_input())
        self._main_layout.addLayout(self._init_iterations_input())
        self._main_layout.addLayout(self._init_method_input())
        self._main_layout.addWidget(self._start_button)
        self._main_layout.addLayout(self._init_answer())

        self._plot_widget.mpl_connect("draw_event", lambda _: self._update_range_label())
        self._function_input.textChanged.connect(self._error_label.hide)
        self._function_input.editingFinished.connect(self._update_function)
        self._start_button.clicked.connect(self._run_solution)

        return self._main_layout


app = QtWidgets.QApplication(sys.argv)
w = Task1Window()
w.resize(600, 700)
w.show()
app.exec_()
