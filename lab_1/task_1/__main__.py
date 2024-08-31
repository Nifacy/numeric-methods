import argparse
import pathlib
import sys

import numpy as np

from common.matrix_utils import read_matrix
from common.matrix_utils import read_vector
from common.typing import Matrix

from . import lib


def _print_matrix(matrix: Matrix) -> None:
    f = np.vectorize(lambda x: round(x, 5))
    print(f(matrix))


def _check_determinant(d: float) -> None:
    if d == 0.0:
        raise ValueError("matrix can't be a singular")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", type=pathlib.Path, default=None)
    return parser.parse_args()


def _dialog_input():
    n = int(input("Enter number of equations: "))

    print("Enter matrix A:")
    A = read_matrix(n, n, sys.stdin)

    print("Enter vector b:")
    b = read_vector(n, sys.stdin)

    return A, b


def _file_input(path: pathlib.Path):
    with path.open("r", encoding="utf-8") as file:
        n = int(file.readline().strip())
        A = read_matrix(n, n, file)
        b = read_vector(n, file)
        return A, b


def _main():
    args = _parse_args()

    if args.input_file is None:
        A, b = _dialog_input()
    else:
        A, b = _file_input(args.input_file)

    l, u, p = lib.lu_decompose(A)
    d = lib.determinant(l, u, p)
    _check_determinant(d)
    x = lib.solve_system(l, u, p, b)
    inversed = lib.inverse_matrix(l, u, p)

    print("LU decompose:")
    print("L:")
    _print_matrix(l)
    print("U:")
    _print_matrix(u)
    print("Permuation matrix:")
    _print_matrix(p)

    print()
    print(f"Solution x: {x}")

    print()
    print(f"Determinant of A: det(A) = {round(d, 5)}")

    print()
    print("Inversed matrix A:")
    _print_matrix(inversed)

    print("\n--- CHECKS ---\n")
    print("L * U:")
    _print_matrix(np.matmul(l, u))
    print("P * A:")
    _print_matrix(np.matmul(p, A))
    print(f"A * x = {np.matmul(A, x.T).T}")
    print("A * (A ^ (-1)):")
    _print_matrix(np.matmul(A, inversed))


if __name__ == "__main__":
    try:
        _main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"error: {e}")
        exit(1)
