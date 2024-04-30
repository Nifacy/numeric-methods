from typing import Callable

import numpy as np
from numpy.typing import NDArray

Function = Callable[[float], float]
MultiArgFunction = Callable[[NDArray[np.float64]], float]

Matrix = NDArray[np.float64]
Vector = NDArray[np.float64]
