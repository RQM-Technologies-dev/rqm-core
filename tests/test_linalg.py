"""Tests for rqm_core.linalg."""

import math

import numpy as np
import pytest

from rqm_core.linalg import (
    normalize_vector,
    vector_norm,
    matrix_trace,
    matrix_determinant,
    matrix_dagger,
    matrix_close,
    complex_close,
    is_unitary,
)


# ---------------------------------------------------------------------------
# normalize_vector
# ---------------------------------------------------------------------------


def test_normalize_vector_unit_result():
    v = np.array([3.0, 4.0])
    result = normalize_vector(v)
    assert abs(np.linalg.norm(result) - 1.0) == pytest.approx(0.0, abs=1e-9)


def test_normalize_vector_direction():
    v = np.array([0.0, 0.0, 5.0])
    result = normalize_vector(v)
    assert np.allclose(result, [0.0, 0.0, 1.0])


def test_normalize_vector_zero_raises():
    with pytest.raises(ValueError, match="zero"):
        normalize_vector(np.array([0.0, 0.0, 0.0]))


def test_normalize_vector_3d():
    v = np.array([1.0, 1.0, 1.0])
    result = normalize_vector(v)
    assert abs(np.linalg.norm(result) - 1.0) == pytest.approx(0.0, abs=1e-9)


# ---------------------------------------------------------------------------
# vector_norm
# ---------------------------------------------------------------------------


def test_vector_norm_real():
    assert vector_norm(np.array([3.0, 4.0])) == pytest.approx(5.0)


def test_vector_norm_zero():
    assert vector_norm(np.array([0.0, 0.0])) == pytest.approx(0.0, abs=1e-9)


def test_vector_norm_unit():
    assert vector_norm(np.array([1.0, 0.0, 0.0])) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# matrix_trace
# ---------------------------------------------------------------------------


def test_matrix_trace_identity():
    m = np.eye(2, dtype=np.complex128)
    assert matrix_trace(m) == pytest.approx(2.0)


def test_matrix_trace_general():
    m = np.array([[1 + 2j, 0], [0, 3 + 4j]], dtype=np.complex128)
    assert matrix_trace(m) == pytest.approx(4 + 6j)


# ---------------------------------------------------------------------------
# matrix_determinant
# ---------------------------------------------------------------------------


def test_matrix_determinant_identity():
    m = np.eye(2, dtype=np.complex128)
    assert abs(matrix_determinant(m) - 1.0) == pytest.approx(0.0, abs=1e-9)


def test_matrix_determinant_known():
    m = np.array([[2.0, 0.0], [0.0, 3.0]], dtype=np.complex128)
    assert abs(matrix_determinant(m) - 6.0) == pytest.approx(0.0, abs=1e-9)


# ---------------------------------------------------------------------------
# matrix_dagger
# ---------------------------------------------------------------------------


def test_matrix_dagger_identity():
    m = np.eye(2, dtype=np.complex128)
    assert np.allclose(matrix_dagger(m), m)


def test_matrix_dagger_conjugate_transpose():
    m = np.array([[1 + 2j, 3 + 4j], [5 + 6j, 7 + 8j]], dtype=np.complex128)
    expected = m.conj().T
    assert np.allclose(matrix_dagger(m), expected)


def test_matrix_dagger_times_original_is_unitary():
    """For a unitary U, U† U = I."""
    from rqm_core.su2 import axis_angle_to_su2
    u = axis_angle_to_su2("y", 0.9)
    assert np.allclose(matrix_dagger(u) @ u, np.eye(2), atol=1e-9)


# ---------------------------------------------------------------------------
# matrix_close
# ---------------------------------------------------------------------------


def test_matrix_close_equal():
    m = np.eye(2, dtype=np.complex128)
    assert matrix_close(m, m)


def test_matrix_close_within_tol():
    a = np.eye(2, dtype=np.complex128)
    b = np.eye(2, dtype=np.complex128) + 1e-10
    assert matrix_close(a, b, atol=1e-9)


def test_matrix_close_outside_tol():
    a = np.eye(2, dtype=np.complex128)
    b = np.eye(2, dtype=np.complex128) * 2.0
    assert not matrix_close(a, b)


# ---------------------------------------------------------------------------
# complex_close
# ---------------------------------------------------------------------------


def test_complex_close_identical():
    assert complex_close(1 + 2j, 1 + 2j)


def test_complex_close_within_tol():
    assert complex_close(1.0, 1.0 + 1e-10)


def test_complex_close_outside_tol():
    assert not complex_close(0.0, 1.0)


# ---------------------------------------------------------------------------
# is_unitary (linalg internal helper)
# ---------------------------------------------------------------------------


def test_linalg_is_unitary_true():
    m = np.eye(2, dtype=np.complex128)
    assert is_unitary(m)


def test_linalg_is_unitary_false():
    m = np.array([[2.0, 0.0], [0.0, 2.0]], dtype=np.complex128)
    assert not is_unitary(m)
