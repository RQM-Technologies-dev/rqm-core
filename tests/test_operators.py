import numpy as np
from rqm_core import (
 pauli_basis,operator_to_pauli_coefficients,pauli_coefficients_to_operator,
 computational_basis_projector,partial_trace_first_qubit,partial_trace_second_qubit,
)

def test_pauli_projection_roundtrip():
 I,X,Y,Z=pauli_basis()
 O=.7*I+.2j*X-.3*Y+1.2*Z
 c=operator_to_pauli_coefficients(O)
 assert np.allclose(pauli_coefficients_to_operator(c),O,atol=1e-12)

def test_computational_basis_projectors():
 assert np.allclose(computational_basis_projector(0),np.array([[1,0],[0,0]],complex))
 assert np.allclose(computational_basis_projector(1),np.array([[0,0],[0,1]],complex))

def test_partial_traces_match_kron_identity():
 A=np.array([[1,2],[3,4]],complex);B=np.array([[2,0],[0,5]],complex)
 K=np.kron(A,B)
 assert np.allclose(partial_trace_first_qubit(K),np.trace(A)*B)
 assert np.allclose(partial_trace_second_qubit(K),np.trace(B)*A)
