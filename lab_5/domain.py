from typing import Callable
import numpy as np
from dataclasses import dataclass

from common.tools import solve_tridiagonal_with_solve
from common.typing import Function, Matrix


@dataclass
class Grid:
    """
    Описывает параметры сетки
    """

    L: float # правая граница по x
    T: float # правая граница по t
    N: float # количество точек по x
    M: float # количество точек по t


@dataclass
class StartConditions:
    """
    Описывает функции, соответствующие начальным условиям
    """

    psi: Function
    phi_0: Function
    phi_l: Function


StartConditionCoefs = tuple[tuple[float, float], tuple[float, float]]
"""
Коэффициенты в начальных условиях.
Используются в 3-й начально-краевой задаче
"""


@dataclass
class ExprCoefs:
    """
    Компоненты уравнения начально-краевой задачи
    """
    a: float
    b: float
    g: float
    f: Callable[[float, float], float]


def _get_steps(grid: Grid) -> tuple[float, float]:
    """
    Возвращает параметры h, tau на основе
    параметров сетки
    """
    return grid.L / grid.N, grid.T / grid.M


# первая начально-краевая задача

def explicit_finite_difference_1(coefs: ExprCoefs, conditions: StartConditions, grid: Grid) -> Matrix:
    """
    Решение 1-й начально-краевой задачи с использованием
    явной конечно-разностной сетки.
    """

    N, M = grid.N, grid.M
    psi, phi_0, phi_l = conditions.psi, conditions.phi_0, conditions.phi_l
    a, f = coefs.a, coefs.f
    h, tau = _get_steps(grid)

    U = np.zeros((M + 1, N + 1))
    sigma = a**2 * tau / (h**2)

    for i in range(0, M + 1):
        for j in range(0, N + 1):

            # если t = 0 или x = 0 - используем начальные условия
            if i == 0:
                U[0, j] = psi(j * h)
            elif j == 0:
                U[i, 0] = phi_0(i * tau)
            elif j == N:
                U[i, N] = phi_l(i * tau)

            # в противном случае считаем, используя значения
            # с прошлого временного шага, которые мы уже посчитали
            else:
                U[i, j] = (
                    sigma * U[i - 1, j - 1]
                    + (1 - 2 * sigma) * U[i - 1, j]
                    + sigma * U[i - 1, j + 1]
                    + tau * f(j * h, i * tau)
                )

    return U


def implicit_finite_difference_1(coefs: ExprCoefs, conditions: StartConditions, grid: Grid) -> Matrix:
    """
    Решение 1-й начально-краевой задачи с использованием
    неявной конечно-разностной сетки.
    """

    N, M = grid.N, grid.M
    psi, phi_0, phi_l = conditions.psi, conditions.phi_0, conditions.phi_l
    a, f = coefs.a, coefs.f
    h, tau = _get_steps(grid)

    U = np.zeros((M + 1, N + 1))
    sigma = a**2 * tau / (h**2)

    # для значений функции при t = 0 используем начальное условие
    U[0, :] = [psi(j * h) for j in range(N + 1)]

    for k in range(1, M + 1):
        A = np.zeros((N - 1, 3))
        b = np.zeros((N - 1, 1))

        for j in range(1, N):
            f_val = f(j * h, k * tau)
            if j == 1:
                A[j - 1, :] = [0.0, -1.0 - 2.0 * sigma, sigma]
                b[j - 1, 0] = -U[k - 1, 1] - sigma * phi_0(k * tau) - tau * f_val
            elif j == N - 1:
                A[j - 1, :] = [sigma, -1.0 - 2.0 * sigma, 0.0]
                b[j - 1, 0] = -U[k - 1, N - 1] - sigma * phi_l(k * tau) - tau * f_val
            else:
                A[j - 1, :] = [sigma, -1.0 - 2.0 * sigma, sigma]
                b[j - 1, 0] = -U[k - 1, j] - tau * f_val

        U[k, 0] = phi_0(k * tau)
        U[k, N] = phi_l(k * tau)
        U[k, 1:N] = solve_tridiagonal_with_solve(A, b).T[0] # переводим решение из размерности (n - 2 x 1) в (1 x n - 2)

    return U


