"""General-purpose utility functions for rqm_core."""

import math

import numpy as np
from numpy.typing import NDArray


def angle_wrap(angle: float) -> float:
    """Wrap *angle* (in radians) to the interval ``(-π, π]``.

    Args:
        angle: Angle in radians.

    Returns:
        Equivalent angle in ``(-π, π]``.
    """
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def safe_norm(v: NDArray[np.floating]) -> float:
    """Return the Euclidean norm of *v*, raising ``ValueError`` when it is zero.

    Args:
        v: Real-valued array.

    Returns:
        Euclidean norm of *v*.

    Raises:
        ValueError: If the norm is zero (or numerically indistinguishable from zero).
    """
    n = float(np.linalg.norm(v))
    if n == 0.0:
        raise ValueError("Cannot compute norm of a zero vector.")
    return n


def complex_close(a: complex, b: complex, *, atol: float = 1e-9) -> bool:
    """Return ``True`` if *a* and *b* are numerically close.

    Args:
        a: First complex number.
        b: Second complex number.
        atol: Absolute tolerance (default ``1e-9``).

    Returns:
        ``True`` when ``|a - b| ≤ atol``.
    """
    return abs(a - b) <= atol


def matrix_close(
    a: NDArray[np.complexfloating],
    b: NDArray[np.complexfloating],
    *,
    atol: float = 1e-9,
) -> bool:
    """Return ``True`` if matrices *a* and *b* are element-wise close.

    Args:
        a: First matrix.
        b: Second matrix.
        atol: Absolute tolerance (default ``1e-9``).

    Returns:
        ``True`` when every element satisfies ``|a_ij - b_ij| ≤ atol``.
    """
    return bool(np.allclose(a, b, atol=atol, rtol=0.0))
