"""Before / after compiler verification for entanglement / coupling preservation.

This module exposes :func:`analyze_optimization_preservation`, a helper
that compares an original circuit against an optimised variant to verify
that the compiler has preserved the quantum state fidelity and
entanglement structure.

Design
------
Both circuits are analysed with :func:`analyze_circuit_coupling`.  When
both produce measured results the function additionally:
- computes the state fidelity between the final states;
- checks whether the entanglement classification is identical;
- checks whether key metric values agree within numerical tolerance.

When only qualitative results are available the function is honest: it
reports that preservation cannot be confirmed and does not fabricate a
fidelity value.

Architecture note
-----------------
This is the compiler-facing verification layer.  It is *additive* — it
does not modify or re-implement the quaternionic / SU(2) single-qubit
optimiser.  The comparison is purely about whether the global quantum
state (and thus the observable coupling / entanglement structure) is
preserved after optimisation.
"""

from __future__ import annotations

from rqm_core.analysis.coupling.analyze_circuit_coupling import (
    analyze_circuit_coupling,
)
from rqm_core.analysis.coupling.metrics import (
    compute_pure_state_fidelity,
    is_entangled_from_metrics,
)
from rqm_core.analysis.coupling.simulate_two_qubit_state import (
    simulate_two_qubit_state,
)
from rqm_core.analysis.coupling.types import (
    Circuit,
    CouplingAnalysisOptions,
    OptimizationPreservationResult,
)

#: Tolerance used when comparing metric values across circuits.
_METRIC_DELTA_TOLERANCE: float = 1e-6


def analyze_optimization_preservation(
    original_circuit: Circuit,
    optimized_circuit: Circuit,
    options: CouplingAnalysisOptions | None = None,
) -> OptimizationPreservationResult:
    """Compare *original_circuit* and *optimized_circuit* for preservation.

    This function verifies that an optimisation step preserved the
    quantum state fidelity and entanglement structure of a circuit.

    Args:
        original_circuit:  The circuit before optimisation.
        optimized_circuit: The circuit after optimisation.
        options:           Options forwarded to
                           :func:`analyze_circuit_coupling` for each circuit.
                           ``compare_against_circuit`` is overridden
                           internally and should not be set by the caller.

    Returns:
        :class:`~rqm_core.analysis.coupling.types.OptimizationPreservationResult`

    Notes:
        - ``fidelity_preserved`` is ``None`` when at least one circuit
          could not be simulated.
        - ``preserved_entanglement_structure`` is ``None`` when only
          qualitative analysis was available for either circuit.
        - Honest ``notes`` explain what was and was not computed.
    """
    if options is None:
        options = CouplingAnalysisOptions()

    # Run coupling analysis for each circuit independently (no cross-fidelity
    # request here — we compute fidelity explicitly below from the raw
    # statevectors to avoid double simulation).
    original_result = analyze_circuit_coupling(original_circuit, options)
    optimized_result = analyze_circuit_coupling(optimized_circuit, options)

    notes: list[str] = []
    fidelity_preserved: float | None = None
    preserved_entanglement_structure: bool | None = None

    # ------------------------------------------------------------------
    # Fidelity computation (requires both circuits to be simulatable)
    # ------------------------------------------------------------------
    orig_sv = None
    opt_sv = None

    if original_circuit.num_qubits == 2:
        orig_sv = simulate_two_qubit_state(original_circuit)
    if optimized_circuit.num_qubits == 2:
        opt_sv = simulate_two_qubit_state(optimized_circuit)

    if orig_sv is not None and opt_sv is not None:
        fidelity_preserved = compute_pure_state_fidelity(orig_sv, opt_sv)
        notes.append(
            f"State fidelity between original and optimized final states: "
            f"{fidelity_preserved:.6f}"
        )
    else:
        notes.append(
            "At least one circuit could not be simulated; "
            "fidelity preservation is not available."
        )

    # ------------------------------------------------------------------
    # Entanglement structure comparison
    # ------------------------------------------------------------------
    if (
        original_result.mode == "measured"
        and optimized_result.mode == "measured"
    ):
        orig_entangled = is_entangled_from_metrics(original_result.pair_metrics)
        opt_entangled = is_entangled_from_metrics(optimized_result.pair_metrics)

        if orig_entangled is not None and opt_entangled is not None:
            entanglement_class_preserved = orig_entangled == opt_entangled

            # Check that key metric values agree within tolerance.
            metrics_agree = _metrics_agree(
                original_result.pair_metrics,
                optimized_result.pair_metrics,
            )

            preserved_entanglement_structure = (
                entanglement_class_preserved and metrics_agree
            )

            if preserved_entanglement_structure:
                notes.append(
                    "Entanglement structure is preserved: "
                    "classification and metric values agree within tolerance."
                )
            else:
                notes.append(
                    "Entanglement structure may not be fully preserved: "
                    "classification or metric values differ."
                )
    else:
        notes.append(
            "Entanglement structure comparison requires measured analysis "
            "for both circuits.  Only qualitative gate-level summaries are "
            "available."
        )

    return OptimizationPreservationResult(
        fidelity_preserved=fidelity_preserved,
        original_coupling=original_result,
        optimized_coupling=optimized_result,
        preserved_entanglement_structure=preserved_entanglement_structure,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _metrics_agree(
    metrics_a: list,
    metrics_b: list,
) -> bool:
    """Return True if matching metrics in the two lists agree within tolerance.

    Compares metric values by ``metric_name`` for pairs that appear in both
    lists.  Returns True when all shared metric names have values within
    ``_METRIC_DELTA_TOLERANCE`` of each other.

    Returns True trivially when there are no shared metrics to compare.
    """
    lookup_b: dict[str, float] = {m.metric_name: m.value for m in metrics_b}

    for m in metrics_a:
        if m.metric_name in lookup_b:
            delta = abs(m.value - lookup_b[m.metric_name])
            if delta > _METRIC_DELTA_TOLERANCE:
                return False
    return True
