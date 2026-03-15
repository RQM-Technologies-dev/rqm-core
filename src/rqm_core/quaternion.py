"""Quaternion algebra: representation, arithmetic, and conversions."""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

from rqm_core.linalg import normalize_vector


class Quaternion:
    """Unit-friendly quaternion ``q = w + x·i + y·j + z·k``.

    Attributes:
        w: Scalar (real) part.
        x: Coefficient of **i**.
        y: Coefficient of **j**.
        z: Coefficient of **k**.
    """

    __slots__ = ("w", "x", "y", "z")

    def __init__(self, w: float, x: float, y: float, z: float) -> None:
        """Construct a quaternion from its four components.

        Args:
            w: Scalar part.
            x: Coefficient of **i**.
            y: Coefficient of **j**.
            z: Coefficient of **k**.
        """
        self.w = float(w)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def identity(cls) -> "Quaternion":
        """Return the multiplicative identity quaternion ``(1, 0, 0, 0)``.

        Returns:
            Identity quaternion.
        """
        return cls(1.0, 0.0, 0.0, 0.0)

    @classmethod
    def from_axis_angle(cls, axis: str, angle: float) -> "Quaternion":
        """Construct a unit quaternion representing a rotation.

        The axis-angle formula is::

            q = cos(θ/2) + u·sin(θ/2)

        where ``u`` is the unit vector along *axis*.

        Args:
            axis: One of ``"x"``, ``"y"``, or ``"z"``.
            angle: Rotation angle in radians.

        Returns:
            Unit quaternion for the specified rotation.

        Raises:
            ValueError: If *axis* is not ``"x"``, ``"y"``, or ``"z"``.
        """
        axis_lower = axis.lower()
        if axis_lower not in ("x", "y", "z"):
            raise ValueError(f"axis must be 'x', 'y', or 'z'; got {axis!r}")

        half = angle / 2.0
        c = math.cos(half)
        s = math.sin(half)

        if axis_lower == "x":
            return cls(c, s, 0.0, 0.0)
        if axis_lower == "y":
            return cls(c, 0.0, s, 0.0)
        return cls(c, 0.0, 0.0, s)

    # ------------------------------------------------------------------
    # Arithmetic
    # ------------------------------------------------------------------

    def __mul__(self, other: "Quaternion") -> "Quaternion":
        """Hamilton product of two quaternions.

        Args:
            other: Right-hand quaternion.

        Returns:
            Product quaternion.
        """
        w1, x1, y1, z1 = self.w, self.x, self.y, self.z
        w2, x2, y2, z2 = other.w, other.x, other.y, other.z
        return Quaternion(
            w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
            w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
            w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
            w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        )

    def conjugate(self) -> "Quaternion":
        """Return the quaternion conjugate ``(w, -x, -y, -z)``.

        Returns:
            Conjugate quaternion.
        """
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def norm(self) -> float:
        """Return the Euclidean norm ``sqrt(w²+x²+y²+z²)``.

        Returns:
            Non-negative real norm.
        """
        return math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)

    def __abs__(self) -> float:
        """Return the norm (alias for :meth:`norm`).

        Returns:
            Non-negative real norm.
        """
        return self.norm()

    def normalize(self) -> "Quaternion":
        """Return a unit quaternion (same direction, norm 1).

        Returns:
            Normalized quaternion.

        Raises:
            ValueError: If the quaternion has zero norm.
        """
        n = self.norm()
        if n == 0.0:
            raise ValueError("Cannot normalize a zero quaternion.")
        return Quaternion(self.w / n, self.x / n, self.y / n, self.z / n)

    def inverse(self) -> "Quaternion":
        """Return the multiplicative inverse ``q* / |q|²``.

        Returns:
            Inverse quaternion.

        Raises:
            ValueError: If the quaternion has zero norm.
        """
        n2 = self.w**2 + self.x**2 + self.y**2 + self.z**2
        if n2 == 0.0:
            raise ValueError("Cannot invert a zero quaternion.")
        return Quaternion(
            self.w / n2, -self.x / n2, -self.y / n2, -self.z / n2
        )

    def is_unit(self, *, atol: float = 1e-9) -> bool:
        """Return ``True`` if the quaternion has unit norm.

        Args:
            atol: Absolute tolerance (default ``1e-9``).

        Returns:
            ``True`` when ``| |q| - 1 | ≤ atol``.
        """
        return abs(self.norm() - 1.0) <= atol

    # ------------------------------------------------------------------
    # Conversions
    # ------------------------------------------------------------------

    def to_su2_matrix(self) -> NDArray[np.complex128]:
        """Return the SU(2) matrix corresponding to this quaternion.

        The mapping is::

            [[ w - i·z , -(y + i·x) ],
             [ y - i·x ,  w + i·z  ]]

        Returns:
            2×2 complex numpy array in SU(2).
        """
        w, x, y, z = self.w, self.x, self.y, self.z
        return np.array(
            [
                [complex(w, -z), complex(-y, -x)],
                [complex(y, -x), complex(w, z)],
            ],
            dtype=np.complex128,
        )

    def to_rotation_matrix(self) -> NDArray[np.float64]:
        """Return the equivalent 3×3 SO(3) rotation matrix.

        Uses the standard quaternion-to-rotation formula.

        Returns:
            3×3 real numpy array.
        """
        w, x, y, z = self.w, self.x, self.y, self.z
        return np.array(
            [
                [
                    1 - 2 * (y * y + z * z),
                    2 * (x * y - z * w),
                    2 * (x * z + y * w),
                ],
                [
                    2 * (x * y + z * w),
                    1 - 2 * (x * x + z * z),
                    2 * (y * z - x * w),
                ],
                [
                    2 * (x * z - y * w),
                    2 * (y * z + x * w),
                    1 - 2 * (x * x + y * y),
                ],
            ],
            dtype=np.float64,
        )

    # ------------------------------------------------------------------
    # Dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """Return a developer-friendly string representation.

        Returns:
            String of the form ``Quaternion(w, x, y, z)``.
        """
        return f"Quaternion({self.w!r}, {self.x!r}, {self.y!r}, {self.z!r})"

    def __eq__(self, other: object) -> bool:  # type: ignore[override]
        """Return ``True`` if *other* is numerically equal to this quaternion.

        Comparison is element-wise within a tolerance of ``1e-9``.

        Args:
            other: Object to compare.

        Returns:
            ``True`` when all components are within ``1e-9``.
        """
        if not isinstance(other, Quaternion):
            return NotImplemented
        atol = 1e-9
        return (
            abs(self.w - other.w) <= atol
            and abs(self.x - other.x) <= atol
            and abs(self.y - other.y) <= atol
            and abs(self.z - other.z) <= atol
        )

    def is_close(self, other: "Quaternion", *, atol: float = 1e-9) -> bool:
        """Return ``True`` if *other* is within *atol* of this quaternion.

        Unlike :meth:`__eq__`, this method accepts a configurable tolerance.

        Args:
            other: Quaternion to compare.
            atol: Absolute tolerance (default ``1e-9``).

        Returns:
            ``True`` when all components are within *atol*.
        """
        return (
            abs(self.w - other.w) <= atol
            and abs(self.x - other.x) <= atol
            and abs(self.y - other.y) <= atol
            and abs(self.z - other.z) <= atol
        )