def crank_nicolson_1(coefs: ExprCoefs, conditions: StartConditions, grid: Grid, thetta=0.5):
    """
    Решение 1-й начально-краевой задачи с использованием
    схемы Кранка-Николсона.
    """

    N, M = grid.N, grid.M
    psi, phi_0, phi_l = conditions.psi, conditions.phi_0, conditions.phi_l
    a, f = coefs.a, coefs.f
    h, tau = _get_steps(grid)

    U = np.zeros((M + 1, N + 1))
    sigma = a**2 * tau / (h**2)

    U[0, :] = [psi(j * h) for j in range(N + 1)]

    for k in range(1, M + 1):
        A = np.zeros((N - 1, 3))
        D = np.zeros((N - 1, 1))

        for j in range(1, N):
            f_val = f(j * h, k * tau)
            a, b, c = thetta * sigma, -1.0 - 2.0 * thetta * sigma, thetta * sigma
            d = (
                (1 - thetta)
                * sigma
                * (U[k - 1, j - 1] - 2.0 * U[k - 1, j] + U[k - 1, j + 1])
            )
            if j == 1:
                A[j - 1, :] = [0.0, b, c]
                D[j - 1, 0] = (
                    -U[k - 1, 1] - thetta * sigma * phi_0(k * tau) - tau * f_val - d
                )
            elif j == N - 1:
                A[j - 1, :] = [a, b, 0.0]
                D[j - 1, 0] = (
                    -U[k - 1, N - 1] - thetta * sigma * phi_l(k * tau) - tau * f_val - d
                )
            else:
                A[j - 1, :] = [a, b, c]
                D[j - 1, 0] = -U[k - 1, j] - tau * f_val - d

        U[k, 0] = phi_0(k * tau)
        U[k, N] = phi_l(k * tau)
        U[k, 1:N] = solve_tridiagonal_with_solve(A, D).T[0]

    return U

# вторая и третья начально-краевые задачи

# двуточечная (1 порядок)

def explicit_finite_difference_2(coefs: ExprCoefs, conditions: StartConditions, T: StartConditionCoefs, grid: Grid) -> Matrix:
    """
    Решение 3-й начально-краевой задачи с использованием:
    - явной конечно-разностной сетки
    - двуточечной аппроксимации первого порядка

    2-ю начально-краевую задачу можно воспринимать как
    частный случай, когда beta = 0, delta = 0.
    """

    N, M = grid.N, grid.M
    psi, phi_0, phi_l = conditions.psi, conditions.phi_0, conditions.phi_l
    a, f = coefs.a, coefs.f
    h, tau = _get_steps(grid)

    (alpha, beta), (gamma, delta) = T

    U = np.zeros((M + 1, N + 1))
    sigma = a**2 * tau / (h**2)

    U[0, :] = [psi(j * h) for j in range(N + 1)]

    for k in range(1, M + 1):
        for j in range(1, N):
            U[k, j] = (
                sigma * U[k - 1, j - 1]
                + (1 - 2 * sigma) * U[k - 1, j]
                + sigma * U[k - 1, j + 1]
                + tau * f(j * h, k * tau)
            )


        # так как мы не можем использовать для u(0, k) и u(n, k) значения
        # с прошлого временного шага, то считаем их отдельно, когда
        # узнаем значения для u(i, k).
        k1 = beta * h - alpha
        k2 = delta * h + gamma

        U[k, 0] = - alpha * U[k, 1] / k1 + phi_0(k * tau) * h / k1
        U[k, N] = gamma * U[k, N - 1] / k2 + phi_l(k * tau) * h / k2

    return U


