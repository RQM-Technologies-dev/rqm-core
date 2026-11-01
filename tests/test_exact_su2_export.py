import math
import numpy as np
import pytest
from rqm_core.su2 import axis_angle_to_su2, su2_to_named_gate_sequence, quaternion_to_zyz
from rqm_core import Quaternion

@pytest.mark.parametrize('axis',['x','y','z'])
@pytest.mark.parametrize('angle',[2*math.pi,-2*math.pi,3*math.pi,1e-8,1e-12,.23])
def test_named_sequence_preserves_full_operator(axis,angle):
    matrix=axis_angle_to_su2(axis,angle)
    for simplify in [True,False]:
        sequence=su2_to_named_gate_sequence(matrix,simplify_axis=simplify)
        actual=np.eye(2,dtype=complex)
        # Named sequence convention is matrix-product order.
        for gate,a in sequence:actual=actual@axis_angle_to_su2(gate[-1].lower(),a)
        assert np.linalg.norm(matrix-actual)<1e-10

def test_mixed_signed_quaternion_export():
    for values in [(-.8,.2,.3,.4),(.1,-.8,.2,-.4)]:
        q=Quaternion(*values).normalize();a,b,c=quaternion_to_zyz(q.w,q.x,q.y,q.z)
        actual=axis_angle_to_su2('z',a)@axis_angle_to_su2('y',b)@axis_angle_to_su2('z',c)
        assert np.linalg.norm(actual-q.to_su2_matrix())<1e-10


def _independent_rotation(axis, angle):
    paulis = {
        'x': np.array([[0, 1], [1, 0]], dtype=complex),
        'y': np.array([[0, -1j], [1j, 0]], dtype=complex),
        'z': np.diag([1, -1]),
    }
    return np.cos(angle / 2) * np.eye(2) - 1j * np.sin(angle / 2) * paulis[axis]


def _independent_named_sequence(sequence):
    matrix = np.eye(2, dtype=complex)
    for gate, angle in sequence:
        matrix = matrix @ _independent_rotation(gate[-1].lower(), angle)
    return matrix


@pytest.mark.parametrize('axis', ['x', 'y', 'z'])
@pytest.mark.parametrize('angle', [2 * math.pi, -2 * math.pi, 1e-12])
def test_exact_export_preserves_controlled_embedding_and_inverse(axis, angle):
    expected = _independent_rotation(axis, angle)
    actual = _independent_named_sequence(su2_to_named_gate_sequence(expected))
    controlled_expected = np.eye(4, dtype=complex)
    controlled_expected[2:, 2:] = expected
    controlled_actual = np.eye(4, dtype=complex)
    controlled_actual[2:, 2:] = actual
    np.testing.assert_allclose(controlled_actual, controlled_expected, atol=2e-15, rtol=0)
    inverse = _independent_named_sequence(su2_to_named_gate_sequence(expected.conj().T))
    np.testing.assert_allclose(inverse @ actual, np.eye(2), atol=2e-15, rtol=0)


def test_mixed_noncommuting_sequences_preserve_exact_lift():
    rng = np.random.default_rng(751)
    for _ in range(128):
        angles = rng.uniform(-4 * math.pi, 4 * math.pi, 3)
        expected = _independent_rotation('x', angles[0]) @ _independent_rotation('y', angles[1]) @ _independent_rotation('z', angles[2])
        for simplify in [True, False]:
            actual = _independent_named_sequence(su2_to_named_gate_sequence(expected, simplify_axis=simplify))
            np.testing.assert_allclose(actual, expected, atol=3e-15, rtol=0)


@pytest.mark.parametrize('phase', [1e-12, math.pi / 2 - 1e-12, math.pi / 2 + 1e-12])
def test_u2_factor_export_preserves_phase_near_branch(phase):
    from rqm_core.su2 import factor_u2_global_phase
    source = np.exp(1j * phase) * _independent_rotation('y', .37)
    scalar, su2 = factor_u2_global_phase(source)
    actual = np.exp(1j * scalar) * _independent_named_sequence(su2_to_named_gate_sequence(su2))
    np.testing.assert_allclose(actual, source, atol=2e-15, rtol=0)
