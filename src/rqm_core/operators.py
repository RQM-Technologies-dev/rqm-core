"""Shared one-qubit operator-basis mathematics for the RQM ecosystem.

These primitives are backend- and compiler-policy independent. They centralize
the Pauli operator basis, coefficient projection/reconstruction, computational
basis projectors, and two-qubit partial traces used by higher layers.
"""
from __future__ import annotations
from collections.abc import Iterable
import numpy as np

_I=np.eye(2,dtype=complex)
_X=np.array([[0,1],[1,0]],dtype=complex)
_Y=np.array([[0,-1j],[1j,0]],dtype=complex)
_Z=np.array([[1,0],[0,-1]],dtype=complex)
_PAULI=(_I,_X,_Y,_Z)

def pauli_basis()->tuple[np.ndarray,np.ndarray,np.ndarray,np.ndarray]:
    """Return copies of the canonical (I, X, Y, Z) operator basis."""
    return tuple(m.copy() for m in _PAULI)  # type: ignore[return-value]

def operator_to_pauli_coefficients(operator:np.ndarray)->np.ndarray:
    """Project a 2x2 operator onto the Pauli basis.

    Uses c_mu = Tr(sigma_mu O)/2 so that O = sum_mu c_mu sigma_mu.
    """
    op=np.asarray(operator,dtype=complex)
    if op.shape!=(2,2):
        raise ValueError("operator must have shape (2,2)")
    return np.array([np.trace(s@op)/2 for s in _PAULI],dtype=complex)

def pauli_coefficients_to_operator(coefficients:Iterable[complex])->np.ndarray:
    """Reconstruct a 2x2 operator from four Pauli-basis coefficients."""
    coeff=np.asarray(list(coefficients),dtype=complex)
    if coeff.shape!=(4,):
        raise ValueError("coefficients must contain exactly four values")
    return sum((coeff[i]*_PAULI[i] for i in range(4)),np.zeros((2,2),complex))

def computational_basis_projector(bit:int)->np.ndarray:
    """Return |bit><bit| for bit in {0,1}."""
    if bit not in (0,1):
        raise ValueError("bit must be 0 or 1")
    v=np.zeros(2,dtype=complex);v[bit]=1
    return np.outer(v,v.conj())

def partial_trace_first_qubit(operator:np.ndarray)->np.ndarray:
    """Trace the first qubit from a 4x4 two-qubit operator.

    The matrix is interpreted in the computational basis |00>,|01>,|10>,|11>.
    """
    op=np.asarray(operator,dtype=complex)
    if op.shape!=(4,4):
        raise ValueError("operator must have shape (4,4)")
    x=op.reshape(2,2,2,2)
    return np.einsum("abad->bd",x)

def partial_trace_second_qubit(operator:np.ndarray)->np.ndarray:
    """Trace the second qubit from a 4x4 two-qubit operator."""
    op=np.asarray(operator,dtype=complex)
    if op.shape!=(4,4):
        raise ValueError("operator must have shape (4,4)")
    x=op.reshape(2,2,2,2)
    return np.einsum("abcb->ac",x)

__all__=[
    "pauli_basis","operator_to_pauli_coefficients",
    "pauli_coefficients_to_operator","computational_basis_projector",
    "partial_trace_first_qubit","partial_trace_second_qubit",
]
