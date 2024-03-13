import pathlib
import numpy as np
from dataclasses import dataclass

from tests import _adapter


@dataclass
class SolutionResult:
    iterations: int
    eigen_values: list[float]
    eigen_vectors: list[np.ndarray[float]]


def check(A: np.ndarray[float], eps: float, result: SolutionResult) -> bool:
    for value, vector in zip(result.eigen_values, result.eigen_vectors):
        a, b = A @ vector.T, value * vector

        for x in map(abs, a - b):
            if x >= eps * 5:
                return False

    return True


class SolutionAdapter(
    _adapter.SolutionAdapterBase[tuple[np.ndarray[float], float], SolutionResult]
):
    @property
    def _target_path(self) -> pathlib.Path:
        return _adapter.LAB_DIR / "task_4" / "main.cpp"

    def _serialize(self, input_data: tuple[np.ndarray[float], float]) -> str:
        matrix, precision = input_data
        serialized = [str(precision), f"{len(matrix)}"]

        for row in matrix:
            serialized.append("\t".join(map(str, row)))

        return "\n".join(serialized)

    def _deserialize(self, data: str) -> SolutionResult:
        values, vectors, iterations = None, [], None

        for line in map(str.strip, data.splitlines()):
            if line.startswith("eigen values"):
                values = list(map(float, line.split(":")[1].strip().split()))

            if line.startswith("x"):
                vectors.append(
                    np.array(list(map(float, line.split(":")[1].strip().split())))
                )

            if line.startswith("iterations"):
                iterations = int(line.split(":")[1].strip())

        return SolutionResult(
            iterations=iterations,
            eigen_values=values,
            eigen_vectors=vectors,
        )


testcases = [
    np.array([[4, 2, 1], [2, 5, 3], [1, 3, 6]]),
]
precision = 0.0001
adapter = SolutionAdapter()

for i, matrix in enumerate(testcases, 1):
    result = adapter.run((matrix, precision))
    print(f'Test #{i}: {"OK" if check(matrix, precision, result) else "FAILED"}')
