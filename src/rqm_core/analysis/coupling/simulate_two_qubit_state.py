"""Pure-state 2-qubit circuit simulation.

This module implements an ideal statevector simulator restricted to
2-qubit circuits starting from |00⟩.  It is additive and deliberately
narrow in scope: it supports the common gates needed for coupling
analysis and degrades cleanly for anything outside that scope.

Architecture note
-----------------
This simulator handles the *multi-qubit* structure of a circuit — it
is not a replacement for the quaternionic single-qubit optimizer.  The
single-qubit gates are represented here as 2×2 complex matrices applied
inside a 4-dimensional state space; the quaternionic layer remains the
canonical route for compiling / optimising single-qubit rotations.

Supported gates
---------------
Single-qubit: ``I``, ``X``, ``Y``, ``Z``, ``H``, ``S``, ``T``,
              ``Rx(θ)``, ``Ry(θ)``, ``Rz(θ)``, ``U(θ,φ,λ)`` / ``U3(θ,φ,λ)``
Two-qubit:    ``CNOT`` / ``CX`` (control, target),
              ``CZ`` (symmetric),
              ``SWAP`` (symmetric)

Qubit ordering convention
--------------------------
The state vector has dimension 4 with basis ordering::

    index 0 → |00⟩    (q0=0, q1=0)
    index 1 → |01⟩    (q0=0, q1=1)
    index 2 → |10⟩    (q0=1, q1=0)
    index 3 → |11⟩    (q0=1, q1=1)

Qubit 0 is the *most significant bit* (leftmost in the ket).
Single-qubit gate on qubit 0: full operator = gate ⊗ I
Single-qubit gate on qubit 1: full operator = I ⊗ gate
"""

from __future__ import annotations

import cmath
import math

import numpy as np
from numpy.typing import NDArray

from rqm_core.analysis.coupling.types import (
    Circuit,
    SUPPORTED_SINGLE_QUBIT_GATES,
    SUPPORTED_TWO_QUBIT_GATES,
    GateOp,
)

# ---------------------------------------------------------------------------
# 2×2 single-qubit gate matrices (standard unitary form)
# ---------------------------------------------------------------------------

_I2 = np.eye(2, dtype=np.complex128)


def _gate_matrix_1q(op: GateOp) -> NDArray[np.complex128] | None:
    """Return the 2×2 unitary for *op*, or ``None`` if unsupported.

    All matrices use the standard unitary form (not the SU(2) form with
    adjusted global phase).  For state simulation the global phase is
    irrelevant for entanglement metrics; for fidelity it cancels because
    |⟨ψ₁|ψ₂⟩|² is phase-invariant.
    """
    name = op.name.upper()

    if name == "I":
        return _I2.copy()

    if name == "X":
        return np.array([[0, 1], [1, 0]], dtype=np.complex128)

    if name == "Y":
        return np.array([[0, -1j], [1j, 0]], dtype=np.complex128)

    if name == "Z":
        return np.array([[1, 0], [0, -1]], dtype=np.complex128)

    if name == "H":
        s = 1.0 / math.sqrt(2.0)
        return np.array([[s, s], [s, -s]], dtype=np.complex128)

    if name == "S":
        return np.array([[1, 0], [0, 1j]], dtype=np.complex128)

    if name == "T":
        return np.array(
            [[1, 0], [0, cmath.exp(1j * math.pi / 4.0)]], dtype=np.complex128
        )

    if name == "RX":
        if not op.params:
            return None
        theta = op.params[0]
        c = math.cos(theta / 2.0)
        s = math.sin(theta / 2.0)
        return np.array([[c, -1j * s], [-1j * s, c]], dtype=np.complex128)

    if name == "RY":
        if not op.params:
            return None
        theta = op.params[0]
        c = math.cos(theta / 2.0)
        s = math.sin(theta / 2.0)
        return np.array([[c, -s], [s, c]], dtype=np.complex128)

    if name == "RZ":
        if not op.params:
            return None
        theta = op.params[0]
        return np.array(
            [
                [cmath.exp(-1j * theta / 2.0), 0],
                [0, cmath.exp(1j * theta / 2.0)],
            ],
            dtype=np.complex128,
        )

    if name in ("U", "U3"):
        if len(op.params) < 3:
            return None
        theta, phi, lam = op.params[0], op.params[1], op.params[2]
        c = math.cos(theta / 2.0)
        s = math.sin(theta / 2.0)
        return np.array(
            [
                [c, -cmath.exp(1j * lam) * s],
                [cmath.exp(1j * phi) * s, cmath.exp(1j * (phi + lam)) * c],
            ],
            dtype=np.complex128,
        )

    return None  # unsupported gate


# ---------------------------------------------------------------------------
# 4×4 two-qubit gate matrices
# ---------------------------------------------------------------------------

