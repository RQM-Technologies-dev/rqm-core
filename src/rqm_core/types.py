"""Shared type aliases used across rqm_core."""

from typing import Annotated

import numpy as np
from numpy.typing import NDArray

# A 2-element complex vector representing a quantum spinor (alpha, beta).
ComplexVector2 = Annotated[NDArray[np.complex128], "shape (2,)"]

# A 3-element real vector (x, y, z) on the Bloch sphere.
BlochVector = Annotated[NDArray[np.float64], "shape (3,)"]

# A 2×2 complex matrix in SU(2).
SU2Matrix = Annotated[NDArray[np.complex128], "shape (2, 2)"]
