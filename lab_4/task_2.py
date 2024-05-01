from .task_1 import runge_kutta
from lab_2.task_1.domain import newton_method
from lab_1.task_2 import solve_system
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



def method_2(p, q, f, cond_1, cond_2, a, b, h):
    X = np.arange(a, b + h, h)
    N = len(X)
    answer = np.zeros_like(X)

    g_1 = lambda x: 1 - 0.5 * p(x) * h
    g_2 = lambda x: q(x) * h ** 2 - 2
    g_3 = lambda x: 1 + 0.5 * p(x) * h
    g_4 = lambda x: f(x) * h ** 2

    c1, c2, c3 = cond_1
    if c1 == 0.0:
        y_0 = - c3 / c2
        first = [g_2(X[1]), g_3(X[1]), 0.0], g_4(X[1]) - g_1(X[1]) * y_0
        i = 2
        answer[0] = y_0

    elif c2 == 0.0:
        first = [-1.0, 1.0, 0.0], - c3 / c1 * h
        i = 1

    else:
        first = [c2 * h - c1, c1, 0.0], - c3 * h
        i = 1
    

    c1, c2, c3 = cond_2
    if c1 == 0.0:
        y_n = - c3 / c2
        last = [g_1(X[-1]), g_2(X[-1]), 0.0], g_4(X[-1]) - g_3(X[-1]) * y_n
        j = N - 2
        answer[N - 1] = y_n

    elif c2 == 0.0:
        last = [0.0, -1.0, 1.0], - c3 / c1 * h
        j = N - 1

    else:
        last = [0.0, c2 * h - c1, c1], - c3 * h
        j = N - 1

    A = np.zeros((j - i + 2, 3))
    B = np.zeros((j - i + 2, 1))

    A[0, :], B[0, 0] = first
    A[-1, :], B[-1, 0] = last

    for t in range(i, j):
        t2 = t - i + 1
        x = X[t]
        A[t2, :] = [g_1(x), g_2(x), g_3(x)]
        B[t2, 0] = g_4(x)

    print(A)

    answer[i - 1:j + 1] = solve_system(A, B)
    return answer


if __name__ == "__main__":
    p = lambda x: 4 * x / (2 * x + 1)
    q = lambda x: -4 / (2 * x + 1)
    f = lambda x: 0.0

    cond_1 = (1.0, 0.0, 1.0)
    cond_2 = (1.0, 2.0, -3.0)

    print(method_2(p, q, f, cond_1, cond_2, 0.0, 1.0, 0.1))

    F = lambda x, Y: np.array([
        [Y[1, 0]],
        [- 4 * x / (2 * x + 1) * Y[1, 0] + 4 / (2 * x + 1) * Y[0, 0]],
    ])
    f = lambda x: x + exp(-2 * x)
    X = np.arange(0.0, 1.01, 0.1)
    result = shooting_method(F, [1.0, 0.0, 1.0], [1.0, 2.0, -3.0], X)
    real = np.array([f(x) for x in X])

    print(result[1])

    # plt.plot(result[0], result[1], color="red")
    # plt.plot(X, real, color="blue")
    # plt.show()
