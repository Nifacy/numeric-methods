from math import exp

import numpy as np

from .task_1 import adams, euler, runge_kutta, runge_romberg_error, total_error


def _format_array(l):
    return f'[{" ".join(f"{x:.5f}" for x in l)}]'


if __name__ == "__main__":
    F = lambda x, Y: np.array(
        [
            [Y[1, 0]],
            [(2 - 4 * x**2) * Y[0, 0] - 4 * x * Y[1, 0]],
        ]
    )
    Y_0 = np.array([[1.0], [1.0]])
    X = np.linspace(0.0, 1.0, 11)

    real_answer = np.array([(1 + x) * exp(x**2) for x in X])

    answer_1 = euler(F, Y_0, X)[1]
    answer_1_2 = euler(F, Y_0, X[::2])[1]
    total_error_1 = total_error(real_answer, answer_1)
    runge_romberg_error_1 = runge_romberg_error(
        answer_1, answer_1_2, 4
    )  # TODO: fix p values

    answer_2 = runge_kutta(F, Y_0, X)[1]
    answer_2_2 = runge_kutta(F, Y_0, X[::2])[1]
    total_error_2 = total_error(real_answer, answer_2)
    runge_romberg_error_2 = runge_romberg_error(answer_2, answer_2_2, 4)

    answer_3 = adams(F, Y_0, X)[1]
    answer_3_2 = runge_kutta(F, Y_0, X[::2])[1]
    total_error_3 = total_error(real_answer, answer_3)
    runge_romberg_error_3 = runge_romberg_error(answer_3, answer_3_2, 4)

    print("Метод Эйлера:")
    print("- Ответ:", _format_array(answer_1))
    print("- Погрешность (сравнение с точным решением):", total_error_1)
    print("- Погрешность (метод Рунге-Ромберга):", _format_array(runge_romberg_error_1))

    print("Метод Рунге-Кутта:")
    print("- Ответ:", _format_array(answer_2))
    print("- Погрешность (сравнение с точным решением):", total_error_2)
    print("- Погрешность (метод Рунге-Ромберга):", _format_array(runge_romberg_error_2))

    print("Метод Адамса:")
    print("- Ответ:", _format_array(answer_3))
    print("- Погрешность (сравнение с точным решением):", total_error_3)
    print("- Погрешность (метод Рунге-Ромберга):", _format_array(runge_romberg_error_3))
