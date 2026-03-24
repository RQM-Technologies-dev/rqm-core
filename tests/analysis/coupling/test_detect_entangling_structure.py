"""Tests for detect_entangling_structure – qualitative gate-based detection."""

import pytest

from rqm_core.analysis.coupling.types import Circuit, GateOp
from rqm_core.analysis.coupling.detect_entangling_structure import (
    detect_entangling_structure,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _circuit(*ops: GateOp, num_qubits: int = 2) -> Circuit:
    return Circuit(num_qubits=num_qubits, operations=list(ops))


def _op(name: str, qubits: list[int], params: list[float] | None = None) -> GateOp:
    return GateOp(name=name, qubits=qubits, params=params or [])


# ---------------------------------------------------------------------------
# No entangling gates
# ---------------------------------------------------------------------------


def test_empty_circuit_no_entangling():
    result = detect_entangling_structure(_circuit())
    assert result.has_entangling_gates is False
    assert result.entangling_gate_count == 0
    assert result.entangling_gates_seen == []
    assert result.last_entangling_gate is None
    assert result.candidate_pairs == []


def test_single_qubit_only_no_entangling():
    c = _circuit(_op("H", [0]), _op("X", [1]), _op("Rz", [0], [1.0]))
    result = detect_entangling_structure(c)
    assert result.has_entangling_gates is False
    assert result.entangling_gate_count == 0


# ---------------------------------------------------------------------------
# CNOT detection
# ---------------------------------------------------------------------------


def test_cnot_detected():
    c = _circuit(_op("H", [0]), _op("CNOT", [0, 1]))
    result = detect_entangling_structure(c)
    assert result.has_entangling_gates is True
    assert result.entangling_gate_count == 1
    assert "CNOT" in result.entangling_gates_seen
    assert result.last_entangling_gate is not None
    assert "CNOT" in result.last_entangling_gate


def test_cx_alias_detected():
    c = _circuit(_op("CX", [0, 1]))
    result = detect_entangling_structure(c)
    assert result.has_entangling_gates is True
    assert "CX" in result.entangling_gates_seen


def test_cnot_candidate_pair_extracted():
    c = _circuit(_op("CNOT", [0, 1]))
    result = detect_entangling_structure(c)
    assert (0, 1) in result.candidate_pairs


# ---------------------------------------------------------------------------
# CZ detection
# ---------------------------------------------------------------------------


def test_cz_detected():
    c = _circuit(_op("CZ", [0, 1]))
    result = detect_entangling_structure(c)
    assert result.has_entangling_gates is True
    assert "CZ" in result.entangling_gates_seen
    assert (0, 1) in result.candidate_pairs


# ---------------------------------------------------------------------------
# SWAP detection
# ---------------------------------------------------------------------------


def test_swap_detected():
    c = _circuit(_op("SWAP", [0, 1]))
    result = detect_entangling_structure(c)
    assert result.has_entangling_gates is True
    assert "SWAP" in result.entangling_gates_seen
    assert (0, 1) in result.candidate_pairs


# ---------------------------------------------------------------------------
# Multiple entangling gates
# ---------------------------------------------------------------------------


def test_multiple_entangling_gates_counted():
    c = _circuit(
        _op("CNOT", [0, 1]),
        _op("CZ", [0, 1]),
        _op("CNOT", [0, 1]),
    )
    result = detect_entangling_structure(c)
    assert result.entangling_gate_count == 3


def test_distinct_gate_names_deduplicated():
    c = _circuit(
        _op("CNOT", [0, 1]),
        _op("CNOT", [0, 1]),
        _op("CZ", [0, 1]),
    )
    result = detect_entangling_structure(c)
    # CNOT appears first, CZ second; no duplicates in seen list
    assert result.entangling_gates_seen.count("CNOT") == 1
    assert "CZ" in result.entangling_gates_seen


def test_last_entangling_gate_is_last_in_order():
    c = _circuit(
        _op("CNOT", [0, 1]),
        _op("H", [0]),
        _op("CZ", [0, 1]),
    )
    result = detect_entangling_structure(c)
    assert result.last_entangling_gate is not None
    assert "CZ" in result.last_entangling_gate


# ---------------------------------------------------------------------------
# Gate name case-insensitivity
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["cnot", "Cnot", "CNOT", "cNoT"])
def test_cnot_case_insensitive(name):
    c = _circuit(_op(name, [0, 1]))
    result = detect_entangling_structure(c)
    assert result.has_entangling_gates is True


# ---------------------------------------------------------------------------
# Multi-qubit circuits (>2 qubits)
# ---------------------------------------------------------------------------


def test_three_qubit_circuit_detection():
    c = _circuit(_op("CNOT", [0, 1]), _op("CZ", [1, 2]), num_qubits=3)
    result = detect_entangling_structure(c)
    assert result.has_entangling_gates is True
    assert result.entangling_gate_count == 2
    assert (0, 1) in result.candidate_pairs
    assert (1, 2) in result.candidate_pairs


# ---------------------------------------------------------------------------
# Label format
# ---------------------------------------------------------------------------


def test_cnot_label_format():
    c = _circuit(_op("CNOT", [0, 1]))
    result = detect_entangling_structure(c)
    # Should contain qubit indices in a readable form
    assert "0" in result.last_entangling_gate
    assert "1" in result.last_entangling_gate


def test_cz_label_format():
    c = _circuit(_op("CZ", [0, 1]))
    result = detect_entangling_structure(c)
    assert result.last_entangling_gate is not None
