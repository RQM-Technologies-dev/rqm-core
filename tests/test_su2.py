"""Tests for rqm_core.su2."""

import math

import numpy as np
import pytest

from rqm_core.quaternion import Quaternion
from rqm_core.su2 import (
    quaternion_to_su2,
    su2_to_quaternion,
    axis_angle_to_su2,
    su2_identity,
    is_unitary,
    determinant_close_to_one,
)


# ---------------------------------------------------------------------------
# su2_identity
# ---------------------------------------------------------------------------


def test_su2_identity_shape():
    m = su2_identity()
    assert m.shape == (2, 2)


def test_su2_identity_values():
    m = su2_identity()
    assert np.allclose(m, np.eye(2, dtype=np.complex128))


# ---------------------------------------------------------------------------
# quaternion_to_su2 unitarity and det
# ---------------------------------------------------------------------------


def test_quaternion_to_su2_unitary():
    q = Quaternion.from_axis_angle("x", 0.6)
    m = quaternion_to_su2(q)
    assert is_unitary(m)


def test_quaternion_to_su2_det_one():
    q = Quaternion.from_axis_angle("y", 1.0)
    m = quaternion_to_su2(q)
    assert determinant_close_to_one(m)


def test_axis_angle_to_su2_unitary():
    m = axis_angle_to_su2("z", math.pi / 4)
    assert is_unitary(m)


def test_axis_angle_to_su2_det_one():
    m = axis_angle_to_su2("x", math.pi / 3)
    assert determinant_close_to_one(m)


# ---------------------------------------------------------------------------
# Round-trip conversion
# ---------------------------------------------------------------------------


def test_round_trip_q_to_su2_to_q():
    q = Quaternion.from_axis_angle("y", 0.75)
    m = quaternion_to_su2(q)
    q2 = su2_to_quaternion(m)
    # Allow for global phase: q and -q represent the same rotation
    same = q == q2
    negated = Quaternion(-q2.w, -q2.x, -q2.y, -q2.z) == q
    assert same or negated


def test_su2_to_quaternion_non_unitary_raises():
    bad = np.array([[2.0, 0.0], [0.0, 2.0]], dtype=np.complex128)
    with pytest.raises(ValueError, match="unitary"):
        su2_to_quaternion(bad)


def test_su2_identity_to_quaternion():
    m = su2_identity()
    q = su2_to_quaternion(m)
    identity = Quaternion.identity()
    same = q == identity
    negated = Quaternion(-q.w, -q.x, -q.y, -q.z) == identity
    assert same or negated


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------


def test_is_unitary_true():
    m = axis_angle_to_su2("x", 1.0)
    assert is_unitary(m)


def test_is_unitary_false():
    bad = np.array([[2.0, 0.0], [0.0, 0.5]], dtype=np.complex128)
    assert not is_unitary(bad)


def test_determinant_close_to_one_true():
    m = axis_angle_to_su2("z", 2.0)
    assert determinant_close_to_one(m)


def test_determinant_close_to_one_false():
    bad = np.array([[2.0, 0.0], [0.0, 2.0]], dtype=np.complex128)
    assert not determinant_close_to_one(bad)


# ---------------------------------------------------------------------------
# validate_su2_matrix
# ---------------------------------------------------------------------------


def test_validate_su2_matrix_valid():
    from rqm_core.su2 import validate_su2_matrix
    m = axis_angle_to_su2("z", 1.0)
    validate_su2_matrix(m)  # should not raise


def test_validate_su2_matrix_non_unitary():
    from rqm_core.su2 import validate_su2_matrix
    bad = np.array([[2.0, 0.0], [0.0, 0.5]], dtype=np.complex128)
    with pytest.raises(ValueError, match="unitary"):
        validate_su2_matrix(bad)


def test_validate_su2_matrix_wrong_shape():
    from rqm_core.su2 import validate_su2_matrix
    bad = np.eye(3, dtype=np.complex128)
    with pytest.raises(ValueError):
        validate_su2_matrix(bad)
