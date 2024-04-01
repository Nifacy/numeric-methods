from typing import NamedTuple

import matplotlib

matplotlib.use("Qt5Agg")

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5.QtCore import QPointF, pyqtSignal
from PyQt5.QtGui import QResizeEvent


class Range(NamedTuple):
    begin: float
    end: float


class PlotUpdateEvent(NamedTuple):
    xlim: Range
    ylim: Range
    scale: float


class PlotWidget(FigureCanvasQTAgg):
    on_update = pyqtSignal(PlotUpdateEvent)

    def __init__(self, parent=None, scale: float = 10.0):
        self._scale = scale
        self._center = QPointF(0.0, 0.0)

        figure = Figure(figsize=(1, 1), dpi=100)
        self.axes = figure.add_subplot(111)
        self.axes.grid(axis="x", which="major")
        super(PlotWidget, self).__init__(figure)

        self._update_plot_size()

    def _update_plot_size(self):
        w, h = self.width(), self.height()
        cx, cy = self._center.x(), self._center.y()
        self.axes.set_xlim((cx - w / 2.0) / self._scale, (cx + w / 2.0) / self._scale)
        self.axes.set_ylim((cy - h / 2.0) / self._scale, (cy + h / 2.0) / self._scale)
        self._push_update_event()
        self.draw()

    def resizeEvent(self, event: QResizeEvent) -> None:
        self._update_plot_size()
        return super().resizeEvent(event)

    @property
    def scale(self) -> float:
        return self._scale

    @scale.setter
    def scale(self, value: float) -> float:
        if value <= 0.0:
            raise ValueError("Scale cannot be a negative value")
        self._scale = value
        self._update_plot_size()

    @property
    def center(self) -> QPointF:
        return self._center

    @center.setter
    def center(self, value: QPointF) -> None:
        self._center = value
        self._update_plot_size()

    def _push_update_event(self) -> None:
        update_event_context = PlotUpdateEvent(
            xlim=Range(*self.axes.get_xlim()),
            ylim=Range(*self.axes.get_ylim()),
            scale=self.scale,
        )
        self.on_update.emit(update_event_context)


def add_grid(plot_widget: PlotWidget) -> None:
    ax = plot_widget.axes

    # add grid
    ax.grid(True, which="both", color="gray", alpha=0.5)

    # move axes in center
    ax.spines["left"].set_position("zero")
    ax.spines["bottom"].set_position("zero")

    # remove up and right borders
    ax.spines["right"].set_color("none")
    ax.spines["top"].set_color("none")

    # set styles of axes
    ax.spines["left"].set_linewidth(1.5)
    ax.spines["bottom"].set_linewidth(1.5)
    ax.spines["left"].set_color("gray")
    ax.spines["bottom"].set_color("gray")
    ax.tick_params(axis="both", colors="gray", width=1.5)

    # displat coordinates on major axes
    ax.xaxis.set_tick_params(which="both", width=2)
    ax.yaxis.set_tick_params(which="both", width=2)

    # set scale 1:1
    ax.set_aspect("equal", adjustable="box")
