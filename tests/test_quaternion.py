"""Tests for rqm_core.quaternion."""

import math

import numpy as np
import pytest

from rqm_core.quaternion import Quaternion


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------


def test_identity_components():
    q = Quaternion.identity()
    assert q.w == 1.0
    assert q.x == 0.0
    assert q.y == 0.0
    assert q.z == 0.0


def test_identity_multiplication_left():
    q = Quaternion(0.5, 0.5, 0.5, 0.5)
    result = Quaternion.identity() * q
    assert result == q


def test_identity_multiplication_right():
    q = Quaternion(0.5, 0.5, 0.5, 0.5)
    result = q * Quaternion.identity()
    assert result == q


# ---------------------------------------------------------------------------
# Norm
# ---------------------------------------------------------------------------


def test_norm_identity():
    assert abs(Quaternion.identity()) == pytest.approx(1.0)


def test_norm_general():
    q = Quaternion(1.0, 2.0, 3.0, 4.0)
    expected = math.sqrt(1 + 4 + 9 + 16)
    assert q.norm() == pytest.approx(expected)


def test_abs_matches_norm():
    q = Quaternion(1.0, 1.0, 1.0, 1.0)
    assert abs(q) == pytest.approx(q.norm())


def test_normalize_produces_unit():
    q = Quaternion(1.0, 2.0, 3.0, 4.0).normalize()
    assert q.is_unit()


def test_normalize_zero_raises():
    with pytest.raises(ValueError, match="zero"):
        Quaternion(0.0, 0.0, 0.0, 0.0).normalize()


# ---------------------------------------------------------------------------
# Axis-angle construction
# ---------------------------------------------------------------------------


def test_from_axis_angle_x_unit():
    q = Quaternion.from_axis_angle("x", 0.0)
    assert q == Quaternion.identity()


def test_from_axis_angle_x_pi():
    q = Quaternion.from_axis_angle("x", math.pi)
    assert q.is_unit()
    assert q.w == pytest.approx(0.0, abs=1e-9)
    assert q.x == pytest.approx(1.0)


def test_from_axis_angle_y_pi():
    q = Quaternion.from_axis_angle("y", math.pi)
    assert q.is_unit()
    assert q.y == pytest.approx(1.0)


def test_from_axis_angle_z_pi():
    q = Quaternion.from_axis_angle("z", math.pi)
    assert q.is_unit()
    assert q.z == pytest.approx(1.0)


def test_from_axis_angle_formula():
    angle = 1.2
    q = Quaternion.from_axis_angle("z", angle)
    assert q.w == pytest.approx(math.cos(angle / 2))
    assert q.z == pytest.approx(math.sin(angle / 2))


def test_from_axis_angle_invalid():
    with pytest.raises(ValueError, match="axis"):
        Quaternion.from_axis_angle("w", 1.0)


# ---------------------------------------------------------------------------
# Inverse
# ---------------------------------------------------------------------------


def test_inverse_correctness():
    q = Quaternion.from_axis_angle("y", 0.8)
    q_inv = q.inverse()
    product = q * q_inv
    assert product == Quaternion.identity()


def test_inverse_of_unit_equals_conjugate():
    q = Quaternion.from_axis_angle("z", 1.1)
    assert q.inverse() == q.conjugate()


def test_inverse_zero_raises():
    with pytest.raises(ValueError, match="zero"):
        Quaternion(0.0, 0.0, 0.0, 0.0).inverse()


# ---------------------------------------------------------------------------
# Conjugate
# ---------------------------------------------------------------------------


def test_conjugate_negate_vector_part():
    q = Quaternion(1.0, 2.0, 3.0, 4.0)
    c = q.conjugate()
    assert c.w == pytest.approx(1.0)
    assert c.x == pytest.approx(-2.0)
    assert c.y == pytest.approx(-3.0)
    assert c.z == pytest.approx(-4.0)


def test_conjugate_of_identity():
    assert Quaternion.identity().conjugate() == Quaternion.identity()


