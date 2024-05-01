import argparse
import pathlib
import sys
from typing import TextIO

import numpy as np

from common.matrix_utils import read_matrix
from common.typing import Matrix, Vector


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


# user interface


def _read_tridiagonal_matrix(n: int, input_stream: TextIO) -> Matrix:
    a = np.zeros((n, 3))

    for i in range(n):
        values = list(map(float, input_stream.readline().split()))

        if i == 0:
            a[i, 1:] = values
        elif i == n - 1:
            a[i, :2] = values
        else:
            a[i, :] = values

    return a


def _read_number_of_equations():
    n = int(input("Enter number of equations:"))
    if n <= 0:
        raise ValueError("number can't be zero o negative")
    return n


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", type=pathlib.Path, default=None)
    return parser.parse_args()


def _dialog_input():
    n = _read_number_of_equations()

    print("Enter tridiagonal matrix's coefficients (matrix A):")
    A = _read_tridiagonal_matrix(n)

    print("Enter free coefficients (vector b):")
    b = read_matrix(1, n, sys.stdin).T

    return A, b


def _file_input(path: pathlib.Path):
    with path.open("r", encoding="utf-8") as file:
        n = int(file.readline().strip())
        A = _read_tridiagonal_matrix(n, file)
        b = read_matrix(1, n, file).T
        return A, b


def _main():
    args = _parse_args()

    if args.input_file is None:
        A, b = _dialog_input()
    else:
        A, b = _file_input(args.input_file)

    print('A:')
    print(A)
    print("b:")
    print(b)

    result = solve_system(A, b)
    print(f"Result: {result}")


if __name__ == "__main__":
    try:
        _main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"error: {e}")
        exit(1)
