"""Tests for rqm_core.validation."""

import numpy as np
import pytest

from rqm_core.validation import (
    validate_axis,
    validate_complex_pair,
    validate_square_matrix,
    validate_real_number,
    validate_tolerance,
)


# ---------------------------------------------------------------------------
# validate_axis
# ---------------------------------------------------------------------------


def test_validate_axis_x():
    assert validate_axis("x") == "x"


def test_validate_axis_y():
    assert validate_axis("Y") == "y"


def test_validate_axis_z():
    assert validate_axis("Z") == "z"


def test_validate_axis_uppercase():
    assert validate_axis("X") == "x"


def test_validate_axis_invalid():
    with pytest.raises(ValueError, match="axis"):
        validate_axis("w")


def test_validate_axis_empty():
    with pytest.raises(ValueError, match="axis"):
        validate_axis("")


def test_validate_axis_number():
    with pytest.raises(ValueError, match="axis"):
        validate_axis("1")


# ---------------------------------------------------------------------------
# validate_complex_pair
# ---------------------------------------------------------------------------


def test_validate_complex_pair_valid():
    validate_complex_pair(1.0, 0.0)  # no exception


def test_validate_complex_pair_complex():
    validate_complex_pair(1j, 1.0 + 2j)  # no exception


def test_validate_complex_pair_both_zero():
    with pytest.raises(ValueError, match="zero"):
        validate_complex_pair(0.0, 0.0)


def test_validate_complex_pair_alpha_non_finite():
    with pytest.raises(ValueError, match="finite"):
        validate_complex_pair(float("inf"), 1.0)


def test_validate_complex_pair_beta_non_finite():
    with pytest.raises(ValueError, match="finite"):
        validate_complex_pair(1.0, float("nan"))


# ---------------------------------------------------------------------------
# validate_square_matrix
# ---------------------------------------------------------------------------


def test_validate_square_matrix_valid():
    m = np.eye(2)
    validate_square_matrix(m)  # no exception


def test_validate_square_matrix_3x3():
    m = np.eye(3)
    validate_square_matrix(m)  # no exception


def test_validate_square_matrix_not_square():
    m = np.zeros((2, 3))
    with pytest.raises(ValueError, match="square"):
        validate_square_matrix(m)


def test_validate_square_matrix_1d():
    v = np.array([1.0, 2.0])
    with pytest.raises(ValueError, match="2-D"):
        validate_square_matrix(v)


def test_validate_square_matrix_expected_size_correct():
    m = np.eye(2)
    validate_square_matrix(m, expected_size=2)  # no exception


def test_validate_square_matrix_expected_size_wrong():
    m = np.eye(3)
    with pytest.raises(ValueError, match="2×2"):
        validate_square_matrix(m, expected_size=2)


# ---------------------------------------------------------------------------
# validate_real_number
# ---------------------------------------------------------------------------


def test_validate_real_number_int():
    validate_real_number(1, "x")  # no exception


def test_validate_real_number_float():
    validate_real_number(3.14, "angle")  # no exception


def test_validate_real_number_inf():
    with pytest.raises(ValueError, match="finite"):
        validate_real_number(float("inf"), "angle")


def test_validate_real_number_nan():
    with pytest.raises(ValueError, match="finite"):
        validate_real_number(float("nan"), "angle")


def test_validate_real_number_non_numeric():
    with pytest.raises(TypeError, match="real number"):
        validate_real_number("hello", "x")


# ---------------------------------------------------------------------------
# validate_tolerance
# ---------------------------------------------------------------------------


def test_validate_tolerance_valid():
    validate_tolerance(1e-9)  # no exception


def test_validate_tolerance_small():
    validate_tolerance(1e-15)  # no exception


def test_validate_tolerance_zero():
    with pytest.raises(ValueError, match="positive"):
        validate_tolerance(0.0)


def test_validate_tolerance_negative():
    with pytest.raises(ValueError, match="positive"):
        validate_tolerance(-1e-9)


def test_validate_tolerance_inf():
    with pytest.raises(ValueError, match="positive"):
        validate_tolerance(float("inf"))


def test_validate_tolerance_non_numeric():
    with pytest.raises(TypeError, match="real number"):
        validate_tolerance("small")
