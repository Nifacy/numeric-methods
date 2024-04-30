from sympy import lambdify, symbols, sympify
from common.typing import Function


def function_from_expr(expr: str) -> Function:
    x = symbols("x")
    func = lambdify([x], sympify(expr), "numpy")
    return func