def test_conjugate_times_self_is_norm_squared():
    """q * q.conjugate() should be purely scalar with value |q|²."""
    q = Quaternion(1.0, 2.0, 3.0, 4.0)
    product = q * q.conjugate()
    expected_w = q.norm() ** 2
    assert product.w == pytest.approx(expected_w)
    assert product.x == pytest.approx(0.0, abs=1e-9)
    assert product.y == pytest.approx(0.0, abs=1e-9)
    assert product.z == pytest.approx(0.0, abs=1e-9)


# ---------------------------------------------------------------------------
# is_close
# ---------------------------------------------------------------------------


def test_is_close_identical():
    q = Quaternion(1.0, 2.0, 3.0, 4.0)
    assert q.is_close(q)


def test_is_close_within_default_atol():
    q1 = Quaternion(1.0, 0.0, 0.0, 0.0)
    q2 = Quaternion(1.0 + 1e-10, 0.0, 0.0, 0.0)
    assert q1.is_close(q2)


def test_is_close_outside_default_atol():
    q1 = Quaternion(1.0, 0.0, 0.0, 0.0)
    q2 = Quaternion(1.1, 0.0, 0.0, 0.0)
    assert not q1.is_close(q2)


def test_is_close_custom_atol():
    q1 = Quaternion(1.0, 0.0, 0.0, 0.0)
    q2 = Quaternion(1.05, 0.0, 0.0, 0.0)
    assert q1.is_close(q2, atol=0.1)
    assert not q1.is_close(q2, atol=0.01)


# ---------------------------------------------------------------------------
# SU(2) matrix conversion
# ---------------------------------------------------------------------------


def test_to_su2_identity():
    m = Quaternion.identity().to_su2_matrix()
    assert np.allclose(m, np.eye(2, dtype=np.complex128))


def test_to_su2_shape():
    m = Quaternion.from_axis_angle("x", 0.5).to_su2_matrix()
    assert m.shape == (2, 2)


def test_to_su2_determinant_one():
    q = Quaternion.from_axis_angle("y", 1.3)
    m = q.to_su2_matrix()
    det = np.linalg.det(m)
    assert abs(det - 1.0) == pytest.approx(0.0, abs=1e-9)


def test_to_su2_unitarity():
    from rqm_core.su2 import is_unitary
    q = Quaternion.from_axis_angle("z", 0.9)
    m = q.to_su2_matrix()
    assert is_unitary(m)


# ---------------------------------------------------------------------------
# Rotation matrix
# ---------------------------------------------------------------------------


def test_to_rotation_matrix_identity():
    r = Quaternion.identity().to_rotation_matrix()
    assert np.allclose(r, np.eye(3))


def test_to_rotation_matrix_shape():
    r = Quaternion.from_axis_angle("x", 1.0).to_rotation_matrix()
    assert r.shape == (3, 3)


def test_to_rotation_matrix_orthogonal():
    q = Quaternion.from_axis_angle("y", 0.7)
    r = q.to_rotation_matrix()
    assert np.allclose(r @ r.T, np.eye(3), atol=1e-9)


# ---------------------------------------------------------------------------
# __repr__ and __eq__
# ---------------------------------------------------------------------------


def test_repr():
    q = Quaternion(1.0, 0.0, 0.0, 0.0)
    assert repr(q) == "Quaternion(1.0, 0.0, 0.0, 0.0)"


def test_eq_same():
    q = Quaternion(1.0, 2.0, 3.0, 4.0)
    assert q == Quaternion(1.0, 2.0, 3.0, 4.0)


def test_eq_different():
    assert Quaternion(1.0, 0.0, 0.0, 0.0) != Quaternion(0.0, 1.0, 0.0, 0.0)


def test_eq_not_quaternion():
    assert Quaternion(1.0, 0.0, 0.0, 0.0).__eq__("string") is NotImplemented


# ---------------------------------------------------------------------------
# scalar_part and vector_part
# ---------------------------------------------------------------------------


def test_scalar_part():
    q = Quaternion(1.0, 2.0, 3.0, 4.0)
    assert q.scalar_part() == 1.0


def test_vector_part():
    q = Quaternion(1.0, 2.0, 3.0, 4.0)
    assert q.vector_part() == (2.0, 3.0, 4.0)


def test_scalar_part_identity():
    q = Quaternion.identity()
    assert q.scalar_part() == 1.0


