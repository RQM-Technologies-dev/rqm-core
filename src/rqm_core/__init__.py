"""rqm_core – foundational quaternion and SU(2) mathematics for the RQM ecosystem."""

from rqm_core.quaternion import Quaternion
from rqm_core.su2 import (
    quaternion_to_su2,
    su2_to_quaternion,
    axis_angle_to_su2,
    su2_identity,
    is_unitary_matrix,
    determinant_close_to_one,
)
from rqm_core.bloch import state_to_bloch, bloch_to_state, bloch_from_quaternion
from rqm_core.spinor import (
    normalize_spinor,
    spinor_to_quaternion,
    spinor_to_su2,
    state_fidelity,
)
from rqm_core.linalg import (
    normalize_vector,
    matrix_trace,
    matrix_determinant,
    is_unitary,
)
from rqm_core.utils import angle_wrap, safe_norm, complex_close, matrix_close

__all__ = [
    # Quaternion
    "Quaternion",
    # SU(2)
    "quaternion_to_su2",
    "su2_to_quaternion",
    "axis_angle_to_su2",
    "su2_identity",
    "is_unitary_matrix",
    "determinant_close_to_one",
    # Bloch
    "state_to_bloch",
    "bloch_to_state",
    "bloch_from_quaternion",
    # Spinor
    "normalize_spinor",
    "spinor_to_quaternion",
    "spinor_to_su2",
    "state_fidelity",
    # Linear algebra
    "normalize_vector",
    "matrix_trace",
    "matrix_determinant",
    "is_unitary",
    # Utils
    "angle_wrap",
    "safe_norm",
    "complex_close",
    "matrix_close",
]

__version__ = "0.1.0"
