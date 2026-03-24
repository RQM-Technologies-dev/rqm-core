"""Measured entanglement metrics for pure 2-qubit states.

This module provides mathematical metrics derived from the ideal pure
statevector of a 2-qubit system.  All functions operate on a normalised
4-element complex statevector with basis ordering::

    index 0 → |00⟩,  index 1 → |01⟩,  index 2 → |10⟩,  index 3 → |11⟩

(qubit 0 = MSB — consistent with :mod:`~rqm_core.analysis.coupling.simulate_two_qubit_state`)

Architecture note
-----------------
These metrics operate at the multi-qubit (SU(4) / tensor-product) level.
They are mathematically complementary to the quaternionic / SU(2) analysis
of individual qubits and do not replace it.

Numerical robustness
--------------------
- Tiny negative eigenvalues caused by floating-point drift are clamped to 0
  before entropy computation.
- Results are always in [0, 1] for normalised metrics (by definition for
  pure states).
- The :data:`~rqm_core.analysis.coupling.types.ENTANGLEMENT_TOLERANCE` from
  ``types.py`` is used to classify states as entangled / separable.
"""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

from rqm_core.analysis.coupling.types import (
    ENTANGLEMENT_TOLERANCE,
    PairMetric,
)

# ---------------------------------------------------------------------------
# Partial trace
# ---------------------------------------------------------------------------


def partial_trace_qubit_1(
    sv: NDArray[np.complex128],
) -> NDArray[np.complex128]:
    """Return the reduced density matrix ρ₀ for qubit 0 (tracing out qubit 1).

    For a pure 2-qubit state |ψ⟩ = a|00⟩ + b|01⟩ + c|10⟩ + d|11⟩ with
    statevector ``[a, b, c, d]``, reshape into the 2×2 matrix::

        M = [[a, b],
             [c, d]]

    and return ρ₀ = M @ M†.

    The resulting 2×2 density matrix has trace 1 and eigenvalues in [0, 1].

    Args:
        sv: Normalised statevector of shape ``(4,)`` or ``(4, 1)``.

    Returns:
        2×2 reduced density matrix for qubit 0.
    """
    v = np.asarray(sv, dtype=np.complex128).ravel()
    if v.shape != (4,):
        raise ValueError(f"Expected statevector of shape (4,), got {v.shape}.")
    m = v.reshape(2, 2)
    return m @ m.conj().T


# ---------------------------------------------------------------------------
# Concurrence
# ---------------------------------------------------------------------------


def compute_concurrence(sv: NDArray[np.complex128]) -> float:
    """Compute the concurrence of a pure 2-qubit state.

    For |ψ⟩ = a|00⟩ + b|01⟩ + c|10⟩ + d|11⟩::

        C = 2 · |a·d − b·c|

    The concurrence lies in [0, 1]:
    - C = 0 → separable (product state)
    - C = 1 → maximally entangled (Bell state)

    Args:
        sv: Normalised statevector of shape ``(4,)``.

    Returns:
        Concurrence in ``[0, 1]``.

    References:
        Wootters, W.K. (1998). "Entanglement of Formation of an Arbitrary
        State of Two Qubits." Physical Review Letters, 80(10), 2245–2248.
    """
    v = np.asarray(sv, dtype=np.complex128).ravel()
    a, b, c, d = v[0], v[1], v[2], v[3]
    raw = 2.0 * abs(a * d - b * c)
    # Clamp to [0, 1] to guard against tiny numerical overshoot.
    return float(min(1.0, max(0.0, raw)))


# ---------------------------------------------------------------------------
# Von Neumann entropy
# ---------------------------------------------------------------------------


def compute_von_neumann_entropy(rho: NDArray[np.complex128]) -> float:
    """Compute the von Neumann entropy of a 2×2 density matrix.

    ::

        S(ρ) = −Tr(ρ log₂ ρ) = −Σᵢ λᵢ log₂(λᵢ)

    where ``λᵢ`` are the eigenvalues of ``ρ``.

    For a pure 2-qubit state:
    - S = 0 → qubit 0 is in a pure (separable) state
    - S = 1 → qubit 0 is maximally entangled (Bell state)

    Tiny negative eigenvalues from floating-point drift are clamped to 0
    before the logarithm is evaluated.

    Args:
        rho: 2×2 density matrix (Hermitian, trace ≈ 1).

    Returns:
        Von Neumann entropy in bits (base-2 logarithm), in ``[0, 1]``.
    """
    eigenvalues = np.linalg.eigvalsh(np.asarray(rho, dtype=np.complex128))
    # Clamp tiny negative values caused by floating-point drift.
    eigenvalues = np.clip(eigenvalues.real, 0.0, None)

    entropy = 0.0
    for lam in eigenvalues:
        if lam > 0.0:
            entropy -= float(lam) * math.log2(float(lam))

    # Clamp to [0, 1]: S ≤ log₂(2) = 1 for a 2×2 density matrix.
    return float(min(1.0, max(0.0, entropy)))


