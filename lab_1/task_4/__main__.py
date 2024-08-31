import argparse
import pathlib
import sys

import numpy as np

from common.matrix_utils import read_matrix
from common.typing import Matrix

from . import lib


def _read_matrix_size() -> int:
    n = int(input("Enter matrix size: "))

    if n <= 0:
        raise ValueError("Matrix size can't be negative or zero")
    return n


def _read_epsilon() -> float:
    eps = float(input("Enter precision: "))

    if eps < 0.0:
        raise ValueError("Precision can't be a negativ value")
    return eps


def _read_epsilon_range() -> tuple[float, float, float]:
    a, b, s = map(float, input("Enter epsilon range: ").split())

    if a < 0.0:
        raise ValueError("Range start value can't be negative")
    if b < 0.0:
        raise ValueError("Range end value can't be negative")
    if s < 0.0:
        raise ValueError("Range step value can't be negative")

    return a, b, s


def _print_result(result: lib.EigenTaskResult) -> None:
    print(f"Iterations: {result.iterations}")

    print("Eigen values:")
    print(" ".join(map("{:.3f}".format, result.eigen_values)))

    print("Eigen vectors:")
    for index, eigen_vector in enumerate(result.eigen_vectos):
        print(f"x{index}: {eigen_vector.T}")


def _print_stats_table_head() -> None:
    print(
        "{} | {}".format(
            "precision".ljust(15),
            "iterations".ljust(15),
        )
    )


def _print_stats_entry(eps: float, iterations: int) -> None:
    print("{} | {}".format(str(eps).ljust(15), str(iterations).ljust(15)))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", type=pathlib.Path, default=None)
    parser.add_argument("-s", "--stats-mode", action="store_true")
    return parser.parse_args()


def _dialog_input_standart_mode() -> tuple[Matrix, float]:
    eps = _read_epsilon()
    n = _read_matrix_size()

    print("Enter matrix A:")
    A = read_matrix(n, n, sys.stdin)

    return A, eps


def _file_input_standart_mode(path: pathlib.Path) -> tuple[Matrix, float]:
    with path.open("r", encoding="utf-8") as file:
        eps = float(file.readline().strip())
        n = int(file.readline().strip())
        A = read_matrix(n, n, file)

    return A, eps


def _dialog_input_stats_mode() -> tuple[Matrix, tuple[float, float, float]]:
    rng = _read_epsilon_range()
    n = _read_matrix_size()

    print("Enter matrix A:")
    A = read_matrix(n, n, sys.stdin)

    return A, rng


def _file_input_stats_mode(path: pathlib.Path) -> tuple[Matrix, tuple[float, float, float]]:
    with path.open("r", encoding="utf-8") as file:
        rng = float(file.readline().strip())
        n = int(file.readline().strip())
        A = read_matrix(n, n, file)

    return A, rng


def _main():
    args = _parse_args()

    if args.stats_mode:
        if args.input_file is None:
            A, (a, b, s) = _dialog_input_stats_mode()
        else:
            A, (a, b, s) = _file_input_stats_mode(args.input_file)

        _print_stats_table_head()
        for eps in np.arange(a, b, s):
            result = lib.solve_eigen_task(A, eps)
            _print_stats_entry(eps, result.iterations)

    else:
        if args.input_file is None:
            A, eps = _dialog_input_standart_mode()
        else:
            A, eps = _file_input_standart_mode(args.input_file)

        result = lib.solve_eigen_task(A, eps)
        _print_result(result)


if __name__ == "__main__":
    try:
        _main()
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
