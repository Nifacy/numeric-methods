from .task_1 import runge_kutta
from lab_2.task_1.domain import newton_method
import numpy as np
from math import exp
import matplotlib.pyplot as plt


def shooting_method(
    F, cond_1, cond_2, X,
    underlying_method=runge_kutta,
    found_root=newton_method,
):
    def build_condition(nu):
        match cond_1:
            case (0.0, b, c):
                return np.array([[-c/b], [nu]])
            case (a, 0.0, c):
                return np.array([[nu], [-c/a]])
            case (a, b, c):
                return np.array([
                    [- c / b - a / b * nu],
                    [nu],
                ])
    
    def count_difference(y, dy):
        a, b, c = cond_2
        return a * dy + b * y + c

    def g(nu):
        Y_0 = build_condition(nu)
        answer = underlying_method(F, Y_0, X)
        return count_difference(answer[1][-1], answer[2][-1])

    nu = found_root(g, 0.0, 4.0, 0.001, 10).x
    Y_0 = build_condition(nu)
    return underlying_method(F, Y_0, X)


if __name__ == "__main__":
    F = lambda x, Y: np.array([
        [Y[1, 0]],
        [- 4 * x / (2 * x + 1) * Y[1, 0] + 4 / (2 * x + 1) * Y[0, 0]],
    ])
    f = lambda x: x + exp(-2 * x)
    X = np.arange(0.0, 1.01, 0.1)
    result = shooting_method(F, [1.0, 0.0, 1.0], [1.0, 2.0, -3.0], X)
    real = np.array([f(x) for x in X])

    plt.plot(result[0], result[1], color="red")
    plt.plot(X, real, color="blue")
    plt.show()
