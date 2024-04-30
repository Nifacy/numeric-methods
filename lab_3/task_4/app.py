import argparse
import pathlib

import numpy as np

from common.typing import Vector

from . import lib


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

    value = lib.first_derivative(X, Y, x_star)
    print("Производная 1-го порядка (многочлен 1-й степени):", end=" ")
    match value:
        case (v1, v2):
            print()
            print("- Левосторонняя:", v1)
            print("- Правосторонняя:", v2)
        case np.nan:
            print("Неизвестно")
        case v:
            print(v)

    value = lib.second_derivative(X, Y, x_star)
    print("Производная 1-го порядка (многочлен 2-й степени):", end=" ")
    match value:
        case np.nan:
            print("Неизвестно")
        case v:
            print(v)

    value = lib.second_derivative_factor(X, Y, x_star)
    print("Производная 2-го порядка (многочлен 2-й степени):", end=" ")
    match value:
        case np.nan:
            print("Неизвестно")
        case v:
            print(v)
