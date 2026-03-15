"""Tests for rqm_core.bloch."""

import math

import numpy as np
import pytest

from rqm_core.bloch import state_to_bloch, bloch_to_state, bloch_from_quaternion
from rqm_core.quaternion import Quaternion


# ---------------------------------------------------------------------------
# state_to_bloch – canonical states
# ---------------------------------------------------------------------------


def test_bloch_zero_state():
    """``|0⟩ = (1, 0)`` should map to north pole (0, 0, 1)."""
    v = state_to_bloch(1.0, 0.0)
    assert np.allclose(v, [0.0, 0.0, 1.0], atol=1e-9)


def test_bloch_one_state():
    """``|1⟩ = (0, 1)`` should map to south pole (0, 0, -1)."""
    v = state_to_bloch(0.0, 1.0)
    assert np.allclose(v, [0.0, 0.0, -1.0], atol=1e-9)


def test_bloch_plus_state():
    """``|+⟩ = (1, 1)/√2`` should map to (1, 0, 0)."""
    c = 1.0 / math.sqrt(2.0)
    v = state_to_bloch(c, c)
    assert np.allclose(v, [1.0, 0.0, 0.0], atol=1e-9)


def test_bloch_minus_state():
    """``|-⟩ = (1, -1)/√2`` should map to (-1, 0, 0)."""
    c = 1.0 / math.sqrt(2.0)
    v = state_to_bloch(c, -c)
    assert np.allclose(v, [-1.0, 0.0, 0.0], atol=1e-9)


def test_bloch_y_plus():
    """``|i+⟩ = (1, i)/√2`` should map to (0, 1, 0)."""
    c = 1.0 / math.sqrt(2.0)
    v = state_to_bloch(c, 1j * c)
    assert np.allclose(v, [0.0, 1.0, 0.0], atol=1e-9)


def test_bloch_vector_unit_length():
    """Bloch vector from a normalized state must lie on the unit sphere."""
    v = state_to_bloch(0.6, 0.8)
    assert abs(np.linalg.norm(v) - 1.0) == pytest.approx(0.0, abs=1e-9)


def test_bloch_zero_state_raises():
    with pytest.raises(ValueError, match="non-zero"):
        state_to_bloch(0.0, 0.0)


# ---------------------------------------------------------------------------
# bloch_to_state
# ---------------------------------------------------------------------------


def test_bloch_to_state_north_pole():
    """θ=0 → |0⟩."""
    psi = bloch_to_state(0.0, 0.0)
    assert abs(psi[0]) == pytest.approx(1.0)
    assert abs(psi[1]) == pytest.approx(0.0, abs=1e-9)


def test_bloch_to_state_south_pole():
    """θ=π → |1⟩ (up to global phase)."""
    psi = bloch_to_state(math.pi, 0.0)
    assert abs(psi[0]) == pytest.approx(0.0, abs=1e-9)
    assert abs(psi[1]) == pytest.approx(1.0)


def test_bloch_to_state_x_axis():
    """θ=π/2, φ=0 → |+⟩."""
    psi = bloch_to_state(math.pi / 2, 0.0)
    c = 1.0 / math.sqrt(2.0)
    assert abs(psi[0]) == pytest.approx(c)
    assert abs(psi[1]) == pytest.approx(c)


def test_bloch_to_state_roundtrip():
    """state_to_bloch(bloch_to_state(θ, φ)) should give back (sin θ cos φ, sin θ sin φ, cos θ)."""
    theta, phi = 1.1, 0.7
    psi = bloch_to_state(theta, phi)
    v = state_to_bloch(complex(psi[0]), complex(psi[1]))
    expected = np.array([
        math.sin(theta) * math.cos(phi),
        math.sin(theta) * math.sin(phi),
        math.cos(theta),
    ])
    assert np.allclose(v, expected, atol=1e-9)


# ---------------------------------------------------------------------------
# bloch_from_quaternion
# ---------------------------------------------------------------------------


def test_bloch_from_identity_quaternion():
    """Identity rotation leaves |0⟩ at north pole."""
    v = bloch_from_quaternion(Quaternion.identity())
    assert np.allclose(v, [0.0, 0.0, 1.0], atol=1e-9)


def test_bloch_from_quaternion_x_rotation_pi():
    """180° rotation around x maps north pole to south pole."""
    q = Quaternion.from_axis_angle("x", math.pi)
    v = bloch_from_quaternion(q)
    assert np.allclose(v, [0.0, 0.0, -1.0], atol=1e-9)

# ---------------------------------------------------------------------------
# bloch_radius
# ---------------------------------------------------------------------------


def test_bloch_radius_unit():
    from rqm_core.bloch import bloch_radius
    assert bloch_radius(0.0, 0.0, 1.0) == pytest.approx(1.0)
    assert bloch_radius(1.0, 0.0, 0.0) == pytest.approx(1.0)


def test_bloch_radius_general():
    import math
    from rqm_core.bloch import bloch_radius
    x, y, z = state_to_bloch(0.6, 0.8)
    assert bloch_radius(x, y, z) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# validate_bloch_vector
# ---------------------------------------------------------------------------


def test_validate_bloch_vector_valid():
    from rqm_core.bloch import validate_bloch_vector
    validate_bloch_vector(0.0, 0.0, 1.0)  # no exception


def test_validate_bloch_vector_not_unit():
    from rqm_core.bloch import validate_bloch_vector
    with pytest.raises(ValueError, match="unit sphere"):
        validate_bloch_vector(0.0, 0.0, 2.0)


def test_validate_bloch_vector_non_finite():
    import math
    from rqm_core.bloch import validate_bloch_vector
    with pytest.raises(ValueError, match="finite"):
        validate_bloch_vector(float("inf"), 0.0, 0.0)
