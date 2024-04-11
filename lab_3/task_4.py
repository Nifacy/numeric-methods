import argparse
import pathlib
from typing import Iterator

import numpy as np

Vector = np.ndarray[np.float64]


def find_interval(X: Vector, x: float) -> Iterator[int]:
    """
    Возвращает все индексы i, для которых верно X[i] <= x <= X[i + 1].
    """
    for i in range(len(X) - 1):
        if X[i] <= x <= X[i + 1]:
            yield i


def first_derivative(X: Vector, Y: Vector, i: int, x: float) -> float:
    """
    Производная первого порядка с использованием
    интерполяционного многочлена первой степени
    """
    numerator = Y[i + 1] - Y[i]
    denominator = X[i + 1] - X[i]
    return numerator / denominator


def second_derivative(X: Vector, Y: Vector, i: int, x: float) -> float:
    """
    Производная первого порядка с использованием
    интерполяционного многочлена второй степени
    """
    term1 = (Y[i + 1] - Y[i]) / (X[i + 1] - X[i])
    term2 = (Y[i + 2] - Y[i + 1]) / (X[i + 2] - X[i + 1]) - term1
    term3 = (x - X[i]) * (x - X[i + 1])
    return term1 + term2 / (X[i + 2] - X[i]) * term3


def second_derivative_factor(X: Vector, Y: Vector, i: int, x: float) -> float:
    """
    Производная второго порядка с использованием
    интерполяционного многочлена второй степени
    """
    term1 = (Y[i + 2] - Y[i + 1]) / (X[i + 2] - X[i + 1])
    term2 = (Y[i + 1] - Y[i]) / (X[i + 1] - X[i])
    return 2.0 * (term1 - term2) / (X[i + 2] - X[i])


def read_from_file(filepath: pathlib.Path) -> tuple[Vector, Vector, float]:
    with filepath.open("r", encoding="utf-8") as file:
        X = np.array(list(map(float, file.readline().split())), dtype=np.float64)
        Y = np.array(list(map(float, file.readline().split())), dtype=np.float64)
        x_star = float(file.readline())
    return X, Y, x_star


def dialog_input() -> tuple[Vector, Vector, float]:
    X = np.array(list(map(float, input("X: ").split())), dtype=np.float64)
    Y = np.array(list(map(float, input("Y: ").split())), dtype=np.float64)
    x_star = float(input("X*: "))
    return X, Y, x_star


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input-file",
        type=pathlib.Path,
        default=None,
    )
    return parser.parse_args()


def main():
    arguments = parse_args()

    if arguments.input_file is None:
        X, Y, x_star = dialog_input()
    else:
        X, Y, x_star = read_from_file(arguments.input_file)

    t = list(find_interval(X, x_star))

    print("Производная 1-го порядка (многочлен 1-й степени):", end=" ")
    if len(t) == 2:
        print()
        print("- Левосторонняя:", first_derivative(X, Y, t[0], x_star))
        print("- Правосторонняя:", first_derivative(X, Y, t[1], x_star))

    elif len(t) == 1:
        print(first_derivative(X, Y, t[0], x_star))

    else:
        print("Неизвестно")

    print("Производная 1-го порядка (многочлен 2-й степени):", end=" ")
    if len(t) >= 1 and (t[0] + 2 < len(X)):
        print(second_derivative(X, Y, t[0], x_star))
    else:
        print("Неизвестно")

    print("Производная 2-го порядка (многочлен 2-й степени):", end=" ")
    if len(t) >= 1 and (t[0] + 2 < len(X)):
        print(second_derivative_factor(X, Y, t[0], x_star))
    else:
        print("Неизвестно")


if __name__ == "__main__":
    main()
