import argparse
import pathlib

import numpy as np

from common.utils import function_from_expr

from . import lib


def _calculate_integrals(f, a, b, h):
    X = [i for i in np.arange(a, b + h, h)]
    Y = [f(x) for x in X]

    return {
        "rectangle": lib.rectangle_method(f, X),
        "trapezoid": lib.trapezoid_method(Y, X),
        "simpson": lib.simpson_method(f, X),
    }


def _calculate_runge_rombert_method(result1, result2, h1, h2):
    rrm_values = {}

    for method_name in result1:
        a1, a2 = result1[method_name], result2[method_name]
        rrm_values[method_name] = lib.runge_rombert_method(a1, h1, a2, h2, 4 if method_name == "simpson" else 2)

    return rrm_values


def _dialog_input():
    f = function_from_expr(input("f: "))
    h1 = float(input("h_1: "))
    h2 = float(input("h_2: "))
    a = float(input("a: "))
    b = float(input("b: "))
    return f, h1, h2, a, b


def _read_from_file(path: pathlib.Path):
    with path.open("r", encoding="utf-8") as file:
        f = function_from_expr(file.readline().strip())
        h1, h2 = map(float, file.readline().strip().split())
        a, b = map(float, file.readline().strip().split())
    return f, h1, h2, a, b


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input-file",
        type=pathlib.Path,
        default=None,
    )
    return parser.parse_args()


def main():
    arguments = _parse_args()

    if arguments.input_file is not None:
        f, h1, h2, a, b = _read_from_file(arguments.input_file)
    else:
        f, h1, h2, a, b = _dialog_input()

    res1 = _calculate_integrals(f, a, b, h1)
    res2 = _calculate_integrals(f, a, b, h2)
    rrm_values = _calculate_runge_rombert_method(res1, res2, h1, h2)

    print(f"Численное интегрирование (h = {h1}):")
    print(f'- Метод прямоугольников: {res1["rectangle"]:.5f}')
    print(f'- Метод трапеций: {res1["trapezoid"]:.5f}')
    print(f'- Метод Симпсона: {res1["simpson"]:.5f}')
    print()

    print(f"Численное интегрирование (h = {h2})")
    print(f'- Метод прямоугольников: {res2["rectangle"]:.5f}')
    print(f'- Метод трапеций: {res2["trapezoid"]:.5f}')
    print(f'- Метод Симпсона: {res2["simpson"]:.5f}')
    print()

    print("Метод Рунге-Ромберга-Ричардсона:")
    print("- Метод прямоугольников: {:.5f} (Погрешность: {:.5f})".format(*rrm_values["rectangle"]))
    print("- Метод трапеций: {:.5f} (Погрешность: {:.5f})".format(*rrm_values["trapezoid"]))
    print("- Метод Симпсона: {:.5f} (Погрешность: {:.5f})".format(*rrm_values["simpson"]))
