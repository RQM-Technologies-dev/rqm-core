"""Tests for rqm_core.utils."""

import math

import numpy as np
import pytest

from rqm_core.utils import angle_wrap, safe_norm, is_finite_real, is_finite_complex


# ---------------------------------------------------------------------------
# angle_wrap
# ---------------------------------------------------------------------------


def test_angle_wrap_zero():
    assert angle_wrap(0.0) == pytest.approx(0.0, abs=1e-9)


def test_angle_wrap_pi():
    # π wraps to -π (the interval is (-π, π])
    assert angle_wrap(math.pi) == pytest.approx(-math.pi, abs=1e-9)


def test_angle_wrap_negative_pi():
    # -π wraps to -π
    assert angle_wrap(-math.pi) == pytest.approx(-math.pi, abs=1e-9)


def test_angle_wrap_two_pi():
    assert angle_wrap(2 * math.pi) == pytest.approx(0.0, abs=1e-9)


def test_angle_wrap_three_halves_pi():
    # 3π/2 → -π/2
    assert angle_wrap(3 * math.pi / 2) == pytest.approx(-math.pi / 2, abs=1e-9)


def test_angle_wrap_small_positive():
    assert angle_wrap(0.5) == pytest.approx(0.5)


def test_angle_wrap_small_negative():
    assert angle_wrap(-0.5) == pytest.approx(-0.5)


# ---------------------------------------------------------------------------
# safe_norm
# ---------------------------------------------------------------------------


def test_safe_norm_nonzero():
    v = np.array([3.0, 4.0])
    assert safe_norm(v) == pytest.approx(5.0)


def test_safe_norm_zero_raises():
    with pytest.raises(ValueError, match="zero"):
        safe_norm(np.array([0.0, 0.0]))


def test_safe_norm_unit():
    v = np.array([1.0, 0.0, 0.0])
    assert safe_norm(v) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# is_finite_real
# ---------------------------------------------------------------------------


def test_is_finite_real_normal():
    assert is_finite_real(1.5)


def test_is_finite_real_zero():
    assert is_finite_real(0.0)


def test_is_finite_real_negative():
    assert is_finite_real(-3.14)


def test_is_finite_real_inf():
    assert not is_finite_real(float("inf"))


def test_is_finite_real_nan():
    assert not is_finite_real(float("nan"))


def test_is_finite_real_neg_inf():
    assert not is_finite_real(float("-inf"))


def test_is_finite_real_non_numeric():
    assert not is_finite_real("string")


# ---------------------------------------------------------------------------
# is_finite_complex
# ---------------------------------------------------------------------------


def test_is_finite_complex_normal():
    assert is_finite_complex(1.0 + 2.0j)


def test_is_finite_complex_zero():
    assert is_finite_complex(0.0)


def test_is_finite_complex_real_inf():
    assert not is_finite_complex(float("inf") + 0j)


def test_is_finite_complex_imag_inf():
    assert not is_finite_complex(1.0 + float("inf") * 1j)


def test_is_finite_complex_nan():
    assert not is_finite_complex(complex(float("nan"), 0.0))


def test_is_finite_complex_non_numeric():
    assert not is_finite_complex("string")