def implicit_finite_difference_2(coefs: ExprCoefs, conditions: StartConditions, T: StartConditionCoefs, grid: Grid) -> Matrix:
    """
    Решение 3-й начально-краевой задачи с использованием:
    - неявной конечно-разностной сетки
    - двуточечной аппроксимации первого порядка

    2-ю начально-краевую задачу можно воспринимать как
    частный случай, когда beta = 0, delta = 0.
    """

    N, M = grid.N, grid.M
    psi, phi_0, phi_l = conditions.psi, conditions.phi_0, conditions.phi_l
    a, f = coefs.a, coefs.f
    h, tau = _get_steps(grid)

    U = np.zeros((M + 1, N + 1))
    sigma = a**2 * tau / (h**2)

    (alpha, beta), (gamma, delta) = T

    U[0, :] = [psi(j * h) for j in range(N + 1)]

    for k in range(1, M + 1):
        A = np.zeros((N + 1, 3))
        b = np.zeros((N + 1, 1))

        # здесь мы уже считаем через уравнение на с [1; N - 1]
        # а все значения - [0; N]
        for j in range(N + 1):
            f_val = f(j * h, k * tau)
            if j == 0:
                A[j, :] = [0.0, beta - alpha / h, alpha / h]
                b[j, 0] = phi_0(k * tau) / (beta - alpha / h)
            elif j == N:
                A[j, :] = [gamma / h, delta + gamma / h, 0.0]
                b[j, 0] = phi_l(k * tau) / (delta + gamma / h)
            else:
                A[j, :] = [sigma, -1.0 - 2.0 * sigma, sigma]
                b[j, 0] = -U[k - 1, j] - tau * f_val

        U[k, :] = solve_tridiagonal_with_solve(A, b).T[0]

    return U


def crank_nicolson_2(coefs: ExprCoefs, conditions: StartConditions, T: StartConditionCoefs, grid: Grid, thetta=0.5):
    """
    Решение 3-й начально-краевой задачи с использованием:
    - схемы Кранка-Николсона
    - двуточечной аппроксимации первого порядка

    2-ю начально-краевую задачу можно воспринимать как
    частный случай, когда beta = 0, delta = 0.
    """

    N, M = grid.N, grid.M
    psi, phi_0, phi_l = conditions.psi, conditions.phi_0, conditions.phi_l
    a, f = coefs.a, coefs.f
    h, tau = _get_steps(grid)

    U = np.zeros((M + 1, N + 1))
    sigma = a**2 * tau / (h**2)

    (alpha, beta), (gamma, delta) = T

    U[0, :] = [psi(j * h) for j in range(N + 1)]

    for k in range(1, M + 1):
        A = np.zeros((N + 1, 3))
        b = np.zeros((N + 1, 1))

        # здесь мы уже считаем через уравнение на с [1; N - 1]
        # а все значения - [0; N]
        for j in range(N + 1):
            f_val = f(j * h, k * tau)
            if j == 0:
                A[j, :] = [0.0, beta - alpha / h, alpha / h]
                b[j, 0] = phi_0(k * tau) / (beta - alpha / h)
            elif j == N:
                A[j, :] = [gamma / h, delta + gamma / h, 0.0]
                b[j, 0] = phi_l(k * tau) / (delta + gamma / h)
            else:
                d = (
                    (1 - thetta)
                    * sigma
                    * (U[k - 1, j - 1] - 2.0 * U[k - 1, j] + U[k - 1, j + 1])
                )
                A[j, :] = [thetta * sigma, -1.0 - 2.0 * thetta * sigma, thetta * sigma]
                b[j, 0] = -U[k - 1, j] - tau * f_val - d

        U[k, :] = solve_tridiagonal_with_solve(A, b).T[0]

    return U

# трехточечная (2 порядок)

