from typing import Any, Callable, Mapping

import matplotlib.pyplot as plt
import numpy as np

from common.typing import Function

from .widget import PlotUpdateEvent, PlotWidget

Styles = Mapping[str, Any]
Coords = tuple[float, float]


class BasePlotObject:
    def __init__(self, plot_widget: PlotWidget, styles: Styles | None = None):
        self._widget = plot_widget
        self.__plot = None
        self._styles = styles

    @property
    def _plot(self):
        return self.__plot

    @_plot.setter
    def _plot(self, value):
        self.__plot = value
        if self._styles is not None:
            plt.setp(self.__plot, **self._styles)
        self._widget.draw()

    @property
    def styles(self) -> dict[str, Any]:
        return self._styles

    @styles.setter
    def styles(self, value: Styles) -> None:
        self._styles = value
        if self._styles is not None:
            plt.setp(self.__plot, **self._styles)
        self._widget.draw()

    def hide(self) -> None:
        if self._plot is not None:
            self._plot.set_visible(False)
            self._widget.draw()

    def show(self) -> None:
        if self._plot is not None:
            self._plot.set_visible(True)
            self._widget.draw()

    def __del__(self):
        if self._plot is not None:
            self._plot.remove()
            self._widget.draw()


class OneArgFunction(BasePlotObject):
    def __init__(
        self,
        plot_widget: PlotWidget,
        f: Function,
        step: float = 4.0,
        styles: Mapping[str, Any] | None = None,
    ):
        super().__init__(plot_widget, styles)
        self._func = f
        self._step = step
        self._xlim = self._widget.axes.get_xlim()
        self._last_scale = self._step / self._widget.scale
        self._bind_to_plot_widget()

    def _on_update(self, event: PlotUpdateEvent) -> None:
        self._last_scale = self._step / event.scale
        self._xlim = (event.xlim.begin, event.xlim.end)
        self._render_graph_dots()

    def _render_graph_dots(self) -> None:
        x = np.arange(*self._xlim, self._last_scale)
        y = np.array([self._func(v) for v in x])
        self._plot.set_xdata(x)
        self._plot.set_ydata(y)

    def _bind_to_plot_widget(self) -> None:
        (self._plot,) = self._widget.axes.plot([], **self._styles)
        self._render_graph_dots()
        self._widget.on_update.connect(self._on_update)

    @property
    def function(self) -> Function:
        return self._func

    @function.setter
    def function(self, value: Function) -> None:
        self._func = value
        self._render_graph_dots()
        self._widget.draw()


class Curve(BasePlotObject):
    def __init__(
        self,
        plot_widget: PlotWidget,
        f: Callable[[float, float], float],
        step: float = 8.0,
        styles: Mapping[str, Any] | None = None,
    ):
        super().__init__(plot_widget, None)
        self._func = np.vectorize(f)
        self._step = step
        self._params = styles
        self._xlim = self._widget.axes.get_xlim()
        self._ylim = self._widget.axes.get_ylim()
        self._last_scale = self._step / self._widget.scale
        self._bind_to_plot_widget()

    def _on_update(self, event: PlotUpdateEvent) -> None:
        self._last_scale = self._step / event.scale
        self._xlim = (event.xlim.begin, event.xlim.end)
        self._ylim = (event.ylim.begin, event.ylim.end)
        self._render_curve()

    def _render_curve(self):
        x = np.arange(*self._xlim, self._last_scale)
        y = np.arange(*self._ylim, self._last_scale)
        X, Y = np.meshgrid(x, y)
        Z = self._func(X, Y)
        if self._plot is not None:
            self._plot.remove()
        self._plot = self._widget.axes.contour(X, Y, Z, levels=[0], **self._params)

    def _bind_to_plot_widget(self) -> None:
        self._render_curve()
        self._widget.on_update.connect(self._on_update)

    @property
    def function(self) -> Callable[[float, float], float]:
        return self._func

    @function.setter
    def function(self, value: Callable[[float, float], float]) -> None:
        self._func = value
        self._render_curve()


class RangeSelection(BasePlotObject):
    def __init__(
        self,
        plot_widget: PlotWidget,
        borders: tuple[float, float],
        styles: Mapping[str, Any] | None = None,
    ):
        super().__init__(plot_widget, styles)
        self._borders = borders
        self._plot = self._widget.axes.axvspan(*borders)

    @property
    def borders(self) -> tuple[float, float]:
        return self._borders

    @borders.setter
    def borders(self, value: tuple[float, float]) -> None:
        self._borders = value
        x1, x2 = self._borders
        xy = np.array([[x1, 0], [x1, 1], [x2, 1], [x2, 0], [x1, 0]])
        self._plot.set_xy(xy)
        self._widget.draw()


class VerticalLine(BasePlotObject):
    def __init__(
        self,
        plot_widget: PlotWidget,
        x: float,
        styles: Mapping[str, Any] | None = None,
    ):
        super().__init__(plot_widget, styles)
        self._plot = self._widget.axes.axvline(x)

    @property
    def position(self) -> float:
        return self._plot.get_xdata()[0]

    @position.setter
    def position(self, value: float) -> None:
        self._plot.set_xdata([value, value])
        self._widget.draw()


class RectArea(BasePlotObject):
    def __init__(
        self,
        plot_widget: PlotWidget,
        s1: Coords,
        s2: Coords,
        styles: Mapping[str, Any] | None = None,
    ):
        super().__init__(plot_widget, styles)
        self._s1 = s1
        self._s2 = s2

        (x1, y1), (x2, y2) = s1, s2
        (self._plot,) = self._widget.axes.fill([x1, x2, x2, x1], [y1, y1, y2, y2])

    @property
    def coords(self) -> tuple[Coords, Coords]:
        return self._s1, self._s2

    @coords.setter
    def coords(self, value: tuple[Coords, Coords]) -> None:
        self._s1, self._s2 = value
        (x1, y1), (x2, y2) = self._s1, self._s2
        self._plot.set_xy([[x1, y1], [x2, y1], [x2, y2], [x1, y2], [x1, y1]])
        self._widget.draw()


class Point(BasePlotObject):
    def __init__(
        self,
        plot_widget: PlotWidget,
        pos: Coords,
        styles: Mapping[str, Any] | None = None,
    ):
        super().__init__(plot_widget, styles)
        (self._plot,) = self._widget.axes.plot([pos[0]], [pos[1]], marker="o", picker=5)

    @property
    def position(self) -> Coords:
        x, y = self._plot.get_xdata(), self._plot.get_ydata()
        return x[0], y[0]

    @position.setter
    def position(self, value: Coords) -> None:
        self._plot.set_xdata([value[0]])
        self._plot.set_ydata([value[1]])
        self._widget.draw()
