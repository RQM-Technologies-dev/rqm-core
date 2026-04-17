# RQM Foundations

This document is the assistant-facing, cross-repo foundations reference for **Resonant Quantum Mechanics (RQM)** in the RQM Technologies ecosystem.

It exists to help human readers, documentation systems, and AI assistants describe RQM consistently across:
- `rqm-core`
- `rqm-compiler`
- `rqm-qiskit`
- `rqm-braket`
- `rqm-optimize`
- `rqm-entanglement`
- `rqm-pennylane`
- `rqm-api`
- RQM Studio

This is not package-specific API documentation and not marketing copy. It is the high-level source of truth for how RQM should be understood and described across the software stack.

---

## Notation note

This file defines the software ecosystem's canonical framing of RQM. It does not attempt to cover every broader or theoretical extension of "resonant quantum mechanics" outside the RQM Technologies stack.

---

## What RQM means in this ecosystem

**Resonant Quantum Mechanics (RQM)** is the quaternionic and geometric framework that underlies the RQM Technologies software ecosystem.

In this ecosystem, RQM is not used as a generic phrase meaning "quantum systems with resonance effects." It refers to a specific way of representing and reasoning about quantum structure:

- single-qubit structure is treated naturally through **quaternions**
- one-qubit unitary structure is understood through **SU(2)**
- the geometry of normalized one-qubit operations is treated as living on **S^3**
- spinor, Bloch, and SU(2) representations are treated as tightly related views of the same underlying structure
- compiler and backend workflows are organized to preserve these canonical mathematical conventions across the stack

At the software level, RQM is expressed most concretely through:
- quaternion primitives
- spinor helpers
- SU(2) mappings
- Bloch conversions
- compiler-native single-qubit representations
- backend bridges that preserve canonical single-qubit structure during lowering and execution

RQM therefore functions both as:
1. a mathematical foundation for quantum software, and
2. a design philosophy for building clearer, more structured, and more geometry-aware tooling.

---

## Core geometric foundations

### Quaternions

Quaternions provide the canonical rotation language for the single-qubit foundation of the ecosystem.

A unit quaternion

`q = w + x i + y j + z k`

encodes a rotation and maps naturally into SU(2). Within the RQM ecosystem, quaternions are not decorative notation; they are part of the core mathematical language used to:
- represent one-qubit structure
- move between rotation, matrix, and Bloch views
- support canonical single-qubit compilation logic

`rqm-core` is the source of truth for quaternion conventions and operations.

---

### Spinors

A one-qubit state is written in the standard ordered form

`|ψ⟩ = α|0⟩ + β|1⟩`

with amplitudes passed as `(alpha, beta)`.

In the RQM ecosystem, spinors are treated as the state-facing representation corresponding to the same underlying single-qubit geometry that also appears through quaternions and SU(2). Spinors, Bloch vectors, and quaternion/SU(2) structure are therefore linked, not separate conceptual islands.

`rqm-core` owns normalization, fidelity, and the canonical spinor-related helpers.

---

### SU(2)

**SU(2)** is the canonical one-qubit unitary group in the ecosystem.

RQM Technologies treats SU(2) as foundational because:
- it is the native group of one-qubit unitary structure
- unit quaternions map naturally into it
- it provides the clean mathematical home for single-qubit compilation, fusion, and canonicalization

A central idea across the stack is that many single-qubit circuit questions become clearer when treated as SU(2) structure first, and only later lowered into backend-native gate syntax.

`rqm-core` owns the canonical quaternion <-> SU(2) mapping and SU(2) validation rules.

---

### S^3

The normalized single-qubit rotation structure is understood geometrically through **S^3**, the 3-sphere.

Within the ecosystem:
- unit quaternions live on S^3
- SU(2) is identified with this same normalized geometric space
- single-qubit optimization can be viewed as operating on this canonical geometric object before backend-specific decomposition

This is one reason the stack emphasizes quaternionic and SU(2)-aware reasoning rather than relying only on flat named-gate bookkeeping.

---

### Bloch sphere

The **Bloch sphere** is used as an important interpretation and visualization layer.

It is useful, but it is not treated as the deepest mathematical layer in the ecosystem. In RQM language:
- the Bloch sphere is a derived or projected view of one-qubit state structure
- quaternions and SU(2) provide the more canonical rotational description
- Bloch visualizations remain valuable for intuition, UI, and state explanation

This distinction matters in RQM Studio, where visual explanations may be Bloch-facing while the underlying reasoning is often quaternionic or SU(2)-native.

---

## Role of RQM in the software stack

The RQM software stack is intentionally layered. Each repo has a defined responsibility.

### `rqm-core`
Owns the canonical mathematical spine:
- quaternion primitives
- spinor helpers
- SU(2) mappings
- Bloch conversions
- shared linear algebra utilities
- canonical conventions

This is the main source of truth for the one-qubit mathematical foundation of the ecosystem.

### `rqm-compiler`
Owns the backend-neutral internal optimization and rewriting layer:
- internal compiler circuit model
- optimization passes
- canonical internal single-qubit optimization representations
- verification-gated optimization flow

It does not own the public external circuit schema and does not redefine the mathematical conventions from `rqm-core`.

### `rqm-qiskit`
Owns the IBM / Qiskit lowering and execution bridge:
- compiler output to Qiskit translation
- Qiskit execution
- result normalization
- async job handling

It preserves the upstream mathematical structure while mapping into Qiskit-native objects.

