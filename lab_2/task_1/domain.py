from typing import NamedTuple

from common.linalg import max_value
from common.typing import Function


class MethodResult(NamedTuple):
    x: float
    iterations: int


def _derivative(f: Function) -> Function:
    DX = 0.00001
    return lambda x: (f(x + DX) - f(x)) / DX


def _sign(x: float) -> float:
    if x == 0.0:
        return 0.0
    if x < 0.0:
        return -1.0
    return 1.0


def _build_phi(f: Function, a: float, b: float) -> Function:
    df = _derivative(f)
    max_df = max_value(lambda x: abs(df(x)), a, b)
    sign_f = _sign(df(a))
    return lambda x: x - (sign_f / max_df) * f(x)


def iterations_method(f: Function, a: float, b: float, eps: float, iterations: int) -> MethodResult:
    x0 = (a + b) / 2.0
    phi = _build_phi(f, a, b)
    dphi = _derivative(phi)
    q = max_value(lambda x: abs(dphi(x)), a, b)

    last_x = x0
    i = 0

    while i <= iterations:
        x = phi(last_x)
        if abs(x - last_x) <= (1 - q) / q * eps:
            return MethodResult(x, i)
        last_x = x
        i += 1

    return MethodResult(last_x, i)


def newton_method(f: Function, a: float, b: float, eps: float, iterations: int) -> MethodResult:
    x0 = (a + b) / 2.0
    last_x = x0
    df = _derivative(f)
    i = 0

    while i <= iterations:
        x = last_x - f(last_x) / df(last_x)
        if abs(x - last_x) <= eps:
            return MethodResult(x, i)
        last_x = x
        i += 1

    return MethodResult(last_x, i)


if __name__ == "__main__":
    f = lambda x: 2**x + x**2 - 2.0
    a, b = 0.5, 1.0
    eps = 0.0001
    iterations = 100

    print(iterations_method(f, a, b, eps, iterations))
    print(newton_method(f, a, b, eps, iterations))
