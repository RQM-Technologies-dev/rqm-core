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


def safe_norm(values: NDArray[np.floating]) -> float:
    """Return the Euclidean norm of *values*, raising ``ValueError`` when zero.

    Args:
        values: Array or sequence of real numbers.

    Returns:
        Euclidean norm of *values*.

    Raises:
        ValueError: If the norm is zero (or numerically indistinguishable from zero).
    """
    n = float(np.linalg.norm(values))
    if n == 0.0:
        raise ValueError("Cannot compute norm of a zero vector.")
    return n


def is_finite_real(value: float) -> bool:
    """Return ``True`` if *value* is a finite real number.

    Args:
        value: Number to test.

    Returns:
        ``True`` when *value* is finite (not NaN and not ±∞).
    """
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def is_finite_complex(value: complex) -> bool:
    """Return ``True`` if *value* is a finite complex number.

    Both the real and imaginary parts must be finite.

    Args:
        value: Complex number to test.

    Returns:
        ``True`` when both ``Re(value)`` and ``Im(value)`` are finite.
    """
    try:
        v = complex(value)
        return math.isfinite(v.real) and math.isfinite(v.imag)
    except (TypeError, ValueError):
        return False

