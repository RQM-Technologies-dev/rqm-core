"""Tests for rqm_core.gates – named gate quaternions and gate recognition."""

import math

import numpy as np
import pytest

from rqm_core.gates import (
    gate_identity,
    gate_x,
    gate_y,
    gate_z,
    gate_h,
    gate_s,
    gate_t,
    gate_rx,
    gate_ry,
    gate_rz,
    match_gate,
)
from rqm_core.quaternion import Quaternion
from rqm_core.su2 import is_unitary, determinant_close_to_one, quaternion_to_su2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _su2_matrices_close(q1: Quaternion, q2: Quaternion, *, atol: float = 1e-9) -> bool:
    """Return True if the two quaternions yield the same SU(2) matrix (up to ±sign)."""
    m1 = quaternion_to_su2(q1)
    m2 = quaternion_to_su2(q2)
    return np.allclose(m1, m2, atol=atol) or np.allclose(m1, -m2, atol=atol)


# ---------------------------------------------------------------------------
# gate_identity
# ---------------------------------------------------------------------------


def test_gate_identity_is_unit():
    assert gate_identity().is_unit()


def test_gate_identity_is_quaternion_one():
    q = gate_identity()
    assert q.w == pytest.approx(1.0)
    assert q.x == pytest.approx(0.0, abs=1e-9)
    assert q.y == pytest.approx(0.0, abs=1e-9)
    assert q.z == pytest.approx(0.0, abs=1e-9)


def test_gate_identity_su2_is_identity_matrix():
    m = quaternion_to_su2(gate_identity())
    assert np.allclose(m, np.eye(2, dtype=np.complex128))


# ---------------------------------------------------------------------------
# Pauli gates – unit norm
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("gate_fn", [gate_x, gate_y, gate_z])
def test_pauli_gate_is_unit(gate_fn):
    assert gate_fn().is_unit()


@pytest.mark.parametrize("gate_fn", [gate_x, gate_y, gate_z])
def test_pauli_gate_su2_is_unitary(gate_fn):
    m = quaternion_to_su2(gate_fn())
    assert is_unitary(m)


@pytest.mark.parametrize("gate_fn", [gate_x, gate_y, gate_z])
def test_pauli_gate_su2_det_one(gate_fn):
    m = quaternion_to_su2(gate_fn())
    assert determinant_close_to_one(m)


# ---------------------------------------------------------------------------
# Pauli X, Y, Z – axis alignment (π rotation about respective axis)
# ---------------------------------------------------------------------------


def test_gate_x_axis_and_angle():
    q = gate_x()
    # X is Rx(π): w = cos(π/2) = 0, x = sin(π/2) = 1
    assert q.w == pytest.approx(0.0, abs=1e-9)
    assert q.x == pytest.approx(1.0)
    assert q.y == pytest.approx(0.0, abs=1e-9)
    assert q.z == pytest.approx(0.0, abs=1e-9)


def test_gate_y_axis_and_angle():
    q = gate_y()
    assert q.w == pytest.approx(0.0, abs=1e-9)
    assert q.x == pytest.approx(0.0, abs=1e-9)
    assert q.y == pytest.approx(1.0)
    assert q.z == pytest.approx(0.0, abs=1e-9)


def test_gate_z_axis_and_angle():
    q = gate_z()
    assert q.w == pytest.approx(0.0, abs=1e-9)
    assert q.x == pytest.approx(0.0, abs=1e-9)
    assert q.y == pytest.approx(0.0, abs=1e-9)
    assert q.z == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Pauli X – action on Bloch sphere (|0⟩ → |1⟩)
# ---------------------------------------------------------------------------


def test_gate_x_flips_z_axis():
    """X is a π-rotation about x; maps north pole (0,0,1) → south pole (0,0,-1)."""
    v = gate_x().rotate_vector((0.0, 0.0, 1.0))
    assert v[2] == pytest.approx(-1.0, abs=1e-9)


def test_gate_z_flips_x_axis():
    """Z is a π-rotation about z; maps (1,0,0) → (-1,0,0)."""
    v = gate_z().rotate_vector((1.0, 0.0, 0.0))
    assert v[0] == pytest.approx(-1.0, abs=1e-9)


# ---------------------------------------------------------------------------
# gate_h – Hadamard
# ---------------------------------------------------------------------------


def test_gate_h_is_unit():
    assert gate_h().is_unit()


def test_gate_h_su2_is_unitary():
    assert is_unitary(quaternion_to_su2(gate_h()))


def test_gate_h_su2_det_one():
    assert determinant_close_to_one(quaternion_to_su2(gate_h()))


def test_gate_h_scalar_part_zero():
    """H = π-rotation: w = cos(π/2) = 0."""
    assert gate_h().w == pytest.approx(0.0, abs=1e-9)


def test_gate_h_maps_north_to_equator_x():
    """H maps |0⟩ (north pole) to |+⟩ (equator, x-axis)."""
    v = gate_h().rotate_vector((0.0, 0.0, 1.0))
    # H swaps X and Z axes
    assert v[0] == pytest.approx(1.0, abs=1e-9)
    assert v[2] == pytest.approx(0.0, abs=1e-9)


def test_gate_h_is_self_inverse():
    """H² = I (Hadamard is its own inverse)."""
    q = gate_h() * gate_h()
    assert q.is_close(Quaternion.identity(), atol=1e-9) or q.is_close(
        Quaternion(-1.0, 0.0, 0.0, 0.0), atol=1e-9
    )


