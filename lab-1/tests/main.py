import pathlib
import numpy as np
import subprocess as sp
from dataclasses import dataclass


CURDIR = pathlib.Path(__file__).parent
TESTS_DIR = CURDIR
LAB_DIR = CURDIR.parent


class CompileError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f'Error accured while compile: {message}')


def _normalize(vec: np.ndarray[float]) -> np.ndarray[float]:
    norm = np.linalg.norm(vec)
    return vec / norm


def _round(vec: np.ndarray[float]) -> np.ndarray[float]:
    return np.array([round(x, 3) for x in vec])


def etalone(matrix: np.ndarray[float], precision: float) -> tuple[list[np.ndarray[float], list[float]]]:
    values, vectors = np.linalg.eig(matrix)
    v = []

    for vector in vectors:
        v.append(np.array([round(x, 3) for x in vector]))

    return v, list(map(lambda x: round(x, 3), values))



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


class SolutionAdapter:
    TARGET_PATH = LAB_DIR / 'task_4' / 'main.cpp'
    EXEC_PATH = CURDIR / 'a.exe'

    def __init__(self) -> None:
        self.__compile_program()

    def run(self, matrix: np.ndarray[float], precision: float) -> str:
        input_data = self.__serialize(matrix, precision)
        process = sp.Popen([str(self.EXEC_PATH)], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        stdout, stderr = process.communicate(input_data.encode())
        return self.__deserialize(stdout.decode())

    @classmethod
    def __compile_program(cls) -> None:
        result = sp.run(['g++', str(cls.TARGET_PATH), '-o', str(cls.EXEC_PATH)])

        if result.returncode:
            raise CompileError(result.stderr.decode())

    @classmethod
    def __serialize(cls, matrix: np.ndarray[float], precision: float) -> str:
        serialized = [str(precision), f'{len(matrix)}']

        for row in matrix:
            serialized.append('\t'.join(map(str, row)))

        return '\n'.join(serialized)

    @classmethod
    def __deserialize(cls, data: str) -> SolutionResult:
        values, vectors, iterations = None, [], None

        for line in map(str.strip, data.splitlines()):
            if line.startswith('eigen values'):
                values = list(map(float, line.split(':')[1].strip().split()))
            
            if line.startswith('x'):
                vectors.append(np.array(list(map(float, line.split(':')[1].strip().split()))))

            if line.startswith('iterations'):
                iterations = int(line.split(':')[1].strip())
        
        return SolutionResult(
            iterations=iterations,
            eigen_values=values,
            eigen_vectors=vectors,
        )

adapter = SolutionAdapter()
A, eps = np.array([[4, 2, 1], [2, 5, 3], [1, 3, 6]]), 0.0001
result = adapter.run(A, eps)
expected = etalone(A, eps)

print(check(A, eps, result))
