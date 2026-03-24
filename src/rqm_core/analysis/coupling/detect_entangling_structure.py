"""Qualitative gate-based entanglement detection.

This module scans a circuit's operation list for gates that are known to
be *capable* of producing entanglement and returns a structured summary.

Important distinction
---------------------
Gate *presence* does not guarantee the resulting state is entangled.
For example, a CNOT applied to |10⟩ produces |11⟩ — a separable state.
This function intentionally stops at "entangling gate detected"; the
measured analysis layer (:mod:`~rqm_core.analysis.coupling.metrics`)
makes the entanglement determination from the actual state vector.

This layer corresponds to the ``provenance = "parser"`` path.
"""

from __future__ import annotations

from rqm_core.analysis.coupling.types import (
    Circuit,
    ENTANGLING_GATE_NAMES,
    QualitativeStructure,
)

# Map of known entangling gates to their canonical display form.
_CANONICAL_ENTANGLING_NAME: dict[str, str] = {
    "CNOT": "CNOT",
    "CX": "CX",
    "CZ": "CZ",
    "SWAP": "SWAP",
}


def _format_gate_label(op_name: str, qubits: list[int]) -> str:
    """Return a human-readable label for a two-qubit gate instance."""
    if op_name in ("CNOT", "CX"):
        if len(qubits) >= 2:
            return f"{op_name} q{qubits[0]}->q{qubits[1]}"
    if len(qubits) >= 2:
        return f"{op_name} q{qubits[0]},q{qubits[1]}"
    return f"{op_name} q{qubits[0]}"


def detect_entangling_structure(circuit: Circuit) -> QualitativeStructure:
    """Scan *circuit* for entangling gates and return a qualitative summary.

    This function performs a linear pass through ``circuit.operations``
    and identifies multi-qubit gates that are known to be *capable* of
    producing entanglement.  No state simulation is performed.

    Args:
        circuit: The circuit to scan.

    Returns:
        :class:`~rqm_core.analysis.coupling.types.QualitativeStructure`
        summarising what was found.

    Notes:
        - The return value contains ``candidate_pairs``: qubit pairs
          involved in entangling-capable gates.  These are *candidates*
          for the measured analysis, not confirmed entangled pairs.
        - SWAP is included as a multi-qubit interaction even though it
          does not always produce entanglement; the measured path
          resolves this correctly.
    """
    has_entangling_gates = False
    entangling_gate_count = 0
    seen_names_ordered: list[str] = []
    seen_names_set: set[str] = set()
    last_entangling_gate: str | None = None
    candidate_pairs_ordered: list[tuple[int, int]] = []
    candidate_pairs_set: set[tuple[int, int]] = set()

    for op in circuit.operations:
        upper = op.name.upper()
        canonical = _CANONICAL_ENTANGLING_NAME.get(upper)
        if canonical is None:
            # Not a known entangling gate — skip.
            continue

        has_entangling_gates = True
        entangling_gate_count += 1
        last_entangling_gate = _format_gate_label(op.name, op.qubits)

        if canonical not in seen_names_set:
            seen_names_ordered.append(canonical)
            seen_names_set.add(canonical)

        if len(op.qubits) >= 2:
            pair: tuple[int, int] = (op.qubits[0], op.qubits[1])
            if pair not in candidate_pairs_set:
                candidate_pairs_ordered.append(pair)
                candidate_pairs_set.add(pair)

    return QualitativeStructure(
        has_entangling_gates=has_entangling_gates,
        entangling_gate_count=entangling_gate_count,
        entangling_gates_seen=seen_names_ordered,
        last_entangling_gate=last_entangling_gate,
        candidate_pairs=candidate_pairs_ordered,
    )
