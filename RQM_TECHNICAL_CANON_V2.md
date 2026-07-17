# RQM Technical Canon v2 Alignment

`rqm-core` owns quaternion algebra, unit-quaternion/`SU(2)` conversion, Bloch
and spinor helpers, and tested mathematical conventions.

- Unit quaternions and complete `SU(2)` matrices encode the same
  single-rotation information.
- `q` and `-q` are the same `SO(3)` rotation but distinct `SU(2)` elements.
- Sign folding is unsafe where coherent control makes the phase distinction
  observable.
- Hamilton-product order matters.
- No API here establishes alternative quantum mechanics or more quantum
  information.

EXP-009 found a narrow operational result in a separate fused NumPy benchmark:
49.6% to 74.1% lower median latency at held-out batches 1,024 through 131,072
on one x86-64 machine, but 286.6% slower at batch 32. That result motivates the
planned RQM Quaternion Kernel Pack; it is not a universal or `rqm-core`
performance claim.

Evidence authority:
`RQM-Technologies-dev/rqm-experiments/docs/RQM_TECHNICAL_CANON_V2.md`.
