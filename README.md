# RQM Core

> Core quaternion, spinor, SU(2), and Bloch mathematics for the RQM Python ecosystem.

[![PyPI version](https://img.shields.io/pypi/v/rqm-core.svg)](https://pypi.org/project/rqm-core/)
[![Python versions](https://img.shields.io/pypi/pyversions/rqm-core.svg)](https://pypi.org/project/rqm-core/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-rqmtechnologies.com-blue.svg)](https://www.rqmtechnologies.com/docs)
[![Website](https://img.shields.io/badge/website-rqmtechnologies.com-blue.svg)](https://rqmtechnologies.com)

---

## 🌐 RQM Platform

This repository is part of the RQM Technologies ecosystem.

→ Website: https://rqmtechnologies.com  
→ Documentation: https://www.rqmtechnologies.com/docs

---

## RQM Technical Canon v2

`rqm-core` is the standard-compatible quaternion algebra and `SU(2)` geometry
authority for the RQM software stack. Unit quaternions and complete `SU(2)`
matrices encode the same single-rotation information. This package does not
claim additional quantum information or alternative mechanics.

RQM uses quaternion-native coordinates when their structured representation can
improve software, diagnostics, integration, or measured execution. Those
advantages must be established against strong equivalent baselines. See
[RQM_TECHNICAL_CANON_V2.md](RQM_TECHNICAL_CANON_V2.md).

---

## Install

```bash
pip install rqm-core
```

`rqm-core` is the mathematical foundation layer. It has no RQM-level dependencies — only `numpy` at runtime.

---

## Where This Fits

```
rqm-core  →  rqm-circuits  →  rqm-compiler  →  rqm-qiskit / rqm-braket
                                                        ↓ (optional)
                                                   rqm-optimize
```

`rqm-core` provides the canonical mathematical layer of the RQM ecosystem —
quaternion, spinor, Bloch, and SU(2) foundations.  It owns no circuit schema,
no compiler passes, and no backend execution logic.

**Layer responsibilities:**

| Package | Role |
|---|---|
| **rqm-core** | Mathematical spine — quaternion, spinor, SU(2), Bloch |
| **rqm-circuits** | Canonical external circuit IR / wire format (API, Studio, interchange) |
| **rqm-compiler** | Optimization and rewriting engine — consumes rqm-circuits programs |
| **rqm-entanglement** | Canonical nonlocal layer — two-qubit tensor structure, coupling analysis, entanglement metrics |
| **rqm-qiskit** | IBM / Qiskit lowering and execution bridge |
| **rqm-braket** | AWS / Braket lowering and execution bridge |
| **rqm-optimize** | Optional backend-adjacent optimization / compression layer |

`rqm-circuits 0.2` is the canonical external circuit format for all API and Studio workflows.
`rqm-compiler` consumes and optimizes circuit programs but is not the primary public wire format.
Backend packages (`rqm-qiskit`, `rqm-braket`) translate optimized circuits into vendor-native objects.
`rqm-optimize` is optional and sits later in the execution flow, above the backend bridges.

---

## Next Steps

- Documentation: https://www.rqmtechnologies.com/docs
- Website: https://rqmtechnologies.com
- Next package in the stack: [`rqm-circuits`](https://github.com/RQM-Technologies-dev/rqm-circuits) — the canonical external circuit IR for API and Studio workflows (rqm-circuits 0.2+)
- After circuits: [`rqm-compiler`](https://github.com/RQM-Technologies-dev/rqm-compiler) — optimization and rewriting engine

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
- **Compatibility coupling analysis** – legacy qualitative/measured helpers retained for existing imports; canonical nonlocal analysis now lives in `rqm-entanglement`

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

`q` and `−q` represent the same SO(3)/Bloch rotation, while their SU(2)
matrices differ by a global phase of `−1`.  `spinor_to_quaternion` encodes the
rotation up to global phase — never rely on the sign of the scalar part.

### 5 · Default Tolerance and Axis Labels

All closeness checks default to `atol = 1e-9` (absolute, no relative
component).  Axis labels are `"x"`, `"y"`, `"z"` (case-insensitive);
all angles are in **radians**.

---

## Coupling / Entanglement Analysis

`rqm_core` retains a compatibility analysis layer for existing imports, but it is no longer the canonical owner of coupling and entanglement analysis.  New API and Studio integrations should call `rqm-entanglement`.

### Architecture

The two layers are mathematically complementary and do not compete:

| Layer | Scope | Technology |
|---|---|---|
| **Single-qubit local structure** | Individual qubit rotations | Quaternionic / SU(2) (quaternion optimizer) |
| **Multi-qubit entanglement** | Cross-qubit coupling / correlation | `rqm-entanglement` state analysis, concurrence, entropy |

The quaternionic single-qubit optimizer is the correct route for local SU(2) operations.  The coupling analysis layer adds truthful multi-qubit analysis *beside* it.

### Quickstart

```python
from rqm_core import Circuit, GateOp, analyze_circuit_coupling

# Bell state: H q0, CNOT q0→q1
circuit = Circuit(
    num_qubits=2,
    operations=[
        GateOp(name="H",    qubits=[0]),
        GateOp(name="CNOT", qubits=[0, 1]),
    ],
)

result = analyze_circuit_coupling(circuit)
print(result.mode)          # "measured"
print(result.is_entangled)  # True
print(result.pair_metrics[0].value)  # 1.0  (concurrence)
```

### Measured Analysis Scope (first implementation)

| Criterion | Scope |
|---|---|
| Qubits | Exactly 2 |
| Initial state | \|00⟩ |
| Single-qubit gates | I, X, Y, Z, H, S, T, Rx(θ), Ry(θ), Rz(θ), U(θ,φ,λ) / U3 |
| Two-qubit gates | CNOT / CX, CZ, SWAP |
| Metrics | Concurrence, von Neumann entropy |

Circuits outside this scope receive an honest **qualitative fallback** (gate detection only) with explicit `limitations` in the result — no fabricated measured values.

### Result Contract

```python
@dataclass
class CouplingAnalysisResult:
    mode: str                          # "measured" | "qualitative"
    provenance: str                    # "rqm-core" | "parser"
    qubit_count: int
    analyzed_pairs: list[tuple[int, int]]
    has_entangling_gates: bool
    entangling_gate_count: int
    entangling_gates_seen: list[str]
    last_entangling_gate: str | None
    is_entangled: bool | None          # None in qualitative mode
    pair_metrics: list[PairMetric]     # empty in qualitative mode
    fidelity_preserved: float | None
    notes: list[str]
    limitations: list[str]
```

### Compiler Verification

```python
from rqm_core import analyze_optimization_preservation

result = analyze_optimization_preservation(original_circuit, optimized_circuit)
print(result.fidelity_preserved)              # e.g. 1.0
print(result.preserved_entanglement_structure) # True / False / None
```

---

## What Is Not Included

`rqm-core` intentionally does **not** own:

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

`rqm-core` is the **mathematical spine** of the RQM Python ecosystem.  It provides the
single canonical implementation of all shared mathematical primitives so that
downstream packages never need to re-implement or copy them.

**What rqm-core owns:**
- Quaternion primitives (Hamilton product, conjugate, inverse, axis-angle, SO(3)/SU(2) conversions)
- SU(2) / Bloch / spinor mathematics
- Shared linear algebra helpers
- Coupling / entanglement analysis primitives

**What rqm-core does NOT own:**
- Circuit IR or schema — that is `rqm-circuits`
- Compiler rewrites or optimization passes — that is `rqm-compiler`
- Backend execution or vendor-native objects — that is `rqm-qiskit` / `rqm-braket`
- API service boundaries or Studio wire formats — those live above `rqm-circuits`

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
    analysis/
      coupling/
        types.py                          – Circuit IR + result contract dataclasses
        detect_entangling_structure.py    – qualitative gate-based detection
        simulate_two_qubit_state.py       – ideal 2-qubit pure-state simulator
        metrics.py                        – concurrence, entropy, fidelity helpers
        analyze_circuit_coupling.py       – main public entry point
        analyze_optimization_preservation.py – before/after compiler verification

  tests/
    test_quaternion.py
    test_spinor.py
    test_su2.py
    test_bloch.py
    test_linalg.py
    test_utils.py
    test_validation.py
    test_public_api.py
    analysis/
      coupling/
        test_detect_entangling_structure.py
        test_simulate_two_qubit_state.py
        test_metrics.py
        test_analyze_circuit_coupling.py
        test_analyze_optimization_preservation.py

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

- **`q` and `−q` represent the same SO(3)/Bloch rotation, not the same SU(2)
  matrix.**  Round-trip conversions `q → SU(2) → q` are tested against both
  `q` and `−q` because the sign is a global phase.  Downstream code must never
  compare quaternion scalar parts for sign equality.

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
- [ ] Coupling analysis for >2 qubits (partial trace for n-qubit systems, mutual information)
- [ ] Support for additional gate sets in the 2-qubit simulator

No Qiskit or framework dependencies will ever be added to this package.
