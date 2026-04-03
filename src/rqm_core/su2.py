"""SU(2) matrix construction, validation, and conversion helpers."""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

from rqm_core.linalg import is_unitary as _is_unitary, matrix_determinant
from rqm_core.quaternion import Quaternion
from rqm_core.validation import validate_axis, validate_square_matrix


def quaternion_to_su2(q: Quaternion) -> NDArray[np.complex128]:
    """Convert a unit quaternion to its SU(2) matrix representation.

    Args:
        q: Unit quaternion.  Will be normalized before conversion.

    Returns:
        2×2 complex numpy array in SU(2).
    """
    return q.normalize().to_su2_matrix()


def su2_to_quaternion(matrix: NDArray[np.complex128]) -> Quaternion:
    """Recover the unit quaternion from an SU(2) matrix.

    The inverse of :func:`quaternion_to_su2`.

    The SU(2) matrix has the form::

        [[ α , -β* ],
         [ β ,  α* ]]

    where ``α = w - i·z`` (matching the convention in :meth:`Quaternion.to_su2_matrix`).

    Args:
        matrix: 2×2 complex SU(2) matrix.

    Returns:
        Corresponding unit quaternion (with positive scalar part by convention).

    Raises:
        ValueError: If *matrix* is not unitary.
    """
    m = np.asarray(matrix, dtype=np.complex128)
    if not _is_unitary(m):
        raise ValueError("Matrix is not unitary; cannot convert to quaternion.")

    # top-left element is (w - i·z), bottom-right is (w + i·z)
    # top-right element is -(y + i·x), bottom-left is (y - i·x)
    alpha = m[0, 0]  # w - i*z
    beta = m[1, 0]   # y - i*x

    w = float(alpha.real)
    z = float(-alpha.imag)
    y = float(beta.real)
    x = float(-beta.imag)

    q = Quaternion(w, x, y, z)
    return q.normalize()


def axis_angle_to_su2(axis: str, angle: float) -> NDArray[np.complex128]:
    """Build an SU(2) matrix from an axis and rotation angle.

    Args:
        axis: Rotation axis – one of ``"x"``, ``"y"``, or ``"z"``.
        angle: Rotation angle in radians.

    Returns:
        2×2 SU(2) rotation matrix.
    """
    return Quaternion.from_axis_angle(axis, angle).to_su2_matrix()


def su2_identity() -> NDArray[np.complex128]:
    """Return the 2×2 identity matrix (SU(2) identity element).

    Returns:
        2×2 complex identity matrix.
    """
    return np.eye(2, dtype=np.complex128)


def _wrap_to_pi(angle: float) -> float:
    """Normalize an angle into ``(-π, π]`` deterministically."""
    wrapped = (angle + math.pi) % (2.0 * math.pi) - math.pi
    if wrapped <= -math.pi:
        return math.pi
    return wrapped


def _zero_small(angle: float, *, atol: float) -> float:
    """Clamp tiny angles to exact zero for deterministic output."""
    if abs(angle) <= atol:
        return 0.0
    return angle


def _axis_sequence_if_pure_rotation(
    q: Quaternion, *, atol: float
) -> tuple[tuple[str, float], ...] | None:
    """Return a single-axis named gate sequence when *q* is axis-aligned."""
    x, y, z = q.x, q.y, q.z

    # A pure axis rotation has exactly one meaningful imaginary component.
    if abs(y) <= atol and abs(z) <= atol and abs(x) > atol:
        angle = _zero_small(_wrap_to_pi(2.0 * math.atan2(x, q.w)), atol=atol)
        return (("RX", angle),) if angle != 0.0 else tuple()
    if abs(x) <= atol and abs(z) <= atol and abs(y) > atol:
        angle = _zero_small(_wrap_to_pi(2.0 * math.atan2(y, q.w)), atol=atol)
        return (("RY", angle),) if angle != 0.0 else tuple()
    if abs(x) <= atol and abs(y) <= atol and abs(z) > atol:
        angle = _zero_small(_wrap_to_pi(2.0 * math.atan2(z, q.w)), atol=atol)
        return (("RZ", angle),) if angle != 0.0 else tuple()
    return None


