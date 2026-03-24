"""Tests for analyze_optimization_preservation."""

import math

import pytest

from rqm_core.analysis.coupling.types import (
    Circuit,
    GateOp,
    CouplingAnalysisOptions,
)
from rqm_core.analysis.coupling.analyze_optimization_preservation import (
    analyze_optimization_preservation,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _circuit(*ops: GateOp, num_qubits: int = 2) -> Circuit:
    return Circuit(num_qubits=num_qubits, operations=list(ops))


def _op(name: str, qubits: list[int], params: list[float] | None = None) -> GateOp:
    return GateOp(name=name, qubits=qubits, params=params or [])


def _bell():
    return _circuit(_op("H", [0]), _op("CNOT", [0, 1]))


# ---------------------------------------------------------------------------
# Fidelity preservation — identical circuits
# ---------------------------------------------------------------------------


def test_identical_circuits_fidelity_one():
    result = analyze_optimization_preservation(_bell(), _bell())
    assert result.fidelity_preserved is not None
    assert result.fidelity_preserved == pytest.approx(1.0, abs=1e-9)


def test_identical_separable_circuits_fidelity_one():
    c = _circuit(_op("H", [0]))
    result = analyze_optimization_preservation(c, c)
    assert result.fidelity_preserved is not None
    assert result.fidelity_preserved == pytest.approx(1.0, abs=1e-9)


def test_empty_circuits_fidelity_one():
    c = _circuit()
    result = analyze_optimization_preservation(c, c)
    assert result.fidelity_preserved is not None
    assert result.fidelity_preserved == pytest.approx(1.0, abs=1e-9)


# ---------------------------------------------------------------------------
# Fidelity — different circuits
# ---------------------------------------------------------------------------


def test_different_circuits_fidelity_not_one():
    original = _bell()
    optimized = _circuit(_op("X", [0]))  # |10⟩
    result = analyze_optimization_preservation(original, optimized)
    assert result.fidelity_preserved is not None
    assert result.fidelity_preserved < 0.5


# ---------------------------------------------------------------------------
# Result structure
# ---------------------------------------------------------------------------


def test_result_has_both_coupling_analyses():
    result = analyze_optimization_preservation(_bell(), _bell())
    assert result.original_coupling is not None
    assert result.optimized_coupling is not None


def test_original_coupling_mode_measured():
    result = analyze_optimization_preservation(_bell(), _bell())
    assert result.original_coupling.mode == "measured"


def test_optimized_coupling_mode_measured():
    result = analyze_optimization_preservation(_bell(), _bell())
    assert result.optimized_coupling.mode == "measured"


def test_notes_list_present():
    result = analyze_optimization_preservation(_bell(), _bell())
    assert isinstance(result.notes, list)
    assert len(result.notes) > 0


# ---------------------------------------------------------------------------
# Entanglement structure preservation
# ---------------------------------------------------------------------------


def test_entanglement_structure_preserved_identical_bell():
    result = analyze_optimization_preservation(_bell(), _bell())
    assert result.preserved_entanglement_structure is True


def test_entanglement_structure_not_preserved_when_mismatch():
    """Bell → entangled; separable circuit → not entangled; should flag mismatch."""
    original = _bell()
    optimized = _circuit(_op("H", [0]))  # separable
    result = analyze_optimization_preservation(original, optimized)
    assert result.preserved_entanglement_structure is False


def test_entanglement_structure_none_for_qualitative():
    """3-qubit circuit → qualitative → preserved_entanglement_structure is None."""
    c = _circuit(_op("H", [0]), _op("CNOT", [0, 1]), num_qubits=3)
    result = analyze_optimization_preservation(c, c)
    # Both circuits are qualitative (>2 qubits) → None
    assert result.preserved_entanglement_structure is None


# ---------------------------------------------------------------------------
# Fidelity unavailable for unsimulatable circuits
# ---------------------------------------------------------------------------


def test_fidelity_none_for_unsupported_gate():
    c = _circuit(_op("H", [0]), _op("CCX", [0, 1]))  # Toffoli unsupported
    result = analyze_optimization_preservation(c, c)
    assert result.fidelity_preserved is None
    assert any("not available" in n.lower() or "could not" in n.lower() for n in result.notes)


def test_fidelity_none_for_three_qubit():
    c = _circuit(_op("H", [0]), _op("CNOT", [0, 1]), num_qubits=3)
    result = analyze_optimization_preservation(c, c)
    assert result.fidelity_preserved is None


# ---------------------------------------------------------------------------
# CZ equivalent to H-CNOT-H (up to local rotations)
# Result: both are entangling, fidelity between Bell and CZ state is not 1
# but preserved_entanglement_structure checks classification only
# ---------------------------------------------------------------------------


def test_both_entangling_circuits_preserve_structure():
    """Two different entangling circuits both produce entangled states.

    The fidelity between the final states will not be 1, but
    preserved_entanglement_structure should be True because both
    circuits produce entangled states (concurrence > 0).
    """
    bell = _bell()
    cz_circuit = _circuit(
        _op("H", [0]),
        _op("H", [1]),
        _op("CZ", [0, 1]),
        _op("H", [1]),
    )
    result = analyze_optimization_preservation(bell, cz_circuit)
    # Both produce entangled states → structure preserved (same classification)
    assert result.preserved_entanglement_structure is True