# Basis ordering: |00⟩=0, |01⟩=1, |10⟩=2, |11⟩=3 (q0 = MSB).

_CNOT_Q0_CTRL_Q1_TGT = np.array(
    [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0],
    ],
    dtype=np.complex128,
)
"""CNOT with qubit 0 as control and qubit 1 as target."""

_CNOT_Q1_CTRL_Q0_TGT = np.array(
    [
        [1, 0, 0, 0],
        [0, 0, 0, 1],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
    ],
    dtype=np.complex128,
)
"""CNOT with qubit 1 as control and qubit 0 as target."""

_CZ = np.array(
    [
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, -1],
    ],
    dtype=np.complex128,
)
"""CZ gate (symmetric)."""

_SWAP = np.array(
    [
        [1, 0, 0, 0],
        [0, 0, 1, 0],
        [0, 1, 0, 0],
        [0, 0, 0, 1],
    ],
    dtype=np.complex128,
)
"""SWAP gate (symmetric)."""


def _gate_matrix_2q(op: GateOp) -> NDArray[np.complex128] | None:
    """Return the 4×4 unitary for *op* acting on 2 qubits, or ``None``."""
    name = op.name.upper()
    qubits = op.qubits

    if name in ("CNOT", "CX"):
        if len(qubits) < 2:
            return None
        if qubits[0] == 0 and qubits[1] == 1:
            return _CNOT_Q0_CTRL_Q1_TGT.copy()
        if qubits[0] == 1 and qubits[1] == 0:
            return _CNOT_Q1_CTRL_Q0_TGT.copy()
        return None  # unsupported qubit indices

    if name == "CZ":
        return _CZ.copy()

    if name == "SWAP":
        return _SWAP.copy()

    return None


# ---------------------------------------------------------------------------
# Full operator builder
# ---------------------------------------------------------------------------


def _build_full_operator(op: GateOp, num_qubits: int) -> NDArray[np.complex128] | None:
    """Return the full 2^n × 2^n operator for *op*, or ``None`` if unsupported.

    For the 2-qubit case (``num_qubits == 2``):
    - Single-qubit gate on qubit 0 → ``gate ⊗ I``
    - Single-qubit gate on qubit 1 → ``I ⊗ gate``
    - Two-qubit gate → directly returned from :func:`_gate_matrix_2q`

    Only ``num_qubits == 2`` is currently supported.
    """
    if num_qubits != 2:
        return None

    name = op.name.upper()
    is_single_q = name in {g.upper() for g in SUPPORTED_SINGLE_QUBIT_GATES}
    is_two_q = name in {g.upper() for g in SUPPORTED_TWO_QUBIT_GATES}

    if is_single_q:
        if len(op.qubits) < 1:
            return None
        qubit = op.qubits[0]
        m = _gate_matrix_1q(op)
        if m is None:
            return None
        if qubit == 0:
            return np.kron(m, _I2)
        if qubit == 1:
            return np.kron(_I2, m)
        return None  # qubit index out of range

    if is_two_q:
        return _gate_matrix_2q(op)

    return None  # gate not recognised


# ---------------------------------------------------------------------------
# Public simulation entry point
# ---------------------------------------------------------------------------


def simulate_two_qubit_state(
    circuit: Circuit,
) -> NDArray[np.complex128] | None:
    """Simulate a 2-qubit circuit and return the final pure statevector.

    Starts from |00⟩ and applies each gate in order.  Returns the final
    normalised statevector of shape ``(4,)``, or ``None`` if the circuit
    cannot be simulated (unsupported gate, wrong qubit count, etc.).

    Returning ``None`` rather than raising allows the caller to degrade
    cleanly to qualitative analysis mode without exceptions.

    Args:
        circuit: The circuit to simulate.  Must have ``num_qubits == 2``.

    Returns:
        Complex statevector of shape ``(4,)`` if simulation succeeded,
        or ``None`` if any gate is unsupported or the circuit is not
        2-qubit.

    Notes:
        - The initial state is always |00⟩ = ``[1, 0, 0, 0]``.
        - Supported single-qubit gates: I, X, Y, Z, H, S, T,
          Rx(θ), Ry(θ), Rz(θ), U(θ,φ,λ) / U3(θ,φ,λ).
        - Supported two-qubit gates: CNOT/CX, CZ, SWAP.
        - Gate names are matched case-insensitively.
    """
    if circuit.num_qubits != 2:
        return None

    # Initialise |00⟩
    sv: NDArray[np.complex128] = np.array(
        [1.0, 0.0, 0.0, 0.0], dtype=np.complex128
    )

    for op in circuit.operations:
        full_op = _build_full_operator(op, num_qubits=2)
        if full_op is None:
            # Unsupported gate encountered — abort and signal failure.
            return None
        sv = full_op @ sv

    return sv
