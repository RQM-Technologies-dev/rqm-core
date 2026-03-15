"""Spinor utilities: normalization, conversions, and fidelity."""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

from rqm_core.quaternion import Quaternion
from rqm_core.su2 import quaternion_to_su2
from rqm_core.types import SU2Matrix


def spinor_norm(alpha: complex, beta: complex) -> float:
    """Return the Euclidean norm of the spinor ``(alpha, beta)``.

    Args:
        alpha: Amplitude of ``|0⟩``.
        beta:  Amplitude of ``|1⟩``.

    Returns:
        Non-negative real norm ``sqrt(|alpha|² + |beta|²)``.
    """
    return math.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)


def normalize_spinor(alpha: complex, beta: complex) -> tuple[complex, complex]:
    """Return a normalized two-component spinor.

    Args:
        alpha: Amplitude of ``|0⟩``.
        beta:  Amplitude of ``|1⟩``.

    Returns:
        Pair ``(alpha/N, beta/N)`` where ``N = sqrt(|alpha|² + |beta|²)``.

    Raises:
        ValueError: If both amplitudes are zero.
    """
    norm = spinor_norm(alpha, beta)
    if norm == 0.0:
        raise ValueError("Spinor must be non-zero.")
    return (alpha / norm, beta / norm)


def is_normalized_spinor(
    alpha: complex, beta: complex, *, atol: float = 1e-9
) -> bool:
    """Return ``True`` if the spinor ``(alpha, beta)`` has unit norm.

    Args:
        alpha: Amplitude of ``|0⟩``.
        beta:  Amplitude of ``|1⟩``.
        atol:  Absolute tolerance (default ``1e-9``).

    Returns:
        ``True`` when ``| ||(alpha, beta)|| - 1 | ≤ atol``.
    """
    return abs(spinor_norm(alpha, beta) - 1.0) <= atol


def spinor_to_quaternion(alpha: complex, beta: complex) -> Quaternion:
    """Return the unit quaternion that maps ``|0⟩`` to the spinor ``|ψ⟩``.

    The spinor ``|ψ⟩ = α|0⟩ + β|1⟩`` lives in SU(2) ≅ S³.  We extract the
    quaternion components directly from the normalized amplitudes::

        w = Re(α),  z = -Im(α),  y = Re(β),  x = -Im(β)

    Note: global phase is not physically observable; the quaternion encodes
    the rotation of ``|0⟩`` onto ``|ψ⟩`` up to a global phase.

    Args:
        alpha: Amplitude of ``|0⟩``.
        beta:  Amplitude of ``|1⟩``.

    Returns:
        Unit quaternion corresponding to the spinor.

    Raises:
        ValueError: If the spinor is zero.
    """
    a, b = normalize_spinor(alpha, beta)
    w = a.real
    z = -a.imag
    y = b.real
    x = -b.imag
    return Quaternion(w, x, y, z).normalize()


def spinor_to_su2(alpha: complex, beta: complex) -> SU2Matrix:
    """Return the SU(2) matrix corresponding to the spinor ``|ψ⟩``.

    Args:
        alpha: Amplitude of ``|0⟩``.
        beta:  Amplitude of ``|1⟩``.

    Returns:
        2×2 SU(2) matrix.
    """
    q = spinor_to_quaternion(alpha, beta)
    return quaternion_to_su2(q)


def state_fidelity(
    state1: NDArray[np.complex128],
    state2: NDArray[np.complex128],
) -> float:
    """Compute the quantum state fidelity between two pure states.

    For pure states the fidelity is::

        F = |⟨ψ₁|ψ₂⟩|²

    The states need not be pre-normalized; they are normalized internally.

    Args:
        state1: First state vector (need not be normalized).
        state2: Second state vector (need not be normalized).

    Returns:
        Fidelity in the range ``[0, 1]``.

    Raises:
        ValueError: If either state is zero.
    """
    v1 = np.asarray(state1, dtype=np.complex128).ravel()
    v2 = np.asarray(state2, dtype=np.complex128).ravel()

    n1 = float(np.linalg.norm(v1))
    n2 = float(np.linalg.norm(v2))
    if n1 == 0.0 or n2 == 0.0:
        raise ValueError("State vectors must be non-zero.")

    overlap = np.vdot(v1, v2) / (n1 * n2)
    return float(abs(overlap) ** 2)