def test_vector_part_identity():
    q = Quaternion.identity()
    assert q.vector_part() == (0.0, 0.0, 0.0)


# ---------------------------------------------------------------------------
# from_axis_angle_vec
# ---------------------------------------------------------------------------


def test_from_axis_angle_vec_x_matches_from_axis_angle():
    q1 = Quaternion.from_axis_angle("x", 1.2)
    q2 = Quaternion.from_axis_angle_vec((1.0, 0.0, 0.0), 1.2)
    assert q1 == q2


def test_from_axis_angle_vec_y_matches_from_axis_angle():
    q1 = Quaternion.from_axis_angle("y", 0.8)
    q2 = Quaternion.from_axis_angle_vec((0.0, 1.0, 0.0), 0.8)
    assert q1 == q2


def test_from_axis_angle_vec_z_matches_from_axis_angle():
    q1 = Quaternion.from_axis_angle("z", 2.1)
    q2 = Quaternion.from_axis_angle_vec((0.0, 0.0, 1.0), 2.1)
    assert q1 == q2


def test_from_axis_angle_vec_unnormalized_axis():
    """Unnormalized axis should be normalized internally."""
    q = Quaternion.from_axis_angle_vec((3.0, 0.0, 0.0), math.pi)
    assert q.is_unit()
    assert q.w == pytest.approx(0.0, abs=1e-9)
    assert q.x == pytest.approx(1.0)


def test_from_axis_angle_vec_diagonal_axis():
    s = 1.0 / math.sqrt(2.0)
    q = Quaternion.from_axis_angle_vec((s, 0.0, s), math.pi)
    assert q.is_unit()
    # w = cos(π/2) = 0
    assert q.w == pytest.approx(0.0, abs=1e-9)
    # x and z should each be s·sin(π/2) = s
    assert q.x == pytest.approx(s)
    assert q.z == pytest.approx(s)


def test_from_axis_angle_vec_wrong_length():
    with pytest.raises(ValueError):
        Quaternion.from_axis_angle_vec((1.0, 0.0), 1.0)


def test_from_axis_angle_vec_zero_axis():
    with pytest.raises(ValueError, match="non-zero"):
        Quaternion.from_axis_angle_vec((0.0, 0.0, 0.0), 1.0)


# ---------------------------------------------------------------------------
# canonicalize
# ---------------------------------------------------------------------------


def test_canonicalize_positive_w_unchanged():
    q = Quaternion.from_axis_angle("z", 1.0)
    assert q.w > 0
    assert q.canonicalize().w >= 0.0


def test_canonicalize_negative_w_flipped():
    # Angle of 3π/2 → w = cos(3π/4) < 0
    q = Quaternion.from_axis_angle("z", 3.0 * math.pi / 2.0)
    assert q.w < 0
    c = q.canonicalize()
    assert c.w >= 0.0


def test_canonicalize_is_unit():
    q = Quaternion(0.5, 0.5, 0.5, 0.5)
    assert q.canonicalize().is_unit()


def test_canonicalize_same_rotation_matrix():
    """q and -q should give the same SO(3) rotation; canonicalize preserves that."""
    q = Quaternion.from_axis_angle("x", 3.5)
    c = q.canonicalize()
    r1 = q.normalize().to_rotation_matrix()
    r2 = c.to_rotation_matrix()
    assert np.allclose(r1, r2, atol=1e-9)


def test_sign_fold_preserves_so3_but_changes_controlled_su2_matrix():
    """EXP-001 regression: sign folding cannot be used after coherent control."""
    q_minus = Quaternion(-1.0, 0.0, 0.0, 0.0)
    q_plus = q_minus.canonicalize()
    assert np.allclose(q_minus.to_rotation_matrix(), q_plus.to_rotation_matrix(), atol=1e-12)
    assert np.allclose(q_minus.to_su2_matrix(), -q_plus.to_su2_matrix(), atol=1e-12)

    def controlled(matrix):
        out = np.zeros((4, 4), dtype=complex)
        out[:2, :2] = np.eye(2)
        out[2:, 2:] = matrix
        return out

    assert not np.allclose(
        controlled(q_minus.to_su2_matrix()),
        controlled(q_plus.to_su2_matrix()),
        atol=1e-12,
    )


