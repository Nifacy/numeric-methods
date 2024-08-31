from dataclasses import dataclass

import numpy as np

from common.typing import Matrix


@dataclass
class EigenTaskResult:
    iterations: int
    eigen_values: list[float]
    eigen_vectos: list[Matrix]


def find_max_not_diagonal_element(A: Matrix) -> tuple[int, int]:
    n = len(A)
    max_i, max_j = 0, 1

    for i in range(n):
        for j in range(i + 1, n):
            if abs(A[i, j]) > abs(A[max_i, max_j]):
                max_i, max_j = i, j

    return max_i, max_j


def get_rotation_angle(A: Matrix, i: int, j: int) -> float:
    aii, ajj, aij = A[i, i], A[j, j], A[i, j]
    if aii == ajj:
        return np.pi / 4.0
    return 0.5 * np.arctan(2.0 * aij / (aii - ajj))


def get_rotation_matrix(n: int, i: int, j: int, phi: float) -> Matrix:
    U = np.eye(n)
    c, s = np.cos(phi), np.sin(phi)
    U[i, i] = c
    U[j, j] = c
    U[i, j] = -s
    U[j, i] = s
    return U


def get_next_A(A: Matrix, U: Matrix) -> Matrix:
    return U.T @ A @ U


def t(A: Matrix) -> float:
    n = A.shape[0]
    s = sum(A[i, j] ** 2 for i in range(n) for j in range(i + 1, n))
    return np.sqrt(s)


def solve_eigen_task(M: Matrix, eps: float) -> EigenTaskResult:
    A = M
    n = A.shape[0]
    U = np.eye(n)
    iterations = 0

    while t(A) > eps:
        i, j = find_max_not_diagonal_element(A)
        phi = get_rotation_angle(A, i, j)
        u = get_rotation_matrix(n, i, j, phi)
        A = get_next_A(A, u)
        U = U @ u
        iterations += 1

    eigen_vectors = [U[:, i].reshape(n, 1) for i in range(n)]

    return EigenTaskResult(
        iterations=iterations,
        eigen_values=np.diag(A).tolist(),
        eigen_vectos=eigen_vectors,
    )
