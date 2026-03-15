"""Demonstrate the axis-angle → quaternion → SU(2) → Bloch pipeline."""

import math

from rqm_core.quaternion import Quaternion
from rqm_core.su2 import (
    quaternion_to_su2,
    axis_angle_to_su2,
    is_unitary,
    determinant_close_to_one,
    validate_su2_matrix,
)
from rqm_core.bloch import (
    bloch_from_quaternion,
    bloch_to_state,
    state_to_bloch,
    bloch_radius,
    validate_bloch_vector,
)

print("=== Axis-angle → Quaternion → SU(2) ===\n")

axis = "y"
angle = math.pi / 3  # 60°

# Step 1: axis-angle → quaternion
q = Quaternion.from_axis_angle(axis, angle)
print(f"Rotation: {math.degrees(angle):.1f}° around {axis.upper()}-axis")
print(f"Quaternion:    {q}")
print(f"Scalar part:   {q.scalar_part():.4f}")
print(f"Vector part:   ({q.vector_part()[0]:.4f}, {q.vector_part()[1]:.4f}, {q.vector_part()[2]:.4f})")

# Step 2: quaternion → SU(2)
m = quaternion_to_su2(q)
print(f"\nSU(2) matrix:\n{m}")
print(f"Unitary:       {is_unitary(m)}")
print(f"det ≈ 1:       {determinant_close_to_one(m)}")
validate_su2_matrix(m)
print("validate_su2_matrix: passed ✓")

# Step 3: quaternion → Bloch vector
bx, by, bz = bloch_from_quaternion(q)
print(f"\nBloch vector (from quaternion): ({bx:.4f}, {by:.4f}, {bz:.4f})")
print(f"Bloch radius: {bloch_radius(bx, by, bz):.6f}  (should be 1.0)")
validate_bloch_vector(bx, by, bz)
print("validate_bloch_vector: passed ✓")

# Step 4: compare with state_to_bloch round-trip
print("\n=== Bloch ↔ State round-trip ===\n")
theta, phi = math.pi / 4, math.pi / 6
alpha, beta = bloch_to_state(theta, phi)
bx2, by2, bz2 = state_to_bloch(alpha, beta)
expected_x = math.sin(theta) * math.cos(phi)
expected_y = math.sin(theta) * math.sin(phi)
expected_z = math.cos(theta)

print(f"θ={theta:.3f} rad, φ={phi:.3f} rad")
print(f"  bloch_to_state → ({alpha.real:.4f}{alpha.imag:+.4f}j, {beta.real:.4f}{beta.imag:+.4f}j)")
print(f"  state_to_bloch → ({bx2:.4f}, {by2:.4f}, {bz2:.4f})")
print(f"  expected       → ({expected_x:.4f}, {expected_y:.4f}, {expected_z:.4f})")

import numpy as np
assert np.allclose([bx2, by2, bz2], [expected_x, expected_y, expected_z], atol=1e-9)
print("Round-trip consistent ✓")
