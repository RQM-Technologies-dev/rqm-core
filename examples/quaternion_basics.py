"""Demonstrate basic quaternion operations in rqm_core."""

import math

from rqm_core.quaternion import Quaternion

# 1. Construct a quaternion directly
q1 = Quaternion(1.0, 0.0, 0.0, 0.0)
print("Identity quaternion:", q1)

# 2. Build a rotation from axis and angle
q_x = Quaternion.from_axis_angle("x", math.pi / 4)   # 45° around X
q_y = Quaternion.from_axis_angle("y", math.pi / 2)   # 90° around Y
print("45° around X:", q_x)
print("90° around Y:", q_y)

# 3. Multiply rotations (Hamilton product)
q_combined = q_x * q_y
print("Combined rotation (X then Y):", q_combined)
print("Is unit quaternion:", q_combined.is_unit())

# 4. Conjugate and inverse
print("Conjugate of q_x:", q_x.conjugate())
print("Inverse of q_x:", q_x.inverse())
print("q_x * q_x.inverse() =", q_x * q_x.inverse())

# 5. Convert to SU(2) matrix
print("\nSU(2) matrix for q_y:")
print(q_y.to_su2_matrix())

# 6. Convert to SO(3) rotation matrix
print("\nSO(3) rotation matrix for q_y:")
print(q_y.to_rotation_matrix())
