"""Public projector indices are integer scalars, never boolean masks."""
import numpy as np
import pytest

from rqm_core import computational_basis_projector


@pytest.mark.parametrize('scalar', [int, np.int8, np.int32, np.int64, np.uint8, np.uint64])
@pytest.mark.parametrize('bit', [0, 1])
def test_integer_scalar_indices_return_rank_one_projectors(scalar, bit):
    result = computational_basis_projector(scalar(bit))
    expected = np.zeros((2, 2), dtype=complex)
    expected[bit, bit] = 1
    np.testing.assert_array_equal(result, expected)
    np.testing.assert_array_equal(result.conj().T, result)
    np.testing.assert_array_equal(result @ result, result)
    assert np.trace(result) == 1
    assert np.linalg.matrix_rank(result) == 1


@pytest.mark.parametrize('bit', [True, False, np.bool_(True), np.bool_(False)])
def test_boolean_indices_are_rejected_before_numpy_indexing(bit):
    with pytest.raises(ValueError, match='integer scalar'):
        computational_basis_projector(bit)


@pytest.mark.parametrize('bit', [-1, 2, np.int64(-1), np.uint64(2),
                                  0.0, 1.0, np.float64(1), 1+0j,
                                  float('nan'), float('inf'), '1', None,
                                  np.array(1), np.array([1])])
def test_non_integer_and_out_of_range_indices_are_rejected(bit):
    with pytest.raises(ValueError):
        computational_basis_projector(bit)


def test_projector_results_do_not_share_mutable_storage():
    first = computational_basis_projector(0)
    first[:] = 99
    np.testing.assert_array_equal(computational_basis_projector(0), [[1, 0], [0, 0]])
