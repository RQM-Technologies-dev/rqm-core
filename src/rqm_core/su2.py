"""SU(2) matrix construction, validation, and conversion helpers."""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

from rqm_core.quaternion import Quaternion
from rqm_core.linalg import is_unitary, matrix_determinant


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

    where ``α = w + i·z`` (top-right sign convention from ``to_su2_matrix``).

    Args:
        matrix: 2×2 complex SU(2) matrix.

    Returns:
        Corresponding unit quaternion (with positive scalar part by convention).

    Raises:
        ValueError: If *matrix* is not unitary.
    """
    m = np.asarray(matrix, dtype=np.complex128)
    if not is_unitary(m):
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


# ------------------------------------------------------------------
# Validation helpers
# ------------------------------------------------------------------


def is_unitary_matrix(matrix: NDArray[np.complex128], *, atol: float = 1e-9) -> bool:
    """Return ``True`` if *matrix* is unitary (``M† M ≈ I``).

    Args:
        matrix: Square complex matrix to test.
        atol: Absolute tolerance (default ``1e-9``).

    Returns:
        ``True`` when *matrix* is unitary within *atol*.
    """
    return is_unitary(np.asarray(matrix, dtype=np.complex128), atol=atol)


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
