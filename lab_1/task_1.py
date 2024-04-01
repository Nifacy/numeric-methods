import numpy as np


def forward_step(m: np.ndarray[float], k: int) -> tuple[int, int, list[float]]:
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


def lu_decompose(a: np.ndarray[float]) -> tuple[np.ndarray[float], np.ndarray[float], np.ndarray[float]]:
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


def solve_with_l(l: np.ndarray[float], b: np.ndarray[float]) -> np.ndarray[float]:
    n = l.shape[0]
    x = np.zeros_like(b)

    for i in range(n):
        c = b[i]
        for j in range(i):
            c -= x[j] * l[i, j]
        x[i] = c

    return x


def solve_with_u(u: np.ndarray[float], b: np.ndarray[float]) -> np.ndarray[float]:
    n = u.shape[0]
    x = np.zeros_like(b)

    for i in range(n - 1, -1, -1):
        c = b[i]
        for j in range(i + 1, n):
            c -= x[j] * u[i, j]
        x[i] = c / u[i, i]

    return x


def solve_system(
    l: np.ndarray[float],
    u: np.ndarray[float],
    p: np.ndarray[float],
    b: np.ndarray[float],
) -> np.ndarray[float]:
    z = solve_with_l(l, np.dot(p, b))
    x = solve_with_u(u, z)
    return x


def count_permutation_determinant(p: np.ndarray[float]) -> float:
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


def determinant(l: np.ndarray[float], u: np.ndarray[float], p: np.ndarray[float]) -> float:
    d = 1.0
    n = l.shape[0]

    for i in range(n):
        d *= u[i, i]

    return count_permutation_determinant(p) * d


def inverse_matrix(l: np.ndarray[float], u: np.ndarray[float], p: np.ndarray[float]) -> np.ndarray[float]:
    n = l.shape[0]
    xs = []
    b = np.zeros(n)

    for i in range(n):
        b[i] = 1.0
        xs.append(solve_system(l, u, p, b))
        b[i] = 0.0

    return np.array(xs).T


def print_matrix(matrix: np.ndarray[float]) -> None:
    f = np.vectorize(lambda x: round(x, 5))
    print(f(matrix))


# user interface


def read_matrix(m: int, n: int) -> np.ndarray[float]:
    rows = []
    for _ in range(m):
        rows.append(list(map(float, input().split())))
    return np.array(rows)


def read_vector(n: int) -> np.ndarray[float]:
    return np.array(list(map(float, input().split())))


def check_determinant(d: float) -> None:
    if d == 0.0:
        raise ValueError("matrix can't be a singular")


def _main():
    n = int(input("Enter number of equations: "))

    print("Enter matrix A:")
    A = read_matrix(n, n)

    print("Enter vector b:")
    b = read_vector(n)

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
