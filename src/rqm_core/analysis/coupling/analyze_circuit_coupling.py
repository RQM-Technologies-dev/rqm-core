"""Main public entry point for circuit coupling / entanglement analysis.

This module exposes :func:`analyze_circuit_coupling`, the single stable
function that rqm-api and RQM Studio consume.

Two-layer design
----------------
Step 1 – Qualitative detection (always runs):
    :func:`~rqm_core.analysis.coupling.detect_entangling_structure.detect_entangling_structure`
    scans the circuit for entangling-capable gates.  This is the
    ``provenance = "parser"`` path and it never makes claims about the
    actual quantum state.

Step 2 – Measured analysis (runs when the circuit is in scope):
    :func:`~rqm_core.analysis.coupling.simulate_two_qubit_state.simulate_two_qubit_state`
    computes the ideal pure statevector for 2-qubit circuits whose gates
    are all supported.  Concurrence and entropy are then derived from the
    statevector and used to classify entanglement deterministically.

    If this step fails (unsupported gate, >2 qubits, etc.) the result
    falls back to ``mode = "qualitative"`` with honest ``limitations``.

Step 3 – Fidelity (optional, runs when ``options.compare_against_circuit`` is set):
    Both circuits are simulated and the pure-state fidelity is computed.
    Qualitative notes are added if either circuit could not be simulated.

Architecture note
-----------------
The quaternionic / SU(2) single-qubit optimiser is the correct route for
local single-qubit structure.  This module handles the orthogonal
concern: multi-qubit entanglement / coupling.  Neither layer replaces the
other; they are mathematically complementary.
"""

from __future__ import annotations

from rqm_core.analysis.coupling.detect_entangling_structure import (
    detect_entangling_structure,
)
from rqm_core.analysis.coupling.metrics import (
    compute_pair_metrics,
    compute_pure_state_fidelity,
    is_entangled_from_metrics,
)
from rqm_core.analysis.coupling.simulate_two_qubit_state import (
    simulate_two_qubit_state,
)
from rqm_core.analysis.coupling.types import (
    Circuit,
    CouplingAnalysisOptions,
    CouplingAnalysisResult,
)

_QUALITATIVE_LIMITATION = (
    "Measured entanglement analysis is currently limited to supported "
    "ideal 2-qubit circuits."
)
_QUALITATIVE_NOTE = "Qualitative gate-based coupling detection only."

_DEFAULT_METRIC_PREFERENCE = ["concurrence", "entropy"]


def _qualitative_result(
    circuit: Circuit,
    qualitative,
    notes: list[str],
    limitations: list[str],
    fidelity_preserved: float | None = None,
) -> CouplingAnalysisResult:
    """Build a qualitative-mode result from a :class:`QualitativeStructure`."""
    pairs = qualitative.candidate_pairs or []
    return CouplingAnalysisResult(
        mode="qualitative",
        provenance="parser",
        qubit_count=circuit.num_qubits,
        analyzed_pairs=pairs,
        has_entangling_gates=qualitative.has_entangling_gates,
        entangling_gate_count=qualitative.entangling_gate_count,
        entangling_gates_seen=qualitative.entangling_gates_seen,
        last_entangling_gate=qualitative.last_entangling_gate,
        is_entangled=None,
        pair_metrics=[],
        fidelity_preserved=fidelity_preserved,
        notes=notes,
        limitations=limitations,
    )


def analyze_circuit_coupling(
    circuit: Circuit,
    options: CouplingAnalysisOptions | None = None,
) -> CouplingAnalysisResult:
    """Analyse the coupling / entanglement structure of *circuit*.

    Returns a :class:`~rqm_core.analysis.coupling.types.CouplingAnalysisResult`
    that is ready for direct consumption by rqm-api and RQM Studio.

    The result ``mode`` is:
    - ``"measured"`` – when ideal pure-state simulation succeeded and
      metrics (concurrence, entropy) were computed.
    - ``"qualitative"`` – when the circuit is outside the measured scope
      (>2 qubits, unsupported gate, etc.).  Honest ``limitations`` are
      always included.

    The result is *never* fabricated: ``is_entangled`` is only set to a
    boolean when a measured metric confirms it.

    Args:
        circuit: The circuit to analyse.
        options: Optional :class:`~rqm_core.analysis.coupling.types.CouplingAnalysisOptions`.

    Returns:
        :class:`~rqm_core.analysis.coupling.types.CouplingAnalysisResult`
    """
    if options is None:
        options = CouplingAnalysisOptions()

    metric_preference = options.metric_preference or _DEFAULT_METRIC_PREFERENCE
    notes: list[str] = []
    limitations: list[str] = []

    # ------------------------------------------------------------------
    # Step 1: Qualitative detection (always runs)
    # ------------------------------------------------------------------
    qualitative = detect_entangling_structure(circuit)

    # ------------------------------------------------------------------
    # Step 2: Measured analysis (2-qubit circuits only)
    # ------------------------------------------------------------------
    sv = None
    if circuit.num_qubits == 2:
        sv = simulate_two_qubit_state(circuit)
        if sv is None:
            limitations.append(
                "One or more gates in this circuit are not supported by "
                "the 2-qubit statevector simulator.  "
                + _QUALITATIVE_LIMITATION
            )

    elif options.allow_qualitative_fallback:
        limitations.append(_QUALITATIVE_LIMITATION)

    # ------------------------------------------------------------------
    # Step 3: Fidelity against comparison circuit (optional)
    # ------------------------------------------------------------------
    fidelity_preserved: float | None = None
    if options.compare_against_circuit is not None:
        ref_sv = None
        if options.compare_against_circuit.num_qubits == 2:
            ref_sv = simulate_two_qubit_state(options.compare_against_circuit)

        if sv is not None and ref_sv is not None:
            fidelity_preserved = compute_pure_state_fidelity(sv, ref_sv)
            notes.append(
                f"State fidelity computed between the two circuits: "
                f"{fidelity_preserved:.6f}"
            )
        else:
            notes.append(
                "Fidelity comparison was requested but at least one circuit "
                "could not be simulated.  Fidelity is not available."
            )

    # ------------------------------------------------------------------
    # Return qualitative result if simulation failed or was not applicable
    # ------------------------------------------------------------------
    if sv is None:
        notes_out = [_QUALITATIVE_NOTE] + notes
        return _qualitative_result(
            circuit,
            qualitative,
            notes=notes_out,
            limitations=limitations,
            fidelity_preserved=fidelity_preserved,
        )

    # ------------------------------------------------------------------
    # Build measured result
    # ------------------------------------------------------------------
    pair_filter = options.pair_filter
    pairs: list[tuple[int, int]] = (
        pair_filter if pair_filter is not None else [(0, 1)]
    )

    all_metrics = []
    for pair in pairs:
        all_metrics.extend(
            compute_pair_metrics(sv, pair, metric_preference=metric_preference)
        )

    is_entangled = is_entangled_from_metrics(all_metrics)

    return CouplingAnalysisResult(
        mode="measured",
        provenance="rqm-core",
        qubit_count=circuit.num_qubits,
        analyzed_pairs=pairs,
        has_entangling_gates=qualitative.has_entangling_gates,
        entangling_gate_count=qualitative.entangling_gate_count,
        entangling_gates_seen=qualitative.entangling_gates_seen,
        last_entangling_gate=qualitative.last_entangling_gate,
        is_entangled=is_entangled,
        pair_metrics=all_metrics,
        fidelity_preserved=fidelity_preserved,
        notes=notes,
        limitations=limitations,
    )
