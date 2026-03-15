"""Demonstrate Bloch sphere mappings for quantum spinors."""

import math

import numpy as np

from rqm_core.bloch import state_to_bloch, bloch_to_state, bloch_from_quaternion
from rqm_core.spinor import normalize_spinor, state_fidelity
from rqm_core.quaternion import Quaternion

print("=== Canonical Bloch vectors ===")

# |0⟩ → north pole
print("|0⟩  →", state_to_bloch(1.0, 0.0))

# |1⟩ → south pole
print("|1⟩  →", state_to_bloch(0.0, 1.0))

# |+⟩ → +X equator
c = 1.0 / math.sqrt(2)
print("|+⟩  →", state_to_bloch(c, c))

# |-⟩ → -X equator
print("|-⟩  →", state_to_bloch(c, -c))

# |i+⟩ → +Y equator
print("|i+⟩ →", state_to_bloch(c, 1j * c))

print("\n=== bloch_to_state round-trip ===")
theta, phi = 1.1, 0.7
psi = bloch_to_state(theta, phi)
v = state_to_bloch(complex(psi[0]), complex(psi[1]))
expected = np.array([
    math.sin(theta) * math.cos(phi),
    math.sin(theta) * math.sin(phi),
    math.cos(theta),
])
print(f"θ={theta:.2f}, φ={phi:.2f}")
print("Bloch vector (computed):", v)
print("Bloch vector (expected) :", expected)
print("Match:", np.allclose(v, expected, atol=1e-9))

print("\n=== bloch_from_quaternion ===")
# A π rotation about Y should map the north pole to the south pole
q = Quaternion.from_axis_angle("y", math.pi)
v = bloch_from_quaternion(q)
print("π rotation around Y → Bloch:", v)

print("\n=== State fidelity ===")
psi0 = normalize_spinor(1.0, 0.0)
psi1 = normalize_spinor(0.0, 1.0)
psi_plus = normalize_spinor(c, c)

print(f"F(|0⟩, |0⟩) = {state_fidelity(psi0, psi0):.4f}")
print(f"F(|0⟩, |1⟩) = {state_fidelity(psi0, psi1):.4f}")
print(f"F(|0⟩, |+⟩) = {state_fidelity(psi0, psi_plus):.4f}")
