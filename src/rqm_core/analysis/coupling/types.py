"""Shared types for the coupling / entanglement analysis layer.

Architectural distinction maintained throughout:
  - Local single-qubit structure is handled by the quaternionic /
    SU(2) layer (rqm_core.quaternion, rqm_core.su2, etc.).
  - Multi-qubit entanglement / correlation is the concern of *this*
    module.  These two layers complement each other and do not compete.

Circuit IR
----------
A minimal, self-contained circuit representation is defined here so
that this analysis layer can operate without depending on any specific
upstream circuit compiler.  Higher-level packages (rqm-compiler, etc.)
may translate their own IR into ``Circuit`` / ``GateOp`` objects before
calling :func:`~rqm_core.analysis.coupling.analyze_circuit_coupling`.

Supported gate names
--------------------
Single-qubit: ``"I"``, ``"X"``, ``"Y"``, ``"Z"``, ``"H"``, ``"S"``,
              ``"T"``, ``"Rx"``, ``"Ry"``, ``"Rz"``, ``"U"`` / ``"U3"``
Two-qubit:    ``"CNOT"`` / ``"CX"``, ``"CZ"``, ``"SWAP"``

Any other gate name causes the analysis to fall back to qualitative
(gate-detection-only) mode rather than fabricating measured results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# ---------------------------------------------------------------------------
# Primitive gate IR
# ---------------------------------------------------------------------------

#: Names of two-qubit gates that can *potentially* create entanglement.
#: SWAP is included as a multi-qubit interaction even though it does not
#: always produce entanglement — the measured analysis makes that determination.
ENTANGLING_GATE_NAMES: frozenset[str] = frozenset({"CNOT", "CX", "CZ", "SWAP"})

#: All single-qubit gate names that the simulation layer understands.
SUPPORTED_SINGLE_QUBIT_GATES: frozenset[str] = frozenset(
    {"I", "X", "Y", "Z", "H", "S", "T", "Rx", "Ry", "Rz", "U", "U3"}
)

#: All two-qubit gate names that the simulation layer understands.
SUPPORTED_TWO_QUBIT_GATES: frozenset[str] = frozenset({"CNOT", "CX", "CZ", "SWAP"})


@dataclass
class GateOp:
    """A single gate operation applied to one or more qubits.

    Args:
        name:   Gate name string (see module docstring for supported names).
        qubits: Ordered list of qubit indices (0-based) the gate acts on.
                For single-qubit gates: ``[target]``.
                For two-qubit gates: ``[control, target]`` or ``[q0, q1]``.
        params: Optional gate parameters (angles in radians).
                ``Rx``, ``Ry``, ``Rz`` take one parameter.
                ``U`` / ``U3`` take three parameters ``(θ, φ, λ)``.
    """

    name: str
    qubits: list[int]
    params: list[float] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.qubits:
            raise ValueError(f"GateOp '{self.name}' must specify at least one qubit.")


@dataclass
class Circuit:
    """Minimal circuit representation for entanglement analysis.

    Args:
        num_qubits:  Total number of qubits in the circuit.
        operations:  Ordered list of gate operations to apply.
    """

    num_qubits: int
    operations: list[GateOp] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.num_qubits < 1:
            raise ValueError("Circuit must have at least one qubit.")


# ---------------------------------------------------------------------------
# Analysis result types
# ---------------------------------------------------------------------------

#: Whether the analysis used gate detection only or actual state simulation.
AnalysisMode = Literal["qualitative", "measured"]

#: Where the analysis data originated.
Provenance = Literal["parser", "statevector", "rqm-core"]

#: Known two-qubit gate labels seen during qualitative detection.
EntanglingGateType = Literal["CNOT", "CX", "CZ", "SWAP", "OTHER"]

#: Metric names available from the measured analysis path.
MetricName = Literal[
    "concurrence",
    "entropy",
    "mutual_information",
    "rqm_correlation",
    "fidelity",
]

#: Numerical tolerance used to classify a state as entangled.
#: A slightly larger value than the default ``atol=1e-9`` is used because
#: physical entanglement classification benefits from a modest numerical
#: buffer above pure floating-point noise.
ENTANGLEMENT_TOLERANCE: float = 1e-6


@dataclass
class PairMetric:
    """A single measured metric for a qubit pair.

    Args:
        pair:             The qubit pair ``(q0, q1)`` this metric describes.
        metric_name:      Name of the metric (see :data:`MetricName`).
        value:            Raw computed value.
        normalized_value: Value normalized to ``[0, 1]`` where applicable.
        interpretation:   Human-readable description of what the value means.
    """

    pair: tuple[int, int]
    metric_name: str
    value: float
    normalized_value: float | None = None
    interpretation: str | None = None


@dataclass
class CouplingAnalysisResult:
    """Full result from :func:`~rqm_core.analysis.coupling.analyze_circuit_coupling`.

    Fields
    ------
    mode:
        ``"measured"`` when actual state simulation and metric computation
        were performed; ``"qualitative"`` when only gate-level detection
        was possible.
    provenance:
        ``"rqm-core"`` for statevector-based results;
        ``"parser"`` for gate-detection-only results.
    qubit_count:
        Number of qubits in the circuit.
    analyzed_pairs:
        Qubit pairs for which metrics were computed or detection was run.
    has_entangling_gates:
        ``True`` if any known entangling-capable gate appears in the circuit.
        Gate *presence* does not guarantee the resulting state is entangled
        (see ``is_entangled``).
    entangling_gate_count:
        Number of entangling-capable gate instances found.
    entangling_gates_seen:
        Distinct entangling gate names observed, in order of first occurrence.
    last_entangling_gate:
        Human-readable string describing the last entangling gate seen
        (e.g. ``"CNOT q0->q1"``).
    is_entangled:
        ``True`` / ``False`` when a measured metric confirms the final state
        is / is not entangled.  ``None`` in qualitative mode.
    pair_metrics:
        Measured metrics (concurrence, entropy, etc.) per qubit pair.
        Empty in qualitative mode.
    fidelity_preserved:
        State fidelity between this circuit and the comparison circuit
        if ``options.compare_against_circuit`` was provided; else ``None``.
    notes:
        Informational messages about what was computed.
    limitations:
        Honest description of what was *not* computed and why.
    """

    mode: str
    provenance: str
    qubit_count: int
    analyzed_pairs: list[tuple[int, int]]
    has_entangling_gates: bool
    entangling_gate_count: int
    entangling_gates_seen: list[str]
    last_entangling_gate: str | None
    is_entangled: bool | None
    pair_metrics: list[PairMetric]
    fidelity_preserved: float | None
    notes: list[str]
    limitations: list[str]


@dataclass
class CouplingAnalysisOptions:
    """Options passed to :func:`~rqm_core.analysis.coupling.analyze_circuit_coupling`.

    Args:
        compare_against_circuit:
            If provided, computes state fidelity between the analysed circuit
            and this reference circuit.
        pair_filter:
            If provided, restrict measured analysis to these qubit pairs only.
            (Currently only ``(0, 1)`` is supported for 2-qubit measured analysis.)
        metric_preference:
            Ordered list of metric names to include in results.
            Defaults to ``["concurrence", "entropy"]``.
        initial_state:
            Initial state of all qubits.  Only ``"zero"`` (|00…0⟩) is
            currently supported.
        allow_qualitative_fallback:
            When ``True`` (default), circuits that cannot be simulated are
            analysed qualitatively instead of raising an error.
    """

    compare_against_circuit: Circuit | None = None
    pair_filter: list[tuple[int, int]] | None = None
    metric_preference: list[str] | None = None
    initial_state: str = "zero"
    allow_qualitative_fallback: bool = True


@dataclass
class QualitativeStructure:
    """Intermediate result from :func:`detect_entangling_structure`.

    This is used internally and also exposed for downstream introspection.

    Args:
        has_entangling_gates:   Any known entangling gate is present.
        entangling_gate_count:  Number of entangling gate instances.
        entangling_gates_seen:  Distinct names, in order of first occurrence.
        last_entangling_gate:   Human-readable description of the last one.
        candidate_pairs:        Qubit pairs involved in entangling operations.
    """

    has_entangling_gates: bool
    entangling_gate_count: int
    entangling_gates_seen: list[str]
    last_entangling_gate: str | None
    candidate_pairs: list[tuple[int, int]]


@dataclass
class OptimizationPreservationResult:
    """Result from :func:`~rqm_core.analysis.coupling.analyze_optimization_preservation`.

    Args:
        fidelity_preserved:
            State fidelity between original and optimized final states.
            ``None`` when at least one circuit could not be simulated.
        original_coupling:
            Full :class:`CouplingAnalysisResult` for the original circuit.
        optimized_coupling:
            Full :class:`CouplingAnalysisResult` for the optimized circuit.
        preserved_entanglement_structure:
            ``True`` when both circuits produce the same entanglement
            classification and their key metrics agree within tolerance.
            ``None`` when only qualitative analysis was available.
        notes:
            Informational messages about the comparison.
    """

    fidelity_preserved: float | None
    original_coupling: CouplingAnalysisResult
    optimized_coupling: CouplingAnalysisResult
    preserved_entanglement_structure: bool | None
    notes: list[str]
