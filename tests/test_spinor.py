"""Tests for rqm_core.spinor."""

import math

import numpy as np
import pytest

from rqm_core.spinor import (
    normalize_spinor,
    spinor_norm,
    is_normalized_spinor,
    spinor_to_quaternion,
    spinor_to_su2,
    state_fidelity,
)


# ---------------------------------------------------------------------------
# normalize_spinor
# ---------------------------------------------------------------------------


def test_normalize_spinor_unit_norm():
    psi = normalize_spinor(3.0, 4.0)
    assert abs(np.linalg.norm(psi) - 1.0) == pytest.approx(0.0, abs=1e-9)


def test_normalize_spinor_zero_state():
    psi = normalize_spinor(1.0, 0.0)
    assert abs(psi[0]) == pytest.approx(1.0)
    assert abs(psi[1]) == pytest.approx(0.0, abs=1e-9)


def test_normalize_spinor_complex():
    psi = normalize_spinor(1j, 1.0)
    assert abs(np.linalg.norm(psi) - 1.0) == pytest.approx(0.0, abs=1e-9)


def test_normalize_spinor_zero_raises():
    with pytest.raises(ValueError, match="non-zero"):
        normalize_spinor(0.0, 0.0)


# ---------------------------------------------------------------------------
# spinor_to_quaternion
# ---------------------------------------------------------------------------


def test_spinor_to_quaternion_zero_state():
    """Spinor |0⟩ should map to the identity quaternion."""
    q = spinor_to_quaternion(1.0, 0.0)
    assert q.is_unit()
    assert q.w == pytest.approx(1.0, abs=1e-9)


def test_spinor_to_quaternion_unit():
    q = spinor_to_quaternion(0.6, 0.8)
    assert q.is_unit()


# ---------------------------------------------------------------------------
# spinor_to_su2
# ---------------------------------------------------------------------------


def test_spinor_to_su2_unitary():
    from rqm_core.su2 import is_unitary
    m = spinor_to_su2(1.0 / math.sqrt(2), 1.0 / math.sqrt(2))
    assert is_unitary(m)


def test_spinor_to_su2_det_one():
    from rqm_core.su2 import determinant_close_to_one
    m = spinor_to_su2(0.6, 0.8)
    assert determinant_close_to_one(m)


# ---------------------------------------------------------------------------
# state_fidelity
# ---------------------------------------------------------------------------


def test_fidelity_same_state():
    psi = np.array([1.0, 0.0], dtype=np.complex128)
    assert state_fidelity(psi, psi) == pytest.approx(1.0)


def test_fidelity_orthogonal_states():
    psi0 = np.array([1.0, 0.0], dtype=np.complex128)
    psi1 = np.array([0.0, 1.0], dtype=np.complex128)
    assert state_fidelity(psi0, psi1) == pytest.approx(0.0, abs=1e-9)


def test_fidelity_symmetry():
    a = np.array([0.6, 0.8], dtype=np.complex128)
    b = np.array([1j / math.sqrt(2), 1.0 / math.sqrt(2)], dtype=np.complex128)
    assert state_fidelity(a, b) == pytest.approx(state_fidelity(b, a))


def test_fidelity_range():
    a = np.array([0.6, 0.8], dtype=np.complex128)
    b = np.array([0.8, 0.6], dtype=np.complex128)
    f = state_fidelity(a, b)
    assert 0.0 <= f <= 1.0


def test_fidelity_unnormalized_inputs():
    """Fidelity must work for unnormalized inputs."""
    a = np.array([2.0, 0.0], dtype=np.complex128)   # points in |0⟩ direction
    b = np.array([0.0, 3.0], dtype=np.complex128)   # points in |1⟩ direction
    assert state_fidelity(a, b) == pytest.approx(0.0, abs=1e-9)


def test_fidelity_zero_state_raises():
    zero = np.array([0.0, 0.0], dtype=np.complex128)
    psi = np.array([1.0, 0.0], dtype=np.complex128)
    with pytest.raises(ValueError, match="non-zero"):
        state_fidelity(zero, psi)


# ---------------------------------------------------------------------------
# spinor_norm
# ---------------------------------------------------------------------------


def test_spinor_norm_real():
    assert spinor_norm(3.0, 4.0) == pytest.approx(5.0)


def test_spinor_norm_zero():
    assert spinor_norm(0.0, 0.0) == pytest.approx(0.0, abs=1e-9)


def test_spinor_norm_unit():
    assert spinor_norm(1.0, 0.0) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# is_normalized_spinor
# ---------------------------------------------------------------------------


def test_is_normalized_true():
    assert is_normalized_spinor(1.0, 0.0)


def test_is_normalized_false():
    assert not is_normalized_spinor(3.0, 4.0)


def test_is_normalized_complex():
    import math
    c = 1.0 / math.sqrt(2)
    assert is_normalized_spinor(c, 1j * c)


# ---------------------------------------------------------------------------
# spinor_embed
# ---------------------------------------------------------------------------


def test_spinor_embed_zero_state_maps_to_identity():
    """Direct embedding of |0⟩ = (1, 0) should give q = 1 + 0i + 0j + 0k."""
    from rqm_core.spinor import spinor_embed
    q = spinor_embed(1.0, 0.0)
    assert q.is_unit()
    assert q.w == pytest.approx(1.0)
    assert q.x == pytest.approx(0.0, abs=1e-9)
    assert q.y == pytest.approx(0.0, abs=1e-9)
    assert q.z == pytest.approx(0.0, abs=1e-9)


def test_spinor_embed_one_state():
    """Direct embedding of |1⟩ = (0, 1) should give q = 0 + 0i + 1j + 0k."""
    from rqm_core.spinor import spinor_embed
    q = spinor_embed(0.0, 1.0)
    assert q.is_unit()
    assert q.w == pytest.approx(0.0, abs=1e-9)
    assert q.y == pytest.approx(1.0)


def test_spinor_embed_component_mapping():
    """q_ψ = a0 + a1·i + b0·j + b1·k for α = a0 + a1·i, β = b0 + b1·i."""
    from rqm_core.spinor import spinor_embed
    import math
    c = 1.0 / math.sqrt(2.0)
    # α = c (pure real), β = c·i (pure imaginary)
    q = spinor_embed(c, 1j * c)
    assert q.is_unit()
    # a0 = c, a1 = 0, b0 = 0, b1 = c
    assert q.w == pytest.approx(c)
    assert q.x == pytest.approx(0.0, abs=1e-9)
    assert q.y == pytest.approx(0.0, abs=1e-9)
    assert q.z == pytest.approx(c)


def test_spinor_embed_is_unit():
    from rqm_core.spinor import spinor_embed
    q = spinor_embed(0.6, 0.8)
    assert q.is_unit()


def test_spinor_embed_unnormalized_input_normalizes():
    from rqm_core.spinor import spinor_embed
    q = spinor_embed(3.0, 4.0)
    assert q.is_unit()
    # After normalization: α = 3/5, β = 4/5 (both real)
    assert q.w == pytest.approx(0.6)
    assert q.y == pytest.approx(0.8)


def test_spinor_embed_zero_raises():
    from rqm_core.spinor import spinor_embed
    with pytest.raises(ValueError):
        spinor_embed(0.0, 0.0)
