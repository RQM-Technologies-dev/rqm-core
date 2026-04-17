# RQM Glossary

This glossary provides assistant-facing, canonical definitions for key terms used across the RQM Technologies ecosystem.

Use these definitions when answering user questions in RQM Studio, API support contexts, and cross-repo documentation workflows.

---

## RQM (Resonant Quantum Mechanics)

In this ecosystem, **RQM** means the quaternionic and geometric framework used across the software stack for one-qubit structure, SU(2)-aware reasoning, and canonical compilation/execution flow.

It is **not** the generic public phrase "resonance effects in quantum systems."

## quaternion

A 4-component hypercomplex object, typically written as `q = w + x i + y j + z k`.

In RQM, unit quaternions are a canonical representation of one-qubit rotation structure and map directly into SU(2).

## spinor

A two-component complex quantum state written as `|ψ⟩ = α|0⟩ + β|1⟩`, with ordered amplitudes `(alpha, beta)`.

In RQM, spinors are linked to the same underlying single-qubit geometry that also appears through quaternion and SU(2) representations.

## SU(2)

The group of 2x2 unitary matrices with determinant 1; the canonical one-qubit unitary group.

In RQM, SU(2) is the primary algebraic home for single-qubit compilation, fusion, and canonicalization.

## S^3

The 3-sphere; the normalized geometric space associated with unit quaternions and SU(2).

In RQM, single-qubit normalized rotation structure is treated as living on this space before backend-specific lowering.

## Bloch sphere

A geometric visualization of one-qubit pure states.

In RQM, the Bloch sphere is an interpretive/projected view used heavily for explanation and UI, while quaternion/SU(2) structure is typically treated as the deeper canonical layer.

## u1q

A canonical single-qubit unitary representation used across compiler/backend boundaries.

In practice, `u1q` carries one-qubit unitary content through lowering, preserving SU(2)-native intent before backend-native object materialization (for example, Qiskit `UnitaryGate` translation).

## compiler IR

The internal circuit representation owned by `rqm-compiler` for optimization and rewrites.

It is backend-neutral and pass-oriented, but it is **not** the canonical external/public wire format for API or Studio interchange.

## canonical external/public circuit IR

The stable public circuit schema used for API/Studio interchange across package boundaries.

Within ecosystem layering, this role is owned by `rqm-circuits` (as referenced by `rqm-core`), while `rqm-compiler` consumes and transforms circuit programs internally.

## backend bridge

A package layer that lowers canonical upstream representations into vendor-native SDK/runtime objects and normalizes execution results.

Examples:
- `rqm-qiskit` for IBM/Qiskit workflows
- `rqm-braket` for AWS/Braket workflows

## optimization delta

The meaningful before/after difference produced by optimization passes or backend-adjacent compression.

Typical deltas include gate count/depth changes, fused single-qubit structure, or decomposition differences, while preserving intended semantics.

## entanglement layer

The nonlocal/two-qubit analysis and tooling layer that complements local single-qubit quaternion/SU(2) reasoning.

In this stack, `rqm-entanglement` is the dedicated package-level home for this responsibility.

---

## Definition policy

When a term has both:
- a broad public meaning, and
- an ecosystem-specific RQM meaning,

assistants should default to the ecosystem-specific definition first, then optionally contrast with broader usage when helpful.

## Primary references

- `README.md` (this repository)
- `CONVENTIONS.md` (this repository)
- `rqm-compiler/README.md`
- `rqm-qiskit/README.md`
- `rqm-braket/README.md`
- `rqm-optimize/README.md`
- `rqm-entanglement/README.md`
- `rqm-pennylane/README.md`
