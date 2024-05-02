from math import exp

import matplotlib.pyplot as plt
import numpy as np

from common.linalg import derivative

from .lib.errors import max_absolute_error
from .lib.errors import runge_romberg_error
from .lib.ode import adams
from .lib.ode import euler
from .lib.ode import runge_kutta
from .lib.typing import DiffEquation
from .lib.typing import Grid


def _format_array(l):
    return f'[{" ".join(f"{x:.5f}" for x in l)}]'


if __name__ == "__main__":
    f = lambda x: (1 + x) * exp(x**2)
    df = derivative(f)
    eq = DiffEquation(
        lambda x: 1.0,
        lambda x: -4 * x,
        lambda x: 4 * x**2 - 2,
        lambda x: 0.0,
    )

    grid = Grid(0.0, 1.0, 0.1)
    grid_2 = Grid(grid.a, grid.b, grid.h / 2.0)
    y_0 = np.array([1.0, 1.0])

    real_answer = np.array([f(x) for x in grid.range])

    answer_1 = euler(eq, y_0, grid)[1]
    answer_1_2 = euler(eq, y_0, grid_2)[1]
    # answer_1_3 = euler(eq, y_0_2, grid_3)[1]
    total_error_1 = max_absolute_error(real_answer, answer_1)
    runge_romberg_error_1 = runge_romberg_error(answer_1, answer_1_2, 1)  # TODO: fix p values

    answer_2 = runge_kutta(eq, y_0, grid)[1]
    total_error_2 = max_absolute_error(real_answer, answer_2)
    # runge_romberg_error_2 = runge_romberg_error(answer_2, answer_2_2, 4)

    answer_3 = adams(eq, y_0, grid)[1]
    total_error_3 = max_absolute_error(real_answer, answer_3)
    # runge_romberg_error_3 = runge_romberg_error(answer_3, answer_3_2, 4)

    print("Метод Эйлера:")
    print("- Ответ:", _format_array(answer_1))
    print("- Погрешность (сравнение с точным решением):", total_error_1)
    print("- Погрешность (метод Рунге-Ромберга):", _format_array(runge_romberg_error_1))

    print("Метод Рунге-Кутта:")
    print("- Ответ:", _format_array(answer_2))
    print("- Погрешность (сравнение с точным решением):", total_error_2)
    # print("- Погрешность (метод Рунге-Ромберга):", _format_array(runge_romberg_error_2))

    print("Метод Адамса:")
    print("- Ответ:", _format_array(answer_3))
    print("- Погрешность (сравнение с точным решением):", total_error_3)
    # print("- Погрешность (метод Рунге-Ромберга):", _format_array(runge_romberg_error_3))

    plt.plot(grid.range, runge_romberg_error_1)
    plt.show()
