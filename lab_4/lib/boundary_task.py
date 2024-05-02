import numpy as np

from common.typing import Matrix
from common.typing import Vector
from lab_1.task_1 import lu_decompose
from lab_1.task_1 import solve_system
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


def _solve(A: Matrix, B: Matrix) -> Matrix:
    l, u, p = lu_decompose(A)
    return solve_system(l, u, p, B)


def finite_diff_method(eq: DiffEquation, cond_1: BoundaryCondition, cond_2: BoundaryCondition, grid: Grid) -> Matrix:
    """
    Решение краевой задачи ДУ методом конечных разностей.
    Возвращает матрицу `(2, n)`, где `n` - размерность сетки.
    Матрица имеет форму `(x, y)`
    """

    X = grid.range
    N = len(X) - 1
    h = grid.h

    g_1 = lambda x: 1 - 0.5 * (eq.q(x) / eq.p(x)) * h
    g_2 = lambda x: (eq.r(x) / eq.p(x)) * h**2 - 2
    g_3 = lambda x: 1 + 0.5 * (eq.q(x) / eq.p(x)) * h
    g_4 = lambda x: (eq.f(x) / eq.p(x)) * h**2

    A = np.zeros((N + 1, N + 1))
    B = np.zeros((N + 1, 1))

    match cond_1:
        case (0.0, b, c):
            A[0, 0] = 1.0
            B[0, 0] = -c / b

        case (a, 0.0, c):
            A[0, 0:3] = -3 * a, 4 * a, -a
            B[0, 0] = -c * 2 * h

        case (a, b, c):
            A[0, 0:3] = -3 * a + b * 2 * h, 4 * a, -a
            B[0, 0] = -c * 2 * h

    match cond_2:
        case (0.0, b, c):
            A[N, -1] = 1.0
            B[N, 0] = -c / b

        case (a, 0.0, c):
            A[N, N - 2 : N + 1] = a, -4 * a, 3 * a
            B[N, 0] = -c * 2 * h

        case (a, b, c):
            A[N, N - 2 : N + 1] = a, -4 * a, 3 * a + 2 * b * h
            B[N, 0] = -c * 2 * h

    for i in range(1, N):
        A[i, i - 1 : i + 2] = g_1(X[i]), g_2(X[i]), g_3(X[i])
        B[i, 0] = g_4(X[i])

    return np.array([X, _solve(A, B).flat])
