# Examples

This directory contains runnable example scripts that demonstrate the core features of `rqm_core`.

## Running the Examples

Install the package first:

```bash
pip install -e ".[dev]"
```

Then run any example directly:

```bash
python examples/quaternion_basics.py
python examples/su2_rotation_demo.py
python examples/bloch_mapping_demo.py
```

## Contents

| Script | Description |
|---|---|
| `quaternion_basics.py` | Construct quaternions, multiply rotations, convert to matrices |
| `su2_rotation_demo.py` | Compare quaternion rotation with the equivalent SU(2) matrix |
| `bloch_mapping_demo.py` | Map spinors to Bloch sphere vectors and compute state fidelity |
