import numpy as np

from common.typing import Vector


def max_absolute_error(actual: Vector, predicted: Vector) -> float:
    """
    Вычисление ошибки численного метода решения ДУ путем
    нахождения максимальной разности между значениями предсказанной
    и ожидаемой функциями
    """

    return np.max(np.abs(actual - predicted))


def runge_romberg_error(step_1: Vector, step_2: Vector, p: float) -> float:
    """
    Вычисление ошибки численного метода решения ДУ с порядком точности `p`
    методом Рунге-Ромберга.

    `step_1` - решение, полученное численным методом при шаге `h`,
    а `step_2` - решение, полученное при шаге `2 * h`.
    """

    answer = np.zeros_like(step_2)

    for i, (a, b) in enumerate(zip(step_2, step_1[::2])):
        answer[i] = (a - b) / (2.0**p - 1.0)

    return np.max(np.abs(answer))
