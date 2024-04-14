import argparse
import pathlib
import sys

import numpy as np

from common.matrix_utils import read_matrix, read_vector
from common.typing import Matrix, Vector


def forward_step(m: Matrix, k: int) -> tuple[int, int, list[float]]:
    n = m.shape[0]

    # find element with maximum square to avoid small dividers
    swap_index = k

    for i in range(k + 1, n):
        a, b = m[i, k], m[swap_index, k]
        if a * a > b * b:
            swap_index = i

    m[[k, swap_index]] = m[[swap_index, k]]

    if m[k, k] == 0.0:
        return k, k, []

    # convert raws below so that the elements are zero
    coef = []

    for i in range(k + 1, n):
        c = m[i, k] / m[k, k]

        for j in range(k, n):
            m[i, j] -= c * m[k, j]

        coef.append(c)

    return k, swap_index, coef


def lu_decompose(a: Matrix) -> tuple[Matrix, Matrix, Matrix]:
    n = a.shape[0]

    p = np.eye(n)
    l = np.eye(n)
    u = a.copy()

    for k in range(n - 1):
        *swap, coef = forward_step(u, k)

        for i in range(len(coef)):
            l[i + k + 1, k] = coef[i]

        p[[swap[0], swap[1]]] = p[[swap[1], swap[0]]]

        for t in range(k):
            l[swap[0], t], l[swap[1], t] = l[swap[1], t], l[swap[0], t]

    return l, u, p


def solve_with_l(l: Matrix, b: Vector) -> Vector:
    n = l.shape[0]
    x = np.zeros_like(b)

    for i in range(n):
        c = b[i]
        for j in range(i):
            c -= x[j] * l[i, j]
        x[i] = c

    return x


def solve_with_u(u: Matrix, b: Vector) -> Vector:
    n = u.shape[0]
    x = np.zeros_like(b)

    for i in range(n - 1, -1, -1):
        c = b[i]
        for j in range(i + 1, n):
            c -= x[j] * u[i, j]
        x[i] = c / u[i, i]

    return x


def solve_system(l: Matrix, u: Matrix, p: Matrix, b: Vector) -> Vector:
    z = solve_with_l(l, np.dot(p, b))
    x = solve_with_u(u, z)
    return x


def count_permutation_determinant(p: Matrix) -> float:
    n = p.shape[0]
    indexes = np.zeros(n, dtype=int)
    d = 1.0

    for i in range(n):
        for j in range(n):
            if p[i, j] == 1.0:
                indexes[i] = j

    for i in range(n):
        k = 0

        for j in range(i, n):
            if indexes[j] == i:
                k = j
                break

        indexes[[i, k]] = indexes[[k, i]]

        if k != i:
            d *= -1.0

    return d


def determinant(l: Matrix, u: Matrix, p: Matrix) -> float:
    d = 1.0
    n = l.shape[0]

    for i in range(n):
        d *= u[i, i]

    return count_permutation_determinant(p) * d


def inverse_matrix(l: Matrix, u: Matrix, p: Matrix) -> Matrix:
    n = l.shape[0]
    xs = []
    b = np.zeros(n)

    for i in range(n):
        b[i] = 1.0
        xs.append(solve_system(l, u, p, b))
        b[i] = 0.0

    return np.array(xs).T


def print_matrix(matrix: Matrix) -> None:
    f = np.vectorize(lambda x: round(x, 5))
    print(f(matrix))


# user interface


def check_determinant(d: float) -> None:
    if d == 0.0:
        raise ValueError("matrix can't be a singular")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-file", type=pathlib.Path, default=None)
    return parser.parse_args()


def _dialog_input():
    n = int(input("Enter number of equations: "))

    print("Enter matrix A:")
    A = read_matrix(n, n, sys.stdin)

    print("Enter vector b:")
    b = read_vector(n, sys.stdin)

    return A, b


def _file_input(path: pathlib.Path):
    with path.open("r", encoding="utf-8") as file:
        n = int(file.readline().strip())
        A = read_matrix(n, n, file)
        b = read_vector(n, file)
        return A, b


def _main():
    args = _parse_args()

    if args.input_file is None:
        A, b = _dialog_input()
    else:
        A, b = _file_input(args.input_file)

    l, u, p = lu_decompose(A)
    d = determinant(l, u, p)
    check_determinant(d)
    x = solve_system(l, u, p, b)
    inversed = inverse_matrix(l, u, p)

    print("LU decompose:")
    print("L:")
    print_matrix(l)
    print("U:")
    print_matrix(u)
    print("Permuation matrix:")
    print_matrix(p)

    print()
    print(f"Solution x: {x}")

    print()
    print(f"Determinant of A: det(A) = {round(d, 5)}")

    print()
    print("Inversed matrix A:")
    print_matrix(inversed)

    print("\n--- CHECKS ---\n")
    print("L * U:")
    print_matrix(np.matmul(l, u))
    print("P * A:")
    print_matrix(np.matmul(p, A))
    print(f"A * x = {np.matmul(A, x.T).T}")
    print("A * (A ^ (-1)):")
    print_matrix(np.matmul(A, inversed))


if __name__ == "__main__":
    try:
        _main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"error: {e}")
        exit(1)
