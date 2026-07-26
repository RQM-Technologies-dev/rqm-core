import math

import numpy as np
import pytest

from rqm_core import Quaternion, QuaternionSU2Pair


def test_identity_payload_and_reconstruction() -> None:
    pair = QuaternionSU2Pair.identity()
    assert pair.numeric_payload_bytes == 64
    assert np.allclose(pair.to_unitary(), np.eye(4), atol=1e-15, rtol=0.0)


def test_reconstruction_uses_kron_q1_q0() -> None:
    q0 = Quaternion.from_axis_angle("x", 0.37)
    q1 = Quaternion.from_axis_angle("z", -0.61)
    pair = QuaternionSU2Pair(q0, q1)
    assert np.allclose(
        pair.to_unitary(),
        np.kron(q1.to_su2_matrix(), q0.to_su2_matrix()),
        atol=1e-15,
        rtol=0.0,
    )


def test_componentwise_composition_matches_matrix_order() -> None:
    earlier = QuaternionSU2Pair(
        Quaternion.from_axis_angle("x", 0.2),
        Quaternion.from_axis_angle("y", -0.3),
    )
    later = QuaternionSU2Pair(
        Quaternion.from_axis_angle("z", 0.4),
        Quaternion.from_axis_angle("x", 0.5),
    )
    composed = later.compose_after(earlier)
    assert np.allclose(
        composed.to_unitary(),
        later.to_unitary() @ earlier.to_unitary(),
        atol=1e-14,
        rtol=0.0,
    )


@pytest.mark.parametrize("angle", [1e-14, math.pi - 1e-12, math.pi + 1e-12])
def test_inverse_and_canonicalization_edge_cases(angle: float) -> None:
    pair = QuaternionSU2Pair(
        Quaternion.from_axis_angle("x", angle),
        Quaternion.from_axis_angle("z", -angle),
    )
    product = pair.inverse().compose_after(pair)
    assert np.allclose(product.to_unitary(), np.eye(4), atol=1e-12, rtol=0.0)
    canonical = pair.canonicalize()
    assert canonical.q0.w >= 0.0
    assert canonical.q1.w >= 0.0


def test_rejects_non_unit_components() -> None:
    with pytest.raises(ValueError, match="unit quaternions"):
        QuaternionSU2Pair(Quaternion(2, 0, 0, 0), Quaternion.identity())

