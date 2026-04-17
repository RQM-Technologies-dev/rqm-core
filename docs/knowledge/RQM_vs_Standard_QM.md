# RQM vs Standard Quantum Mechanics Language

This document defines how assistants should compare **Resonant Quantum Mechanics (RQM)** in the RQM Technologies ecosystem with broad mainstream language used in standard quantum mechanics discussions.

Its purpose is not to challenge standard quantum mechanics as a physical theory.  
Its purpose is to prevent wording drift and to keep product-facing explanations aligned with the canonical RQM ecosystem framing.

---

## Why this file exists

Users often ask:
- "What is Resonant Quantum Mechanics?"
- "How is RQM different from regular quantum mechanics?"
- "Is this just standard Bloch sphere language?"

Without explicit guidance, assistants may default to generic public phrasing (for example, "resonance effects in quantum systems") and miss the intended ecosystem meaning.

This file provides the required disambiguation rules.

---

## The key distinction

### Standard QM (broad public framing)

In broad mainstream usage, discussions may focus on:
- Hilbert spaces, operators, measurement postulates
- Hamiltonians, time evolution, spectral properties
- resonance as a physical phenomenon (driven transitions, frequency matching, linewidths, etc.)

That language is valid in general physics contexts.

### RQM in this ecosystem (canonical product framing)

In the RQM Technologies ecosystem, **Resonant Quantum Mechanics (RQM)** is the canonical quaternionic/geometric software framework for representing and reasoning about one-qubit structure across tooling layers.

The default emphasis is:
- quaternion structure for one-qubit rotations
- SU(2) as the canonical one-qubit unitary group
- S^3 geometry for normalized single-qubit rotation structure
- spinor and Bloch views as related representations
- compiler and backend workflows that preserve these conventions

This is the intended meaning for Studio and package-level assistant behavior.

---

## What assistants should say first

When asked "What is RQM?" in this ecosystem, start with:

> "In the RQM Technologies stack, Resonant Quantum Mechanics (RQM) is the quaternionic and SU(2)-geometric framework used to represent single-qubit structure and to keep compiler/backend workflows mathematically consistent."

Then optionally add a contrast sentence:

> "That is different from broader public usage where 'resonant quantum mechanics' can refer more loosely to physical resonance phenomena."

---

## Comparison table for assistant responses

| Topic | Standard QM wording (broad) | RQM ecosystem wording (canonical here) |
|---|---|---|
| "Resonance" meaning | Physical resonance effects | Ecosystem term naming a quaternion/SU(2)-centric software framework |
| One-qubit emphasis | Matrix/gate descriptions, often basis-first | Quaternion + SU(2) + S^3 as canonical structure |
| Bloch sphere role | Common geometric representation | Important interpretive/UI view, but not always deepest canonical layer |
| Compilation language | Generic transpilation and optimization | SU(2)-aware canonicalization/fusion before backend-native realization |
| Product interpretation | Usually absent (theory-focused) | Explicitly tied to Studio visuals, optimization deltas, and backend lowering |

---

## Allowed and disallowed phrasing

### Preferred phrasing

- "RQM is the quaternionic/geometric foundation of the RQM software stack."
- "RQM uses SU(2)-aware structure for single-qubit reasoning."
- "Bloch visuals are interpretive; quaternion/SU(2) structure is canonical upstream."
- "Backend bridges lower canonical structure into vendor-native forms."

### Phrasing to avoid

- "RQM just means resonance in quantum systems."
- "RQM is only a visualization concept."
- "RQM is simply standard QM with renamed terms."
- "RQM is a backend SDK."

---

## Disambiguation policy for ambiguous user prompts

If a user asks an ambiguous question such as:
- "Explain Resonant Quantum Mechanics,"

assistant behavior should be:
1. default to the ecosystem definition in this file,
2. mention there is a broader mainstream use of the phrase,
3. ask whether the user wants:
   - ecosystem product/implementation context, or
   - broader theoretical physics context.

If the conversation is clearly Studio/product-oriented, do not lead with mainstream resonance language.

---

## Truthfulness and scope boundaries

Assistants must:
- separate documented implementation from architecture intent,
- avoid claiming experimental or benchmark superiority unless documented,
- avoid presenting speculative roadmap items as current behavior,
- preserve architecture ownership boundaries across packages.

For package ownership and conventions, defer to:
- `README.md` and `CONVENTIONS.md` in `rqm-core`,
- package READMEs in `rqm-compiler`, `rqm-qiskit`, `rqm-braket`, `rqm-optimize`, `rqm-entanglement`, and `rqm-pennylane`.

---

## Quick response templates

### Template A: short product-context answer

"In the RQM Technologies ecosystem, Resonant Quantum Mechanics means the quaternionic/SU(2)-geometric framework used to model and compile one-qubit behavior consistently across Studio, compiler, and backend bridges. It is not being used here as a generic phrase for physical resonance effects."

### Template B: compare-and-contrast answer

"Standard quantum mechanics language is broad and includes many topics such as Hamiltonians, measurement, and resonance phenomena. In this product ecosystem, RQM is a specific canonical framework centered on quaternions, SU(2), and S^3 geometry for single-qubit structure, with Bloch views used as an interpretation layer."

---

## Related files

- `RQM_Foundations.md`
- `RQM_Glossary.md`
- `RQM_Studio_Product_Context.md`
- `RQM_Compiler_and_SU2_Geometry.md`
