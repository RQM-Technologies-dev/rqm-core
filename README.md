# RQM Core

> Core quaternion, spinor, SU(2), and Bloch mathematics for the RQM Python ecosystem.

---

## Why This Package Exists

Higher-level RQM libraries (simulators, compilers, hardware adapters) all require a
common, reliable layer of linear algebra and quantum geometry.  `rqm-core` is that layer.

It provides a single, versioned source of truth for the mathematical primitives shared
across the whole ecosystem: no duplication, no conflicting conventions, and no framework lock-in.

---

## Design Principles

| Principle | What it means in practice |
|---|---|
| **Tiny** | Only implement primitives that are needed by ≥2 packages |
| **Stable** | Slow to change; breaking changes require a major version bump |
| **Dependency-light** | Only `numpy` at runtime |
| **Canonical** | One correct convention, clearly documented, used everywhere |
| **Well-tested** | Strong test coverage from the first commit |

---

## What Is Included

- **Quaternion primitives** – Hamilton product, conjugate, inverse, axis-angle construction, SO(3) and SU(2) conversions
- **Spinor helpers** – normalization, norm, fidelity, spinor↔quaternion/SU(2) mappings
- **SU(2) conversions** – construction from quaternions and axis-angle, validation, round-trips
- **Bloch sphere mappings** – state↔Bloch, Bloch↔state, quaternion rotation to Bloch vector
- **Matrix helpers** – trace, determinant, conjugate transpose (dagger), norm, closeness checks
- **Validation utilities** – axis, complex pair, matrix shape, real number, tolerance checks

---

## Mathematical Conventions

The full reference lives in [`CONVENTIONS.md`](CONVENTIONS.md).
The five items every downstream package needs to know:

### 1 · SU(2) Convention

A unit quaternion `q = w + xi + yj + zk` maps to SU(2) as:

```
U(q) = [[ w − iz ,  −y − ix ],
         [ y − ix ,   w + iz ]]
```

Implemented in `Quaternion.to_su2_matrix()`; inverted by `su2_to_quaternion()`.

### 2 · Spinor Convention

States are written `|ψ⟩ = α|0⟩ + β|1⟩` with `|0⟩` as the north-pole
computational-basis ground state.  Amplitudes are always passed as the ordered
pair `(alpha, beta)`.  Functions that require unit norm normalize internally.

### 3 · Bloch Sphere Parameterization

```
|ψ⟩ = cos(θ/2)|0⟩ + e^{iφ} sin(θ/2)|1⟩
```

`theta` ∈ `[0, π]` (polar/colatitude), `phi` ∈ `[0, 2π)` (azimuthal).
`|0⟩` → north pole `(0, 0, +1)`;  `|1⟩` → south pole `(0, 0, −1)`.

### 4 · Global Phase

`q` and `−q` represent the same rotation.  `spinor_to_quaternion` encodes
the rotation up to global phase — never rely on the sign of the scalar part.

### 5 · Default Tolerance and Axis Labels

All closeness checks default to `atol = 1e-9` (absolute, no relative
component).  Axis labels are `"x"`, `"y"`, `"z"` (case-insensitive);
all angles are in **radians**.

---

## What Is Intentionally *Not* Included

- Qiskit / PennyLane / Cirq adapters
- Backend execution or hardware drivers
- Circuit transpilation or compilation
- Plotting or visualisation
- Cloud workflow integration
- Notebook tooling
- Algorithm frameworks or optimisation workflows

Those belong in higher-level packages.

---

## Installation

```bash
pip install rqm-core
```

Development install (includes `pytest` and `pytest-cov`):

```bash
pip install "rqm-core[dev]"
```

---

## Quickstart

```python
from rqm_core.quaternion import Quaternion
from rqm_core.bloch import state_to_bloch
import math

# 90° rotation around Y
q = Quaternion.from_axis_angle("y", math.pi / 2)
print(q)
# Quaternion(0.7071..., 0.0, 0.7071..., 0.0)

# SU(2) matrix
print(q.to_su2_matrix())

# |+⟩ state on the Bloch sphere → equator at (1, 0, 0)
c = 1 / math.sqrt(2)
x, y, z = state_to_bloch(c, c)
print(x, y, z)  # 1.0  0.0  0.0
```

---

## Package Structure

```
src/rqm_core/
  __init__.py      – canonical public API
  quaternion.py    – Quaternion class (Hamilton algebra, SO(3)/SU(2) conversions)
  spinor.py        – spinor normalization, fidelity, spinor↔quaternion/SU(2)
  su2.py           – SU(2) construction, validation, quaternion round-trips
  bloch.py         – Bloch sphere mappings and validation
  linalg.py        – matrix helpers (dagger, trace, determinant, closeness)
  validation.py    – shared validation helpers (axis, matrix shape, tolerances)
  types.py         – shared type aliases (ComplexVector2, BlochVector, SU2Matrix, …)
  utils.py         – small math utilities (angle_wrap, safe_norm, is_finite_*)

tests/
  test_quaternion.py
  test_spinor.py
  test_su2.py
  test_bloch.py
  test_linalg.py
  test_utils.py
  test_validation.py
  test_public_api.py

examples/
  quaternion_basics.py    – quaternion construction, composition, conversion
  spinor_basics.py        – spinor normalization, Bloch mapping, fidelity
  su2_bloch_demo.py       – axis-angle → SU(2) → Bloch pipeline
  bloch_mapping_demo.py   – canonical Bloch vectors and round-trip checks
  su2_rotation_demo.py    – SU(2) construction and quaternion round-trip
```

---

## Testing

```bash
pip install ".[dev]"
pytest --cov=rqm_core --cov-report=term-missing
```

---

## Roadmap

`rqm-core` is intended to remain **small and stable** while higher-level packages evolve around it.

Planned additions for future minor versions:

- [ ] Quaternion SLERP (spherical linear interpolation)
- [ ] SO(3) rotation-matrix ↔ quaternion round-trip helpers
- [ ] Mixed-state density matrix utilities
- [ ] SU(2) Lie-algebra generators and exponential map
- [ ] Type stub files (`.pyi`) for IDE completions

No Qiskit or framework dependencies will ever be added to this package.

