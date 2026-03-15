"""Centralised validation helpers for rqm_core.

All functions raise ``ValueError`` with friendly, specific messages so that
callers can surface problems clearly to users.
"""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

_VALID_AXES = frozenset(("x", "y", "z"))


def validate_axis(axis: str) -> str:
    """Validate and return the canonical (lower-case) axis name.

    Args:
        axis: Axis label – must be ``"x"``, ``"y"``, or ``"z"`` (case-insensitive).

    Returns:
        Lower-case axis string (``"x"``, ``"y"``, or ``"z"``).

    Raises:
        ValueError: If *axis* is not a valid axis label.
    """
    lower = str(axis).lower()
    if lower not in _VALID_AXES:
        raise ValueError(
            f"axis must be one of 'x', 'y', 'z'; got {axis!r}"
        )
    return lower


def validate_complex_pair(alpha: complex, beta: complex) -> None:
    """Validate that *(alpha, beta)* form a non-zero complex spinor.

    Args:
        alpha: First component.
        beta:  Second component.

    Raises:
        ValueError: If either value is not finite, or if both are zero.
    """
    if not (math.isfinite(alpha.real) and math.isfinite(alpha.imag)):
        raise ValueError(
            f"alpha must be a finite complex number; got {alpha!r}"
        )
    if not (math.isfinite(beta.real) and math.isfinite(beta.imag)):
        raise ValueError(
            f"beta must be a finite complex number; got {beta!r}"
        )
    if alpha == 0.0 and beta == 0.0:
        raise ValueError(
            "The spinor (alpha, beta) must not be the zero vector."
        )


def validate_square_matrix(
    matrix: NDArray,
    expected_size: int | None = None,
) -> None:
    """Validate that *matrix* is a 2-D square numpy array.

    Args:
        matrix:        Array to inspect.
        expected_size: If provided, also assert that each side equals this value.

    Raises:
        ValueError: If *matrix* is not 2-D, not square, or the wrong size.
    """
    m = np.asarray(matrix)
    if m.ndim != 2:
        raise ValueError(
            f"Matrix must be 2-D; got {m.ndim}-D array."
        )
    rows, cols = m.shape
    if rows != cols:
        raise ValueError(
            f"Matrix must be square; got shape {m.shape}."
        )
    if expected_size is not None and rows != expected_size:
        raise ValueError(
            f"Expected a {expected_size}×{expected_size} matrix; got {rows}×{cols}."
        )


def validate_real_number(value: float, name: str) -> None:
    """Validate that *value* is a finite real number.

    Args:
        value: Number to check.
        name:  Human-readable parameter name used in the error message.

    Raises:
        TypeError:  If *value* is not a real number.
        ValueError: If *value* is infinite or NaN.
    """
    if not isinstance(value, (int, float)):
        raise TypeError(
            f"{name} must be a real number; got {type(value).__name__!r}"
        )
    if not math.isfinite(float(value)):
        raise ValueError(
            f"{name} must be finite; got {value!r}"
        )


def validate_tolerance(tol: float) -> None:
    """Validate that *tol* is a positive finite float.

    Args:
        tol: Tolerance value to check.

    Raises:
        TypeError:  If *tol* is not a real number.
        ValueError: If *tol* is not positive or is not finite.
    """
    if not isinstance(tol, (int, float)):
        raise TypeError(
            f"Tolerance must be a real number; got {type(tol).__name__!r}"
        )
    if not math.isfinite(float(tol)) or float(tol) <= 0.0:
        raise ValueError(
            f"Tolerance must be a positive finite number; got {tol!r}"
        )
