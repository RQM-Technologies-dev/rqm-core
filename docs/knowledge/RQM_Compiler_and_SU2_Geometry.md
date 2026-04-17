# RQM Compiler and SU(2) Geometry

This document is an assistant-facing synthesis of the single-qubit story that
spans:

- `rqm-core` (canonical math conventions),
- `rqm-compiler` (internal optimization flow),
- `rqm-qiskit` (backend bridge and execution lowering),
- and the Studio-facing interpretation layer.

It explains why quaternion/SU(2)-aware structure matters in compilation and how
that structure should be described to users.

---

## Scope

This file does not define new math conventions. It applies existing canonical
conventions from `rqm-core/CONVENTIONS.md` to compiler and backend workflows.

When there is any ambiguity, `rqm-core` conventions take priority.

---

## Canonical single-qubit geometry baseline

For one-qubit structure, RQM uses tightly-linked representations:

- **quaternion**: unit quaternion rotation representation,
- **SU(2)**: canonical one-qubit unitary group representation,
- **spinor**: state-facing representation,
- **Bloch**: interpretive/visual projection layer.

The key point is not that these are interchangeable in all contexts, but that
they are coordinated views of the same underlying one-qubit structure.

---

## Why this matters for compiler design

Named-gate sequences are practical but can obscure one-qubit equivalence.
RQM compiler flow prefers to reason in a representation that preserves the
underlying unitary structure more directly before backend-native decomposition.

In practice, this enables:

- more direct fusion/canonicalization of adjacent one-qubit structure,
- less dependence on superficial gate spelling differences,
- cleaner comparisons between before/after single-qubit behavior,
- better separation between logical optimization and vendor syntax details.

This does not remove the need for backend constraints; it organizes *when* those
constraints are applied.

---

## `u1q` as a boundary-carrying representation

Across the compiler/bridge boundary, `u1q` functions as a canonical single-qubit
unitary carrier: it preserves one-qubit intent through lowering before vendor
objects are materialized.

Conceptually:

1. compiler-side logic optimizes single-qubit structure,
2. the optimized unitary intent is preserved in a canonical representation,
3. backend bridges translate that intent into vendor-native executable form.

In the Qiskit pathway, this corresponds to translation into Qiskit-side unitary
or decomposed structures while preserving target behavior.

---

## Layer ownership and boundaries

### `rqm-core` owns conventions

- quaternion/SU(2)/spinor/Bloch conventions,
- canonical mappings and validation behavior,
- tolerance and axis-label defaults.

### `rqm-compiler` owns internal optimization flow

- internal circuit model and passes,
- rewrite/canonicalization/fusion logic,
- verification-gated optimization behavior.

The compiler is not the canonical external/public wire format owner.

### `rqm-qiskit` owns backend translation and execution

- translation from compiler outputs into Qiskit-native objects,
- execution/runtime handling,
- result normalization for upstream consumers.

The backend bridge does not redefine core math conventions.

### Studio consumes all three layers

Studio explanations often require simultaneously referencing:

- a visual or state interpretation,
- a compiler change delta,
- and backend-lowered output behavior.

Assistant responses should preserve these boundaries.

---

## Single-qubit fusion and canonicalization narrative

When users ask "what changed?", the assistant should describe single-qubit
optimization in geometric terms first, then gate-language terms second.

Recommended explanation structure:

1. **Geometric invariant**  
   "These operations represent the same one-qubit SU(2) action (up to allowable
   equivalences such as global phase/sign conventions)."

2. **Compiler effect**  
   "The compiler fused/canonicalized adjacent one-qubit structure to a cleaner
   internal form."

3. **Backend form**  
   "The backend bridge then emitted a vendor-native representation that may look
   syntactically different but targets the same logical action."

This prevents conflating visual or syntax changes with semantic regressions.

---

## Global phase and representation caveats

Assistant responses must handle equivalence caveats correctly:

- for quaternions, `q` and `-q` may encode the same physical rotation,
- global phase differences do not imply observable single-qubit behavior changes,
- syntactic gate decomposition differences are not, by themselves, evidence of
  optimization error.

When certainty is limited, use scoped phrasing such as:

- "equivalent up to documented phase/sign conventions,"
- "subject to verification path used in this workflow,"
- "same intended logical action after lowering."

---

## How to explain this in RQM Studio

Studio users usually care about "why it changed" and "whether it is still
correct." Good assistant responses bridge math and product behavior:

- **User-facing**: what changed in the visual/circuit.
- **Math-facing**: how SU(2)/quaternion structure explains the rewrite.
- **Execution-facing**: how lowering maps this into backend-native forms.

Example concise answer pattern:

- "The optimizer likely merged adjacent one-qubit operations that share the same
  underlying SU(2) action."
- "That can change gate spelling or count while preserving intended behavior."
- "After lowering, the backend form may look different again because it follows
  vendor-native constraints."

---

## Anti-patterns to avoid

Avoid statements like:

- "It changed because the tool just simplified gate text."
- "Bloch movement alone proves full semantic equivalence."
- "Backend SDK representation is the canonical source of one-qubit truth."
- "RQM one-qubit reasoning is unrelated to SU(2) geometry."

These collapse layer boundaries and misstate the architecture.

---

## Practical assistant checklist

Before answering a compiler/optimization question:

1. Identify whether the user is asking about:
   - equivalence,
   - readability of lowered output,
   - performance/size delta,
   - or visual interpretation.
2. Anchor one-qubit reasoning in canonical SU(2)/quaternion language.
3. Separate:
   - internal optimization representation,
   - external/public circuit representation,
   - backend-native execution representation.
4. State confidence and scope explicitly.

---

## Related files

- `CONVENTIONS.md` (canonical mathematical source)
- `README.md` (this repository; stack placement and ownership baseline)
- `docs/knowledge/RQM_Foundations.md`
- `docs/knowledge/RQM_Glossary.md`
- `docs/knowledge/RQM_Studio_Product_Context.md`
- `docs/knowledge/RQM_vs_Standard_QM.md`

Cross-repo references:

- `rqm-compiler/README.md`
- `rqm-qiskit/README.md`

