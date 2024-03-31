from typing import TypeVar, ParamSpec, Callable
import time


R = TypeVar("R")
P = ParamSpec("P")


def timer(func: Callable[P, R]) -> Callable[P, R]:
    def _wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f'[timer] {func.__name__} : {end - start} ms')
        return result
    return _wrapper
