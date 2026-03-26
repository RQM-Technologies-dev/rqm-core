"""rqm_core – foundational quaternion, spinor, SU(2), and Bloch mathematics.

This package also includes an additive coupling / entanglement analysis layer
for multi-qubit circuits.  See :mod:`rqm_core.analysis.coupling` for details.

Architecture layers (rqm_core → rqm_circuits → rqm_compiler → backends):
  - Local single-qubit structure → quaternionic / SU(2) (this module's core)
  - Multi-qubit entanglement / correlation → :mod:`rqm_core.analysis.coupling`
  - Circuit IR / wire format → rqm-circuits (canonical external boundary)
  - Optimization / rewriting → rqm-compiler
  - Backend execution → rqm-qiskit / rqm-braket
"""

from rqm_core.quaternion import Quaternion
from rqm_core.spinor import (
    normalize_spinor,
    spinor_norm,
    is_normalized_spinor,
    spinor_to_quaternion,
    spinor_embed,
    spinor_to_su2,
    state_fidelity,
)
from rqm_core.su2 import (
    su2_identity,
    quaternion_to_su2,
    su2_to_quaternion,
    axis_angle_to_su2,
    is_unitary,
    determinant_close_to_one,
    validate_su2_matrix,
)
from rqm_core.bloch import (
    state_to_bloch,
    bloch_to_state,
    bloch_from_quaternion,
    bloch_radius,
    validate_bloch_vector,
    measurement_probabilities,
)
from rqm_core.linalg import (
    normalize_vector,
    vector_norm,
    matrix_trace,
    matrix_determinant,
    matrix_dagger,
    matrix_close,
    complex_close,
)
from rqm_core.gates import (
    gate_identity,
    gate_x,
    gate_y,
    gate_z,
    gate_h,
    gate_s,
    gate_t,
    gate_rx,
    gate_ry,
    gate_rz,
    match_gate,
)
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
    # Quaternion
    "Quaternion",
    # Spinor
    "normalize_spinor",
    "spinor_norm",
    "is_normalized_spinor",
    "spinor_to_quaternion",
    "spinor_embed",
    "spinor_to_su2",
    "state_fidelity",
    # SU(2)
    "su2_identity",
    "quaternion_to_su2",
    "su2_to_quaternion",
    "axis_angle_to_su2",
    "is_unitary",
    "determinant_close_to_one",
    "validate_su2_matrix",
    # Bloch
    "state_to_bloch",
    "bloch_to_state",
    "bloch_from_quaternion",
    "bloch_radius",
    "validate_bloch_vector",
    "measurement_probabilities",
    # Linear algebra
    "normalize_vector",
    "vector_norm",
    "matrix_trace",
    "matrix_determinant",
    "matrix_dagger",
    "matrix_close",
    "complex_close",
    # Gates
    "gate_identity",
    "gate_x",
    "gate_y",
    "gate_z",
    "gate_h",
    "gate_s",
    "gate_t",
    "gate_rx",
    "gate_ry",
    "gate_rz",
    "match_gate",
    # Analysis – circuit IR
    "GateOp",
    "Circuit",
    # Analysis – result types
    "PairMetric",
    "CouplingAnalysisResult",
    "CouplingAnalysisOptions",
    "OptimizationPreservationResult",
    # Analysis – entry points
    "analyze_circuit_coupling",
    "analyze_optimization_preservation",
]

__version__ = "0.1.0"
