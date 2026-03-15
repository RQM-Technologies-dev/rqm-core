"""Bloch sphere mappings between quantum states and 3-D vectors."""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

from rqm_core.quaternion import Quaternion


def state_to_bloch(alpha: complex, beta: complex) -> tuple[float, float, float]:
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
        Bloch vector ``(x, y, z)`` as a 3-tuple of floats.

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
    return (x, y, z)


def bloch_to_state(theta: float, phi: float) -> tuple[complex, complex]:
    """Convert Bloch sphere angles to a normalized two-component spinor.

    The standard parameterization::

        |ψ⟩ = cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩

    Args:
        theta: Polar angle in radians (colatitude from north pole).
        phi:   Azimuthal angle in radians.

    Returns:
        Normalized spinor ``(alpha, beta)`` as a 2-tuple of complex numbers.
    """
    alpha = complex(math.cos(theta / 2.0))
    beta = complex(np.exp(1j * phi)) * math.sin(theta / 2.0)
    return (alpha, beta)


def bloch_from_quaternion(q: Quaternion) -> tuple[float, float, float]:
    """Return the Bloch vector obtained by rotating ``|0⟩`` with quaternion *q*.

    The north-pole state ``|0⟩`` maps to Bloch vector ``(0, 0, 1)``.
    Applying the rotation matrix of *q* to this vector yields the Bloch
    vector of the rotated state.

    Args:
        q: Unit quaternion representing the rotation.

    Returns:
        Bloch vector ``(x, y, z)`` as a 3-tuple of floats.
    """
    r = q.normalize().to_rotation_matrix()
    north_pole = np.array([0.0, 0.0, 1.0], dtype=np.float64)
    result = r @ north_pole
    return (float(result[0]), float(result[1]), float(result[2]))


def bloch_radius(x: float, y: float, z: float) -> float:
    """Return the radial distance of a Bloch vector from the origin.

    For a pure state the Bloch vector lies on the unit sphere, so
    ``bloch_radius(x, y, z) == 1``.

    Args:
        x: x-component of the Bloch vector.
        y: y-component of the Bloch vector.
        z: z-component of the Bloch vector.

    Returns:
        Euclidean norm ``sqrt(x² + y² + z²)``.
    """
    return math.sqrt(x * x + y * y + z * z)


def validate_bloch_vector(
    x: float, y: float, z: float, *, atol: float = 1e-9
) -> None:
    """Validate that ``(x, y, z)`` is a valid pure-state Bloch vector.

    A valid Bloch vector for a pure state must:
    - contain only finite values
    - lie on the unit sphere (radius ≈ 1)

    Args:
        x:    x-component.
        y:    y-component.
        z:    z-component.
        atol: Absolute tolerance for the unit-sphere check (default ``1e-9``).

    Raises:
        ValueError: If any component is non-finite or the radius is not 1.
    """
    for name, val in (("x", x), ("y", y), ("z", z)):
        if not math.isfinite(float(val)):
            raise ValueError(
                f"Bloch vector component {name} must be finite; got {val!r}"
            )
    r = bloch_radius(x, y, z)
    if abs(r - 1.0) > atol:
        raise ValueError(
            f"Bloch vector must lie on the unit sphere (radius 1); got radius {r:.6g}"
        )

