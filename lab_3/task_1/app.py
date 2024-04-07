from dataclasses import dataclass
import sys
from math import *
from typing import Callable, Iterable

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
from PyQt5.QtCore import QPointF, pyqtSignal
from sympy import lambdify, symbols, sympify

from common.plot_widget.controllers import ResizeController
from common.plot_widget.objects import OneArgFunction, Point
from common.plot_widget.widget import PlotWidget, add_grid
from lab_3.task_1 import domain

def _expr_to_func(expr: str) -> Callable[[float], float]:
    x = symbols("x")
    func = lambdify([x], sympify(expr), "numpy")
    return func


class NodeItemWidget(QWidget):
    @dataclass(frozen=True)
    class UpdateEvent:
        x: float
        y: float

    on_update = pyqtSignal(UpdateEvent)

    def __init__(self, f: Callable[[float], float], parent: QWidget | None = None):
        super().__init__(parent)
        self._f = f
        self._layout = QHBoxLayout(self)
        self._argument_label = QLabel()
        self._argument_input = self._get_argument_input_widget()
        self._value_label = QLabel()

        self._layout.addWidget(self._argument_label)
        self._layout.addWidget(self._argument_input)
        self._layout.addWidget(self._value_label, 1)

        self._argument_input.valueChanged.connect(self._update)
        self._update()

    @classmethod
    def _get_argument_input_widget(cls) -> QDoubleSpinBox:
        argument_input = QDoubleSpinBox()
        argument_input.setDecimals(3)
        argument_input.setValue(0)
        argument_input.setSingleStep(0.01)
        return argument_input

    def _update(self) -> None:
        x = self._argument_input.value()
        y = self._f(x)

        self._argument_label.setText("X = ")
        self._value_label.setText(f"Y = {y:.3f}")
        self.on_update.emit(self.UpdateEvent(x=x, y=y))


class NodeListWidget(QWidget):
    on_create = pyqtSignal(NodeItemWidget)
    on_remove = pyqtSignal(NodeItemWidget)

    def __init__(self, f: Callable[[float], float], parent: QWidget | None = None):
        super().__init__(parent)
        self._nodes = []
        self._layout = QVBoxLayout(self)

    def add(self, node_item: NodeItemWidget) -> None:
        self._layout.addWidget(node_item)
        self._nodes.append(node_item)
        self.on_create.emit(node_item)
    
    def remove(self, index_or_item: NodeItemWidget | int) -> NodeItemWidget:
        if isinstance(index_or_item, NodeItemWidget):
            item = index_or_item
        else:
            item = self._nodes[index_or_item]
        
        self._nodes.remove(item)
        self._layout.removeWidget(item)
        self.on_remove.emit(item)

        return item

    def __iter__(self) -> Iterable[NodeItemWidget]:
        return iter(self._nodes)
    
    def __len__(self) -> int:
        return len(self._nodes)
    
    def _remove_last_item(self):
        if self._nodes:
            self.remove(-1)
    
    def _add_new_item(self):
        new_node = NodeItemWidget()

    def _init_control_layout(self) -> QHBoxLayout:
        self._add_button = QPushButton("+")
        self._remove_button = QPushButton("-")



class Task1Window(QWidget):
    DEFAULT_FUNCTION = "sqrt(x)"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(self._init_objects())
        self._nodes = []

    def _init_objects(self):
        self._input_layout = QVBoxLayout()
        self._input_layout.addLayout(self._init_function_input())
        
        self._add_node_button = QPushButton("Добавить узел")

        self._node_layout = QHBoxLayout()
        self._node_argument_label = QLabel('X = ')
        self._node_value_label = QLabel('Y = 1.000')

        self._node_argument_input = QDoubleSpinBox()
        self._node_argument_input.setDecimals(3)
        self._node_argument_input.setValue(0)
        self._node_argument_input.setSingleStep(0.01)

        self._node_layout.addWidget(self._node_argument_label)
        self._node_layout.addWidget(self._node_argument_input)
        self._node_layout.addWidget(self._node_value_label, 1)

        self._accuracy_check_argument_layout = QHBoxLayout()
        self._accuracy_check_argument_label = QLabel('X* = ')
        self._accuracy_check_argument_input = QDoubleSpinBox()
        self._accuracy_check_argument_input.setDecimals(3)
        self._accuracy_check_argument_input.setValue(0)
        self._accuracy_check_argument_input.setSingleStep(0.01)
        self._accuracy_check_argument_layout.addWidget(self._accuracy_check_argument_label)
        self._accuracy_check_argument_layout.addWidget(self._accuracy_check_argument_input, 1)

        self._start_button = QPushButton("Start")
        self._spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self._init_plot_widget()
        self._node_1 = NodeItemWidget(_expr_to_func(self.DEFAULT_FUNCTION))
        def foo(event):
            self._point_2.position = (event.x, event.y)
        def bar(event):
            self._point_1.position = (event.x, event.y)
        self._node_1.on_update.connect(foo)
        self._node_2 = NodeItemWidget(_expr_to_func(self.DEFAULT_FUNCTION))
        self._node_2.on_update.connect(bar)
        self._input_layout.addWidget(self._node_1)
        self._input_layout.addWidget(self._node_2)
        self._input_layout.addWidget(self._add_node_button)
        self._input_layout.addLayout(self._accuracy_check_argument_layout)
        self._input_layout.addLayout(self._init_method_input())
        self._input_layout.addSpacerItem(self._spacer)
        self._input_layout.addWidget(self._start_button)


        self._main_layout = QHBoxLayout()
        self._main_layout.addWidget(self._plot_widget, 5)
        self._main_layout.addLayout(self._input_layout, 4)

        return self._main_layout

    def _init_plot_widget(self):
        self._plot_widget = PlotWidget(self, 30)
        f = _expr_to_func(self.DEFAULT_FUNCTION)
        # p = NewtonInterpolationPolynomial([])

        self._func_graphic = OneArgFunction(
            plot_widget=self._plot_widget,
            f=f,
            styles={
                "color": "red",
                "linewidth": 1,
            },
        )

        self._point_1 = Point(
            plot_widget=self._plot_widget,
            pos=(0, 0),
            styles={"color": "green", "linewidth": 2},
        )

        self._point_2 = Point(
            plot_widget=self._plot_widget,
            pos=(0, 0),
            styles={"color": "green", "linewidth": 2},
        )

        # self._p_graphic = OneArgFunction(
        #     plot_widget=self._plot_widget,
        #     f=p,
        #     styles={
        #         "color": "orange",
        #         "linewidth": 1,
        #     }
        # )

        self._resize_controller = ResizeController(self._plot_widget)
        add_grid(self._plot_widget)

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
        self._method_preifx = QLabel("Метод интерполяции: ")
        self._method_combo_box = QComboBox()

        self._method_combo_box.addItems(["Лагранжа", "Ньютона"])

        self._method_layout.addWidget(self._method_preifx)
        self._method_layout.addWidget(self._method_combo_box, 1)

        return self._method_layout


    def _init_error_label(self):
        self._error_label = QLabel("Ошибка: Функция введена неверно")
        self._error_label.setStyleSheet("color: red")
        self._error_label.hide()

        return self._error_label


app = QtWidgets.QApplication(sys.argv)
w = Task1Window()
w.resize(800, 500)
w.show()
app.exec_()