def su2_to_named_gate_sequence(
    matrix: NDArray[np.complex128],
    *,
    simplify_axis: bool = True,
    atol: float = 1e-9,
) -> tuple[tuple[str, float], ...]:
    """Decompose an SU(2) element into named single-qubit rotation gates.

    Convention:

    * Primary decomposition is Euler ZYZ in named-gate form
      ``RZ(φ) -> RY(θ) -> RZ(λ)``.
    * Returned angles are normalized to ``(-π, π]`` and tiny values
      ``|angle| <= atol`` are clamped to exactly ``0`` for determinism.
    * Near-identity rotations (``θ ≈ 0`` and vanishing Z phase) return an
      empty sequence ``()``.
    * If ``simplify_axis=True`` and the element is a pure x/y/z-axis
      rotation within *atol*, return a single ``RX``/``RY``/``RZ`` gate.

    The decomposition is backend-agnostic and contains no provider policy.

    Args:
        matrix: 2×2 SU(2) matrix.
        simplify_axis: Enable safe single-axis simplification.
        atol: Absolute tolerance for unitary checks and zero-clamping.

    Returns:
        Tuple of ``(gate_name, angle)`` entries.

    Raises:
        ValueError: If *matrix* is not a valid SU(2) matrix.
    """
    validate_su2_matrix(matrix, atol=atol)
    m = np.asarray(matrix, dtype=np.complex128)

    alpha = m[0, 0]
    beta = m[1, 0]

    c = abs(alpha)
    s = abs(beta)
    theta = _zero_small(_wrap_to_pi(2.0 * math.atan2(s, c)), atol=atol)

    # Near-RZ branch (theta ≈ 0): only sum (φ + λ) is observable.
    # Deterministic gauge choice: set φ = 0, keep λ from alpha phase.
    if abs(theta) <= atol:
        phi = 0.0
        lambd = _zero_small(_wrap_to_pi(-2.0 * math.atan2(alpha.imag, alpha.real)), atol=atol)
    else:
        a = math.atan2(alpha.imag, alpha.real)  # a = arg(alpha)
        b = math.atan2(beta.imag, beta.real)    # b = arg(beta)
        phi = _zero_small(_wrap_to_pi(b - a), atol=atol)
        lambd = _zero_small(_wrap_to_pi(-a - b), atol=atol)

    q = su2_to_quaternion(m)
    if simplify_axis:
        axis_sequence = _axis_sequence_if_pure_rotation(q, atol=atol)
        if axis_sequence is not None:
            return axis_sequence

    if theta == 0.0 and phi == 0.0 and lambd == 0.0:
        return tuple()
    return (("RZ", phi), ("RY", theta), ("RZ", lambd))


def quaternion_to_named_gate_sequence(
    q: Quaternion, *, simplify_axis: bool = True, atol: float = 1e-9
) -> tuple[tuple[str, float], ...]:
    """Decompose a unit quaternion into named rotation gates.

    This is a convenience wrapper over :func:`su2_to_named_gate_sequence`
    using the quaternion→SU(2) convention in :func:`quaternion_to_su2`.

    Args:
        q: Quaternion representing a single-qubit SU(2) element.
        simplify_axis: Enable safe single-axis simplification.
        atol: Absolute tolerance used for normalization and decomposition.

    Returns:
        Tuple of ``(gate_name, angle)`` entries.
    """
    return su2_to_named_gate_sequence(
        quaternion_to_su2(q), simplify_axis=simplify_axis, atol=atol
    )


# ------------------------------------------------------------------
# Validation helpers
# ------------------------------------------------------------------


def is_unitary(matrix: NDArray[np.complex128], *, atol: float = 1e-9) -> bool:
    """Return ``True`` if *matrix* is unitary (``M† M ≈ I``).

    This is a convenience re-export of :func:`rqm_core.linalg.is_unitary`
    scoped to the SU(2) domain.  All SU(2) matrices constructed by this
    module satisfy this property.

    Args:
        matrix: Square complex matrix to test.
        atol: Absolute tolerance (default ``1e-9``).

    Returns:
        ``True`` when *matrix* is unitary within *atol*.
    """
    return _is_unitary(np.asarray(matrix, dtype=np.complex128), atol=atol)


def determinant_close_to_one(
    matrix: NDArray[np.complex128], *, atol: float = 1e-9
) -> bool:
    """Return ``True`` if ``det(matrix) ≈ 1``.

    Args:
        matrix: Square complex matrix.
        atol: Absolute tolerance (default ``1e-9``).

    Returns:
        ``True`` when ``|det(M) - 1| ≤ atol``.
    """
    det = matrix_determinant(np.asarray(matrix, dtype=np.complex128))
    return abs(det - 1.0) <= atol


def validate_su2_matrix(
    matrix: NDArray[np.complex128], *, atol: float = 1e-9
) -> None:
    """Validate that *matrix* is a proper SU(2) matrix.

    Checks that the matrix is 2×2, unitary (``M† M ≈ I``), and has
    determinant close to 1.

    Args:
        matrix: Matrix to validate.
        atol: Absolute tolerance (default ``1e-9``).

    Raises:
        ValueError: If the matrix fails any SU(2) check.
    """
    validate_square_matrix(matrix, expected_size=2)
    m = np.asarray(matrix, dtype=np.complex128)
    if not _is_unitary(m, atol=atol):
        raise ValueError(
            "Matrix is not unitary (M† M ≠ I); not a valid SU(2) matrix."
        )
    det = matrix_determinant(m)
    if abs(det - 1.0) > atol:
        raise ValueError(
            f"Matrix determinant is {det:.6g}, expected 1; not a valid SU(2) matrix."
        )
