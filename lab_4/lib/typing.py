from dataclasses import dataclass

import numpy as np

from common.typing import Function
from common.typing import Vector


@dataclass
class DiffEquation:
    """
    Представляет ДУ вида
    `p(x) * y" + q(x) * y' + r(x) * y + f(x) = 0`
    """

    p: Function
    q: Function
    r: Function
    f: Function


@dataclass
class BoundaryCondition:
    """
    Представляет условие для краевой задачи из ДУ, имеющее вид
    `a * y' + b * y + c = 0`
    """

    a: float
    b: float
    c: float


@dataclass
class Grid:
    """
    Представляет сетку с шагом `h` на отрезке `[a; b]`
    """

    a: float
    b: float
    h: float

    @property
    def range(self) -> Vector:
        return np.arange(self.a, self.b + self.h, self.h)
