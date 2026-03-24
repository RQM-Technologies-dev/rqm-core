"""Tests for the main analyze_circuit_coupling entry point.

Each test case corresponds to a scenario from the problem specification:
  A. Separable product state (H on q0 only, no entangling gate)
  B. Bell state (H q0, CNOT q0→q1) — maximally entangled
  C. CNOT on basis state without superposition — entangling gate, separable result
  D. SWAP-only circuit — multi-qubit, state may still be separable
  E. Fidelity preservation (identical or equivalent circuits)
  F. Unsupported scope (>2 qubits or unsupported gate)
"""

import math

import pytest

from rqm_core.analysis.coupling.types import (
    Circuit,
    GateOp,
    CouplingAnalysisOptions,
)
from rqm_core.analysis.coupling.analyze_circuit_coupling import (
    analyze_circuit_coupling,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _circuit(*ops: GateOp, num_qubits: int = 2) -> Circuit:
    return Circuit(num_qubits=num_qubits, operations=list(ops))


def _op(name: str, qubits: list[int], params: list[float] | None = None) -> GateOp:
    return GateOp(name=name, qubits=qubits, params=params or [])


# ---------------------------------------------------------------------------
# A. Separable product state — H on q0 only, no entangling gate
# ---------------------------------------------------------------------------


class TestSeparableProductState:
    def _circuit(self):
        return _circuit(_op("H", [0]))  # H on q0 only — |+0⟩ (separable)

    def test_mode_is_measured(self):
        result = analyze_circuit_coupling(self._circuit())
        assert result.mode == "measured"

    def test_provenance_is_rqm_core(self):
        result = analyze_circuit_coupling(self._circuit())
        assert result.provenance == "rqm-core"

    def test_no_entangling_gates_qualitative(self):
        result = analyze_circuit_coupling(self._circuit())
        assert result.has_entangling_gates is False
        assert result.entangling_gate_count == 0
        assert result.entangling_gates_seen == []

    def test_is_not_entangled(self):
        result = analyze_circuit_coupling(self._circuit())
        assert result.is_entangled is False

    def test_concurrence_near_zero(self):
        result = analyze_circuit_coupling(self._circuit())
        c = next(m for m in result.pair_metrics if m.metric_name == "concurrence")
        assert c.value == pytest.approx(0.0, abs=1e-6)

    def test_entropy_near_zero(self):
        result = analyze_circuit_coupling(self._circuit())
        e = next(m for m in result.pair_metrics if m.metric_name == "entropy")
        assert e.value == pytest.approx(0.0, abs=1e-6)

    def test_qubit_count(self):
        result = analyze_circuit_coupling(self._circuit())
        assert result.qubit_count == 2

    def test_fidelity_preserved_none_without_comparison(self):
        result = analyze_circuit_coupling(self._circuit())
        assert result.fidelity_preserved is None


# ---------------------------------------------------------------------------
# B. Bell state — H q0, CNOT q0→q1
# ---------------------------------------------------------------------------


class TestBellState:
    def _circuit(self):
        return _circuit(_op("H", [0]), _op("CNOT", [0, 1]))

    def test_mode_is_measured(self):
        result = analyze_circuit_coupling(self._circuit())
        assert result.mode == "measured"

    def test_has_entangling_gates(self):
        result = analyze_circuit_coupling(self._circuit())
        assert result.has_entangling_gates is True
        assert result.entangling_gate_count == 1
        assert "CNOT" in result.entangling_gates_seen

    def test_is_entangled_true(self):
        result = analyze_circuit_coupling(self._circuit())
        assert result.is_entangled is True

    def test_concurrence_near_one(self):
        result = analyze_circuit_coupling(self._circuit())
        c = next(m for m in result.pair_metrics if m.metric_name == "concurrence")
        assert c.value == pytest.approx(1.0, abs=1e-6)

    def test_entropy_near_one(self):
        result = analyze_circuit_coupling(self._circuit())
        e = next(m for m in result.pair_metrics if m.metric_name == "entropy")
        assert e.value == pytest.approx(1.0, abs=1e-6)

    def test_last_entangling_gate_contains_cnot(self):
        result = analyze_circuit_coupling(self._circuit())
        assert result.last_entangling_gate is not None
        assert "CNOT" in result.last_entangling_gate

    def test_analyzed_pairs_contains_0_1(self):
        result = analyze_circuit_coupling(self._circuit())
        assert (0, 1) in result.analyzed_pairs

    def test_pair_metrics_have_normalized_values(self):
        result = analyze_circuit_coupling(self._circuit())
        for m in result.pair_metrics:
            if m.metric_name in ("concurrence", "entropy"):
                assert m.normalized_value is not None
                assert 0.0 <= m.normalized_value <= 1.0


# ---------------------------------------------------------------------------
# C. CNOT on basis state without superposition — gate present, state separable
# ---------------------------------------------------------------------------


class TestCNOTNoSuperposition:
    """X q0, CNOT q0→q1: produces |11⟩ — a separable state."""

    def _circuit(self):
        return _circuit(_op("X", [0]), _op("CNOT", [0, 1]))

    def test_has_entangling_gates_true(self):
        result = analyze_circuit_coupling(self._circuit())
        assert result.has_entangling_gates is True

    def test_is_not_entangled(self):
        """Proving gate presence ≠ guaranteed entanglement."""
        result = analyze_circuit_coupling(self._circuit())
        assert result.is_entangled is False

    def test_concurrence_near_zero(self):
        result = analyze_circuit_coupling(self._circuit())
        c = next(m for m in result.pair_metrics if m.metric_name == "concurrence")
        assert c.value == pytest.approx(0.0, abs=1e-6)

    def test_mode_is_measured(self):
        result = analyze_circuit_coupling(self._circuit())
        assert result.mode == "measured"


# ---------------------------------------------------------------------------
# D. SWAP-only circuit — multi-qubit interaction, state may still be separable
# ---------------------------------------------------------------------------


class TestSWAPOnly:
    def _circuit(self):
        return _circuit(_op("SWAP", [0, 1]))

    def test_swap_detected_qualitatively(self):
        result = analyze_circuit_coupling(self._circuit())
        assert result.has_entangling_gates is True
        assert "SWAP" in result.entangling_gates_seen

    def test_swap_does_not_falsely_claim_entanglement(self):
        """SWAP on |00⟩ leaves |00⟩ — separable."""
        result = analyze_circuit_coupling(self._circuit())
        assert result.mode == "measured"
        assert result.is_entangled is False

    def test_swap_concurrence_zero(self):
        result = analyze_circuit_coupling(self._circuit())
        c = next(m for m in result.pair_metrics if m.metric_name == "concurrence")
        assert c.value == pytest.approx(0.0, abs=1e-6)

    def test_swap_followed_by_h_not_entangled(self):
        """X q0, SWAP: |10⟩ → |01⟩, still separable."""
        c = _circuit(_op("X", [0]), _op("SWAP", [0, 1]))
        result = analyze_circuit_coupling(c)
        assert result.is_entangled is False


# ---------------------------------------------------------------------------
# E. Fidelity preservation — identical circuits
# ---------------------------------------------------------------------------


class TestFidelityPreservation:
    def _bell_circuit(self):
        return _circuit(_op("H", [0]), _op("CNOT", [0, 1]))

    def test_fidelity_identical_circuits_is_one(self):
        original = self._bell_circuit()
        options = CouplingAnalysisOptions(compare_against_circuit=self._bell_circuit())
        result = analyze_circuit_coupling(original, options)
        assert result.fidelity_preserved is not None
        assert result.fidelity_preserved == pytest.approx(1.0, abs=1e-9)

    def test_fidelity_different_states_not_one(self):
        original = self._bell_circuit()
        different = _circuit(_op("X", [0]))  # |10⟩ — orthogonal to Bell
        options = CouplingAnalysisOptions(compare_against_circuit=different)
        result = analyze_circuit_coupling(original, options)
        assert result.fidelity_preserved is not None
        assert result.fidelity_preserved < 0.5

    def test_fidelity_note_added_to_result(self):
        original = self._bell_circuit()
        options = CouplingAnalysisOptions(compare_against_circuit=self._bell_circuit())
        result = analyze_circuit_coupling(original, options)
        assert any("fidelity" in n.lower() for n in result.notes)

    def test_fidelity_unavailable_without_compare_circuit(self):
        result = analyze_circuit_coupling(self._bell_circuit())
        assert result.fidelity_preserved is None


# ---------------------------------------------------------------------------
# F. Unsupported scope — >2 qubits
# ---------------------------------------------------------------------------


class TestUnsupportedScope:
    def test_three_qubit_circuit_qualitative_mode(self):
        c = _circuit(_op("H", [0]), _op("CNOT", [0, 1]), num_qubits=3)
        result = analyze_circuit_coupling(c)
        assert result.mode == "qualitative"

    def test_three_qubit_limitations_honest(self):
        c = _circuit(_op("H", [0]), _op("CNOT", [0, 1]), num_qubits=3)
        result = analyze_circuit_coupling(c)
        assert len(result.limitations) > 0

    def test_three_qubit_no_fake_measured_values(self):
        c = _circuit(_op("H", [0]), _op("CNOT", [0, 1]), num_qubits=3)
        result = analyze_circuit_coupling(c)
        assert result.is_entangled is None
        assert result.pair_metrics == []

    def test_three_qubit_qualitative_still_detects_gates(self):
        c = _circuit(_op("H", [0]), _op("CNOT", [0, 1]), num_qubits=3)
        result = analyze_circuit_coupling(c)
        assert result.has_entangling_gates is True
        assert result.entangling_gate_count == 1

    def test_unsupported_gate_name_qualitative_fallback(self):
        """A gate not in the supported list should cause qualitative fallback."""
        c = _circuit(_op("H", [0]), _op("CCX", [0, 1]))  # Toffoli
        result = analyze_circuit_coupling(c)
        assert result.mode == "qualitative"
        assert result.is_entangled is None

    def test_unsupported_gate_limitations_honest(self):
        c = _circuit(_op("H", [0]), _op("CCX", [0, 1]))
        result = analyze_circuit_coupling(c)
        assert len(result.limitations) > 0


# ---------------------------------------------------------------------------
# Result contract shape
# ---------------------------------------------------------------------------


class TestResultContract:
    """Verify the stable result contract shape expected by rqm-api / Studio."""

    def test_all_required_fields_present_measured(self):
        result = analyze_circuit_coupling(
            _circuit(_op("H", [0]), _op("CNOT", [0, 1]))
        )
        assert isinstance(result.mode, str)
        assert isinstance(result.provenance, str)
        assert isinstance(result.qubit_count, int)
        assert isinstance(result.analyzed_pairs, list)
        assert isinstance(result.has_entangling_gates, bool)
        assert isinstance(result.entangling_gate_count, int)
        assert isinstance(result.entangling_gates_seen, list)
        assert isinstance(result.pair_metrics, list)
        assert isinstance(result.notes, list)
        assert isinstance(result.limitations, list)

    def test_all_required_fields_present_qualitative(self):
        c = _circuit(_op("H", [0]), _op("CNOT", [0, 1]), num_qubits=3)
        result = analyze_circuit_coupling(c)
        assert isinstance(result.mode, str)
        assert result.is_entangled is None
        assert result.pair_metrics == []
        assert len(result.limitations) > 0

    def test_pair_metric_fields(self):
        result = analyze_circuit_coupling(
            _circuit(_op("H", [0]), _op("CNOT", [0, 1]))
        )
        for m in result.pair_metrics:
            assert isinstance(m.pair, tuple)
            assert isinstance(m.metric_name, str)
            assert isinstance(m.value, float)
            assert m.normalized_value is None or isinstance(m.normalized_value, float)


# ---------------------------------------------------------------------------
# Metric preference option
# ---------------------------------------------------------------------------


def test_metric_preference_concurrence_only():
    c = _circuit(_op("H", [0]), _op("CNOT", [0, 1]))
    options = CouplingAnalysisOptions(metric_preference=["concurrence"])
    result = analyze_circuit_coupling(c, options)
    names = [m.metric_name for m in result.pair_metrics]
    assert "concurrence" in names
    assert "entropy" not in names


def test_metric_preference_entropy_only():
    c = _circuit(_op("H", [0]), _op("CNOT", [0, 1]))
    options = CouplingAnalysisOptions(metric_preference=["entropy"])
    result = analyze_circuit_coupling(c, options)
    names = [m.metric_name for m in result.pair_metrics]
    assert "entropy" in names
    assert "concurrence" not in names
