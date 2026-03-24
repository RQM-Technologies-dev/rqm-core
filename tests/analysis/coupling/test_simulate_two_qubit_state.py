"""Tests for the 2-qubit pure-state simulator."""

import math

import numpy as np
import pytest

from rqm_core.analysis.coupling.types import Circuit, GateOp
from rqm_core.analysis.coupling.simulate_two_qubit_state import (
    simulate_two_qubit_state,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _circuit(*ops: GateOp, num_qubits: int = 2) -> Circuit:
    return Circuit(num_qubits=num_qubits, operations=list(ops))


def _op(name: str, qubits: list[int], params: list[float] | None = None) -> GateOp:
    return GateOp(name=name, qubits=qubits, params=params or [])


def _sv_close(sv, expected, atol=1e-9):
    """Return True if statevectors agree up to global phase."""
    sv = np.asarray(sv, dtype=np.complex128)
    expected = np.asarray(expected, dtype=np.complex128)
    # Check element-wise closeness or closeness up to global phase factor.
    if np.allclose(sv, expected, atol=atol):
        return True
    # Find first non-zero expected element and compute the phase.
    for e in expected:
        if abs(e) > 1e-12:
            phase = e / abs(e)
            if np.allclose(sv, expected / phase, atol=atol):
                return True
    return False


# ---------------------------------------------------------------------------
# Basic sanity
# ---------------------------------------------------------------------------


def test_empty_circuit_returns_ket_00():
    sv = simulate_two_qubit_state(_circuit())
    assert sv is not None
    assert np.allclose(sv, [1, 0, 0, 0], atol=1e-12)


def test_identity_gate_leaves_ket_00():
    sv = simulate_two_qubit_state(_circuit(_op("I", [0]), _op("I", [1])))
    assert sv is not None
    assert np.allclose(sv, [1, 0, 0, 0], atol=1e-12)


def test_returns_none_for_non_2qubit_circuit():
    c = Circuit(num_qubits=3, operations=[])
    assert simulate_two_qubit_state(c) is None


def test_returns_none_for_unsupported_gate():
    c = _circuit(_op("CCX", [0, 1]))  # Toffoli – not supported
    assert simulate_two_qubit_state(c) is None


# ---------------------------------------------------------------------------
# Single-qubit gates
# ---------------------------------------------------------------------------


def test_x_gate_on_qubit_0():
    """X on q0: |00⟩ → |10⟩ = [0, 0, 1, 0]."""
    sv = simulate_two_qubit_state(_circuit(_op("X", [0])))
    assert sv is not None
    assert np.allclose(sv, [0, 0, 1, 0], atol=1e-12)


def test_x_gate_on_qubit_1():
    """X on q1: |00⟩ → |01⟩ = [0, 1, 0, 0]."""
    sv = simulate_two_qubit_state(_circuit(_op("X", [1])))
    assert sv is not None
    assert np.allclose(sv, [0, 1, 0, 0], atol=1e-12)


def test_hadamard_on_qubit_0():
    """H on q0: |00⟩ → |+0⟩ = [1, 0, 1, 0] / √2."""
    sv = simulate_two_qubit_state(_circuit(_op("H", [0])))
    assert sv is not None
    s = 1.0 / math.sqrt(2.0)
    assert np.allclose(sv, [s, 0, s, 0], atol=1e-9)


def test_hadamard_on_qubit_1():
    """H on q1: |00⟩ → |0+⟩ = [1, 1, 0, 0] / √2."""
    sv = simulate_two_qubit_state(_circuit(_op("H", [1])))
    assert sv is not None
    s = 1.0 / math.sqrt(2.0)
    assert np.allclose(sv, [s, s, 0, 0], atol=1e-9)


def test_s_gate():
    """S on q1 applied to |01⟩ (first X q1) should give i|01⟩."""
    sv = simulate_two_qubit_state(_circuit(_op("X", [1]), _op("S", [1])))
    assert sv is not None
    assert np.allclose(sv, [0, 1j, 0, 0], atol=1e-9)


def test_t_gate():
    t_phase = complex(math.cos(math.pi / 4), math.sin(math.pi / 4))
    sv = simulate_two_qubit_state(_circuit(_op("X", [1]), _op("T", [1])))
    assert sv is not None
    assert np.allclose(sv, [0, t_phase, 0, 0], atol=1e-9)


@pytest.mark.parametrize("theta", [0.0, math.pi / 4, math.pi / 2, math.pi])
def test_rx_on_qubit_0(theta):
    """Rx(θ) on q0 from |00⟩: state should be normalised."""
    sv = simulate_two_qubit_state(_circuit(_op("Rx", [0], [theta])))
    assert sv is not None
    assert abs(np.linalg.norm(sv) - 1.0) < 1e-9


@pytest.mark.parametrize("theta", [0.0, math.pi / 3, math.pi])
def test_ry_on_qubit_1(theta):
    sv = simulate_two_qubit_state(_circuit(_op("Ry", [1], [theta])))
    assert sv is not None
    assert abs(np.linalg.norm(sv) - 1.0) < 1e-9


@pytest.mark.parametrize("theta", [0.0, math.pi / 2, 2 * math.pi])
def test_rz_on_qubit_0(theta):
    sv = simulate_two_qubit_state(_circuit(_op("Rz", [0], [theta])))
    assert sv is not None
    assert abs(np.linalg.norm(sv) - 1.0) < 1e-9


def test_rx_pi_equals_x_up_to_phase():
    """Rx(π) and X are the same rotation up to global phase."""
    sv_rx = simulate_two_qubit_state(_circuit(_op("Rx", [0], [math.pi])))
    sv_x = simulate_two_qubit_state(_circuit(_op("X", [0])))
    assert sv_rx is not None and sv_x is not None
    # Fidelity should be 1
    overlap = abs(np.vdot(sv_rx, sv_x)) ** 2
    assert overlap == pytest.approx(1.0, abs=1e-9)


def test_u_gate_basic():
    """U(π, 0, π) = X up to global phase."""
    sv = simulate_two_qubit_state(_circuit(_op("U", [0], [math.pi, 0.0, math.pi])))
    sv_x = simulate_two_qubit_state(_circuit(_op("X", [0])))
    assert sv is not None and sv_x is not None
    fidelity = abs(np.vdot(sv, sv_x)) ** 2
    assert fidelity == pytest.approx(1.0, abs=1e-9)


def test_u3_alias():
    """U3 is accepted as an alias for U."""
    sv = simulate_two_qubit_state(_circuit(_op("U3", [0], [math.pi, 0.0, math.pi])))
    assert sv is not None


# ---------------------------------------------------------------------------
# Two-qubit gates
# ---------------------------------------------------------------------------


def test_cnot_on_ket_00():
    """CNOT(q0->q1) on |00⟩ leaves |00⟩."""
    sv = simulate_two_qubit_state(_circuit(_op("CNOT", [0, 1])))
    assert sv is not None
    assert np.allclose(sv, [1, 0, 0, 0], atol=1e-12)


def test_cnot_on_ket_10():
    """CNOT(q0->q1) on |10⟩ produces |11⟩."""
    sv = simulate_two_qubit_state(
        _circuit(_op("X", [0]), _op("CNOT", [0, 1]))
    )
    assert sv is not None
    assert np.allclose(sv, [0, 0, 0, 1], atol=1e-12)


def test_cnot_on_ket_01():
    """CNOT(q0->q1) on |01⟩ leaves |01⟩ (control=0, no flip)."""
    sv = simulate_two_qubit_state(
        _circuit(_op("X", [1]), _op("CNOT", [0, 1]))
    )
    assert sv is not None
    assert np.allclose(sv, [0, 1, 0, 0], atol=1e-12)


def test_cnot_reversed_control():
    """CNOT(q1->q0) on |01⟩ should produce |11⟩."""
    sv = simulate_two_qubit_state(
        _circuit(_op("X", [1]), _op("CNOT", [1, 0]))
    )
    assert sv is not None
    # |01⟩: q1=1 (control) → flip q0: |01⟩ → |11⟩
    assert np.allclose(sv, [0, 0, 0, 1], atol=1e-12)


def test_cx_alias_same_as_cnot():
    sv_cnot = simulate_two_qubit_state(_circuit(_op("CNOT", [0, 1])))
    sv_cx = simulate_two_qubit_state(_circuit(_op("CX", [0, 1])))
    assert sv_cnot is not None and sv_cx is not None
    assert np.allclose(sv_cnot, sv_cx, atol=1e-12)


def test_cz_on_ket_11():
    """CZ on |11⟩ should produce -|11⟩."""
    sv = simulate_two_qubit_state(
        _circuit(_op("X", [0]), _op("X", [1]), _op("CZ", [0, 1]))
    )
    assert sv is not None
    assert np.allclose(sv, [0, 0, 0, -1], atol=1e-12)


def test_cz_on_ket_00():
    """CZ on |00⟩ is the identity."""
    sv = simulate_two_qubit_state(_circuit(_op("CZ", [0, 1])))
    assert sv is not None
    assert np.allclose(sv, [1, 0, 0, 0], atol=1e-12)


def test_swap_on_ket_10():
    """SWAP on |10⟩ produces |01⟩."""
    sv = simulate_two_qubit_state(
        _circuit(_op("X", [0]), _op("SWAP", [0, 1]))
    )
    assert sv is not None
    assert np.allclose(sv, [0, 1, 0, 0], atol=1e-12)


def test_swap_on_ket_01():
    """SWAP on |01⟩ produces |10⟩."""
    sv = simulate_two_qubit_state(
        _circuit(_op("X", [1]), _op("SWAP", [0, 1]))
    )
    assert sv is not None
    assert np.allclose(sv, [0, 0, 1, 0], atol=1e-12)


# ---------------------------------------------------------------------------
# Bell state
# ---------------------------------------------------------------------------


def test_bell_state_h_cnot():
    """H q0, CNOT q0->q1 starting from |00⟩ produces Bell state (|00⟩+|11⟩)/√2."""
    sv = simulate_two_qubit_state(
        _circuit(_op("H", [0]), _op("CNOT", [0, 1]))
    )
    assert sv is not None
    s = 1.0 / math.sqrt(2.0)
    assert np.allclose(sv, [s, 0, 0, s], atol=1e-9)


# ---------------------------------------------------------------------------
# Normalisation invariant
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "ops",
    [
        [_op("H", [0]), _op("CNOT", [0, 1])],
        [_op("X", [0]), _op("CNOT", [0, 1])],
        [_op("H", [0]), _op("H", [1]), _op("CZ", [0, 1])],
        [_op("X", [0]), _op("SWAP", [0, 1])],
        [_op("Rx", [0], [0.7]), _op("Ry", [1], [1.3]), _op("CNOT", [0, 1])],
    ],
)
def test_statevector_is_always_normalised(ops):
    sv = simulate_two_qubit_state(_circuit(*ops))
    if sv is not None:
        assert abs(np.linalg.norm(sv) - 1.0) < 1e-9
