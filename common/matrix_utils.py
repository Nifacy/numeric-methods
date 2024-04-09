import numpy as np
from typing import TextIO


def read_matrix(m: int, n: int, input_stream: TextIO) -> np.ndarray[float]:
    rows = []
    for _ in range(m):
        rows.append(list(map(float, input_stream.readline().strip().split())))
    return np.array(rows)


def read_vector(n: int, input_stream: TextIO) -> np.ndarray[float]:
    return np.array(list(map(float, input_stream.readline().strip().split())))
