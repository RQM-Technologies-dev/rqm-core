"""rqm_core.analysis – multi-qubit coupling and entanglement analysis.

This sub-package provides an additive, modular layer for analysing
multi-qubit entanglement and coupling.  It sits *beside* the
quaternionic single-qubit optimizer, not in place of it.

Architecture distinction kept explicit throughout:
  - Local single-qubit structure → quaternionic / SU(2) (unchanged)
  - Multi-qubit entanglement / correlation → this analysis layer
"""

from rqm_core.analysis.coupling.types import (
    GateOp,
    Circuit,
    PairMetric,
    CouplingAnalysisResult,
    CouplingAnalysisOptions,
    OptimizationPreservationResult,
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
    "analyze_circuit_coupling",
    "analyze_optimization_preservation",
]
