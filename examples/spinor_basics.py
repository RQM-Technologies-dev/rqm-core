"""Demonstrate spinor normalization, Bloch mapping, and quaternion conversion."""

import math

from rqm_core.spinor import (
    normalize_spinor,
    spinor_norm,
    is_normalized_spinor,
    spinor_to_quaternion,
    state_fidelity,
)
from rqm_core.bloch import state_to_bloch

# 1. Normalize an arbitrary spinor
alpha_raw, beta_raw = 3.0, 4.0  # unnormalized
print("=== Spinor normalization ===")
print(f"Raw:         ({alpha_raw}, {beta_raw})")
print(f"Norm:        {spinor_norm(alpha_raw, beta_raw):.4f}")
alpha, beta = normalize_spinor(alpha_raw, beta_raw)
print(f"Normalized:  ({alpha:.4f}, {beta:.4f})")
print(f"Is unit:     {is_normalized_spinor(alpha, beta)}")

# 2. Map to Bloch sphere
print("\n=== Bloch sphere mapping ===")
c = 1.0 / math.sqrt(2)

states = {
    "|0⟩": (1.0, 0.0),
    "|1⟩": (0.0, 1.0),
    "|+⟩": (c, c),
    "|-⟩": (c, -c),
    "|i+⟩": (c, 1j * c),
}

for name, (a, b) in states.items():
    x, y, z = state_to_bloch(a, b)
    print(f"  {name:5s} → Bloch ({x:+.4f}, {y:+.4f}, {z:+.4f})")

# 3. Convert to quaternion
print("\n=== Spinor to quaternion ===")
q = spinor_to_quaternion(alpha, beta)
print(f"Spinor: ({alpha:.4f}, {beta:.4f})")
print(f"Quaternion: {q}")
print(f"Unit:       {q.is_unit()}")

# 4. Fidelity calculations
print("\n=== State fidelity ===")
import numpy as np
psi0 = np.array([1.0, 0.0], dtype=complex)
psi1 = np.array([0.0, 1.0], dtype=complex)
psi_plus = np.array([c, c], dtype=complex)

print(f"F(|0⟩, |0⟩)  = {state_fidelity(psi0, psi0):.4f}")
print(f"F(|0⟩, |1⟩)  = {state_fidelity(psi0, psi1):.4f}")
print(f"F(|0⟩, |+⟩)  = {state_fidelity(psi0, psi_plus):.4f}")
print(f"F(|+⟩, |+⟩)  = {state_fidelity(psi_plus, psi_plus):.4f}")
