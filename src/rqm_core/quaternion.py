"""Quaternion algebra: representation, arithmetic, and conversions."""

from __future__ import annotations

import math
from typing import Sequence

import numpy as np
from numpy.typing import NDArray

from rqm_core.validation import validate_axis


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
        axis_lower = validate_axis(axis)

        half = angle / 2.0
        c = math.cos(half)
        s = math.sin(half)

        if axis_lower == "x":
            return cls(c, s, 0.0, 0.0)
        if axis_lower == "y":
            return cls(c, 0.0, s, 0.0)
        return cls(c, 0.0, 0.0, s)

    @classmethod
    def from_axis_angle_vec(
        cls,
        axis: Sequence[float],
        angle: float,
    ) -> "Quaternion":
        """Construct a unit quaternion from an arbitrary rotation axis and angle.

        The axis-angle formula is::

            q = cos(θ/2) + u·sin(θ/2)

        where ``u = (ux, uy, uz)`` is the *unit* version of *axis*.

        This generalises :meth:`from_axis_angle` to rotations about any
        direction, not only the cardinal axes.  The axes ``i``, ``j``, ``k``
        correspond to the x-, y-, z-directions respectively, matching the
        Pauli-gate mapping ``i↔X``, ``j↔Y``, ``k↔Z``.

        Args:
            axis: A non-zero 3-element sequence ``(ux, uy, uz)`` giving the
                rotation axis.  It need not be pre-normalised.
            angle: Rotation angle *θ* in radians.  The quaternion half-angle
                parameter is ``φ = θ/2``, so the physical Bloch-sphere
                rotation is ``2φ = θ``.

        Returns:
            Unit quaternion ``cos(θ/2) + (ux·i + uy·j + uz·k)·sin(θ/2)``.

        Raises:
            ValueError: If *axis* is the zero vector or has a length other
                than 3.
        """
        ax = list(axis)
        if len(ax) != 3:
            raise ValueError(
                f"axis must be a 3-element sequence; got length {len(ax)}"
            )
        ux, uy, uz = float(ax[0]), float(ax[1]), float(ax[2])
        norm = math.sqrt(ux * ux + uy * uy + uz * uz)
        if norm == 0.0:
            raise ValueError("axis must be a non-zero vector.")
        ux, uy, uz = ux / norm, uy / norm, uz / norm
        half = angle / 2.0
        c = math.cos(half)
        s = math.sin(half)
        return cls(c, ux * s, uy * s, uz * s)

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

    def canonicalize(self) -> "Quaternion":
        """Return the canonical representative with non-negative scalar part.

        Both ``q`` and ``-q`` describe the same physical rotation in SO(3),
        while their SU(2) matrices differ by the global phase ``-1``.  For
        phase-invariant compiler canonicalization the convention ``w ≥ 0`` is
        chosen so descriptor output is deterministic.  Callers must not apply
        this sign choice in contexts where a local global phase can become
        observable, such as controlled operations.

        Returns:
            ``self.normalize()`` if its scalar part is non-negative,
            otherwise ``-self.normalize()``.
        """
        q = self.normalize()
        if q.w < 0.0:
            return Quaternion(-q.w, -q.x, -q.y, -q.z)
        return q

    def to_axis_angle(
        self, *, atol: float = 1e-9
    ) -> tuple[tuple[float, float, float], float]:
        """Extract the rotation axis and angle from this unit quaternion.

        Given ``q = w + x·i + y·j + z·k`` with ``|q| = 1``, the physical
        rotation angle is::

            θ = 2·arccos(w)

        and the rotation axis is::

            û = (x, y, z) / sin(θ/2)     if sin(θ/2) > atol

        For rotations close to the identity (``θ ≈ 0``) the axis is
        undefined; the x-axis is returned as a conventional default.

        The quaternion is normalized internally before extraction.

        Args:
            atol: Threshold below which ``sin(θ/2)`` is considered zero
                (default ``1e-9``).

        Returns:
            2-tuple ``(axis, angle)`` where *axis* is a unit 3-tuple
            ``(ux, uy, uz)`` and *angle* is in radians ``[0, 2π)``.
        """
        q = self.normalize()
        # Clamp w to [-1, 1] to guard against tiny floating-point errors.
        w_clamped = max(-1.0, min(1.0, q.w))
        half_angle = math.acos(w_clamped)
        angle = 2.0 * half_angle
        s = math.sin(half_angle)
        if s > atol:
            axis: tuple[float, float, float] = (q.x / s, q.y / s, q.z / s)
        else:
            # Identity or 2π rotation – axis is arbitrary; use x by convention.
            axis = (1.0, 0.0, 0.0)
        return axis, angle

    def rotate_vector(
        self, v: Sequence[float]
    ) -> tuple[float, float, float]:
        """Rotate a 3-D vector by this quaternion via the sandwich product.

        Implements::

            p' = q · p · q⁻¹

        where ``p = 0 + vx·i + vy·j + vz·k`` is the pure-quaternion
        representation of *v*.  For a unit quaternion ``q⁻¹ = q*``
        (the conjugate).

        This is the standard way to rotate a Bloch vector or any 3-D vector
        by the rotation encoded in *q*.

        Args:
            v: A 3-element sequence ``(vx, vy, vz)``.

        Returns:
            Rotated vector as a 3-tuple ``(vx', vy', vz')``.

        Raises:
            ValueError: If *v* does not have exactly 3 elements.
        """
        vec = list(v)
        if len(vec) != 3:
            raise ValueError(
                f"v must be a 3-element sequence; got length {len(vec)}"
            )
        vx, vy, vz = float(vec[0]), float(vec[1]), float(vec[2])
        p = Quaternion(0.0, vx, vy, vz)
        q = self.normalize()
        rotated = q * p * q.conjugate()
        return (rotated.x, rotated.y, rotated.z)

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def scalar_part(self) -> float:
        """Return the scalar (real) part ``w``.

        Returns:
            Scalar component of the quaternion.
        """
        return self.w

    def vector_part(self) -> tuple[float, float, float]:
        """Return the vector (pure imaginary) part ``(x, y, z)``.

        Returns:
            3-tuple ``(x, y, z)`` of the pure-imaginary components.
        """
        return (self.x, self.y, self.z)

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
