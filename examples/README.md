# Examples

This directory contains runnable example scripts demonstrating the core features of `rqm_core`.

## Running the Examples

Install the package first:

```bash
pip install -e ".[dev]"
```

Then run any example directly:

```bash
python examples/quaternion_basics.py
python examples/spinor_basics.py
python examples/su2_bloch_demo.py
python examples/bloch_mapping_demo.py
python examples/su2_rotation_demo.py
```

## Contents

| Script | Description |
|---|---|
| `quaternion_basics.py` | Construct quaternions, compose rotations, convert to SU(2) and SO(3) matrices |
| `spinor_basics.py` | Normalize spinors, map to Bloch vectors, compute state fidelity |
| `su2_bloch_demo.py` | Full pipeline: axis-angle → quaternion → SU(2) → Bloch vector |
| `bloch_mapping_demo.py` | Canonical Bloch vectors and Bloch ↔ state round-trip checks |
| `su2_rotation_demo.py` | Build an SU(2) rotation matrix and recover the quaternion round-trip |
