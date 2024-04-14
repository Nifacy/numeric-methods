import sys
from dataclasses import dataclass

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
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

from common.plot_widget.controllers import ResizeController
from common.plot_widget.objects import OneArgFunction
from common.plot_widget.objects import Point
from common.plot_widget.widget import PlotWidget
from common.plot_widget.widget import add_grid
from common.typing import Function
from common.utils import function_from_expr
from lab_3.task_1 import domain


class NodeItemWidget(QWidget):
    @dataclass(frozen=True)
    class UpdateEvent:
        x: float
        y: float

    on_update = pyqtSignal(UpdateEvent)

    def __init__(self, f: Function, parent: QWidget | None = None):
        super().__init__(parent)

        self._f = f
        self._argument_label = QLabel()
        self._argument_input = self._get_argument_input_widget()
        self._value_label = QLabel()

        self._layout = QHBoxLayout(self)
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
    def function(self) -> Function:
        return self._f

    @function.setter
    def function(self, value: Function) -> None:
        self._f = value
        self._update()

    @property
    def position(self) -> tuple[float, float]:
        x = self._argument_input.value()
        y = self._f(x)
        return x, y
    
    def set_argument(self, x: float) -> None:
        self._argument_input.setValue(x)

    def _update(self) -> None:
        x, y = self.position
        self._argument_label.setText("X = ")
        self._value_label.setText(f"Y = {y:.3f}")
        self.on_update.emit(self.UpdateEvent(x=x, y=y))


class NodeListWidget(QWidget):
    on_create = pyqtSignal(NodeItemWidget)
    on_remove = pyqtSignal(NodeItemWidget)

    def __init__(self, f: Function, parent: QWidget | None = None):
        super().__init__(parent)
        self._f = f
        self._min_list_length = 0
        self._nodes = []

        self._nodes_layout = QVBoxLayout()

        self._main_layout = QVBoxLayout(self)
        self._main_layout.addLayout(self._nodes_layout)
        self._main_layout.addLayout(self._init_control_layout())

    def add(self, node_item: NodeItemWidget) -> None:
        self._nodes_layout.addWidget(node_item)
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
        self._nodes_layout.removeWidget(item)
        self.on_remove.emit(item)

        return item

    def set_min_length(self, length: int) -> None:
        self._min_list_length = length

        while len(self._nodes) < self._min_list_length:
            self._add_new_item()

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


# TODO: refactor this part
class Task1Window(QWidget):
    DEFAULT_FUNCTION = "sqrt(x)"
    DEFAULT_NODE_COORDINATES = [0.0, 1.7, 3.4, 5.1]
    INTERPLOATION_FACTORIES = {
        "Лагранжа": domain.LagrangeInterpolationPolynomial,
        "Ньютона": domain.NewtonInterpolationPolynomial,
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self._node_points: list[BoundNodePoint] = []
        self._f = function_from_expr(self.DEFAULT_FUNCTION)

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
        self._input_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

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

        for node_coord in self.DEFAULT_NODE_COORDINATES:
            node_item = NodeItemWidget(self._f)
            node_item.set_argument(node_coord)
            self._node_list.add(node_item)

        self._node_list.set_min_length(4)
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
        self._node_points.append(
            BoundNodePoint(
                point=node_point,
                node=node_item,
            )
        )
        self._update_interpolation_function()

    def _update_error_rate(self):
        x = self._accuracy_check_argument_input.value()
        f = self._func_graphic.function
        p = self._p_graphic.function
        error_rate = domain.error_rate(p, f, x)
        self._error_rate_label.setText(f"Погрешность: {error_rate}")

    def _remove_node_point(self, node_item: NodeItemWidget) -> None:
        for index, bound_point in enumerate(self._node_points):
            if bound_point.node == node_item:
                self._node_points.pop(index)
                break

    def _init_plot_widget(self):
        self._plot_widget = PlotWidget(self, 30)
        f = function_from_expr(self.DEFAULT_FUNCTION)
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
            },
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

        # check that points don't have similar x coordinate
        x_coords = set()
        for index, point in enumerate(points):
            if point[0] in x_coords:
                self._node_points[index].node.set_argument(point[0] + 0.01)
                return

            x_coords.add(point[0])

        p = interpolation_factory(points)
        self._p_graphic.function = p

    def _init_accuraccy_check_argument_input(self):
        self._accuracy_check_argument_layout = QHBoxLayout()
        self._accuracy_check_argument_label = QLabel("X* = ")
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
