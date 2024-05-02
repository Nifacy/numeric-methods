from itertools import product
from typing import overload

import numpy as np

from common.typing import Function, MultiArgFunction, Vector


@overload
def max_value(f: Function, a: float, b: float) -> float: ...


@overload
def max_value(f: MultiArgFunction, a: Vector, b: Vector) -> float: ...


def max_value(
    f: Function | MultiArgFunction,
    a: float | Vector,
    b: float | Vector,
) -> float:
    if isinstance(a, float):
        return _max_value_1d(f, a, b)
    return _max_value_2d(f, a, b)


def _max_value_1d(f: Function, a: float, b: float) -> float:
    step = 0.001
    return max((f(x) for x in np.arange(a, b, step)), default=0.0)


def _max_value_2d(f: MultiArgFunction, a: Vector, b: Vector) -> float:
    step = 0.01
    ranges = [np.arange(i, j, step) for i, j in zip(a, b)]
    return max(map(f, product(*ranges)))


def derivative(f: Function, dx: float = 0.0001) -> Function:
    def df(x: float):
        return (f(x + dx) - f(x)) / dx
    return df