# ---------------------------------------------------------------------------
# gate_s and gate_t
# ---------------------------------------------------------------------------


def test_gate_s_is_unit():
    assert gate_s().is_unit()


def test_gate_t_is_unit():
    assert gate_t().is_unit()


def test_gate_s_components():
    """S = Rz(π/2): w = cos(π/4), z = sin(π/4)."""
    q = gate_s()
    assert q.w == pytest.approx(math.cos(math.pi / 4.0))
    assert q.z == pytest.approx(math.sin(math.pi / 4.0))


def test_gate_t_components():
    """T = Rz(π/4): w = cos(π/8), z = sin(π/8)."""
    q = gate_t()
    assert q.w == pytest.approx(math.cos(math.pi / 8.0))
    assert q.z == pytest.approx(math.sin(math.pi / 8.0))


def test_gate_s_squared_is_gate_z():
    """S² = Z (Rz(π/2) * Rz(π/2) = Rz(π))."""
    q = gate_s() * gate_s()
    assert _su2_matrices_close(q, gate_z())


def test_gate_t_squared_is_gate_s():
    """T² = S (Rz(π/4) * Rz(π/4) = Rz(π/2))."""
    q = gate_t() * gate_t()
    assert _su2_matrices_close(q, gate_s())


# ---------------------------------------------------------------------------
# gate_rx, gate_ry, gate_rz – rotation factories
# ---------------------------------------------------------------------------


def test_gate_rx_zero_is_identity():
    assert gate_rx(0.0) == Quaternion.identity()


def test_gate_ry_zero_is_identity():
    assert gate_ry(0.0) == Quaternion.identity()


def test_gate_rz_zero_is_identity():
    assert gate_rz(0.0) == Quaternion.identity()


def test_gate_rx_pi_matches_gate_x():
    assert _su2_matrices_close(gate_rx(math.pi), gate_x())


def test_gate_ry_pi_matches_gate_y():
    assert _su2_matrices_close(gate_ry(math.pi), gate_y())


def test_gate_rz_pi_matches_gate_z():
    assert _su2_matrices_close(gate_rz(math.pi), gate_z())


def test_gate_rx_formula():
    theta = 1.3
    q = gate_rx(theta)
    assert q.w == pytest.approx(math.cos(theta / 2.0))
    assert q.x == pytest.approx(math.sin(theta / 2.0))


def test_gate_ry_formula():
    theta = 0.7
    q = gate_ry(theta)
    assert q.w == pytest.approx(math.cos(theta / 2.0))
    assert q.y == pytest.approx(math.sin(theta / 2.0))


def test_gate_rz_formula():
    theta = 2.5
    q = gate_rz(theta)
    assert q.w == pytest.approx(math.cos(theta / 2.0))
    assert q.z == pytest.approx(math.sin(theta / 2.0))


def test_gate_rx_is_unit():
    assert gate_rx(1.1).is_unit()


def test_gate_ry_is_unit():
    assert gate_ry(1.1).is_unit()


def test_gate_rz_is_unit():
    assert gate_rz(1.1).is_unit()


# ---------------------------------------------------------------------------
# Gate composition via quaternion multiplication
# ---------------------------------------------------------------------------


def test_rx_composition_adds_angles():
    """Rx(a) * Rx(b) = Rx(a + b) (same-axis fusion)."""
    a, b = 0.4, 0.9
    product = gate_rx(b) * gate_rx(a)
    expected = gate_rx(a + b)
    assert _su2_matrices_close(product, expected)


def test_rz_composition_adds_angles():
    a, b = 0.3, 1.1
    product = gate_rz(b) * gate_rz(a)
    expected = gate_rz(a + b)
    assert _su2_matrices_close(product, expected)


def test_gate_x_self_inverse():
    """X * X = I."""
    product = gate_x() * gate_x()
    assert _su2_matrices_close(product, gate_identity())


def test_gate_y_self_inverse():
    product = gate_y() * gate_y()
    assert _su2_matrices_close(product, gate_identity())


def test_gate_z_self_inverse():
    product = gate_z() * gate_z()
    assert _su2_matrices_close(product, gate_identity())


# ---------------------------------------------------------------------------
# match_gate
# ---------------------------------------------------------------------------


def test_match_gate_identity():
    assert match_gate(gate_identity()) == "I"


def test_match_gate_x():
    assert match_gate(gate_x()) == "X"


def test_match_gate_y():
    assert match_gate(gate_y()) == "Y"


def test_match_gate_z():
    assert match_gate(gate_z()) == "Z"


def test_match_gate_h():
    assert match_gate(gate_h()) == "H"


def test_match_gate_s():
    assert match_gate(gate_s()) == "S"


def test_match_gate_t():
    assert match_gate(gate_t()) == "T"


def test_match_gate_negative_representative():
    """match_gate should recognize -q as the same gate as q."""
    q = gate_x()
    neg_q = Quaternion(-q.w, -q.x, -q.y, -q.z)
    assert match_gate(neg_q) == "X"


def test_match_gate_unrecognized_returns_none():
    q = gate_rx(0.123)  # non-standard angle
    assert match_gate(q) is None


def test_match_gate_unnormalized_input():
    """match_gate must work even if the quaternion is not pre-normalized."""
    q = gate_z()
    scaled = Quaternion(2.0 * q.w, 2.0 * q.x, 2.0 * q.y, 2.0 * q.z)
    assert match_gate(scaled) == "Z"
