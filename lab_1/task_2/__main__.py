import argparse
import pathlib
import sys
from typing import TextIO

import numpy as np

from common.matrix_utils import read_matrix
from common.typing import Matrix

from . import lib


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

    print("A:")
    print(A)
    print("b:")
    print(b)

    result = lib.solve_system(A, b)
    print(f"Result: {result}")


if __name__ == "__main__":
    try:
        _main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"error: {e}")
        exit(1)
