from typing import Callable, Mapping, Any
from .plot_widget import PlotWidget, PlotUpdateEvent
import matplotlib.pyplot as plt
import numpy as np


class FunctionVisualizer:
    def __init__(
        self,
        f: Callable[[float], float],
        plot_widget: PlotWidget,
        styles: Mapping[str, Any] | None = None,
    ):
        self._widget = plot_widget
        self._f = f
        self._scale = 4.0
        self._styles = {} if styles is None else dict(styles)
        self._xlim = (0, 0)
        self._last_scale = 1.0
        self._bind_to_plot_widget()

    def _on_update(self, event: PlotUpdateEvent) -> None:
        self._last_scale = self._scale / event.scale
        self._xlim = (event.xlim.begin, event.xlim.end)
        self._render_graph_dots()

    def _render_graph_dots(self):
        x = np.arange(*self._xlim, self._last_scale)
        y = np.array([self._f(v) for v in x])
        self._plot.set_xdata(x)
        self._plot.set_ydata(y)


    def _bind_to_plot_widget(self) -> None:
        self._plot, = self._widget.axes.plot([], **self._styles)
        self._widget.on_update.connect(self._on_update)

    @property
    def styles(self) -> dict[str, Any]:
        return self._styles

    @styles.setter
    def styles(self, value: Mapping[str, Any]) -> None:
        self._styles = dict(value)
        plt.setp(self._plot, **self._styles)

    @property
    def function(self) -> Callable[[float], float]:
        return self._f
    
    @function.setter
    def function(self, value: Callable[[float], float]) -> None:
        self._f = value
        self._render_graph_dots()
        self._widget.draw()

    def __del__(self) -> None:
        self._widget.on_update.disconnect(self._on_update)


class RangeSelectionVisualizer:
    def __init__(self, borders: tuple[float, float], plot_widget: PlotWidget, styles: Mapping[str, Any] | None = None):
        self._widget = plot_widget
        self._borders = borders
        self._styles = dict(styles) if styles is not None else dict()
        self._plot = self._widget.axes.axvspan(borders[0], borders[1], **self._styles)

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

    @property
    def styles(self) -> dict[str, Any]:
        return self._styles

    @styles.setter
    def styles(self, value: Mapping[str, Any]) -> None:
        self._styles = dict(value)
        plt.setp(self._plot, **self._styles)


class VLineVisualizer:
    def __init__(self, plot_widget: PlotWidget, x: float, styles: Mapping[str, Any] | None = None):
        self._widget = plot_widget
        self._plot = self._widget.axes.axvline(x)

        if styles is not None:
            plt.setp(self._plot, **styles)

    @property
    def position(self) -> float:
        return self._plot.get_xdata()[0]
    
    @position.setter
    def position(self, value: float) -> None:
        self._plot.set_xdata([value, value])
        self._widget.draw()

    def hide(self) -> None:
        self._plot.set_visible(False)
        self._widget.draw()

    def show(self) -> None:
        self._plot.set_visible(True)
        self._widget.draw()
