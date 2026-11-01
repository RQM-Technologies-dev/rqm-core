import math
import numpy as np
import pytest
from rqm_core.su2 import scalar_phase_to_named_gate_sequence

@pytest.mark.parametrize('phase',[0.,math.pi,-math.pi,.23,-.23,2*math.pi,1e-12])
def test_exact_scalar_phase_carrier(phase):
    matrix=np.eye(2,dtype=complex)
    for name,a in scalar_phase_to_named_gate_sequence(phase):
        gate=np.diag([1,np.exp(1j*a)]) if name=='phaseshift' else np.diag([np.exp(-.5j*a),np.exp(.5j*a)])
        matrix=gate@matrix
    assert np.linalg.norm(matrix-np.exp(1j*phase)*np.eye(2))<1e-12

@pytest.mark.parametrize('phase',[float('inf'),float('nan')])
def test_scalar_phase_rejects_nonfinite(phase):
    with pytest.raises(ValueError):scalar_phase_to_named_gate_sequence(phase)


def test_scalar_phase_rejects_overflowing_gate_angles():
    with pytest.raises(ValueError, match='finite gate angles'):
        scalar_phase_to_named_gate_sequence(1e308)


def test_scalar_phase_embeds_as_same_scalar_on_two_qubits():
    phase = .37
    carrier = np.eye(2, dtype=complex)
    for name, angle in scalar_phase_to_named_gate_sequence(phase):
        gate = np.diag([1, np.exp(1j * angle)]) if name == 'phaseshift' else np.diag([np.exp(-.5j * angle), np.exp(.5j * angle)])
        carrier = gate @ carrier
    np.testing.assert_allclose(np.kron(carrier, np.eye(2)), np.exp(1j * phase) * np.eye(4), atol=1e-15, rtol=0)
