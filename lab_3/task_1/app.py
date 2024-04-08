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

    @property
    def function(self) -> Callable[[float], float]:
        return self._f
    
    @function.setter
    def function(self, value: Callable[[float], float]) -> None:
        self._f = value
        self._update()

    @property
    def position(self) -> tuple[float, float]:
        x = self._argument_input.value()
        y = self._f(x)
        return x, y

    def _update(self) -> None:
        x, y = self.position
        self._argument_label.setText("X = ")
        self._value_label.setText(f"Y = {y:.3f}")
        self.on_update.emit(self.UpdateEvent(x=x, y=y))


class NodeListWidget(QWidget):
    on_create = pyqtSignal(NodeItemWidget)
    on_remove = pyqtSignal(NodeItemWidget)

    def __init__(self, f: Callable[[float], float], parent: QWidget | None = None):
        super().__init__(parent)
        self._f = f
        self._min_list_length = 0
        self._nodes = []

        self._main_layout = QVBoxLayout(self)
        self._layout = QVBoxLayout()

        self._main_layout.addLayout(self._layout)
        self._main_layout.addLayout(self._init_control_layout())

    def add(self, node_item: NodeItemWidget) -> None:
        self._layout.addWidget(node_item)
        self._nodes.append(node_item)
        self.on_create.emit(node_item)
    
    def remove(self, index_or_item: NodeItemWidget | int) -> NodeItemWidget:
        if isinstance(index_or_item, NodeItemWidget):
            item = index_or_item
        else:
            item = self._nodes[index_or_item]

        if len(self._nodes) == self._min_list_length:
            raise ValueError("Amount of nodes can't be lower then minimum")

        self._nodes.remove(item)
        self._layout.removeWidget(item)
        self.on_remove.emit(item)

        return item

    def set_min_length(self, length: int) -> None:
        self._min_list_length = length

        while len(self._nodes) < self._min_list_length:
            self._add_new_item()

    def __iter__(self) -> Iterable[NodeItemWidget]:
        return iter(self._nodes)
    
    def __len__(self) -> int:
        return len(self._nodes)
    
    def _remove_last_item(self):
        if self._nodes and len(self._nodes) > self._min_list_length:
            self.remove(-1)

    def _add_new_item(self):
        new_node = NodeItemWidget(self._f)
        self.add(new_node)

    def _init_control_layout(self) -> QHBoxLayout:
        self._control_layout = QHBoxLayout()
        self._add_button = QPushButton("+")
        self._remove_button = QPushButton("-")

        self._control_layout.addWidget(self._remove_button)
        self._control_layout.addWidget(self._add_button)

        self._remove_button.clicked.connect(self._remove_last_item)
        self._add_button.clicked.connect(self._add_new_item)

        return self._control_layout



@dataclass(frozen=True)
class BoundNodePoint:
    point: Point
    node: NodeItemWidget


class Task1Window(QWidget):
    DEFAULT_FUNCTION = "sqrt(x)"
    INTERPLOATION_FACTORIES = {
        "Лагранжа": domain.LagrangeInterpolationPolynomial,
        "Ньютона": domain.NewtonInterpolationPolynomial,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._node_points: list[BoundNodePoint] = []
        self._f = _expr_to_func(self.DEFAULT_FUNCTION)
        self.setLayout(self._init_objects())

    def _init_objects(self):
        self._init_plot_widget()
        method_layout = self._init_method_input()
        self._error_rate_label = QLabel()

        self._input_layout = QVBoxLayout()
        self._input_layout.addLayout(self._init_function_input())
        self._input_layout.addWidget(self._init_nodes_widget())
        self._input_layout.addLayout(method_layout)
        self._input_layout.addLayout(self._init_accuraccy_check_argument_input())
        self._input_layout.addWidget(self._error_rate_label)
        self._input_layout.addSpacerItem(QSpacerItem(
            20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding
        ))

        self._main_layout = QHBoxLayout()
        self._main_layout.addWidget(self._plot_widget, 5)
        self._main_layout.addLayout(self._input_layout, 4)
        self._accuracy_check_argument_input.valueChanged.connect(self._update_error_rate)

        self._update_error_rate()

        return self._main_layout

    def _init_nodes_widget(self):
        self._node_list = NodeListWidget(self._f, self)
        self._node_list.on_create.connect(self._create_new_node_point)
        self._node_list.on_remove.connect(self._remove_node_point)
        self._node_list.set_min_length(1)
        return self._node_list

    def _create_new_node_point(self, node_item: NodeItemWidget) -> None:
        node_point = Point(
            plot_widget=self._plot_widget,
            pos=node_item.position,
            styles={
                "color": "green",
                "linewidth": 2,
            },
        )

        def _update_point(event):
            node_point.position = (event.x, event.y)

        node_item.on_update.connect(_update_point)
        node_item.on_update.connect(self._update_interpolation_function)
        node_item.on_update.connect(self._update_error_rate)
        self._node_points.append(BoundNodePoint(
            point=node_point,
            node=node_item,
        ))
        self._update_interpolation_function()

    def _update_error_rate(self):
        x = self._accuracy_check_argument_input.value()
        points = [bound_point.point.position for bound_point in self._node_points]
        f = self._func_graphic.function
        error_rate = domain.error_rate(points, f, x)
        self._error_rate_label.setText(f"Погрешность: {error_rate}")

    def _remove_node_point(self, node_item: NodeItemWidget) -> None:
        for index, bound_point in enumerate(self._node_points):
            if bound_point.node == node_item:
                self._node_points.pop(index)
                break

    def _init_plot_widget(self):
        self._plot_widget = PlotWidget(self, 30)
        f = _expr_to_func(self.DEFAULT_FUNCTION)
        p = domain.NewtonInterpolationPolynomial([])

        self._func_graphic = OneArgFunction(
            plot_widget=self._plot_widget,
            f=f,
            styles={
                "color": "red",
                "linewidth": 1,
            },
        )

        self._p_graphic = OneArgFunction(
            plot_widget=self._plot_widget,
            f=p,
            styles={
                "color": "orange",
                "linewidth": 1,
            }
        )

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

        self._method_combo_box.currentTextChanged.connect(self._update_interpolation_function)
        self._method_combo_box.currentTextChanged.connect(self._update_error_rate)

        return self._method_layout

    def _update_interpolation_function(self):
        method_name = self._method_combo_box.currentText()
        interpolation_factory = self.INTERPLOATION_FACTORIES[method_name]
        points = [bound_point.point.position for bound_point in self._node_points]
        p = interpolation_factory(points)
        self._p_graphic.function = p

    def _init_accuraccy_check_argument_input(self):
        self._accuracy_check_argument_layout = QHBoxLayout()
        self._accuracy_check_argument_label = QLabel('X* = ')
        self._accuracy_check_argument_input = QDoubleSpinBox()
        self._accuracy_check_argument_input.setDecimals(3)
        self._accuracy_check_argument_input.setValue(0)
        self._accuracy_check_argument_input.setSingleStep(0.01)
        self._accuracy_check_argument_layout.addWidget(self._accuracy_check_argument_label)
        self._accuracy_check_argument_layout.addWidget(self._accuracy_check_argument_input, 1)
        return self._accuracy_check_argument_layout


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
