"""Spinor utilities: normalization, conversions, and fidelity."""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

from rqm_core.quaternion import Quaternion
from rqm_core.su2 import quaternion_to_su2
from rqm_core.types import ComplexVector2, SU2Matrix


def normalize_spinor(alpha: complex, beta: complex) -> ComplexVector2:
    """Return a normalized two-component spinor.

    Args:
        alpha: Amplitude of ``|0⟩``.
        beta:  Amplitude of ``|1⟩``.

    Returns:
        Unit spinor ``[α/N, β/N]`` where ``N = sqrt(|α|² + |β|²)``.

    Raises:
        ValueError: If both amplitudes are zero.
    """
    norm = math.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    if norm == 0.0:
        raise ValueError("Spinor must be non-zero.")
    return np.array([alpha / norm, beta / norm], dtype=np.complex128)


def spinor_to_quaternion(alpha: complex, beta: complex) -> Quaternion:
    """Return the unit quaternion that maps ``|0⟩`` to the spinor ``|ψ⟩``.

    The spinor ``|ψ⟩ = α|0⟩ + β|1⟩`` lives in SU(2) ≅ S³.  We extract the
    quaternion components directly from the normalized amplitudes::

        w = Re(α),  z = -Im(α),  y = Re(β),  x = -Im(β)

    Args:
        alpha: Amplitude of ``|0⟩``.
        beta:  Amplitude of ``|1⟩``.

    Returns:
        Unit quaternion corresponding to the spinor.

    Raises:
        ValueError: If the spinor is zero.
    """
    psi = normalize_spinor(alpha, beta)
    a, b = complex(psi[0]), complex(psi[1])
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
