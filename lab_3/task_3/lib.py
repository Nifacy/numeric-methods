from itertools import product
import numpy as np

from common.typing import Function, Matrix, Vector
from lab_1 import task_1


class MinimalSquareInterpolation:
    def __init__(self, n: int, nodes: list[tuple[float, float]]) -> None:
        x, y = map(np.array, zip(*nodes))
        Phi = self._get_phi_matrix(x, n)
        self._weights = self._get_weights(Phi, y)

    @classmethod
    def _get_phi_matrix(cls, x: Vector, n: int) -> Matrix:
        phi = lambda i, x: x ** i
        Phi = np.zeros((len(x), n + 1))

        for i, j in product(range(len(x)), range(n + 1)):
            Phi[i, j] = phi(j, x[i])

        return Phi

    @classmethod
    def _get_weights(self, Phi: Matrix, y: Vector) -> Vector:
        A = np.matmul(Phi.T, Phi)
        b = np.matmul(Phi.T, y.reshape((-1, 1)))
        b = np.array(b.flat)
        l, u, p = task_1.lu_decompose(A)
        return task_1.solve_system(l, u, p, b)

    def __call__(self, x: float) -> float:
        value = 0.0
        for i, w in enumerate(self._weights):
            value += w * (x**i)
        return value

    def __repr__(self) -> str:
        expr = []
        for i, w in enumerate(self._weights):
            if i == 0:
                expr.append(str(w))
            elif i == 1:
                expr.append(f"{w} * x")
            else:
                expr.append(f"{w} * (x ^ {i})")
        return f'{self.__class__.__name__}({" + ".join(expr)})'


def square_error_rate(p: Function, nodes: list[tuple[float, float]]):
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
