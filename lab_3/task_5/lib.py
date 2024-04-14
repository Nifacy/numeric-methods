import numpy as np

from common.typing import Function
from common.typing import Vector


def rectangle_method(f: Function, X: Vector) -> float:
    n = len(X)
    h = np.array([X[i] - X[i - 1] for i in range(1, n)])
    value = 0.0

    for i in range(n - 1):
        x = (X[i] + X[i + 1]) * 0.5
        value += h[i] * f(x)

    return value


def trapezoid_method(Y: Vector, X: Vector) -> float:
    n = len(X)
    h = np.array([X[i] - X[i - 1] for i in range(1, n)])
    value = 0.0

    for i in range(n - 1):
        value += (Y[i] + Y[i + 1]) * h[i]

    return value * 0.5


def simpson_method(f: Function, X: Vector) -> float:
    n = len(X)
    h = np.array([X[i] - X[i - 1] for i in range(1, n)])
    value = 0.0
    Y = np.zeros(2 * n - 1)

    for i in range(n):
        Y[2 * i] = f(X[i])
        if i + 1 < n:
            Y[2 * i + 1] = f((X[i] + X[i + 1]) * 0.5)

    for i in range(n - 1):
        value += (Y[2 * i] + 4 * Y[2 * i + 1] + Y[2 * i + 2]) * h[i] * 0.5

    return value / 3.0


def runge_rombert_method(integral_1: float, h1: float, integral_2: float, h2: float, p: int) -> tuple[float, float]:
    return (
        integral_1 + (integral_1 - integral_2) / ((h2 / h1) ** p - 1.0),  # улучшенное значение
        abs((integral_1 - integral_2) / (2**p - 1.0)),  # погрешность измерения
    )
