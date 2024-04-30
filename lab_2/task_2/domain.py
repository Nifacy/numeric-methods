from math import exp
from typing import NamedTuple

import numpy as np
from common.linalg import max_value
from common.typing import Matrix
from common.typing import MultiArgFunction
from common.typing import Vector
from lab_1 import task_1


class MethodResult(NamedTuple):
    x: np.ndarray[float]
    iterations: int


class VectorFunction(np.ndarray):
    def __new__(cls, input_array) -> "VectorFunction":
        obj = np.asarray(input_array).view(cls)
        return obj

    def __call__(self, x: Vector) -> Vector:
        return np.array([func(x) for func in self])


def _sign(x: float) -> float:
    if x == 0.0:
        return 0.0
    if x < 0.0:
        return -1.0
    return 1.0


def _partial_derivative(f: MultiArgFunction, arg_index: int) -> MultiArgFunction:
    dx = 0.0001

    def _df(x):
        n = len(x)
        x2 = x + np.array([dx if i == arg_index else 0.0 for i in range(n)])
        return (f(x2) - f(x)) / dx

    return _df


def _derivative(f: MultiArgFunction, n: int) -> VectorFunction:
    return VectorFunction([_partial_derivative(f, i) for i in range(n)])


def _jakobi_matrix(f: VectorFunction) -> VectorFunction:
    n = len(f)
    return VectorFunction([_derivative(el, n) for el in f])


def _norm(matrix: Vector) -> float:
    return abs(matrix).max()


def _build_phi(f: VectorFunction, n: int, index: int, s1: Vector, s2: Vector) -> MultiArgFunction:
    f_el = f[index]
    df = _derivative(f_el, n)
    pdf = _partial_derivative(f_el, index)
    f_sign = _sign(pdf(s1))
    mx = max_value(lambda x: _norm(df(x)), s1, s2)
    return lambda x: x[index] - (f_sign / mx) * f_el(x)


def _solve_system(A: Matrix, b: Vector) -> Vector:
    l, u, p = task_1.lu_decompose(A)
    return task_1.solve_system(l, u, p, b)


def iteration_method(f: MultiArgFunction, s1: Vector, s2: Vector, eps: float, iterations: int) -> MethodResult:
    n = len(f)
    phi = VectorFunction([_build_phi(f, n, i, s1, s2) for i in range(n)])
    last_x = (s1 + s2) / 2.0
    i = 0

    while i <= iterations:
        x = phi(last_x)
        if _norm(x - last_x) <= eps:
            return MethodResult(x, i)
        last_x = x
        i += 1

    return MethodResult(last_x, i)


def newton_method(f: MultiArgFunction, s1: Vector, s2: Vector, eps: float, iterations: int) -> MethodResult:
    J = _jakobi_matrix(f)
    last_x = (s1 + s2) / 2.0
    i = 0

    while i <= iterations:
        dx = _solve_system(J(last_x), -f(last_x))
        x = last_x + dx

        if _norm(x - last_x) <= eps:
            return MethodResult(x, i)

        last_x = x
        i += 1

    return MethodResult(last_x, i)


if __name__ == "__main__":
    a = 2.0
    f1 = lambda x: x[0] ** 2 + x[1] ** 2 - a**2
    f2 = lambda x: x[0] - exp(x[1]) + a
    f = VectorFunction([f1, f2])

    s1, s2 = np.array([1.0, 1.0]), np.array([2.0, 2.0])

    eps = 0.0001
    iterations = 100

    print(iteration_method(f, s1, s2, eps, iterations))
    print(newton_method(f, s1, s2, eps, iterations))
