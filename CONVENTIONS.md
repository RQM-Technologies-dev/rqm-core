# Mathematical Conventions

This document is the single source of truth for every mathematical convention
used in `rqm-core`.  All higher-level packages in the RQM ecosystem
(`rqm-qiskit`, `rqm-circuits`, `rqm-compiler`, …) **must** adopt these
conventions and may cite this file as their authority.

---

## 1 — SU(2) Convention

A unit quaternion `q = w + xi + yj + zk` is mapped to a 2×2 SU(2) matrix by:

```
q  →  [[ w − iz ,  −y − ix ],
       [ y − ix ,   w + iz ]]
```

Equivalently, writing `α = w − iz` and `β = y − ix`:

```
U(q) = [[ α  , −β* ],
         [ β  ,  α* ]]
```

This is the standard "left spinor" embedding of the unit quaternions into
`SU(2)`.  The correspondence is implemented in
`Quaternion.to_su2_matrix()` and inverted by `su2_to_quaternion()`.

---

## 2 — Spinor Convention

A two-component quantum state is written as:

```
|ψ⟩ = α |0⟩ + β |1⟩
```

- `|0⟩` is the **computational-basis ground state** (north-pole of the Bloch
  sphere).
- `|1⟩` is the **computational-basis excited state** (south pole).
- `(α, β)` are arbitrary complex amplitudes; functions that require a unit
  spinor normalize internally and document this behaviour.

The spinor components are always passed as the ordered pair `(alpha, beta)`.

---

## 3 — Bloch Sphere Parameterization

The standard **physics** parameterization is used throughout:

```
|ψ⟩ = cos(θ/2) |0⟩  +  e^{iφ} sin(θ/2) |1⟩
```

| Parameter | Range | Description |
|---|---|---|
| `theta` (θ) | `[0, π]` | Polar angle (colatitude from north pole) |
| `phi` (φ) | `[0, 2π)` | Azimuthal angle |

Cartesian Bloch coordinates are derived from a normalized state as:

```
x = 2 Re(α* β)
y = 2 Im(α* β)
z = |α|² − |β|²
```

Canonical Bloch vectors:

| State | Bloch vector |
|---|---|
| `|0⟩` (north pole) | `(0, 0, +1)` |
| `|1⟩` (south pole) | `(0, 0, −1)` |
| `|+⟩` = (`|0⟩`+`|1⟩`)/√2 | `(+1, 0, 0)` |
| `|−⟩` = (`|0⟩`−`|1⟩`)/√2 | `(−1, 0, 0)` |
| `|i+⟩` = (`|0⟩`+i`|1⟩`)/√2 | `(0, +1, 0)` |

---

## 4 — Global Phase

A global complex phase `e^{iθ}` applied to `|ψ⟩` does not change any
observable.  Concretely:

- Two quaternions `q` and `−q` represent **the same rotation** in SO(3) and
  the same physical state on the Bloch sphere.
- `spinor_to_quaternion` encodes the rotation of `|0⟩` onto `|ψ⟩` **up to
  global phase**.  Consumers must not rely on the sign of the returned
  quaternion's scalar part.
- Round-trip tests (`q → SU(2) → q`) allow for a sign flip: equality is
  checked against both `q` and `−q`.

---

## 5 — Default Tolerance and Axis Labels

### Tolerance

All closeness checks and validation functions accept an `atol` keyword
argument with a default of **`1e-9`** (absolute tolerance, no relative
component).  This value was chosen to be safely below single-precision
floating-point noise while remaining above typical double-precision
rounding errors in matrix products.

```python
# All of these use atol=1e-9 by default:
q.is_unit()
is_normalized_spinor(alpha, beta)
matrix_close(a, b)
is_unitary(m)
determinant_close_to_one(m)
validate_bloch_vector(x, y, z)
validate_su2_matrix(m)
```

### Axis Labels

Cardinal rotation axes are identified by the single-character strings
`"x"`, `"y"`, or `"z"`.  Inputs are **case-insensitive** (`"X"` → `"x"`).
All angles are in **radians**.

```python
Quaternion.from_axis_angle("y", math.pi / 2)  # 90° around Y
axis_angle_to_su2("z", math.pi)               # 180° around Z
```
