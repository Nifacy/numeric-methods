from itertools import product
from math import exp
from typing import Callable
import numpy as np



class VectorFunction(np.ndarray):
    def __new__(cls, input_array) -> 'VectorFunction':
        obj = np.asarray(input_array).view(cls)
        return obj

    def __call__(self, x: np.ndarray[float]) -> np.ndarray[float]:
        return np.array([func(x) for func in self])


def sign(x: float) -> float:
    if x == 0.0: return 0.0
    if x < 0.0: return -1.0
    return 1.0


def max_value(f: Callable[[np.ndarray[float]], float], a: np.ndarray[float], b: np.ndarray[float]) -> float:
    ranges = [np.arange(i, j, 0.01) for i, j in zip(a, b)]
    return max(map(f, product(*ranges)))


def partial_derivative(f: Callable[[np.ndarray[float]], float], arg_index: int) -> Callable[[np.ndarray[float]], float]:
    dx = 0.0001
    def _df(x):
        n = len(x)
        x2 = x + np.array([dx if i == arg_index else 0.0 for i in range(n)])
        return (f(x2) - f(x)) / dx
    return _df


def derivative(f: Callable[[np.ndarray[float]], float], n: int) -> VectorFunction:
    return VectorFunction([
        partial_derivative(f, i)
        for i in range(n)
    ])


def jakobi_matrix(f: VectorFunction) -> VectorFunction:
    n = len(f)
    return VectorFunction([
        derivative(el, n)
        for el in f
    ])


def norm(matrix):
    return abs(matrix).max()

def build_phi(f, n, index, s1, s2):
    f_el = f[index]
    df = derivative(f_el, n)
    pdf = partial_derivative(f_el, index)
    f_sign = sign(pdf(s1))
    mx = max_value(lambda x: norm(df(x)), s1, s2)
    return lambda x: x[index] - (f_sign / mx) * f_el(x)


def iteration_method(f, s1, s2, eps, iterations):
    n = len(f)
    phi = VectorFunction([build_phi(f, n, i, s1, s2) for i in range(n)])
    last_x = (s1 + s2) / 2.0
    i = 0

    while i <= iterations:
        x = phi(last_x)
        if norm(x - last_x) <= eps:
            return x
        last_x = x
        i += 1

    return last_x


def newton_method(f, s1, s2, eps, iterations):
    J = jakobi_matrix(f)
    last_x = (s1 + s2) / 2.0
    i = 0

    while i <= iterations:
        dx = np.linalg.solve(J(last_x), -f(last_x))
        x = last_x + dx

        if norm(x - last_x) <= eps:
            return x

        last_x = x
        i += 1
    
    return last_x


a = 2.0
f1 = lambda x: x[0] ** 2 + x[1] ** 2 - a ** 2
f2 = lambda x: x[0] - exp(x[1]) + a
f = VectorFunction([f1, f2])

s1, s2 = np.array([1.0, 1.0]), np.array([2.0, 2.0])

eps = 0.0001
iterations = 100

print(iteration_method(f, s1, s2, eps, iterations))
print(newton_method(f, s1, s2, eps, iterations))
