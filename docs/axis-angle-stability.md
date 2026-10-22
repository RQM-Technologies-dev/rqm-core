# Axis-angle stability and release compatibility

`Quaternion.to_axis_angle` uses the normalized quaternion's vector norm and `2 * atan2(vector_norm, w)`. The axis divides by that same vector norm. This fixes loss of tiny angles and non-unit axes from extracting `acos(w)` then recomputing its sine. For example, RY(1e-7) now returns angle1e-7 and axis(0,1,0), rather than angle≈9.8843121e-8 and axis.y≈1.01170419.

The method preserves signed S3 semantics. It does not canonicalize q and -q. Angles range over [0,2π], including exact negative identity; the former half-open docstring was inaccurate. Below the existing vector-norm tolerance, the conventional x-axis remains. Small angles may now be retained where acos rounded them to zero. Use atol=0 to retain any nonzero vector direction. Floating-point angles arbitrarily close to2π can still round to2π; exact reconstruction below that spacing is not promised. General Quaternion.normalize overflow/underflow behavior is outside this change.

Independent tests construct inputs and reconstruct signed quaternion components with sine/cosine, check axis unit norm, cardinal/arbitrary directions, scale normalization, antipodes, exact endpoints, tolerance boundaries, and a vector whose squared norm underflows. Existing full core tests remain applicable. No API mathematics is added.

## Release gate

This PR does not change the package version, publish a wheel, merge the existing release PR, or update a consumer lockfile. The open release0.3.0 PR is separate. Before publishing or adopting a release, review that release's complete contents and consumer compatibility.

In rqm-api, the visual adapter already delegates this calculation to core. Its released0.2.2 regression deliberately records the old non-unit-axis value at RY1e-7. A future reviewed dependency update must replace that known-limitation expectation with corrected unit-axis/angle assertions, update provenance/lock hashes, and rerun signed-state and complete API qualification against the actual published artifact. Source-overlay testing is diagnostic, not released-artifact qualification. The UI's documented near-zero-to-identity recovery remains separate and unchanged.

October22 local compatibility diagnostic: overriding imports with this source tree (without installing or changing versions) ran all38 API visual tests:37 passed; only the intentional released0.2.2 bug-value regression failed, because the angle is now1e-7. This is the expected consumer test update identified above, not a claim that current API release qualification passed against a new wheel.
