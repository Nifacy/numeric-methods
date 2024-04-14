from typing import Iterator

import numpy as np

from common.typing import Vector


def find_interval(X: Vector, x: float) -> Iterator[int]:
    """
    Возвращает все индексы i, для которых верно X[i] <= x <= X[i + 1].
    """
    return [i for i in range(len(X) - 1) if X[i] <= x <= X[i + 1]]


def first_derivative(X: Vector, Y: Vector, x: float) -> float | tuple[float, float]:
    """
    Производная первого порядка с использованием
    интерполяционного многочлена первой степени
    """
    indexes = find_interval(X, x)

    if not indexes:
        return np.nan

    results = []
    for i in indexes:
        numerator = Y[i + 1] - Y[i]
        denominator = X[i + 1] - X[i]
        results.append(numerator / denominator)

    if len(results) == 1:
        return results[0]
    return (results[0], results[1])


def second_derivative(X: Vector, Y: Vector, x: float) -> float:
    """
    Производная первого порядка с использованием
    интерполяционного многочлена второй степени
    """
    indexes = find_interval(X, x)

    if not indexes:
        return np.nan

    i = indexes[0]

    if i + 2 >= len(X):
        return np.nan

    term1 = (Y[i + 1] - Y[i]) / (X[i + 1] - X[i])
    term2 = (Y[i + 2] - Y[i + 1]) / (X[i + 2] - X[i + 1]) - term1
    term3 = 2 * x - X[i] - X[i + 1]

    return term1 + term2 / (X[i + 2] - X[i]) * term3


def second_derivative_factor(X: Vector, Y: Vector, x: float) -> float:
    """
    Производная второго порядка с использованием
    интерполяционного многочлена второй степени
    """
    indexes = find_interval(X, x)

    if not indexes:
        return np.nan

    i = indexes[0]

    if i + 2 >= len(X):
        return np.nan

    term1 = (Y[i + 2] - Y[i + 1]) / (X[i + 2] - X[i + 1])
    term2 = (Y[i + 1] - Y[i]) / (X[i + 1] - X[i])

    return 2.0 * (term1 - term2) / (X[i + 2] - X[i])
