import abc
import pathlib
import subprocess as sp

CWD = pathlib.Path(".").absolute()
CURDIR = pathlib.Path(__file__).parent.relative_to(CWD)
TESTS_DIR = CURDIR
LAB_DIR = CURDIR.parent


class CompileError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"Error accured while compile: {message}")


class SolutionAdapterBase[T, R](abc.ABC):
    EXEC_PATH = CURDIR / "a.exe"

    def __init__(self) -> None:
        self._compile_program()

    def _compile_program(self) -> None:
        command = ["g++", str(self._target_path), "-o", str(self.EXEC_PATH)]
        result = sp.run(command)
        if result.returncode:
            raise CompileError((result.stderr or b"").decode())

    def run(self, input_data: T) -> R:
        serialized_input = self._serialize(input_data)
        process = sp.Popen(
            [str(self.EXEC_PATH)], stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE
        )
        stdout, _ = process.communicate(serialized_input.encode())
        return self._deserialize(stdout.decode())

    @abc.abstractproperty
    def _target_path(self) -> pathlib.Path:
        raise NotImplementedError

    @abc.abstractmethod
    def _serialize(self, input_data: T) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def _deserialize(self, serialized: str) -> R:
        raise NotImplementedError
