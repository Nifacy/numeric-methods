from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
import sys

import numpy as np

from common.plot_widget.widget import PlotWidget
from common.utils import function_from_expr
from lab_4.lib.ode import euler, runge_kutta, adams
from lab_4.lib.errors import max_absolute_error, runge_romberg_error
from lab_4.lib.typing import DiffEquation, Grid


# TODO: fix bug with reset xlim, ylim
class Window(QWidget):
    METHOD_BY_ALIAS = {
        "Эйлера": euler,
        "Рунге-Кутта": runge_kutta,
        "Адамса": adams,
    }

    DEFAULT_VALUES = {
        "p": "1.0",
        "q": "-4 * x",
        "r": "4 * x ** 2 - 2",
        "f": "0.0",
        "y": "(1 + x) * exp(x ** 2)",
        "y0": 1.0,
        "y'0": 1.0,
        "a": 0.0,
        "b": 1.0,
        "h": 0.1,
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setLayout(self._init_objects())

        self._start_button.clicked.connect(self._run_method)
        self._run_method()

    def _init_objects(self):
        self._main_layout = QHBoxLayout()
        self._main_layout.addLayout(self._init_input_layout())
        self._main_layout.addLayout(self._init_result_layout(), 1)
        return self._main_layout
    
    def _init_input_layout(self):
        self._p_layout, _, self._p_input = self._init_text_input("p(x) = ", self.DEFAULT_VALUES["p"])
        self._q_layout, _, self._q_input = self._init_text_input("q(x) = ", self.DEFAULT_VALUES["q"])
        self._r_layout, _, self._r_input = self._init_text_input("r(x) = ", self.DEFAULT_VALUES["r"])
        self._f_layout, _, self._f_input = self._init_text_input("f(x) = ", self.DEFAULT_VALUES["f"])
        self._y_layout, _, self._y_input = self._init_text_input("y(x) = ", self.DEFAULT_VALUES["y"])

        self._input_layout = QVBoxLayout()
        self._input_layout.addLayout(self._p_layout)
        self._input_layout.addLayout(self._q_layout)
        self._input_layout.addLayout(self._r_layout)
        self._input_layout.addLayout(self._f_layout)
        self._input_layout.addLayout(self._y_layout)
        self._input_layout.addLayout(self._init_method_choose_input())
        self._input_layout.addLayout(self._init_start_value_layout())
        self._input_layout.addLayout(self._init_range_layout())
        self._input_layout.addWidget(self._init_start_button())
        self._input_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        return self._input_layout
    
    def _init_result_layout(self):
        self._result_layout = QVBoxLayout()
        self._result_layout.addLayout(self._init_graph_layout(), 1)
        self._result_layout.addLayout(self._init_abs_error_layout())
        return self._result_layout
    
    def _init_text_input(self, label: str, default_value: str = ""):
        prefix = QLabel(label)
        input_field = QLineEdit()
        input_field.setText(default_value)

        layout = QHBoxLayout()
        layout.addWidget(prefix)
        layout.addWidget(input_field, 1)

        return layout, prefix, input_field

    def _init_range_layout(self):
        self._a_layout, _, self._a_input = self._init_float_input("a: ", min_value=0.0, default_value=self.DEFAULT_VALUES["a"])
        self._b_layout, _, self._b_input = self._init_float_input("b: ", min_value=0.0, default_value=self.DEFAULT_VALUES["b"])
        self._h_layout, _, self._h_input = self._init_float_input("h: ", min_value=0.0, step=0.1, default_value=self.DEFAULT_VALUES["h"])
    
        self._range_layout = QHBoxLayout()
        self._range_layout.addLayout(self._a_layout)
        self._range_layout.addLayout(self._b_layout)
        self._range_layout.addLayout(self._h_layout)

        return self._range_layout

    def _init_method_choose_input(self):
        self._method_layout = QHBoxLayout()
        self._method_preifx = QLabel("Метод: ")
        self._method_combo_box = QComboBox()

        self._method_combo_box.addItems(list(self.METHOD_BY_ALIAS.keys()))

        self._method_layout.addWidget(self._method_preifx)
        self._method_layout.addWidget(self._method_combo_box, 1)

        return self._method_layout

    def _init_start_value_layout(self):
        self._y0_layout, _, self._y0_input = self._init_float_input("y(a) = ", step=0.01, default_value=self.DEFAULT_VALUES["y0"])
        self._dy0_layout, _, self._dy0_input = self._init_float_input("y'(a) = ", step=0.01, default_value=self.DEFAULT_VALUES["y'0"])

        self._start_value_layout = QHBoxLayout()
        self._start_value_layout.addLayout(self._y0_layout)
        self._start_value_layout.addLayout(self._dy0_layout)

        return self._start_value_layout

    def _init_float_input(self, label, min_value=None, max_value=None, step=None, default_value=None):
        prefix = QLabel(label)
        input_field = QDoubleSpinBox()

        if min_value is not None:
            input_field.setMinimum(min_value)
        if max_value is not None:
            input_field.setMaximum(max_value)
        if step is not None:
            input_field.setSingleStep(step)
        if default_value is not None:
            input_field.setValue(default_value)
        
        layout = QHBoxLayout()
        layout.addWidget(prefix)
        layout.addWidget(input_field, 1)

        return layout, prefix, input_field

    def _init_start_button(self):
        self._start_button = QPushButton("Расчет")
        return self._start_button
    
    def _init_graph_layout(self):
        self._func_graph = PlotWidget(scale=30, auto_update=False)
        self._error_graph = PlotWidget(scale=30, auto_update=False)

        self._graph_layout = QHBoxLayout()
        self._graph_layout.addWidget(self._func_graph)
        self._graph_layout.addWidget(self._error_graph)

        return self._graph_layout
    
    def _init_abs_error_layout(self):
        self._abs_error_prefix = QLabel("Абсолютная погрешность: ")
        self._abs_error_value = QLabel("-")

        self._abs_error_layout = QHBoxLayout()
        self._abs_error_layout.addWidget(self._abs_error_prefix)
        self._abs_error_layout.addWidget(self._abs_error_value, 1)

        return self._abs_error_layout
    
    def _run_method(self):
        method_alias = self._method_combo_box.currentText()
        method = self.METHOD_BY_ALIAS[method_alias]

        f = function_from_expr(self._y_input.text() or "0")
        eq = DiffEquation(
            function_from_expr(self._p_input.text() or "0"),
            function_from_expr(self._q_input.text() or "0"),
            function_from_expr(self._r_input.text() or "0"),
            function_from_expr(self._f_input.text() or "0"),
        )

        y0 = np.array([
            self._y0_input.value(),
            self._dy0_input.value(),
        ])

        grid = Grid(
            self._a_input.value(),
            self._b_input.value(),
            self._h_input.value(),
        )
        grid_2 = Grid(grid.a, grid.b, grid.h / 2)

        result = method(eq, y0, grid)
        result_2 = method(eq, y0, grid_2)
        actual = np.array([f(x) for x in grid.range])
        abs_error = max_absolute_error(actual, result[1])
        runge_error = runge_romberg_error(result[1], result_2[1], 1)

        self._func_graph.axes.clear()
        self._func_graph.axes.plot(
            grid.range, result[1],
            color="red",
        )
        self._func_graph.axes.plot(
            grid.range, actual,
            color="blue",
        )
        self._func_graph.axes.set_xlim(
            left=grid.a - 0.1,
            right=grid.b + 0.1,
        )
        self._func_graph.axes.set_ylim(
            bottom=min(np.min(result[1]), np.min(actual)) - 0.1,
            top=max(np.max(result[1]), np.max(actual)) + 0.1,
        )
        self._func_graph.axes.grid()
        self._func_graph.axes.set_title("Сравнение функций", fontweight="bold")
        self._func_graph.draw()

        self._error_graph.axes.clear()
        self._error_graph.axes.plot(
            grid.range, runge_error,
            color="orange",
        )
        self._error_graph.axes.set_xlim(
            left=grid.a - 0.1,
            right=grid.b + 0.1,
        )
        self._error_graph.axes.set_ylim(
            top=np.max(runge_error),
            bottom=np.min(runge_error),
        )
        self._error_graph.axes.grid()
        self._error_graph.axes.set_title("Погрешность (метод Рунге-Ромберга)", fontweight="bold")
        self._error_graph.draw()

        self._abs_error_value.setText(f"{abs_error:.5f}")
        


app = QtWidgets.QApplication(sys.argv)
w = Window()
w.resize(980, 420)
w.show()
app.exec_()
