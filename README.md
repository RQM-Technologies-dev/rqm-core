# RQM Core

> Foundational mathematics library for the RQM Python ecosystem.

`rqm-core` provides canonical, well-tested implementations of:

- **Quaternion algebra** – Hamilton product, conjugation, norm, inverse, axis-angle construction
- **SU(2) mappings** – bijection between unit quaternions and 2 × 2 special-unitary matrices
- **Bloch sphere geometry** – conversion between quantum spinors and Bloch vectors
- **Spinor utilities** – normalization, fidelity, and spinor↔quaternion/SU(2) conversions
- **Shared numerical utilities** – `numpy`-backed linear algebra helpers and tolerance functions

This package intentionally has **no dependency on Qiskit or any quantum framework**; it is the
stable mathematical foundation that higher RQM packages (e.g. `rqm-qiskit`) build upon.

---

## Overview

### Quaternion representation of rotations

A unit quaternion `q = w + x·i + y·j + z·k` with `|q| = 1` encodes a rotation in SO(3).
It is the most numerically stable way to compose and interpolate rotations, avoiding the
gimbal-lock problem of Euler angles and the redundancy of rotation matrices.

The axis-angle formula used throughout `rqm-core` is:

```
q = cos(θ/2) + u · sin(θ/2)
```

where `u` is the unit vector along the rotation axis and `θ` is the rotation angle.

### Relationship between SU(2) and quaternions

There is a two-to-one Lie group homomorphism `SU(2) → SO(3)`.  Every unit quaternion maps to
a unique 2 × 2 special unitary matrix via:

```
q ↦  [[ w − i·z ,  −(y + i·x) ],
      [ y − i·x ,   w + i·z  ]]
```

The quaternion and its negative represent the same physical rotation but correspond to
distinct SU(2) elements (a global phase).

### Bloch sphere geometry

A qubit state `|ψ⟩ = α|0⟩ + β|1⟩` corresponds to a point on the unit sphere in ℝ³:

```
x = 2 Re(α̅ · β)
y = 2 Im(α̅ · β)
z = |α|² − |β|²
```

The standard poles are `|0⟩ → (0, 0, 1)` and `|1⟩ → (0, 0, −1)`.

### Supporting higher RQM packages

`rqm-core` exports stable, versioned APIs.  Dependent packages import directly:

```python
from rqm_core.quaternion import Quaternion
from rqm_core.su2 import quaternion_to_su2
```

---

## Installation

```bash
pip install rqm-core
```

For development (includes `pytest` and `pytest-cov`):

```bash
pip install "rqm-core[dev]"
```

---

## Quickstart

```python
from rqm_core.quaternion import Quaternion

# Build a 90° rotation around Y
q = Quaternion.from_axis_angle("y", 1.5707963267948966)
print(q)
# → Quaternion(0.7071..., 0.0, 0.7071..., 0.0)

# Get the equivalent SU(2) matrix
print(q.to_su2_matrix())

# Compose rotations
q2 = Quaternion.from_axis_angle("z", 1.2)
q_combined = q * q2
```

```python
from rqm_core.bloch import state_to_bloch
import math

c = 1 / math.sqrt(2)
print(state_to_bloch(c, c))   # |+⟩ → [1. 0. 0.]
```

---

## Package Structure

```
src/rqm_core/
  __init__.py     – public API surface
  quaternion.py   – Quaternion class
  su2.py          – SU(2) construction and validation
  bloch.py        – Bloch sphere conversions
  spinor.py       – Spinor utilities and fidelity
  linalg.py       – Low-level numpy linear algebra helpers
  types.py        – Shared type aliases (ComplexVector2, BlochVector, SU2Matrix)
  utils.py        – Tolerance and wrapping utilities

tests/
  test_quaternion.py
  test_su2.py
  test_bloch.py
  test_spinor.py

examples/
  quaternion_basics.py
  su2_rotation_demo.py
  bloch_mapping_demo.py
  README.md
```

---

## Running Tests

```bash
pip install ".[dev]"
pytest --cov=rqm_core --cov-report=term-missing
```

---

## Roadmap

- [ ] Quaternion SLERP (spherical linear interpolation)
- [ ] Full SO(3) rotation-matrix ↔ quaternion round-trip
- [ ] Mixed-state density matrix utilities
- [ ] SU(2) Lie-algebra (generators and exponential map)
- [ ] Type-stub files (`.pyi`) for IDE support

