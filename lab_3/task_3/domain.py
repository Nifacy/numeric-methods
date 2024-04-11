from typing import Callable

import numpy as np

from lab_1 import task_1


class MinimalSquareInterpolation:
    def __init__(self, n: int, nodes: list[tuple[float, float]]) -> None:
        A, b = self._get_normal_system_coefs(nodes, n)
        l, u, p = task_1.lu_decompose(A)
        self._coef = task_1.solve_system(l, u, p, b)

    @classmethod
    def _get_normal_system_coefs(cls, nodes, n):
        A = np.zeros((n + 1, n + 1))
        b = np.zeros(n + 1)

        for k in range(n + 1):
            for i in range(n + 1):
                A[k, i] = cls._get_a_coef(nodes, k, i)
            b[k] = cls._get_b_coef(nodes, k)

        return A, b

    @classmethod
    def _get_a_coef(cls, nodes, k, i):
        value = 0.0
        N = len(nodes)
        for j in range(N):
            value += nodes[j][0] ** (k + i)
        return value

    @classmethod
    def _get_b_coef(cls, nodes, k):
        value = 0.0
        N = len(nodes)
        for j in range(N):
            value += nodes[j][1] * nodes[j][0] ** k
        return value

    def __call__(self, x: float) -> float:
        value = 0.0
        for i, coef in enumerate(self._coef):
            value += coef * (x**i)
        return value

    def __repr__(self) -> str:
        expr = []
        for i, coef in enumerate(self._coef):
            if i == 0:
                expr.append(str(coef))
            elif i == 1:
                expr.append(f"{coef} * x")
            else:
                expr.append(f"{coef} * (x ^ {i})")
        return f'{self.__class__.__name__}({" + ".join(expr)})'


def square_error_rate(p: Callable[[float], float], nodes: list[tuple[float, float]]):
    value = 0.0
    for x, y in nodes:
        value += (p(x) - y) ** 2
    return value


if __name__ == "__main__":
    nodes = [
        (0.0, 0.0),
        (1.7, 1.3038),
        (3.4, 1.8439),
        (5.1, 2.2583),
        (6.8, 2.6077),
        (8.5, 2.9155),
    ]

    p = MinimalSquareInterpolation(2, nodes)
    print(p)
    print(p(3.4))
    print(square_error_rate(p, nodes))
