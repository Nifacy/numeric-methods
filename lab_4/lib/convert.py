from typing import Callable

import numpy as np

from common.typing import Vector

from .typing import DiffEquation


def convert_to_system_function(eq: DiffEquation) -> Callable[[float, Vector], Vector]:
    """
    Перевод дифференциальное уравнение к системе, имеющий вид
    `Y' = F(Y)`, где `Y = (z y)`, `z = y'`
    """

    a = lambda x: -eq.q(x) / eq.p(x)
    b = lambda x: -eq.r(x) / eq.p(x)
    c = lambda x: -eq.f(x) / eq.p(x)

    return lambda x, Y: np.array(
        [
            Y[1],
            a(x) * Y[1] + b(x) * Y[0] + c(x),
        ]
    )
