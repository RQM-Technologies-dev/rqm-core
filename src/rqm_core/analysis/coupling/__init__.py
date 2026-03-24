"""Coupling analysis sub-package – public re-exports."""

from rqm_core.analysis.coupling.types import (
    GateOp,
    Circuit,
    PairMetric,
    CouplingAnalysisResult,
    CouplingAnalysisOptions,
    OptimizationPreservationResult,
)
from rqm_core.analysis.coupling.detect_entangling_structure import (
    detect_entangling_structure,
)
from rqm_core.analysis.coupling.simulate_two_qubit_state import (
    simulate_two_qubit_state,
)
from rqm_core.analysis.coupling.metrics import (
    partial_trace_qubit_1,
    compute_concurrence,
    compute_von_neumann_entropy,
    compute_pure_state_fidelity,
    normalize_metric_value,
)
from rqm_core.analysis.coupling.analyze_circuit_coupling import (
    analyze_circuit_coupling,
)
from rqm_core.analysis.coupling.analyze_optimization_preservation import (
    analyze_optimization_preservation,
)

__all__ = [
    "GateOp",
    "Circuit",
    "PairMetric",
    "CouplingAnalysisResult",
    "CouplingAnalysisOptions",
    "OptimizationPreservationResult",
    "detect_entangling_structure",
    "simulate_two_qubit_state",
    "partial_trace_qubit_1",
    "compute_concurrence",
    "compute_von_neumann_entropy",
    "compute_pure_state_fidelity",
    "normalize_metric_value",
    "analyze_circuit_coupling",
    "analyze_optimization_preservation",
]
