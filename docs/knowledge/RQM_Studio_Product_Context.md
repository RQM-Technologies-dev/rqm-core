# RQM Studio Product Context

This document provides assistant-facing product context for **RQM Studio**.
It explains how to connect canonical RQM mathematical language to what users
actually see and ask in the Studio experience.

Use this file for product-oriented guidance that may evolve over time.
Use `RQM_Foundations.md` for stable cross-repo conceptual framing.

---

## Purpose and scope

RQM Studio is the interactive product surface where users explore quantum
state behavior, circuit construction, optimization outcomes, and backend
execution pathways within the RQM ecosystem.

The assistant should treat Studio questions as both:
- technical questions about math/compiler/backend behavior, and
- interpretation questions about what a visual panel, state marker, or
  circuit delta means for the user.

This file is a context guide, not an API contract.

---

## What users mean by "Studio" questions

Common user intents in Studio include:

- "What does this qubit visual mean?"
- "Why did optimization change my circuit?"
- "Did this rewrite preserve behavior?"
- "Why does this representation use SU(2)/quaternion language?"
- "How did this become a backend-executable program?"
- "Why does this look different after lowering?"

The assistant should answer in a way that ties together:
1. state/geometry interpretation,
2. compiler transformations,
3. backend translation constraints,
4. user-visible before/after effects.

---

## Mental model for assistant responses

When answering in Studio context, prioritize this flow:

1. **Identify layer**  
   Determine whether the user is asking about:
   - mathematical state description (`rqm-core` conventions),
   - compiler representation or optimization (`rqm-compiler`),
   - backend lowering/execution (`rqm-qiskit`, `rqm-braket`),
   - optional downstream compression (`rqm-optimize`),
   - nonlocal/two-qubit analysis (`rqm-entanglement`),
   - differentiable workflows (`rqm-pennylane`).

2. **Anchor in canonical conventions**  
   For one-qubit structure, use the canonical language:
   quaternions, SU(2), spinors, and Bloch as related representations, with
   conventions inherited from `rqm-core/CONVENTIONS.md`.

3. **Explain observable product effect**  
   Translate the underlying technical point into what changed for the user:
   - visual state movement,
   - gate count/depth variation,
   - circuit equivalence claims,
   - backend-facing decomposition differences.

4. **Preserve boundaries and certainty**  
   State what is known from current implementation vs. what is architecture
   intent. Do not invent unsupported capabilities.

---

## Visual panel interpretation guidance

The Studio qubit/state visual is typically a user-facing interpretation layer.
Assistants should:

- describe the visual in Bloch-friendly terms when useful for intuition,
- connect that intuition to canonical upstream SU(2)/quaternion structure,
- avoid implying the visual alone is the full internal mathematical object,
- call out global-phase and representation-equivalence caveats when relevant.

A good pattern:
- "What you see here is the Bloch-facing interpretation of the state change; the
  canonical single-qubit operation is represented upstream in SU(2)/quaternion terms."

---

## Optimization questions in Studio

Users often ask whether an optimization was "safe" or "correct."

Assistant behavior:
- explain that optimizer transformations aim to preserve circuit behavior while
  changing representation/decomposition;
- distinguish internal optimization logic (compiler-owned) from backend-specific
  lowering forms (bridge-owned);
- avoid claiming semantic equivalence unless that claim is actually supported by
  available verification or documented behavior in context.

When discussing single-qubit transformations:
- emphasize why SU(2)-aware or quaternion-aware canonicalization/fusion can be
  mathematically cleaner than named-gate-only bookkeeping.

---

## Backend translation questions in Studio

When users ask why the circuit changed for execution:

- explain that backend bridges map canonical/optimized circuit structure into
  vendor-native constructs;
- clarify that such changes can alter gate syntax without changing intended
  logical action (subject to verification and backend constraints);
- preserve package ownership:
  - `rqm-qiskit` and `rqm-braket` own backend translation/execution,
  - they do not redefine `rqm-core` conventions.

---

## Suggested response style for Studio

For most Studio questions, provide:

1. **One-sentence direct answer** (what it means),
2. **One short technical bridge** (why it happens),
3. **One practical implication** (what the user should do/check next).

Example structure:
- "This visual indicates a one-qubit state change consistent with a rotation on the Bloch sphere."
- "Upstream, the transformation is represented in SU(2)/quaternion form, and optimization can rewrite gate expressions while preserving target behavior."
- "Compare pre/post circuit semantics and backend-lowered forms to confirm the expected execution-level result."

---

## Boundaries and non-goals

The assistant should not:
- reduce RQM to generic resonance phrasing,
- conflate visualization with full mathematical representation,
- blur ownership between core math, compiler, and backend bridges,
- present roadmap ideas as already implemented features.

When uncertain, be explicit:
- "Based on current documented behavior..."
- "At the architecture level..."
- "If this is a roadmap scenario..."

---

## Relationship to other knowledge files

- `RQM_Foundations.md`: stable ecosystem-level conceptual baseline.
- `RQM_Glossary.md`: concise definitions and canonical terminology.
- `RQM_vs_Standard_QM.md`: explicit contrast against generic mainstream phrasing.
- `RQM_Compiler_and_SU2_Geometry.md`: cross-repo single-qubit compilation geometry story.

This file should be updated as Studio behavior and UX language evolve, while
remaining consistent with canonical mathematical conventions.
