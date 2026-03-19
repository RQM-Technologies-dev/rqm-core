"""Tests that the public rqm_core API is complete and importable."""

import pytest


# ---------------------------------------------------------------------------
# Top-level import
# ---------------------------------------------------------------------------


def test_package_importable():
    import rqm_core  # noqa: F401


def test_version_present():
    import rqm_core
    assert hasattr(rqm_core, "__version__")
    assert rqm_core.__version__ == "0.1.0"


# ---------------------------------------------------------------------------
# __all__ completeness
# ---------------------------------------------------------------------------

_EXPECTED_EXPORTS = [
    # Quaternion
    "Quaternion",
    # Spinor
    "normalize_spinor",
    "spinor_norm",
    "is_normalized_spinor",
    "spinor_to_quaternion",
    "spinor_embed",
    "spinor_to_su2",
    "state_fidelity",
    # SU(2)
    "su2_identity",
    "quaternion_to_su2",
    "su2_to_quaternion",
    "axis_angle_to_su2",
    "is_unitary",
    "determinant_close_to_one",
    "validate_su2_matrix",
    # Bloch
    "state_to_bloch",
    "bloch_to_state",
    "bloch_from_quaternion",
    "bloch_radius",
    "validate_bloch_vector",
    "measurement_probabilities",
    # Linear algebra
    "normalize_vector",
    "vector_norm",
    "matrix_trace",
    "matrix_determinant",
    "matrix_dagger",
    "matrix_close",
    "complex_close",
    # Gates
    "gate_identity",
    "gate_x",
    "gate_y",
    "gate_z",
    "gate_h",
    "gate_s",
    "gate_t",
    "gate_rx",
    "gate_ry",
    "gate_rz",
    "match_gate",
]


def test_all_exports_present():
    import rqm_core
    for name in _EXPECTED_EXPORTS:
        assert hasattr(rqm_core, name), f"rqm_core.{name} is missing"


def test_all_list_matches_expected():
    import rqm_core
    for name in _EXPECTED_EXPORTS:
        assert name in rqm_core.__all__, f"{name!r} not in rqm_core.__all__"


# ---------------------------------------------------------------------------
# Spot-checks: key names are callable
# ---------------------------------------------------------------------------


def test_quaternion_class_usable():
    from rqm_core import Quaternion
    q = Quaternion.identity()
    assert q.w == 1.0


def test_normalize_spinor_callable():
    from rqm_core import normalize_spinor
    a, b = normalize_spinor(3.0, 4.0)
    assert abs(a) ** 2 + abs(b) ** 2 == pytest.approx(1.0)


def test_state_to_bloch_callable():
    from rqm_core import state_to_bloch
    x, y, z = state_to_bloch(1.0, 0.0)
    assert z == pytest.approx(1.0)


def test_su2_identity_callable():
    import numpy as np
    from rqm_core import su2_identity
    m = su2_identity()
    assert m.shape == (2, 2)
    assert m.dtype == complex


def test_is_unitary_callable():
    import numpy as np
    from rqm_core import is_unitary
    assert is_unitary(np.eye(2, dtype=np.complex128))


def test_matrix_dagger_callable():
    import numpy as np
    from rqm_core import matrix_dagger
    m = np.array([[1 + 1j, 0], [0, 1 - 1j]], dtype=np.complex128)
    d = matrix_dagger(m)
    assert d.shape == (2, 2)


def test_bloch_radius_callable():
    from rqm_core import bloch_radius
    assert bloch_radius(0.0, 0.0, 1.0) == pytest.approx(1.0)


def test_validate_bloch_vector_callable():
    from rqm_core import validate_bloch_vector
    validate_bloch_vector(0.0, 0.0, 1.0)  # no exception


def test_validate_su2_matrix_callable():
    from rqm_core import validate_su2_matrix, axis_angle_to_su2
    validate_su2_matrix(axis_angle_to_su2("x", 0.5))  # no exception


def test_spinor_norm_callable():
    from rqm_core import spinor_norm
    assert spinor_norm(0.0, 1.0) == pytest.approx(1.0)


def test_is_normalized_spinor_callable():
    from rqm_core import is_normalized_spinor
    assert is_normalized_spinor(1.0, 0.0)
    assert not is_normalized_spinor(2.0, 0.0)
