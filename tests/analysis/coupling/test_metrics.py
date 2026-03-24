"""Tests for the measured entanglement metrics module."""

import math

import numpy as np
import pytest

from rqm_core.analysis.coupling.metrics import (
    partial_trace_qubit_1,
    compute_concurrence,
    compute_von_neumann_entropy,
    compute_pure_state_fidelity,
    normalize_metric_value,
    compute_pair_metrics,
    is_entangled_from_metrics,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sv(*amplitudes: complex) -> np.ndarray:
    """Build a normalised statevector from raw amplitudes."""
    v = np.array(amplitudes, dtype=np.complex128)
    return v / np.linalg.norm(v)


def _ket_00() -> np.ndarray:
    return np.array([1, 0, 0, 0], dtype=np.complex128)


def _ket_01() -> np.ndarray:
    return np.array([0, 1, 0, 0], dtype=np.complex128)


def _ket_10() -> np.ndarray:
    return np.array([0, 0, 1, 0], dtype=np.complex128)


def _ket_11() -> np.ndarray:
    return np.array([0, 0, 0, 1], dtype=np.complex128)


def _bell() -> np.ndarray:
    """(|00⟩ + |11⟩) / √2"""
    s = 1.0 / math.sqrt(2.0)
    return np.array([s, 0, 0, s], dtype=np.complex128)


def _plus_zero() -> np.ndarray:
    """(|00⟩ + |10⟩) / √2  =  |+⟩ ⊗ |0⟩ (separable)"""
    s = 1.0 / math.sqrt(2.0)
    return np.array([s, 0, s, 0], dtype=np.complex128)


# ---------------------------------------------------------------------------
# partial_trace_qubit_1
# ---------------------------------------------------------------------------


def test_partial_trace_shape():
    rho = partial_trace_qubit_1(_ket_00())
    assert rho.shape == (2, 2)


def test_partial_trace_trace_is_one():
    rho = partial_trace_qubit_1(_bell())
    assert abs(np.trace(rho) - 1.0) < 1e-9


def test_partial_trace_ket_00_is_pure_zero():
    """ρ₀ for |00⟩ should be |0⟩⟨0|."""
    rho = partial_trace_qubit_1(_ket_00())
    expected = np.array([[1, 0], [0, 0]], dtype=np.complex128)
    assert np.allclose(rho, expected, atol=1e-12)


def test_partial_trace_bell_is_maximally_mixed():
    """ρ₀ for Bell state should be I/2."""
    rho = partial_trace_qubit_1(_bell())
    expected = np.array([[0.5, 0], [0, 0.5]], dtype=np.complex128)
    assert np.allclose(rho, expected, atol=1e-9)


def test_partial_trace_separable_product_state():
    """ρ₀ for |+⟩⊗|0⟩ should be |+⟩⟨+| = [[1,1],[1,1]]/2."""
    rho = partial_trace_qubit_1(_plus_zero())
    expected = np.array([[0.5, 0.5], [0.5, 0.5]], dtype=np.complex128)
    assert np.allclose(rho, expected, atol=1e-9)


# ---------------------------------------------------------------------------
# compute_concurrence
# ---------------------------------------------------------------------------


def test_concurrence_bell_state_is_one():
    assert compute_concurrence(_bell()) == pytest.approx(1.0, abs=1e-9)


def test_concurrence_ket_00_is_zero():
    assert compute_concurrence(_ket_00()) == pytest.approx(0.0, abs=1e-9)


def test_concurrence_ket_10_is_zero():
    assert compute_concurrence(_ket_10()) == pytest.approx(0.0, abs=1e-9)


def test_concurrence_ket_11_is_zero():
    assert compute_concurrence(_ket_11()) == pytest.approx(0.0, abs=1e-9)


def test_concurrence_plus_zero_separable():
    """Separable state |+⟩⊗|0⟩ has concurrence 0."""
    assert compute_concurrence(_plus_zero()) == pytest.approx(0.0, abs=1e-9)


def test_concurrence_partial_entanglement():
    """Partially entangled state 0.6|00⟩ + 0.8|11⟩: C = 2*|0.6*0.8| = 0.96."""
    sv = _sv(0.6, 0, 0, 0.8)  # will be normalised
    # After normalisation norm = sqrt(0.36 + 0.64) = 1.0 exactly
    c = compute_concurrence(sv)
    expected = 2.0 * abs(0.6 * 0.8)
    assert c == pytest.approx(expected, abs=1e-6)


def test_concurrence_in_range_01():
    for sv in [_ket_00(), _ket_01(), _ket_10(), _ket_11(), _bell(), _plus_zero()]:
        c = compute_concurrence(sv)
        assert 0.0 <= c <= 1.0


# ---------------------------------------------------------------------------
# compute_von_neumann_entropy
# ---------------------------------------------------------------------------


def test_entropy_bell_state_is_one():
    rho = partial_trace_qubit_1(_bell())
    assert compute_von_neumann_entropy(rho) == pytest.approx(1.0, abs=1e-9)


def test_entropy_ket_00_is_zero():
    rho = partial_trace_qubit_1(_ket_00())
    assert compute_von_neumann_entropy(rho) == pytest.approx(0.0, abs=1e-9)


def test_entropy_separable_product_state_is_zero():
    rho = partial_trace_qubit_1(_plus_zero())
    assert compute_von_neumann_entropy(rho) == pytest.approx(0.0, abs=1e-9)


def test_entropy_in_range_01():
    for sv in [_ket_00(), _ket_01(), _ket_10(), _ket_11(), _bell(), _plus_zero()]:
        rho = partial_trace_qubit_1(sv)
        s = compute_von_neumann_entropy(rho)
        assert 0.0 <= s <= 1.0


def test_entropy_does_not_raise_on_tiny_negative_eigenvalue():
    """Slightly perturbed density matrix with tiny negative eigenvalue should not NaN."""
    rho = np.array([[0.5 + 1e-15, 0.5], [0.5, 0.5 - 1e-15]], dtype=np.complex128)
    # Should not raise and should be in [0, 1]
    s = compute_von_neumann_entropy(rho)
    assert 0.0 <= s <= 1.0
    assert math.isfinite(s)


# ---------------------------------------------------------------------------
# compute_pure_state_fidelity
# ---------------------------------------------------------------------------


def test_fidelity_same_state_is_one():
    assert compute_pure_state_fidelity(_bell(), _bell()) == pytest.approx(1.0, abs=1e-9)


def test_fidelity_orthogonal_states_is_zero():
    assert compute_pure_state_fidelity(_ket_00(), _ket_11()) == pytest.approx(
        0.0, abs=1e-9
    )


def test_fidelity_bell_vs_ket_00():
    """Bell state is not identical to |00⟩; fidelity should be 0.5."""
    f = compute_pure_state_fidelity(_bell(), _ket_00())
    assert f == pytest.approx(0.5, abs=1e-9)


def test_fidelity_in_range_01():
    pairs = [
        (_bell(), _ket_00()),
        (_plus_zero(), _bell()),
        (_ket_01(), _ket_10()),
    ]
    for sv1, sv2 in pairs:
        f = compute_pure_state_fidelity(sv1, sv2)
        assert 0.0 <= f <= 1.0


def test_fidelity_global_phase_invariant():
    """F should be the same for sv and e^{iθ}·sv."""
    sv = _bell()
    phase = complex(math.cos(0.7), math.sin(0.7))
    assert compute_pure_state_fidelity(sv, phase * sv) == pytest.approx(1.0, abs=1e-9)


# ---------------------------------------------------------------------------
# normalize_metric_value
# ---------------------------------------------------------------------------


def test_normalize_concurrence():
    assert normalize_metric_value("concurrence", 0.75) == pytest.approx(0.75, abs=1e-9)


def test_normalize_entropy():
    assert normalize_metric_value("entropy", 0.9) == pytest.approx(0.9, abs=1e-9)


def test_normalize_fidelity():
    assert normalize_metric_value("fidelity", 0.99) == pytest.approx(0.99, abs=1e-9)


def test_normalize_unknown_metric_returns_none():
    assert normalize_metric_value("rqm_correlation", 0.5) is None


def test_normalize_clamps_above_one():
    assert normalize_metric_value("concurrence", 1.0 + 1e-12) == pytest.approx(
        1.0, abs=1e-9
    )


def test_normalize_clamps_below_zero():
    assert normalize_metric_value("entropy", -1e-15) == pytest.approx(0.0, abs=1e-9)


# ---------------------------------------------------------------------------
# compute_pair_metrics
# ---------------------------------------------------------------------------


def test_pair_metrics_bell_state():
    metrics = compute_pair_metrics(_bell(), (0, 1))
    names = {m.metric_name for m in metrics}
    assert "concurrence" in names
    assert "entropy" in names
    c = next(m for m in metrics if m.metric_name == "concurrence")
    assert c.value == pytest.approx(1.0, abs=1e-9)
    e = next(m for m in metrics if m.metric_name == "entropy")
    assert e.value == pytest.approx(1.0, abs=1e-9)


def test_pair_metrics_separable_state():
    metrics = compute_pair_metrics(_ket_00(), (0, 1))
    c = next(m for m in metrics if m.metric_name == "concurrence")
    assert c.value == pytest.approx(0.0, abs=1e-9)


def test_pair_metrics_normalized_values_present():
    metrics = compute_pair_metrics(_bell(), (0, 1))
    for m in metrics:
        if m.metric_name in ("concurrence", "entropy"):
            assert m.normalized_value is not None
            assert 0.0 <= m.normalized_value <= 1.0


def test_pair_metrics_interpretation_present():
    metrics = compute_pair_metrics(_bell(), (0, 1))
    for m in metrics:
        assert m.interpretation is not None and len(m.interpretation) > 0


def test_pair_filter_metric_preference():
    metrics = compute_pair_metrics(
        _bell(), (0, 1), metric_preference=["concurrence"]
    )
    names = [m.metric_name for m in metrics]
    assert names == ["concurrence"]


# ---------------------------------------------------------------------------
# is_entangled_from_metrics
# ---------------------------------------------------------------------------


def test_is_entangled_bell_state():
    metrics = compute_pair_metrics(_bell(), (0, 1))
    assert is_entangled_from_metrics(metrics) is True


def test_is_not_entangled_product_state():
    metrics = compute_pair_metrics(_ket_00(), (0, 1))
    assert is_entangled_from_metrics(metrics) is False


def test_is_entangled_returns_none_for_empty_metrics():
    assert is_entangled_from_metrics([]) is None
