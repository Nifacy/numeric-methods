from dataclasses import dataclass
from typing import Optional
from matplotlib.backend_bases import MouseButton, MouseEvent, PickEvent
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import pyqtSignal, QObject

from .objects import BasePlotObject, Point, RangeSelection, RectArea
from .widget import PlotWidget

class ResizeController:
    def __init__(self, plot_widget: PlotWidget):
        self._widget = plot_widget
        self._start_pos: QPointF | None = None
        self._start_center: QPointF | None = None
        self._subscribe_on_events()

    def _on_mouse_press(self, event: MouseEvent) -> None:
        if event.button == MouseButton.RIGHT:
            self._start_pos = QPointF(float(event.x), float(event.y))
            self._start_center = self._widget.center

    def _on_mouse_move(self, event: MouseEvent) -> None:
        if self._start_pos is None:
            return
        pos = QPointF(float(event.x), float(event.y))
        delta = pos - self._start_pos
        self._widget.center = self._start_center - delta

    def _on_mouse_release(self, _: MouseEvent) -> None:
        self._start_pos = None
        self._start_center = None

    def _on_scroll(self, event: MouseEvent) -> None:
        if event.button == "up":
            self._widget.scale = 1.1 * self._widget.scale
        elif event.button == "down":
            self._widget.scale = 0.9 * self._widget.scale

    def _subscribe_on_events(self) -> None:
        self._widget.mpl_connect("button_press_event", self._on_mouse_press)
        self._widget.mpl_connect("motion_notify_event", self._on_mouse_move)
        self._widget.mpl_connect("button_release_event", self._on_mouse_release)
        self._widget.mpl_connect("scroll_event", self._on_scroll)


class RangeSelectionController:
    def __init__(self, plot_widget: PlotWidget, range_obj: RangeSelection):
        self._widget = plot_widget
        self._range_object = range_obj
        self._range = [0.0, 0.0]
        self._pressed = False
        self._subscribe_on_events()

    def _on_mouse_press(self, event: MouseEvent) -> None:
        if event.button == MouseButton.LEFT:
            self._pressed = True
            self._range[0] = event.xdata
            self._range_object.borders = (self._range[0], self._range[0])

    def _on_mouse_move(self, event: MouseEvent) -> None:
        if self._pressed and (event.xdata is not None):
            self._range[1] = event.xdata
            self._range_object.borders = tuple(sorted(self._range))

    def _on_mouse_release(self, _: MouseEvent) -> None:
        self._pressed = False

    def _subscribe_on_events(self) -> None:
        self._widget.mpl_connect("button_press_event", self._on_mouse_press)
        self._widget.mpl_connect("motion_notify_event", self._on_mouse_move)
        self._widget.mpl_connect("button_release_event", self._on_mouse_release)


class RectSelectionController:
    def __init__(self, plot_widget: PlotWidget, rect_area: RectArea):
        self._widget = plot_widget
        self._rect_area = rect_area
        self._s1 = (0.0, 0.0)
        self._s2 = (0.0, 0.0)
        self._pressed = False
        self._subscribe_on_events()

    def _on_mouse_press(self, event: MouseEvent) -> None:
        if event.button == MouseButton.LEFT:
            self._pressed = True
            self._s1 = (event.xdata, event.ydata)
            self._rect_area.coords = (self._s1, self._s1)

    def _on_mouse_move(self, event: MouseEvent) -> None:
        if self._pressed and (event.xdata is not None):
            self._s2 = (event.xdata, event.ydata)
            (x1, x2), (y1, y2) = sorted([self._s1[0], self._s2[0]]), sorted(
                [self._s1[1], self._s2[1]]
            )
            self._rect_area.coords = ((x1, y1), (x2, y2))

    def _on_mouse_release(self, _: MouseEvent) -> None:
        self._pressed = False

    def _subscribe_on_events(self) -> None:
        self._widget.mpl_connect("button_press_event", self._on_mouse_press)
        self._widget.mpl_connect("motion_notify_event", self._on_mouse_move)
        self._widget.mpl_connect("button_release_event", self._on_mouse_release)


class PointDragController(QObject):
    _lock: Optional['PointDragController'] = None
    EPSILON = 5

    @dataclass(frozen=True, slots=True)
    class PositionUpdateEvent:
        x: float
        y: float

    on_update = pyqtSignal(PositionUpdateEvent)

    def __init__(self, plot_widget: PlotWidget, point: Point):
        super().__init__()
        self._widget = plot_widget
        self._point = point
        self._last_position: tuple[float, float] | None = None
        self._subscribe_on_events()

    def _on_pick(self, event: PickEvent) -> None:
        if event.artist != self._point._plot:
            return
        
        if PointDragController._lock is not None:
            return
        
        PointDragController._lock = self
        self._last_position = (event.mouseevent.xdata, event.mouseevent.ydata)

    def _on_motion(self, event: MouseEvent) -> None:
        if PointDragController._lock is not self:
            return

        if event.xdata is None or event.ydata is None:
            return

        cx, cy = self._last_position
        dx, dy = event.xdata - cx, event.ydata - cy
        px, py = self._point.position
        self._point.position = (px + dx, py + dy)
        self._last_position = (event.xdata, event.ydata)
        self.on_update.emit(self.PositionUpdateEvent(*self._point.position))

    def _on_release(self, _: MouseEvent) -> None:
        if PointDragController._lock is self:
            PointDragController._lock = None

    def _subscribe_on_events(self) -> None:
        self._widget.mpl_connect("pick_event", self._on_pick)
        self._widget.mpl_connect("motion_notify_event", self._on_motion)
        self._widget.mpl_connect("button_release_event", self._on_release)