# ---------------------------------------------------------------------------
# Pure-state fidelity
# ---------------------------------------------------------------------------


def compute_pure_state_fidelity(
    sv1: NDArray[np.complex128],
    sv2: NDArray[np.complex128],
) -> float:
    """Compute the quantum state fidelity between two pure statevectors.

    ::

        F = |⟨ψ₁|ψ₂⟩|²

    The states are normalised internally; they need not be pre-normalised.

    This delegates to :func:`rqm_core.spinor.state_fidelity` which is the
    canonical implementation in this library.

    Args:
        sv1: First statevector.
        sv2: Second statevector.

    Returns:
        Fidelity in ``[0, 1]``.

    Raises:
        ValueError: If either state vector is zero.
    """
    # Import here to keep the dependency explicit and avoid circular imports.
    from rqm_core.spinor import state_fidelity

    return state_fidelity(
        np.asarray(sv1, dtype=np.complex128),
        np.asarray(sv2, dtype=np.complex128),
    )


# ---------------------------------------------------------------------------
# Metric normalisation and interpretation
# ---------------------------------------------------------------------------


def normalize_metric_value(metric_name: str, value: float) -> float | None:
    """Return the normalised (to ``[0, 1]``) version of *value*, or ``None``.

    Normalisation rules:
    - ``"concurrence"`` → already in [0, 1]; returned as-is.
    - ``"entropy"`` → already in [0, 1] for a 2×2 density matrix; as-is.
    - ``"fidelity"`` → already in [0, 1]; returned as-is.
    - All others → ``None`` (no known normalisation for this metric).
    """
    if metric_name in ("concurrence", "entropy", "fidelity"):
        return float(min(1.0, max(0.0, value)))
    return None


def _interpret_concurrence(value: float) -> str:
    if value < ENTANGLEMENT_TOLERANCE:
        return "separable (product state)"
    if value > 1.0 - ENTANGLEMENT_TOLERANCE:
        return "maximally entangled"
    return "partially entangled"


def _interpret_entropy(value: float) -> str:
    if value < ENTANGLEMENT_TOLERANCE:
        return "pure product state (zero entanglement entropy)"
    if value > 1.0 - ENTANGLEMENT_TOLERANCE:
        return "maximal single-qubit entanglement entropy"
    return "partial entanglement entropy"


def _interpret_fidelity(value: float) -> str:
    if value > 1.0 - ENTANGLEMENT_TOLERANCE:
        return "identical states"
    if value > 0.99:
        return "near-identical states"
    if value > 0.9:
        return "high similarity"
    return "distinct states"


# ---------------------------------------------------------------------------
# Composite metric computation
# ---------------------------------------------------------------------------


def compute_pair_metrics(
    sv: NDArray[np.complex128],
    pair: tuple[int, int],
    *,
    metric_preference: list[str] | None = None,
) -> list[PairMetric]:
    """Compute measured metrics for qubit *pair* from statevector *sv*.

    Currently supports:
    - ``"concurrence"`` – direct formula for pure 2-qubit states.
    - ``"entropy"`` – von Neumann entropy of the reduced density matrix.

    Args:
        sv:                Normalised 4-element statevector.
        pair:              Qubit pair ``(q0, q1)`` — for labelling only.
        metric_preference: Ordered list of metric names to include.
                           Defaults to ``["concurrence", "entropy"]``.

    Returns:
        List of :class:`~rqm_core.analysis.coupling.types.PairMetric` objects.
    """
    requested = metric_preference or ["concurrence", "entropy"]
    metrics: list[PairMetric] = []

    rho0 = partial_trace_qubit_1(sv)

    for name in requested:
        if name == "concurrence":
            val = compute_concurrence(sv)
            metrics.append(
                PairMetric(
                    pair=pair,
                    metric_name="concurrence",
                    value=val,
                    normalized_value=normalize_metric_value("concurrence", val),
                    interpretation=_interpret_concurrence(val),
                )
            )
        elif name == "entropy":
            val = compute_von_neumann_entropy(rho0)
            metrics.append(
                PairMetric(
                    pair=pair,
                    metric_name="entropy",
                    value=val,
                    normalized_value=normalize_metric_value("entropy", val),
                    interpretation=_interpret_entropy(val),
                )
            )
        # Other metric names are silently skipped (honest degradation).

    return metrics


def is_entangled_from_metrics(pair_metrics: list[PairMetric]) -> bool | None:
    """Determine entanglement from a list of measured metrics.

    Uses concurrence if present; falls back to entropy.
    Returns ``None`` if neither is available.

    A state is classified as entangled when the primary metric exceeds
    :data:`~rqm_core.analysis.coupling.types.ENTANGLEMENT_TOLERANCE`.
    """
    for m in pair_metrics:
        if m.metric_name == "concurrence":
            return m.value > ENTANGLEMENT_TOLERANCE
    for m in pair_metrics:
        if m.metric_name == "entropy":
            return m.value > ENTANGLEMENT_TOLERANCE
    return None
