from typing import TextIO

import numpy as np

from .typing import Matrix
from .typing import Vector


def read_matrix(m: int, n: int, input_stream: TextIO) -> Matrix:
    rows = []
    for _ in range(m):
        rows.append(list(map(float, input_stream.readline().strip().split())))
    return np.array(rows)


def read_vector(n: int, input_stream: TextIO) -> Vector:
    return np.array(list(map(float, input_stream.readline().strip().split())))


def print_matrix(matrix: Matrix) -> None:
    f = np.vectorize(lambda x: round(x, 5))
    print(f(matrix))
