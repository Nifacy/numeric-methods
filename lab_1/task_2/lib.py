import numpy as np

from common.typing import Matrix
from common.typing import Vector


def calculate_run_coefficients(A: Matrix, B: Matrix) -> Matrix:
    n = A.shape[0]
    result = np.zeros((n, 2))

    for i in range(n):
        a, b, c, d = *A[i, :3], B[i, 0]

        if i == 0:
            if d == 0.0:
                raise ValueError("Can't find solution of system")
            result[i, :] = -c / b, d / b

        else:
            p_last, q_last = result[i - 1, :]
            t = b + a * p_last
            if t == 0.0:
                raise ValueError("Can't find solution of system")
            result[i, :] = -c / t, (d - a * q_last) / t

    return result


def solve_using_coefficients(run_coefs: Matrix) -> Vector:
    n = run_coefs.shape[0]
    result = np.zeros(n)

    result[n - 1] = run_coefs[n - 1, 1]
    for i in range(0, n - 1)[::-1]:
        result[i] = run_coefs[i, 0] * result[i + 1] + run_coefs[i, 1]

    return result


def solve_system(A: Matrix, b: Matrix) -> Vector:
    run_coefs = calculate_run_coefficients(A, b)
    return solve_using_coefficients(run_coefs)
