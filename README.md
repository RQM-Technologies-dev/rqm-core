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

## Ecosystem Role

`rqm-core` is the **spine** of the RQM Python ecosystem.  It provides the
single canonical implementation of all shared mathematical primitives so that
downstream packages never need to re-implement or copy them.

**How downstream packages declare the dependency** (example `pyproject.toml` excerpt):

```toml
[project]
dependencies = [
    "rqm-core>=0.1.0",
]
```

**How downstream packages import:**

```python
# rqm-qiskit, rqm-circuits, rqm-compiler, etc.
from rqm_core import Quaternion, axis_angle_to_su2, state_to_bloch
```

**Contract for downstream maintainers:**

- All conventions are defined in [`CONVENTIONS.md`](CONVENTIONS.md) and must
  not be re-defined or overridden locally.
- Breaking changes to `rqm-core` require a **major version bump** (`1.0.0`, …).
- Any primitive needed by two or more packages belongs here, not in the
  individual packages.

---

## Quickstart

```python
from rqm_core import Quaternion, state_to_bloch, axis_angle_to_su2
import math

# 90° rotation around Y
q = Quaternion.from_axis_angle("y", math.pi / 2)
print(q)
# Quaternion(0.7071..., 0.0, 0.7071..., 0.0)

# SU(2) matrix directly from axis-angle
print(axis_angle_to_su2("y", math.pi / 2))

# |+⟩ state on the Bloch sphere → equator at (1, 0, 0)
c = 1 / math.sqrt(2)
x, y, z = state_to_bloch(c, c)
print(x, y, z)  # 1.0  0.0  0.0
```

---

## Package Structure

```
rqm-core/
  CONVENTIONS.md            – canonical mathematical conventions reference
  pyproject.toml            – package metadata and build config
  src/rqm_core/
    __init__.py      – canonical public API (import everything from here)
    py.typed         – PEP 561 marker (enables type checking in downstream packages)
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
# Install the package in editable mode with test dependencies
pip install -e ".[dev]"

# Run the full test suite
pytest

# Run with coverage report
pytest --cov=rqm_core --cov-report=term-missing

# Run a single test file
pytest tests/test_quaternion.py -v

# Run only the public-API contract tests
pytest tests/test_public_api.py -v
```

---

## Architectural Notes

- **`su2.is_unitary` is a thin domain-scoped shim** over `linalg.is_unitary`.
  Both exist intentionally: `linalg.is_unitary` is the general-purpose helper;
  `su2.is_unitary` is the public entry point for SU(2)-context callers and is
  what `rqm_core.is_unitary` resolves to in the top-level API.

- **`q` and `−q` represent the same rotation.**  Round-trip conversions
  `q → SU(2) → q` are tested against both `q` and `−q`.  Downstream code
  must never compare quaternion scalar parts for sign equality.

- **The `src/` layout** means `rqm_core` is only importable after installation
  (`pip install -e .`).  Running tests directly without installing first will
  produce `ModuleNotFoundError`.

- **`py.typed`** is included in the installed wheel (via `[tool.setuptools.package-data]`),
  enabling `mypy` and `pyright` in any package that depends on `rqm-core`.

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

