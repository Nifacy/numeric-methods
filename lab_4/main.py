import numpy as np
from math import exp


def euler(F, Y_0, X):
    answer = np.zeros((1 + len(Y_0), len(X)))
    answer[:, 0] = (X[0], *Y_0.flat)
    Y = Y_0

    for i in range(1, len(X)):
        h = X[i] - X[i - 1]
        Y = Y + h * F(X[i - 1], Y)
        answer[:, i] = (X[i], *Y.flat)

    return answer


def runge_kutta(F, Y_0, X):
    Y = Y_0
    answer = np.zeros((1 + len(Y_0), len(X)))
    answer[:, 0] = (X[0], *Y.flat)

    for i in range(1, len(X)):
        h = X[i] - X[i - 1]
        K_1 = h * F(X[i - 1], Y)
        K_2 = h * F(X[i - 1] + h * 0.5, Y + K_1 * 0.5)
        K_3 = h * F(X[i - 1] + h * 0.5, Y + K_2 * 0.5)
        K_4 = h * F(X[i - 1] + h, Y + K_3)
        Y = Y + (K_1 + 2.0 * K_2 + 2.0 * K_3 + K_4) / 6.0
        answer[:, i] = (X[i], *Y.flat)

    return answer


def adams(F, Y_0, X):
    answer = np.zeros((1 + len(Y_0), len(X)))
    answer[:, :4] = runge_kutta(F, Y_0, X[:4])
    
    for i in range(4, len(X)):
        h = X[i] - X[i - 1]
        f = [F(answer[0, j], answer[1:, j].reshape((-1, 1))) for j in range(i - 4, i)]
        Y = answer[1:, i - 1].reshape((-1, 1)) + h / 24 * (55 * f[3] - 59 * f[2] + 37 * f[1] - 9 * f[0])
        answer[:, i] = (X[i], *Y.flat)
    
    return answer


def total_error(real_y, y):
    return np.max(np.abs(real_y - y))


# TODO: fix logic in this function
def runge_romberg_error(y_1, y_2, p):
    return (y_1[::2] - y_2) / (2.0 ** p - 1.0)


def _format_array(l):
    return f'[{" ".join(f"{x:.5f}" for x in l)}]'


if __name__ == "__main__":
    F = lambda x, Y: np.array([
        [Y[1, 0]],
        [(2 - 4 * x ** 2) * Y[0, 0] - 4 * x * Y[1, 0]],
    ])
    Y_0 = np.array([[1.0], [1.0]])
    X = np.linspace(0.0, 1.0, 11)

    real_answer = np.array([(1 + x) * exp(x ** 2) for x in X])

    answer_1 = euler(F, Y_0, X)[1]
    answer_1_2 = euler(F, Y_0, X[::2])[1]
    total_error_1 = total_error(real_answer, answer_1)
    runge_romberg_error_1 = runge_romberg_error(answer_1, answer_1_2, 4) # TODO: fix p values

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
