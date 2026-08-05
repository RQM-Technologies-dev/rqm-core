"""Tests for rqm_core.su2."""

import math

import numpy as np
import pytest

from rqm_core.quaternion import Quaternion
from rqm_core.su2 import (
    factor_u2_global_phase,
    quaternion_to_su2,
    quaternion_to_zyz,
    quaternion_to_named_gate_sequence,
    su2_to_quaternion,
    su2_to_named_gate_sequence,
    axis_angle_to_su2,
    su2_identity,
    is_unitary,
    determinant_close_to_one,
)


def test_factor_u2_identity_has_zero_phase() -> None:
    phase, special_unitary = factor_u2_global_phase(
        np.eye(2, dtype=np.complex128)
    )

    assert phase == 0.0
    assert np.allclose(special_unitary, np.eye(2), atol=1e-12)
    assert determinant_close_to_one(special_unitary)


def test_factor_u2_recovers_explicit_global_phase() -> None:
    rotation = axis_angle_to_su2("y", 0.73)
    source = np.exp(1j * 0.37) * rotation

    phase, special_unitary = factor_u2_global_phase(source)

    assert phase == pytest.approx(0.37)
    assert np.allclose(special_unitary, rotation, atol=1e-12)
    assert np.allclose(np.exp(1j * phase) * special_unitary, source, atol=1e-12)


def test_factor_u2_uses_deterministic_modulo_pi_branch() -> None:
    rotation = axis_angle_to_su2("x", -0.41)
    source = np.exp(1j * 2.2) * rotation

    phase, special_unitary = factor_u2_global_phase(source)

    assert -math.pi / 2 < phase <= math.pi / 2
    assert phase == pytest.approx(2.2 - math.pi)
    assert np.allclose(special_unitary, -rotation, atol=1e-12)
    assert np.allclose(np.exp(1j * phase) * special_unitary, source, atol=1e-12)


def test_factor_u2_pauli_x_handles_negative_determinant() -> None:
    pauli_x = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)

    phase, special_unitary = factor_u2_global_phase(pauli_x)

    assert phase == pytest.approx(math.pi / 2)
    assert determinant_close_to_one(special_unitary)
    assert np.allclose(np.exp(1j * phase) * special_unitary, pauli_x, atol=1e-12)


@pytest.mark.parametrize(
    "invalid",
    [
        np.eye(3, dtype=np.complex128),
        np.array([[2.0, 0.0], [0.0, 0.5]], dtype=np.complex128),
    ],
)
def test_factor_u2_rejects_non_u2_input(invalid: np.ndarray) -> None:
    with pytest.raises(ValueError):
        factor_u2_global_phase(invalid)


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


@pytest.mark.parametrize(
    ("axis", "angle", "expected"),
    [
        (
            "x",
            0.73,
            np.array(
                [
                    [math.cos(0.73 / 2), -1j * math.sin(0.73 / 2)],
                    [-1j * math.sin(0.73 / 2), math.cos(0.73 / 2)],
                ],
                dtype=np.complex128,
            ),
        ),
        (
            "y",
            -0.41,
            np.array(
                [
                    [math.cos(-0.41 / 2), -math.sin(-0.41 / 2)],
                    [math.sin(-0.41 / 2), math.cos(-0.41 / 2)],
                ],
                dtype=np.complex128,
            ),
        ),
        (
            "z",
            1.19,
            np.array(
                [
                    [np.exp(-1j * 1.19 / 2), 0.0],
                    [0.0, np.exp(1j * 1.19 / 2)],
                ],
                dtype=np.complex128,
            ),
        ),
    ],
)
def test_axis_angle_to_su2_matches_standard_rx_ry_rz(axis, angle, expected):
    assert np.allclose(axis_angle_to_su2(axis, angle), expected, atol=1e-9)


def test_quaternion_sign_is_global_phase_not_identical_su2():
    q = Quaternion.from_axis_angle_vec((1.0, 2.0, 3.0), 0.79)
    neg_q = Quaternion(-q.w, -q.x, -q.y, -q.z)

    assert np.allclose(q.to_rotation_matrix(), neg_q.to_rotation_matrix(), atol=1e-9)
    assert not np.allclose(quaternion_to_su2(q), quaternion_to_su2(neg_q), atol=1e-9)
    assert np.allclose(quaternion_to_su2(q), -quaternion_to_su2(neg_q), atol=1e-9)