# ---------------------------------------------------------------------------
# to_axis_angle
# ---------------------------------------------------------------------------


def test_to_axis_angle_x_rotation():
    theta = 1.3
    q = Quaternion.from_axis_angle("x", theta)
    axis, angle = q.to_axis_angle()
    assert angle == pytest.approx(theta)
    assert math.isclose(axis[0], 1.0, abs_tol=1e-9)
    assert math.isclose(axis[1], 0.0, abs_tol=1e-9)
    assert math.isclose(axis[2], 0.0, abs_tol=1e-9)


def test_to_axis_angle_y_rotation():
    theta = 0.9
    q = Quaternion.from_axis_angle("y", theta)
    axis, angle = q.to_axis_angle()
    assert angle == pytest.approx(theta)
    assert math.isclose(axis[1], 1.0, abs_tol=1e-9)


def test_to_axis_angle_z_rotation():
    theta = 2.2
    q = Quaternion.from_axis_angle("z", theta)
    axis, angle = q.to_axis_angle()
    assert angle == pytest.approx(theta)
    assert math.isclose(axis[2], 1.0, abs_tol=1e-9)


def test_to_axis_angle_identity_arbitrary_axis():
    q = Quaternion.identity()
    axis, angle = q.to_axis_angle()
    assert angle == pytest.approx(0.0, abs=1e-9)
    # Axis is arbitrary for identity; just check it's a unit vector
    n = math.sqrt(sum(a ** 2 for a in axis))
    assert n == pytest.approx(1.0)


def test_to_axis_angle_roundtrip():
    """from_axis_angle_vec(axis, angle) → to_axis_angle() should recover the original."""
    original_axis = (1.0 / math.sqrt(3.0),) * 3
    original_angle = 1.7
    q = Quaternion.from_axis_angle_vec(original_axis, original_angle)
    recovered_axis, recovered_angle = q.to_axis_angle()
    assert recovered_angle == pytest.approx(original_angle)
    for got, expected in zip(recovered_axis, original_axis):
        assert got == pytest.approx(expected, abs=1e-9)


# ---------------------------------------------------------------------------
# rotate_vector
# ---------------------------------------------------------------------------


def test_rotate_vector_identity_no_change():
    v = (1.0, 2.0, 3.0)
    q = Quaternion.identity()
    result = q.rotate_vector(v)
    assert result[0] == pytest.approx(1.0)
    assert result[1] == pytest.approx(2.0)
    assert result[2] == pytest.approx(3.0)


def test_rotate_vector_x_pi_rotates_y_to_minus_y():
    """180° rotation about x maps (0,1,0) → (0,-1,0)."""
    q = Quaternion.from_axis_angle("x", math.pi)
    v = q.rotate_vector((0.0, 1.0, 0.0))
    assert v[0] == pytest.approx(0.0, abs=1e-9)
    assert v[1] == pytest.approx(-1.0, abs=1e-9)
    assert v[2] == pytest.approx(0.0, abs=1e-9)


def test_rotate_vector_z_pi_rotates_x_to_minus_x():
    """180° rotation about z maps (1,0,0) → (-1,0,0)."""
    q = Quaternion.from_axis_angle("z", math.pi)
    v = q.rotate_vector((1.0, 0.0, 0.0))
    assert v[0] == pytest.approx(-1.0, abs=1e-9)
    assert v[1] == pytest.approx(0.0, abs=1e-9)
    assert v[2] == pytest.approx(0.0, abs=1e-9)


def test_rotate_vector_preserves_norm():
    q = Quaternion.from_axis_angle_vec((1.0, 1.0, 1.0), 1.2)
    v = (0.6, 0.8, 0.0)
    result = q.rotate_vector(v)
    original_norm = math.sqrt(sum(c ** 2 for c in v))
    result_norm = math.sqrt(sum(c ** 2 for c in result))
    assert result_norm == pytest.approx(original_norm)


def test_rotate_vector_wrong_length():
    q = Quaternion.identity()
    with pytest.raises(ValueError):
        q.rotate_vector((1.0, 0.0))
