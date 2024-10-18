import numpy as np
from sympy import lambdify, symbols, sympify

from .typing import Matrix, Vector


def solve_tridiagonal_with_solve(A: Matrix, d: Vector) -> Vector:
    """
    Решение уравнения методом прогонки

    Parameters:
    - A - матрица коэффициентов. Первая строка имеет вид (0, a, b)
      последняя строка - (b, c, 0), остальные - (a, b, c)
    - d - матрица свободных коэффициентов
    """
    
    n = len(d)

    # Инициализация полной матрицы
    full_matrix = np.zeros((n, n))

    # Заполнение главной, верхней и нижней диагоналей
    for i in range(n):
        full_matrix[i, i] = A[i, 1]  # Главная диагональ (b)
        if i > 0:
            full_matrix[i, i - 1] = A[i, 0]  # Нижняя диагональ (a)
        if i < n - 1:
            full_matrix[i, i + 1] = A[i, 2]  # Верхняя диагональ (c)

    # Решаем систему линейных уравнений с полной матрицей
    x = np.linalg.solve(full_matrix, d)

    return x


def function_from_expr(expr: str, s: str):
    """
    Создает функцию на основе выражения

    Parameters:
    - expr - выражение
    - s - набор свободных переменных функции, записанных через пробел
    """
    x = symbols(s)
    func = lambdify(x, sympify(expr), "numpy")
    return func