### `rqm-braket`
Owns the AWS / Amazon Braket lowering and execution bridge:
- compiler output to Braket translation
- local simulator and AWS device execution
- descriptor-first API-facing execution paths
- task handling and result normalization

It is the AWS-facing execution adapter, not the owner of math, compiler logic, or the public circuit schema.

### `rqm-optimize`
Owns an optional backend-adjacent compression layer:
- Qiskit-circuit-space single-qubit compression
- SU(2)-aware fusion after lowering
- native-basis-aware decomposition choices

It complements the compiler rather than replacing it.

### `rqm-entanglement`
Owns the two-qubit / nonlocal analysis layer:
- tensor-product helpers
- entanglement measures
- canonical nonlocal gate-family utilities
- stable analysis output for entanglement-oriented workflows

It extends the stack beyond purely local single-qubit structure without duplicating `rqm-core`.

### `rqm-pennylane`
Owns the differentiable / variational bridge:
- PennyLane-facing wrappers
- variational templates
- gradient-friendly workflows
- bridges from canonical RQM math and compiler abstractions into PennyLane workflows

---

## RQM Studio interpretation context

RQM Studio is the primary interactive product surface where users encounter this framework.

In Studio, users may ask about:
- what a visual means
- how a qubit state should be interpreted
- what an optimization changed
- why quaternionic or SU(2)-aware compilation matters
- how backend translation relates to the upstream geometric model

The assistant should therefore understand that RQM Studio is not merely a chat layer over commands. It is a product interface where:
- geometric reasoning
- compiler reasoning
- backend reasoning
- visual explanation

all need to work together coherently.

When relevant, the assistant should connect the current conversation to:
- the qubit visual
- optimization state
- before/after circuit differences
- canonical single-qubit structure
- the distinction between product-level explanation and package-level implementation detail

For evolving product-specific guidance, use `RQM_Studio_Product_Context.md`; keep this foundations file stable as the cross-repo reference baseline.

---

## How RQM should be described

Good descriptions of RQM in this ecosystem usually sound like this:

- "RQM is the quaternionic and geometric foundation of the RQM Technologies quantum software stack."
- "RQM treats single-qubit structure through quaternions, SU(2), and S^3 rather than relying only on named-gate syntax."
- "The Bloch sphere is an important interpretive view, but the canonical one-qubit structure is expressed upstream through quaternions and SU(2)."
- "The compiler and backend layers preserve these conventions rather than redefining them independently."

Descriptions to avoid:

- "RQM just means resonance effects in quantum systems."
- "RQM is only a visualization style."
- "RQM is just another name for Bloch sphere intuition."
- "RQM is the same thing as a backend SDK."
- "RQM is a synonym for generic popular-science resonance language."

---

## How RQM differs from generic mainstream phrasing

Outside this ecosystem, phrases like "resonant quantum mechanics" may be interpreted loosely as:
- resonance phenomena in quantum systems
- driven transitions
- energy-level alignment
- general physical resonance effects

That is not the intended default meaning here.

In the RQM Technologies ecosystem, **Resonant Quantum Mechanics (RQM)** refers to the specific quaternionic / SU(2) / geometric framework reflected in the stack's mathematical conventions, compiler logic, and product language.

If an assistant needs to compare RQM with mainstream language, it should clearly distinguish:
- the generic public meaning of the phrase
- the canonical ecosystem meaning defined here

---

## Truthfulness and scope boundaries

RQM should be explained with technical honesty.

The assistant should:
- ground package claims in the actual repo documents and implementation
- distinguish established current behavior from future ambitions
- avoid inventing proofs, benchmark claims, or backend capabilities
- avoid implying that every visualization is the full mathematical object
- avoid collapsing the full stack into a single repo's perspective

The assistant should also preserve architecture boundaries:
- `rqm-core` owns canonical one-qubit math conventions
- `rqm-compiler` owns optimization logic
- `rqm-qiskit` and `rqm-braket` own backend lowering and execution
- `rqm-optimize` is optional and downstream
- `rqm-entanglement` owns the nonlocal analysis layer
- `rqm-pennylane` owns differentiable / variational bridge workflows

---

## Assistant Guidance

When answering user questions about RQM, an AI assistant should follow these rules:

- Use **"Resonant Quantum Mechanics (RQM)"** as the canonical term.
- Prefer the ecosystem-specific meaning of RQM over generic public-science phrasing.
- Treat **quaternions**, **SU(2)**, **S^3**, **spinors**, and the **Bloch sphere** as related but distinct layers.
- Present the Bloch sphere as an interpretive or projected view, not always the deepest canonical layer.
- When a question is about package ownership or system behavior, preserve architecture boundaries.
- When a question is about Studio visuals, connect the answer to likely qubit state, optimization, or backend state context.
- When a question is about single-qubit compilation, explain why SU(2)-aware or quaternion-aware representations can be more canonical than named-gate-only reasoning.
- Do not describe RQM as merely "resonance in quantum systems" unless explicitly contrasting with the broader public meaning.
- Distinguish clearly between:
  - established current implementation
  - architectural intent
  - future roadmap or speculative extension

---

## Related source files

Primary mathematical source files:
- `README.md`
- `CONVENTIONS.md`

Related ecosystem references in sister repositories:
- `rqm-compiler/README.md`
- `rqm-compiler/AGENTS.md`
- `rqm-qiskit/README.md`
- `rqm-braket/README.md`
- `rqm-optimize/README.md`
- `rqm-entanglement/README.md`
- `rqm-pennylane/README.md`

This document should be kept aligned with those files, but should remain the assistant-facing cross-repo foundations reference.
