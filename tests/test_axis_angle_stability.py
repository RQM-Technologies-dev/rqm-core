"""Signed-S3 reconstruction and boundary regressions, independent of extraction."""
import math

import numpy as np
import pytest

from rqm_core import Quaternion


def components(q):
    return np.array([q.w, q.x, q.y, q.z])


@pytest.mark.parametrize('angle', [1e-12, 1e-9, 1e-7, math.pi,
                                   2 * math.pi - 1e-7, 2 * math.pi - 1e-12])
@pytest.mark.parametrize('scale', [1e-100, 1.0, 1e100])
def test_axis_is_unit_and_reconstructs_signed_normalized_input(angle, scale):
    axis = np.array([2.0, -3.0, 6.0]) / 7.0
    expected = np.r_[math.cos(angle / 2), axis * math.sin(angle / 2)]
    q = Quaternion(*(scale * expected))
    recovered_axis, recovered_angle = q.to_axis_angle(atol=0)
    assert math.hypot(*recovered_axis) == pytest.approx(1, abs=3e-16)
    assert recovered_axis == pytest.approx(axis, abs=3e-16)
    assert recovered_angle == pytest.approx(angle, rel=5e-16, abs=0)
    rebuilt = np.r_[math.cos(recovered_angle / 2),
                    np.array(recovered_axis) * math.sin(recovered_angle / 2)]
    np.testing.assert_allclose(rebuilt, expected, rtol=1e-15, atol=5e-16)


def test_reported_ry_regression():
    axis, angle = Quaternion.from_axis_angle('y', 1e-7).to_axis_angle(atol=1e-12)
    assert axis == pytest.approx((0, 1, 0), abs=2e-16)
    assert angle == pytest.approx(1e-7, rel=3e-16, abs=0)


@pytest.mark.parametrize('sign,angle', [(1, 0), (-1, 2 * math.pi)])
def test_exact_signed_identity_and_zero_error(sign, angle):
    axis, actual = Quaternion(sign, 0, 0, 0).to_axis_angle(atol=0)
    assert axis == (1, 0, 0)
    assert actual == angle
    with pytest.raises(ValueError, match='zero quaternion'):
        Quaternion(0, 0, 0, 0).to_axis_angle()


def test_subnormal_vector_norm_does_not_square_to_zero():
    axis, angle = Quaternion(1, 0, 1e-200, 0).to_axis_angle(atol=0)
    assert axis == (0, 1, 0)
    assert angle == pytest.approx(2e-200, rel=1e-15, abs=0)


@pytest.mark.parametrize('sign', [1, -1])
def test_atol_keeps_default_axis_and_bounds_reconstruction_error(sign):
    atol = 1e-9
    for magnitude in (atol / 2, atol, atol * 2):
        q = Quaternion(sign * math.sqrt(1 - magnitude**2), 0, magnitude, 0)
        axis, angle = q.to_axis_angle(atol=atol)
        assert axis == ((1, 0, 0) if magnitude <= atol else (0, 1, 0))
        rebuilt = np.r_[math.cos(angle / 2), np.array(axis) * math.sin(angle / 2)]
        assert np.max(np.abs(rebuilt - components(q))) <= 2 * atol


def test_random_antipodes_keep_distinct_signed_reconstructions():
    rng = np.random.default_rng(22)
    for raw in rng.normal(size=(100, 4)):
        q = raw / np.linalg.norm(raw)
        axes, angles = [], []
        for signed in (q, -q):
            axis, angle = Quaternion(*signed).to_axis_angle()
            assert math.hypot(*axis) == pytest.approx(1, abs=4e-16)
            rebuilt = np.r_[math.cos(angle / 2), np.array(axis) * math.sin(angle / 2)]
            np.testing.assert_allclose(rebuilt, signed, rtol=0, atol=7e-16)
            axes.append(axis)
            angles.append(angle)
        np.testing.assert_allclose(axes[0], -np.array(axes[1]), atol=4e-16)
        assert sum(angles) == pytest.approx(2 * math.pi, abs=1e-15)