def explicit_finite_difference_3(coefs: ExprCoefs, conditions: StartConditions, T: StartConditionCoefs, grid: Grid):
    """
    Решение 3-й начально-краевой задачи с использованием:
    - явной конечно-разностной сетки
    - трехточечной аппроксимации второго порядка

    2-ю начально-краевую задачу можно воспринимать как
    частный случай, когда beta = 0, delta = 0.
    """

    N, M = grid.N, grid.M
    psi, phi_0, phi_l = conditions.psi, conditions.phi_0, conditions.phi_l
    a, f = coefs.a, coefs.f
    h, tau = _get_steps(grid)
    (alpha, beta), (gamma, delta) = T

    U = np.zeros((M + 1, N + 1))
    sigma = a**2 * tau / (h**2)

    U[0, :] = [psi(j * h) for j in range(N + 1)]

    for k in range(1, M + 1):
        for j in range(1, N):
            U[k, j] = (
                sigma * U[k - 1, j - 1]
                + (1 - 2 * sigma) * U[k - 1, j]
                + sigma * U[k - 1, j + 1]
                + tau * f(j * h, k * tau)
            )

        g1 = -3 * alpha + 2 * beta * h
        g2 = 3 * gamma + 2 * delta * h

        U[k, 0] = (
            2 * h / g1 * phi_0(k * tau)
            - 4 * alpha / g1 * U[k, 1]
            + alpha / g1 * U[k, 2]
        )
        U[k, N] = (
            2 * h / g2 * phi_l(k * tau)
            + 4 * gamma / g2 * U[k, N - 1]
            - gamma / g2 * U[k, N - 2]
        )

    return U


def implicit_finite_difference_3(coefs: ExprCoefs, conditions: StartConditions, T: StartConditionCoefs, grid: Grid):
    """
    Решение 3-й начально-краевой задачи с использованием:
    - неявной конечно-разностной сетки
    - трехточечной аппроксимации второго порядка

    2-ю начально-краевую задачу можно воспринимать как
    частный случай, когда beta = 0, delta = 0.
    """

    N, M = grid.N, grid.M
    psi, phi_0, phi_l = conditions.psi, conditions.phi_0, conditions.phi_l
    a, f = coefs.a, coefs.f
    h, tau = _get_steps(grid)
    (alpha, beta), (gamma, delta) = T

    U = np.zeros((M + 1, N + 1))
    sigma = a**2 * tau / (h**2)

    U[0, :] = [psi(j * h) for j in range(N + 1)]

    for k in range(1, M + 1):
        A = np.zeros((N + 1, N + 1))
        b = np.zeros((N + 1, 1))

        for j in range(N + 1):
            f_val = f(j * h, k * tau)
            if j == 0:
                A[j, 0] = 2 * beta * h - 3 * alpha
                A[j, 1] = 4 * alpha
                A[j, 2] = -alpha
                b[j, 0] = 2 * h * phi_0(k * tau)
            elif j == N:
                A[j, N - 2] = gamma
                A[j, N - 1] = -4 * gamma
                A[j, N] = 3 * gamma + 2 * delta * h
                b[j, 0] = 2 * h * phi_l(k * tau)
            else:
                A[j, j - 1] = sigma
                A[j, j] = -1.0 - 2.0 * sigma
                A[j, j + 1] = sigma
                b[j, 0] = -U[k - 1, j] - tau * f_val

        # так как матрица теперь не трехдиагональная
        # то мы не можем использовать метод прогонки.
        # Используем обычный метод решения уравнений.
        U[k, :] = np.linalg.solve(A, b).T[0]

    return U


def crank_nicolson_3(coefs: ExprCoefs, conditions: StartConditions, T: StartConditionCoefs, grid: Grid, thetta=0.5):
    """
    Решение 3-й начально-краевой задачи с использованием:
    - схемы Кранка-Николсона
    - трехточечной аппроксимации второго порядка

    2-ю начально-краевую задачу можно воспринимать как
    частный случай, когда beta = 0, delta = 0.
    """

    N, M = grid.N, grid.M
    psi, phi_0, phi_l = conditions.psi, conditions.phi_0, conditions.phi_l
    a, f = coefs.a, coefs.f
    h, tau = _get_steps(grid)
    (alpha, beta), (gamma, delta) = T

    U = np.zeros((M + 1, N + 1))
    sigma = a**2 * tau / (h**2)

    U[0, :] = [psi(j * h) for j in range(N + 1)]

    for k in range(1, M + 1):
        A = np.zeros((N + 1, N + 1))
        b = np.zeros((N + 1, 1))

        for j in range(N + 1):
            f_val = f(j * h, k * tau)
            if j == 0:
                A[j, 0] = 2 * beta * h - 3 * alpha
                A[j, 1] = 4 * alpha
                A[j, 2] = -alpha
                b[j, 0] = 2 * h * phi_0(k * tau)
            elif j == N:
                A[j, N - 2] = gamma
                A[j, N - 1] = -4 * gamma
                A[j, N] = 3 * gamma + 2 * delta * h
                b[j, 0] = 2 * h * phi_l(k * tau)
            else:
                d = (
                    (1 - thetta)
                    * sigma
                    * (U[k - 1, j - 1] - 2.0 * U[k - 1, j] + U[k - 1, j + 1])
                )

                A[j, j - 1] = thetta * sigma
                A[j, j] = -1.0 - 2.0 * thetta * sigma
                A[j, j + 1] = thetta * sigma
                b[j, 0] = -U[k - 1, j] - tau * f_val - d

        # так как матрица теперь не трехдиагональная
        # то мы не можем использовать метод прогонки.
        # Используем обычный метод решения уравнений.
        U[k, :] = np.linalg.solve(A, b).T[0]

    return U

