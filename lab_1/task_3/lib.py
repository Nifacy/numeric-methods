from dataclasses import dataclass

import numpy as np

from common.typing import Matrix
from lab_1.task_1 import lib


@dataclass
class IterativeMethodResult:
    result: Matrix
    iterations: int


def norm(m: Matrix) -> float:
    return np.sum(m**2)


def jakobi_method(A: Matrix, b: Matrix) -> tuple[Matrix, Matrix]:
    n = len(A)
    alpha, beta = np.zeros((n, n)), np.zeros((n, 1))

    for i in range(n):
        diag_alpha = A[i, i]
        beta[i, 0] = b[i, 0] / diag_alpha

        for j in range(n):
            alpha[i, j] = 0.0 if i == j else -A[i, j] / diag_alpha

    return alpha, beta


def inverse_matrix(m: Matrix):
    return lib.inverse_matrix(*lib.lu_decompose(m))


def seidel_method(A: Matrix, b: Matrix) -> tuple[Matrix, Matrix]:
    n = A.shape[0]
    B, C = np.zeros((n, n)), np.zeros((n, n))
    alpha, beta = jakobi_method(A, b)

    for i in range(n):
        for j in range(n):
            if j >= i:
                C[i, j] = alpha[i, j]
            else:
                B[i, j] = alpha[i, j]

    T = inverse_matrix(np.eye(n, n) - B)
    return T @ C, T @ beta


def epsilon(alpha_norm: float, x1: Matrix, x2: Matrix) -> float:
    coef = alpha_norm / (1 - alpha_norm)
    diff = x1 - x2
    return coef * norm(diff)


def iterative_method(alpha: Matrix, beta: Matrix, eps: float) -> IterativeMethodResult:
    alpha_norm = norm(alpha)
    iterations = 0
    x, x2 = beta, beta

    while True:
        iterations += 1
        x2 = alpha @ x + beta

        if epsilon(alpha_norm, x, x2) <= eps:
            break

        x = x2

    return IterativeMethodResult(
        result=x2,
        iterations=iterations,
    )
