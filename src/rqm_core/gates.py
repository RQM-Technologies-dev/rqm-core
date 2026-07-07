"""Named single-qubit gate quaternions and gate recognition.

Every single-qubit SU(2) gate is exactly representable as a unit quaternion::

    q = cos(θ/2) + u·sin(θ/2)

where ``u = ux·i + uy·j + uz·k`` is the unit rotation axis and ``θ`` is
the physical Bloch-sphere rotation angle.  The compiler-native quaternion form
is the half-angle spinor representative on S³.

Axis–Pauli correspondence (fixed convention, used everywhere in rqm-core):

    i  ↔  X rotation direction  (Pauli-X axis)
    j  ↔  Y rotation direction  (Pauli-Y axis)
    k  ↔  Z rotation direction  (Pauli-Z axis)

All gate quaternions below follow this convention and the half-angle formula.
"""

from __future__ import annotations

import math

from rqm_core.quaternion import Quaternion

# ---------------------------------------------------------------------------
# Rotation-gate factories
# ---------------------------------------------------------------------------


def gate_rx(theta: float) -> Quaternion:
    """Return the unit quaternion for ``Rx(θ)`` – rotation about the x-axis.

    ::

        Rx(θ) ↔ q = cos(θ/2) + i·sin(θ/2)

    Args:
        theta: Rotation angle in radians.

    Returns:
        Unit quaternion representing ``Rx(θ)``.
    """
    return Quaternion.from_axis_angle("x", theta)


def gate_ry(theta: float) -> Quaternion:
    """Return the unit quaternion for ``Ry(θ)`` – rotation about the y-axis.

    ::

        Ry(θ) ↔ q = cos(θ/2) + j·sin(θ/2)

    Args:
        theta: Rotation angle in radians.

    Returns:
        Unit quaternion representing ``Ry(θ)``.
    """
    return Quaternion.from_axis_angle("y", theta)


def gate_rz(theta: float) -> Quaternion:
    """Return the unit quaternion for ``Rz(θ)`` – rotation about the z-axis.

    ::

        Rz(θ) ↔ q = cos(θ/2) + k·sin(θ/2)

    Args:
        theta: Rotation angle in radians.

    Returns:
        Unit quaternion representing ``Rz(θ)``.
    """
    return Quaternion.from_axis_angle("z", theta)


# ---------------------------------------------------------------------------
# Named standard gates
# ---------------------------------------------------------------------------


def gate_identity() -> Quaternion:
    """Return the quaternion for the identity gate ``I``.

    ::

        I ↔ q = 1   (no rotation)

    Returns:
        Identity quaternion ``(1, 0, 0, 0)``.
    """
    return Quaternion.identity()


def gate_x() -> Quaternion:
    """Return the quaternion for the Pauli-X gate.

    X is a π-rotation about the x-axis::

        X ↔ q = cos(π/2) + i·sin(π/2) = i   (up to global phase)

    Returns:
        Unit quaternion ``(0, 1, 0, 0)``.
    """
    return gate_rx(math.pi)


def gate_y() -> Quaternion:
    """Return the quaternion for the Pauli-Y gate.

    Y is a π-rotation about the y-axis::

        Y ↔ q = cos(π/2) + j·sin(π/2) = j   (up to global phase)

    Returns:
        Unit quaternion ``(0, 0, 1, 0)``.
    """
    return gate_ry(math.pi)


def gate_z() -> Quaternion:
    """Return the quaternion for the Pauli-Z gate.

    Z is a π-rotation about the z-axis::

        Z ↔ q = cos(π/2) + k·sin(π/2) = k   (up to global phase)

    Returns:
        Unit quaternion ``(0, 0, 0, 1)``.
    """
    return gate_rz(math.pi)


def gate_s() -> Quaternion:
    """Return the quaternion for the S gate (phase gate, ``√Z``).

    S is equivalent to ``Rz(π/2)`` up to global phase::

        S ↔ q = cos(π/4) + k·sin(π/4)

    Returns:
        Unit quaternion for the S gate.
    """
    return gate_rz(math.pi / 2.0)


def gate_t() -> Quaternion:
    """Return the quaternion for the T gate (``π/8`` gate, ``√S``).

    T is equivalent to ``Rz(π/4)`` up to global phase::

        T ↔ q = cos(π/8) + k·sin(π/8)

    Returns:
        Unit quaternion for the T gate.
    """
    return gate_rz(math.pi / 4.0)


def gate_h() -> Quaternion:
    """Return the quaternion for the Hadamard gate.

    H is a π-rotation about the diagonal axis ``(x + z)/√2``::

        H ↔ q = (i + k) / √2   (up to global phase)

    This axis-angle representation makes explicit that Hadamard is a
    geometric rotation, not merely a matrix with mixed entries.

    Returns:
        Unit quaternion for the Hadamard gate.
    """
    s = 1.0 / math.sqrt(2.0)
    return Quaternion.from_axis_angle_vec((s, 0.0, s), math.pi)


# ---------------------------------------------------------------------------
# Gate recognition
# ---------------------------------------------------------------------------

# Table of named gates and their canonical quaternions (w ≥ 0 representative).
# We match both q and -q because they represent the same SO(3)/Bloch rotation;
# their SU(2) matrices differ by a global phase.
_NAMED_GATES: list[tuple[str, Quaternion]] = [
    ("I", gate_identity()),
    ("X", gate_x()),
    ("Y", gate_y()),
    ("Z", gate_z()),
    ("H", gate_h()),
    ("S", gate_s()),
    ("T", gate_t()),
]


def match_gate(q: Quaternion, *, atol: float = 1e-6) -> str | None:
    """Return the name of the standard gate that *q* represents, or ``None``.

    Both ``q`` and ``-q`` encode the same physical SO(3)/Bloch rotation; this
    function checks closeness to both spinor representatives of each named
    gate.  Their SU(2) matrices differ by a global phase.

    Named gates checked (in order): ``"I"``, ``"X"``, ``"Y"``, ``"Z"``,
    ``"H"``, ``"S"``, ``"T"``.

    Args:
        q:    Quaternion to match (need not be normalized).
        atol: Component-wise absolute tolerance (default ``1e-6``).

    Returns:
        Gate name string such as ``"X"`` or ``"H"``, or ``None`` if the
        quaternion does not match any standard gate within *atol*.
    """
    qn = q.normalize()
    for name, ref in _NAMED_GATES:
        ref_n = ref.normalize()
        neg_ref = Quaternion(-ref_n.w, -ref_n.x, -ref_n.y, -ref_n.z)
        if qn.is_close(ref_n, atol=atol) or qn.is_close(neg_ref, atol=atol):
            return name
    return None