# двуточечная (2 порядок)

def explicit_finite_difference_4(coefs: ExprCoefs, conditions: StartConditions, T: StartConditionCoefs, grid: Grid):
    """
    Решение 3-й начально-краевой задачи с использованием:
    - явной конечно-разностной сетки
    - двуточечной аппроксимации второго порядка

    2-ю начально-краевую задачу можно воспринимать как
    частный случай, когда beta = 0, delta = 0.
    """

    N, M = grid.N, grid.M
    psi, phi_0, phi_l = conditions.psi, conditions.phi_0, conditions.phi_l
    a, b, g, f = coefs.a, coefs.b, coefs.g, coefs.f
    h, tau = _get_steps(grid)
    (alpha, beta), (gamma, delta) = T

    U = np.zeros((M + 1, N + 1))

    sigma_1 = a**2 * tau / (h**2)
    sigma_2 = b * tau / (2.0 * h)
    sigma_3 = g * tau

    U[0, :] = [psi(j * h) for j in range(N + 1)]

    for k in range(1, M + 1):
        for j in range(1, N):
            U[k, j] = (sigma_1 - sigma_2) * U[k - 1, j - 1]
            U[k, j] += (1.0 - 2.0 * sigma_1 + sigma_3) * U[k - 1, j]
            U[k, j] += (sigma_1 + sigma_2) * U[k - 1, j + 1]
            U[k, j] += tau * f(j * h, k * tau)

        b0 = (
            alpha * 2.0 * a**2 / h
            + alpha * h / tau
            - alpha * g * h
            - beta * (2.0 * a**2 - b * h)
        )
        c0 = -2.0 * a**2 / h * alpha
        d0 = alpha * h / tau * U[k - 1, 0] - phi_0(k * tau) * (2 * a**2 - b * h)
        U[k, 0] = d0 / b0 - c0 / b0 * U[k, 1]

        an = -2 * a**2 / h * gamma
        bn = (
            gamma * 2 * a**2 / h
            + gamma * h / tau
            - gamma * g * h
            + delta * (2 * a**2 + b * h)
        )
        dn = gamma * h / tau * U[k - 1, N] + phi_l(k * tau) * (2 * a**2 + b * h)
        U[k, N] = dn / bn - an / bn * U[k, N - 1]

    return U


