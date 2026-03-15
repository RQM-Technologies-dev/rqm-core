"""Show the correspondence between quaternion rotation and SU(2) matrices."""

import math

import numpy as np

from rqm_core.quaternion import Quaternion
from rqm_core.su2 import (
    quaternion_to_su2,
    su2_to_quaternion,
    axis_angle_to_su2,
    is_unitary_matrix,
    determinant_close_to_one,
)

angle = math.pi / 3   # 60°

# Build the quaternion and corresponding SU(2) matrix
q = Quaternion.from_axis_angle("z", angle)
m = quaternion_to_su2(q)

print(f"Rotation angle: {math.degrees(angle):.1f}°  (π/3 rad)")
print("\nQuaternion:", q)
print("\nSU(2) matrix:")
print(m)

print("\nIs unitary:", is_unitary_matrix(m))
print("det ≈ 1:   ", determinant_close_to_one(m))

# Round-trip: matrix → quaternion
q_recovered = su2_to_quaternion(m)
print("\nRecovered quaternion:", q_recovered)
print("Round-trip consistent:", q == q_recovered)

# Build directly from axis and angle
m2 = axis_angle_to_su2("z", angle)
print("\nDirect axis_angle_to_su2 result matches:", np.allclose(m, m2))
