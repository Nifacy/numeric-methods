import sys
from dataclasses import dataclass

from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtWidgets import QSpacerItem
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget

from common.plot_widget.controllers import PointDragController
from common.plot_widget.controllers import ResizeController
from common.plot_widget.objects import OneArgFunction
from common.plot_widget.objects import Point
from common.plot_widget.widget import PlotWidget
from common.plot_widget.widget import add_grid
from lab_3.task_2 import lib


class PointsTable(QTableWidget):
    HEADER_STYLE = """
        QHeaderView::section { 
            background-color: #d8d8d8;
            font: bold 10pt Arial;
            border: 1px solid #000;
        }
        QTableCornerButton::section {
            border: 1px solid #000;
        }
    """

    CELLS_FONT = QtGui.QFont("Arial", 10)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_table()

    def update(self, points: list[tuple[float, float]]) -> None:
        self.setRowCount(len(points))
        for i, (x, y) in enumerate(points):
            self._add_row(i, x, y)

    def _setup_table(self):
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["X", "Y"])
        self.horizontalHeader().setStyleSheet(self.HEADER_STYLE)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setSectionsClickable(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)

    def _add_row(self, i, x, y):
        self.setVerticalHeaderItem(i, QTableWidgetItem(str(i + 1)))
        self.setItem(i, 0, QTableWidgetItem("{:.5f}".format(x)))
        self.setItem(i, 1, QTableWidgetItem("{:.5f}".format(y)))
        self.item(i, 0).setTextAlignment(Qt.AlignCenter)
        self.item(i, 1).setTextAlignment(Qt.AlignCenter)
        self.item(i, 0).setFont(self.CELLS_FONT)
        self.item(i, 1).setFont(self.CELLS_FONT)


class Window(QWidget):
    DEFAULT_COORDINATES: list[tuple[float, float]] = [(0.0, 0.0), (1.7, 1.3038), (3.4, 1.8439), (5.1, 2.2583), (6.8, 2.6077)]

    @dataclass(frozen=True, slots=True)
    class NodesChanged:
        nodes: tuple[tuple[float, float], ...]

    on_nodes_changed = pyqtSignal(NodesChanged)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._node_points = []
        self._init_ui()
        self._connect_signals()

    def _init_ui(self):
        self._init_layouts()
        self._init_plot_widget()
        self._init_info_layout()
        self._init_value_layout()
        self._create_node_points()
        self._main_layout.addLayout(self._panel)
        self._panel.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def _connect_signals(self):
        self.on_nodes_changed.connect(self._update_graphic)
        self.on_nodes_changed.connect(self._update_points_info)
        self.on_nodes_changed.connect(self._update_value_layout)
        self._argument_input.valueChanged.connect(self._update_value_layout)
        self._push_nodes_changed_event()

    def _init_layouts(self):
        self._main_layout = QHBoxLayout(self)
        self._panel = QVBoxLayout()
        self._panel.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

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
        self._main_layout.addWidget(self._plot_widget, 1)

    def _init_info_layout(self):
        self._points_table = PointsTable(self)
        self._info_layout = QVBoxLayout()
        self._info_layout.setContentsMargins(20, 20, 20, 20)

        self._info_layout.addWidget(self._points_table)
        self._panel.addLayout(self._info_layout)

        self._info_layout.setAlignment(self._points_table, Qt.AlignCenter)

    def _init_value_layout(self):
        self._argument_input_label = QLabel(text="X* = ")
        self._argument_input = QDoubleSpinBox()
        self._argument_input.setDecimals(3)
        self._argument_input.setValue(0.001)
        self._argument_input.setSingleStep(0.001)
        self._value_label = QLabel(text="f(X*) = 0.0")

        self._value_layout = QHBoxLayout()
        self._value_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self._value_layout.addWidget(self._argument_input_label)
        self._value_layout.addWidget(self._argument_input)
        self._value_layout.addWidget(self._value_label)
        self._value_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self._value_layout.setContentsMargins(20, 20, 20, 20)
        self._panel.addLayout(self._value_layout)

    def _create_node_points(self):
        for node_coords in self.DEFAULT_COORDINATES:
            self._create_node_point(node_coords)

    def _create_node_point(self, coords: tuple[float, float]) -> None:
        node_point = Point(
            plot_widget=self._plot_widget,
            pos=coords,
            styles={
                "color": "red",
                "linewidth": 5,
            },
        )
        controller = PointDragController(
            plot_widget=self._plot_widget,
            point=node_point,
        )
        controller.on_update.connect(self._push_nodes_changed_event)
        self._node_points.append((node_point, controller))

    def _push_nodes_changed_event(self) -> None:
        self.on_nodes_changed.emit(
            self.NodesChanged(
                nodes=tuple(point.position for (point, _) in self._node_points),
            ),
        )

    def _update_graphic(self, event: NodesChanged) -> None:
        nodes = sorted(event.nodes, key=lambda p: p[0])
        try:
            p = lib.CubicSplineInterploation(nodes)
            self._func_graphic.function = p
        except:
            pass

    def _update_points_info(self, event: NodesChanged) -> None:
        self._points_table.update(event.nodes)

    def _update_value_layout(self):
        argument = self._argument_input.value()
        f = self._func_graphic.function
        value = f(argument)
        self._value_label.setText(f"f(X*) = {value:.5f}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = Window()
    w.resize(650, 400)
    w.show()
    app.exec_()