def implicit_finite_difference_4(coefs: ExprCoefs, conditions: StartConditions, T: StartConditionCoefs, grid: Grid):
    """
    Решение 3-й начально-краевой задачи с использованием:
    - неявной конечно-разностной сетки
    - двуточечной аппроксимации второго порядка

    2-ю начально-краевую задачу можно воспринимать как
    частный случай, когда beta = 0, delta = 0.
    """

    N, M = grid.N, grid.M
    psi, phi_0, phi_l = conditions.psi, conditions.phi_0, conditions.phi_l
    a, b, g, f = coefs.a, coefs.b, coefs.g, coefs.f
    h, tau = _get_steps(grid)
    (alpha, beta), (gamma, delta) = T

    U = np.zeros((M + 1, N + 1))
    U[0, :] = [psi(j * h) for j in range(N + 1)]

    for k in range(1, M + 1):
        A = np.zeros((N + 1, 3))
        B = np.zeros((N + 1, 1))

        for j in range(N + 1):
            a_j = -(a**2 / (h**2) - b / (2 * h))
            b_j = 2 * a**2 / (h**2) + 1 / tau - g
            c_j = -(a**2 / h**2 + b / (2 * h))
            d_j = U[k - 1, j] / tau + f(j * h, k * tau)

            A[j, :] = [a_j, b_j, c_j]
            B[j, 0] = d_j

        b0 = (
            alpha * 2.0 * a**2 / h
            + alpha * h / tau
            - alpha * g * h
            - beta * (2.0 * a**2 - b * h)
        )
        c0 = -2.0 * a**2 / h * alpha
        d0 = alpha * h / tau * U[k - 1, 0] - phi_0(k * tau) * (2 * a**2 - b * h)
        A[0, :] = [0.0, b0, c0]
        B[0, 0] = d0

        an = -2 * a**2 / h * gamma
        bn = (
            gamma * 2 * a**2 / h
            + gamma * h / tau
            - gamma * g * h
            + delta * (2 * a**2 + b * h)
        )
        dn = gamma * h / tau * U[k - 1, N] + phi_l(k * tau) * (2 * a**2 + b * h)
        A[N, :] = [an, bn, 0.0]
        B[N, 0] = dn

        U[k, :] = solve_tridiagonal_with_solve(A, B).T[0]

    return U


def crank_nicolson_4(coefs: ExprCoefs, conditions: StartConditions, T: StartConditionCoefs, grid: Grid, thetta=0.5):
    """
    Решение 3-й начально-краевой задачи с использованием:
    - схемы Кранка-Николсона
    - двуточечной аппроксимации второго порядка

    2-ю начально-краевую задачу можно воспринимать как
    частный случай, когда beta = 0, delta = 0.
    """

    N, M = grid.N, grid.M
    psi, phi_0, phi_l = conditions.psi, conditions.phi_0, conditions.phi_l
    a, b, g, f = coefs.a, coefs.b, coefs.g, coefs.f
    h, tau = _get_steps(grid)
    (alpha, beta), (gamma, delta) = T

    U = np.zeros((M + 1, N + 1))
    sigma = a ** 2 * tau / (h ** 2)
    U[0, :] = [psi(j * h) for j in range(N + 1)]

    for k in range(1, M + 1):
        A = np.zeros((N + 1, 3))
        B = np.zeros((N + 1, 1))

        for j in range(1, N):
            d = (
                (1 - thetta)
                * sigma
                * (U[k - 1, j - 1] - 2.0 * U[k - 1, j] + U[k - 1, j + 1])
            )
            a_j = -thetta * (a**2 / (h**2) - b / (2 * h))
            b_j = 2 * thetta * a**2 / (h**2) + 1 / tau - g
            c_j = -thetta * (a**2 / h**2 + b / (2 * h))
            d_j = U[k - 1, j] / tau + f(j * h, k * tau) + d / tau

            A[j, :] = [a_j, b_j, c_j]
            B[j, 0] = d_j

        b0 = (
            alpha * 2.0 * a**2 / h
            + alpha * h / tau
            - alpha * g * h
            - beta * (2.0 * a**2 - b * h)
        )
        c0 = -2.0 * a**2 / h * alpha
        d0 = alpha * h / tau * U[k - 1, 0] - phi_0(k * tau) * (2 * a**2 - b * h)
        A[0, :] = [0.0, b0, c0]
        B[0, 0] = d0

        an = -2 * a**2 / h * gamma
        bn = (
            gamma * 2 * a**2 / h
            + gamma * h / tau
            - gamma * g * h
            + delta * (2 * a**2 + b * h)
        )
        dn = gamma * h / tau * U[k - 1, N] + phi_l(k * tau) * (2 * a**2 + b * h)
        A[N, :] = [an, bn, 0.0]
        B[N, 0] = dn

        U[k, :] = solve_tridiagonal_with_solve(A, B).T[0]

    return U
