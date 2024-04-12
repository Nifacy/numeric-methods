import argparse
import pathlib

import numpy as np
from sympy import lambdify, symbols, sympify


def rectangle_method(f, X):
    n = len(X)
    h = np.array([X[i] - X[i - 1] for i in range(1, n)])
    value = 0.0

    for i in range(n - 1):
        x = (X[i] + X[i + 1]) * 0.5
        value += h[i] * f(x)

    return value


def trapezoid_method(X, Y):
    n = len(X)
    h = np.array([X[i] - X[i - 1] for i in range(1, n)])
    value = 0.0

    for i in range(n - 1):
        value += (Y[i] + Y[i + 1]) * h[i]

    return value * 0.5


def simpson_method(f, X):
    n = len(X)
    h = np.array([X[i] - X[i - 1] for i in range(1, n)])
    value = 0.0
    Y = np.zeros(2 * n - 1)

    for i in range(n):
        Y[2 * i] = f(X[i])
        if i + 1 < n:
            Y[2 * i + 1] = f((X[i] + X[i + 1]) * 0.5)

    for i in range(n - 1):
        value += (Y[2 * i] + 4 * Y[2 * i + 1] + Y[2 * i + 2]) * h[i] * 0.5

    return value / 3.0


def runge_rombert_method(integral_1, h1, integral_2, h2, p):
    return (
        integral_1 + (integral_1 - integral_2) / ((h2 / h1) ** p - 1.0),
        abs((integral_1 - integral_2) / (2**p - 1.0)),
    )


def _calculate_integrals(f, a, b, h):
    X = [i for i in np.arange(a, b + h, h)]
    Y = [f(x) for x in X]

    return {
        "rectangle": rectangle_method(f, X),
        "trapezoid": trapezoid_method(X, Y),
        "simpson": simpson_method(f, X),
    }


def _expr_to_func(expr: str):
    x = symbols("x")
    func = lambdify([x], sympify(expr), "numpy")
    return func


def _dialog_input():
    f = _expr_to_func(input("f: "))
    h1 = float(input("h_1: "))
    h2 = float(input("h_2: "))
    a = float(input("a: "))
    b = float(input("b: "))
    return f, h1, h2, a, b


def _read_from_file(path: pathlib.Path):
    with path.open("r", encoding="utf-8") as file:
        f = _expr_to_func(file.readline().strip())
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
    rrm_values = {}

    for method_name in res1:
        a1, a2 = res1[method_name], res2[method_name]
        rrm_values[method_name] = runge_rombert_method(
            a1, h1, a2, h2, 4 if method_name == "simpson" else 2
        )

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
    print(
        "- Метод прямоугольников: {:.5f} (Погрешность: {:.5f})".format(
            *rrm_values["rectangle"]
        )
    )
    print(
        "- Метод трапеций: {:.5f} (Погрешность: {:.5f})".format(
            *rrm_values["trapezoid"]
        )
    )
    print(
        "- Метод Симпсона: {:.5f} (Погрешность: {:.5f})".format(*rrm_values["simpson"])
    )


if __name__ == "__main__":
    main()
