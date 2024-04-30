import numpy as np


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
        Y = answer[1:, i - 1].reshape((-1, 1)) + h / 24 * (
            55 * f[3] - 59 * f[2] + 37 * f[1] - 9 * f[0]
        )
        answer[:, i] = (X[i], *Y.flat)

    return answer


# TODO: fix logic in this function
def runge_romberg_error(y_1, y_2, p):
    return (y_1[::2] - y_2) / (2.0**p - 1.0)


def total_error(real_y, y):
    return np.max(np.abs(real_y - y))
