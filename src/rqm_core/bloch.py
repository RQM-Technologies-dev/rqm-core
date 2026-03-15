"""Bloch sphere mappings between quantum states and 3-D vectors."""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

from rqm_core.quaternion import Quaternion
from rqm_core.types import BlochVector


def state_to_bloch(alpha: complex, beta: complex) -> BlochVector:
    """Map a two-component quantum state to its Bloch vector.

    For normalized state ``|ψ⟩ = α|0⟩ + β|1⟩`` the Bloch coordinates are::

        x = 2 Re(conj(α) · β)
        y = 2 Im(conj(α) · β)
        z = |α|² − |β|²

    The state is *not* required to be pre-normalized; it is normalized internally.

    Args:
        alpha: Amplitude of ``|0⟩``.
        beta:  Amplitude of ``|1⟩``.

    Returns:
        Bloch vector ``(x, y, z)`` as a length-3 float64 numpy array.

    Raises:
        ValueError: If both amplitudes are zero.
    """
    norm = math.sqrt(abs(alpha) ** 2 + abs(beta) ** 2)
    if norm == 0.0:
        raise ValueError("State vector must be non-zero.")
    alpha = alpha / norm
    beta = beta / norm

    product = alpha.conjugate() * beta
    x = 2.0 * product.real
    y = 2.0 * product.imag
    z = abs(alpha) ** 2 - abs(beta) ** 2
    return np.array([x, y, z], dtype=np.float64)


def bloch_to_state(theta: float, phi: float) -> NDArray[np.complex128]:
    """Convert Bloch sphere angles to a normalized two-component spinor.

    The standard parameterization::

        |ψ⟩ = cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩

    Args:
        theta: Polar angle in radians (colatitude from north pole).
        phi:   Azimuthal angle in radians.

    Returns:
        Normalized spinor ``[α, β]`` as a length-2 complex128 numpy array.
    """
    alpha = math.cos(theta / 2.0)
    beta = cmath_exp(1j * phi) * math.sin(theta / 2.0)
    return np.array([alpha, beta], dtype=np.complex128)


def bloch_from_quaternion(q: Quaternion) -> BlochVector:
    """Return the Bloch vector obtained by rotating ``|0⟩`` with quaternion *q*.

    The north-pole state ``|0⟩`` maps to Bloch vector ``(0, 0, 1)``.
    Applying the rotation matrix of *q* to this vector yields the Bloch
    vector of the rotated state.

    Args:
        q: Unit quaternion representing the rotation.

    Returns:
        Bloch vector ``(x, y, z)`` as a length-3 float64 numpy array.
    """
    r = q.normalize().to_rotation_matrix()
    north_pole = np.array([0.0, 0.0, 1.0], dtype=np.float64)
    return r @ north_pole


# ---------------------------------------------------------------------------
# Private helper
# ---------------------------------------------------------------------------

def cmath_exp(z: complex) -> complex:
    """Return ``e^z`` for complex *z* using numpy."""
    return complex(np.exp(z))
