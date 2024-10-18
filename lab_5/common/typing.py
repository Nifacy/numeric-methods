from typing import Callable

import numpy as np
from numpy.typing import NDArray

Function = Callable[[float], float]

Matrix = NDArray[np.float64]
Vector = NDArray[np.float64]
