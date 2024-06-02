import numpy as np

from common.typing import Matrix
from common.typing import Vector
from lab_1.task_2 import solve_system
# from lab_1.task_1 import lu_decompose
# from lab_1.task_1 import solve_system
from lab_2.task_1.domain import newton_method

from .ode import OdeSolveMethod
from .ode import runge_kutta
from .typing import BoundaryCondition
from .typing import DiffEquation
from .typing import Grid


def shooting_method(
    eq: DiffEquation,
    cond_1: BoundaryCondition,
    cond_2: BoundaryCondition,
    grid: Grid,
    underlying_method: OdeSolveMethod = runge_kutta,
    found_root=newton_method,
) -> Matrix:
    """
    Решение краевой задачи ДУ методом стрельбы.
    Возвращает матрицу `(3, n)`, где `n` - размерность матрицы.
    Матрица имеет вид `(x, y, y')`.

    Поддерживает задание используемого метода решения ОДУ через
    аргумент `underlying_method`.

    Поддерживает задание метода для поиска оптимального значения nu
    через аргумент `found_root`.
    """

    def build_ode_condition(nu: float) -> Vector:
        match cond_1:
            case (0.0, b, c):
                return np.array([-c / b, nu])
            case (a, 0.0, c):
                return np.array([nu, -c / a])
            case (a, b, c):
                return np.array(
                    [
                        -c / b - a / b * nu,
                        nu,
                    ]
                )

    def count_difference(y: float, dy: float):
        a, b, c = cond_2
        return a * dy + b * y + c

    def g(nu: float) -> float:
        Y_0 = build_ode_condition(nu)
        answer = underlying_method(eq, Y_0, grid)
        return count_difference(answer[1][-1], answer[2][-1])

    nu = found_root(g, 0.0, 4.0, 0.001, 10).x
    Y_0 = build_ode_condition(nu)
    return underlying_method(eq, Y_0, grid)


# def _solve(A: Matrix, B: Matrix) -> Matrix:
#     l, u, p = lu_decompose(A)
#     return solve_system(l, u, p, B)


def finite_diff_method(eq: DiffEquation, cond_1: BoundaryCondition, cond_2: BoundaryCondition, grid: Grid) -> Matrix:
    """
    Решение краевой задачи ДУ методом конечных разностей.
    Возвращает матрицу `(2, n)`, где `n` - размерность сетки.
    Матрица имеет форму `(x, y)`
    """

    X = grid.range
    N = len(X)
    answer = np.zeros_like(X)

    p = lambda x: eq.q(x) / eq.p(x)
    q = lambda x: eq.r(x) / eq.p(x)
    f = lambda x: - eq.f(x) / eq.p(x)
    h = grid.h

    g_1 = lambda x: 1 - 0.5 * p(x) * h
    g_2 = lambda x: q(x) * h ** 2 - 2
    g_3 = lambda x: 1 + 0.5 * p(x) * h
    g_4 = lambda x: f(x) * h ** 2
    
    c1, c2, c3 = cond_1
    if c1 == 0.0:
        y_0 = - c3 / c2
        first = [0.0, g_2(X[1]), g_3(X[1])], g_4(X[1]) - g_1(X[1]) * y_0
        i = 2
        answer[0] = y_0

    elif c2 == 0.0:
        first = [0.0, -c1, c1], - c3 * h
        i = 1

    else:
        first = [0.0, -c1, c1 + c2 * h], - c3 * h
        i = 1

    c1, c2, c3 = cond_2
    if c1 == 0.0:
        y_n = - c3 / c2
        last = [g_1(X[-2]), g_2(X[-2]), 0.0], g_4(X[-2]) - g_3(X[-2]) * y_n
        j = N - 2
        answer[N - 1] = y_n

    elif c2 == 0.0:
        last = [-c1, c1, 0.0], - c3 * h
        j = N - 1

    else:
        last = [-c1, c1 + c2 * h, 0.0], - c3 * h
        j = N - 1

    A = np.zeros((j - i + 2, 3)) # матрица коэффициентов (n x 3)
    B = np.zeros((j - i + 2, 1)) # матрица совбодных коэффициентов (n x 1)
    A[0, :], B[0, 0] = first
    A[-1, :], B[-1, 0] = last

    for t in range(i, j):
        t2 = t - i + 1
        x = X[t - 1]
        A[t2, :] = [g_1(x), g_2(x), g_3(x)]
        B[t2, 0] = g_4(x)

    # решаем систему методом прогонки
    answer[i - 1:j + 1] = solve_system(A, B)
    return np.array([X, answer.flat])