# ---------------------------------------------------------------------------
# Round-trip conversion
# ---------------------------------------------------------------------------


def test_round_trip_q_to_su2_to_q():
    q = Quaternion.from_axis_angle("y", 0.75)
    m = quaternion_to_su2(q)
    q2 = su2_to_quaternion(m)
    # Allow for global phase: q and -q represent the same Bloch/SO(3) rotation.
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


def test_validate_su2_matrix_det_not_one():
    from rqm_core.su2 import validate_su2_matrix
    # Unitary but det = -1 (SU(2) requires det = +1)
    bad = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=np.complex128)
    with pytest.raises(ValueError, match="determinant"):
        validate_su2_matrix(bad)


# ---------------------------------------------------------------------------
# Named-gate decomposition helpers
# ---------------------------------------------------------------------------


def _sequence_to_matrix(
    sequence: tuple[tuple[str, float], ...]
) -> np.ndarray:
    """Build an SU(2) matrix from a named rotation sequence."""
    result = su2_identity()
    for gate, angle in sequence:
        if gate == "RX":
            result = result @ axis_angle_to_su2("x", angle)
        elif gate == "RY":
            result = result @ axis_angle_to_su2("y", angle)
        elif gate == "RZ":
            result = result @ axis_angle_to_su2("z", angle)
        else:
            raise AssertionError(f"Unexpected gate {gate!r}")
    return result


def test_named_decomposition_identity_is_empty():
    seq = quaternion_to_named_gate_sequence(Quaternion.identity())
    assert seq == tuple()


def test_named_decomposition_near_identity_is_empty():
    q = Quaternion.from_axis_angle("z", 1e-12)
    seq = quaternion_to_named_gate_sequence(q, atol=1e-9)
    assert seq == tuple()


def test_named_decomposition_pure_z_is_deterministic():
    angle = 1.234
    q = Quaternion.from_axis_angle("z", angle)
    seq = quaternion_to_named_gate_sequence(q)
    assert seq == (("RZ", pytest.approx(angle)),)


def test_named_decomposition_pure_x_and_y_single_axis():
    x_seq = quaternion_to_named_gate_sequence(
        Quaternion.from_axis_angle("x", 0.8)
    )
    y_seq = quaternion_to_named_gate_sequence(
        Quaternion.from_axis_angle("y", -0.6)
    )
    assert x_seq == (("RX", pytest.approx(0.8)),)
    assert y_seq == (("RY", pytest.approx(-0.6)),)


def test_named_decomposition_generic_reconstructs_same_matrix():
    q = Quaternion(0.71, -0.23, 0.35, -0.56).normalize()
    original = quaternion_to_su2(q)
    seq = quaternion_to_named_gate_sequence(q, simplify_axis=False)
    rebuilt = _sequence_to_matrix(seq)
    assert len(seq) == 3
    assert seq[0][0] == "RZ"
    assert seq[1][0] == "RY"
    assert seq[2][0] == "RZ"
    assert np.allclose(original, rebuilt, atol=1e-9)


def test_named_decomposition_is_deterministic_over_repeated_runs():
    q = Quaternion(0.48, -0.19, 0.61, 0.59).normalize()
    seq_first = quaternion_to_named_gate_sequence(q, simplify_axis=False)
    for _ in range(10):
        assert quaternion_to_named_gate_sequence(
            q, simplify_axis=False
        ) == seq_first


def test_su2_named_decomposition_matches_quaternion_helper():
    q = Quaternion.from_axis_angle_vec((1.0, 1.0, 1.0), 0.7)
    m = quaternion_to_su2(q)
    from_q = quaternion_to_named_gate_sequence(q)
    from_m = su2_to_named_gate_sequence(m)
    assert from_q == from_m


def test_quaternion_to_zyz_reconstructs_same_matrix():
    q = Quaternion(0.71, -0.23, 0.35, -0.56).normalize()
    alpha, beta, gamma = quaternion_to_zyz(q.w, q.x, q.y, q.z)
    rebuilt = (
        axis_angle_to_su2("z", alpha)
        @ axis_angle_to_su2("y", beta)
        @ axis_angle_to_su2("z", gamma)
    )
    assert np.allclose(quaternion_to_su2(q), rebuilt, atol=1e-9)
