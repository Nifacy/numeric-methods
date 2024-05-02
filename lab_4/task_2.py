from math import exp

import matplotlib.pyplot as plt
import numpy as np

from .lib.boundary_task import finite_diff_method
from .lib.boundary_task import shooting_method
from .lib.typing import BoundaryCondition
from .lib.typing import DiffEquation
from .lib.typing import Grid

if __name__ == "__main__":
    eq = DiffEquation(
        lambda x: (2 * x + 1),
        lambda x: 4 * x,
        lambda x: -4.0,
        lambda x: 0.0,
    )
    f = lambda x: x + exp(-2 * x)
    grid = Grid(0.0, 1.0, 0.1)

    cond_1 = BoundaryCondition(1.0, 0.0, 1.0)
    cond_2 = BoundaryCondition(1.0, 2.0, -3.0)

    result_1 = shooting_method(eq, cond_1, cond_2, grid)[1]
    result_2 = finite_diff_method(eq, cond_1, cond_2, grid)[1]
    actual = np.array([f(x) for x in grid.range])

    plt.plot(grid.range, result_2, color="red")
    plt.plot(grid.range, actual, color="blue")
    plt.show()
