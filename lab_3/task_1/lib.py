from math import factorial

import numpy as np

from common.linalg import max_value
from common.typing import Function


class LagrangeInterpolationPolynomial:
    def __init__(self, nodes: list[tuple[float, float]]):
        self._x, self._y = zip(*nodes) if nodes else ([], [])

    def l(self, i: int, x: float) -> float:
        value = 1.0
        for j in range(len(self._x)):
            if j == i:
                continue
            value *= (x - self._x[j]) / (self._x[i] - self._x[j])
        return value

    def __call__(self, x: float) -> float:
        value = 0.0
        for i in range(len(self._x)):
            value += self._y[i] * self.l(i, x)
        return value


class NewtonInterpolationPolynomial:
    def __init__(self, nodes: list[tuple[float, float]]):
        x, y = zip(*nodes) if nodes else ([], [])
        self._diffs = self._count_differences(x, y)
        self._x = x

    @staticmethod
    def _count_differences(x: list[float], y: list[float]) -> list[list[float]]:
        n = len(x)
        diffs = [[] for _ in range(n)]

        for i in range(n):
            if i == 0:
                diffs[0] = y
            else:
                for j in range(n - i):
                    diffs[i].append(
                        (diffs[i - 1][j] - diffs[i - 1][j + 1]) / (x[j] - x[j + i])
                    )

        return diffs

    def __call__(self, x: float) -> float:
        value = 0.0

        for i in range(len(self._x)):
            coef = 1.0
            for j in range(i):
                coef *= x - self._x[j]
            coef *= self._diffs[i][0]
            value += coef

        return value


def _omega(xs: list[float]):
    def _function(x: float) -> float:
        value = 1.0
        for element in xs:
            value *= x - element
        return value

    return _function


def _derivative(f: Function):
    dx = 0.0001

    def _df(x: float) -> float:
        return (f(x + dx) - f(x)) / dx

    return _df


def error_rate(p: Function, f: Function, x: float) -> float:
    return abs(p(x) - f(x))
