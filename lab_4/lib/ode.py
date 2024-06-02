from typing import Callable

import numpy as np

from common.typing import Matrix
from common.typing import Vector

from .convert import convert_to_system_function
from .typing import DiffEquation
from .typing import Grid

OdeSolveMethod = Callable[[DiffEquation, Vector, Grid], Matrix]
"""
Общий тип для всех методов решения обыкновенного
дифференциального уравнения
"""


def euler(eq: DiffEquation, y_0: Vector, grid: Grid) -> Matrix:
    """
    Решение обыкновенного дифференциального уравнения
    с помощью метода Эйлера.

    Возвращает матрицу `(3, n)`, где `n` - размер сетки.
    Возвращаемая матрица имеет структуру `(x y y')`
    """

    F = convert_to_system_function(eq)
    X = grid.range
    Y = y_0

    answer = np.zeros((1 + len(y_0), len(X)))
    answer[:, 0] = (X[0], *y_0.flat)

    for i in range(1, len(X)):
        Y = Y + grid.h * F(X[i - 1], Y)
        answer[:, i] = (X[i], *Y.flat)

    return answer


def euler_with_continuations(eq: DiffEquation, y_0: Vector, grid: Grid) -> Matrix:
    """
    Решение обыкновенного дифференциального уравнения
    с помощью метода Эйлера с продолжениями.

    Возвращает матрицу `(3, n)`, где `n` - размер сетки.
    Возвращаемая матрица имеет структуру `(x y y')`
    """

    P = euler(eq, y_0, grid)

    F = convert_to_system_function(eq)
    X = grid.range
    Y = y_0

    answer = np.zeros((1 + len(y_0), len(X)))
    answer[:, 0] = (X[0], *y_0.flat)

    for i in range(1, len(X)):
        Y_P = np.array(list(P[1:, i].flat))
        Y = Y + grid.h * (F(X[i - 1], Y) + F(X[i], Y_P)) * 0.5
        answer[:, i] = (X[i], *Y.flat)

    return answer


def runge_kutta(eq: DiffEquation, y_0: Vector, grid: Grid) -> Matrix:
    """
    Решение обыкновенного дифференциального уравнения
    с помощью метода Рунге-Кутта.

    Возвращает матрицу `(3, n)`, где `n` - размер сетки.
    Возвращаемая матрица имеет структуру `(x y y')`
    """

    h = grid.h
    F = convert_to_system_function(eq)
    X = grid.range
    Y = y_0

    answer = np.zeros((1 + len(y_0), len(X)))
    answer[:, 0] = (X[0], *y_0.flat)

    for i in range(1, len(X)):
        K_1 = h * F(X[i - 1], Y)
        K_2 = h * F(X[i - 1] + h * 0.5, Y + K_1 * 0.5)
        K_3 = h * F(X[i - 1] + h * 0.5, Y + K_2 * 0.5)
        K_4 = h * F(X[i - 1] + h, Y + K_3)
        Y = Y + (K_1 + 2.0 * K_2 + 2.0 * K_3 + K_4) / 6.0
        answer[:, i] = (X[i], *Y.flat)

    return answer


def adams(eq: DiffEquation, y_0: Vector, grid: Grid, underlying_method: OdeSolveMethod = runge_kutta) -> Matrix:
    """
    Решение обыкновенного дифференциального уравнения
    с помощью метода Адамса.

    Поддерживает настройку вспомогательного метода через
    аргумент `underlying_method`
    """

    F = convert_to_system_function(eq)
    X = grid.range
    h = grid.h

    answer = np.zeros((1 + len(y_0), len(X)))
    answer[:, :4] = underlying_method(eq, y_0, Grid(X[0], X[3], h))

    for i in range(4, len(X)):
        f = [F(answer[0, j], answer[1:, j]) for j in range(i - 4, i)]
        Y = answer[1:, i - 1] + h / 24 * (55 * f[3] - 59 * f[2] + 37 * f[1] - 9 * f[0])
        answer[:, i] = (X[i], *Y.flat)

    return answer
