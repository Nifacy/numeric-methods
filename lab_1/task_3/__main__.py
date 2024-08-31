import argparse
import enum
import pathlib
import sys
from dataclasses import dataclass

from common.matrix_utils import print_matrix
from common.matrix_utils import read_matrix
from common.typing import Matrix

from . import lib


class _IterationMethod(enum.Enum):
    JAKOBI = 1
    SEIDEL = 2


@dataclass
class _InputData:
    A: Matrix
    b: Matrix
    eps: float
    iteration_method: _IterationMethod


def _read_iteration_method() -> _IterationMethod:
    print("Choose iteration method:")
    print("1. Jakobi method")
    print("2. Seidel method")

    n = int(input("> "))

    if n in _IterationMethod:
        return _IterationMethod(n)
    raise ValueError(f"Unknown method's code {n}")


def _read_number_of_equations():
    n = int(input("Enter number of equations: "))

    if n <= 0:
        raise ValueError("Number can't be zero o negative")
    return n


def _read_accuracy():
    eps = float(input("Enter accuracy: "))

    if eps <= 0:
        raise ValueError("Accuracy can't be zero o negative")
    return eps


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", type=pathlib.Path, default=None)
    return parser.parse_args()


def _dialog_input() -> _InputData:
    n = _read_number_of_equations()

    print("Enter matrix A:")
    A = read_matrix(n, n, sys.stdin)

    print("Enter matrix b:")
    b = read_matrix(n, 1, sys.stdin)

    eps = _read_accuracy()
    iteration_method = _read_iteration_method()

    return _InputData(
        A=A,
        b=b,
        eps=eps,
        iteration_method=iteration_method,
    )


def _file_input(path: pathlib.Path) -> _InputData:
    with path.open("r", encoding="utf-8") as file:
        n = int(file.readline().strip())
        A = read_matrix(n, n, file)
        b = read_matrix(n, 1, file)
        eps = float(file.readline().strip())
        iteration_method = _IterationMethod(int(file.readline().strip()))

        return _InputData(
            A=A,
            b=b,
            eps=eps,
            iteration_method=iteration_method,
        )


def _main():
    args = _parse_args()
    input_data = _dialog_input() if args.input_file is None else _file_input(args.input_file)

    match input_data.iteration_method:
        case _IterationMethod.JAKOBI:
            alpha, beta = lib.jakobi_method(input_data.A, input_data.b)
        case _IterationMethod.SEIDEL:
            alpha, beta = lib.seidel_method(input_data.A, input_data.b)

    result = lib.iterative_method(alpha, beta, input_data.eps)

    print("Result:")
    print_matrix(result.result)
    print(f"Iterations: {result.iterations}")


if __name__ == "__main__":
    try:
        _main()
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        exit(1)
