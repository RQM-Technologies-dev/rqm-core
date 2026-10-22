# 0.2.3 maintenance qualification

Base: v0.2.2 (`6d1a06dfa7d40847df3d0fc60f635c78365abec8`).
Only scientific change: the reviewed Quaternion.to_axis_angle correction from
PR #22 (`037a9b129e1e826452757e9d034aefe89482cb57`) and its 33 regression cases.
No operator/projector additions or exports from 0.3.0 are included.
The default near-identity tolerance convention remains unchanged. With atol=0,
scaled direction normalization preserves unit axes even for subnormal vectors;
angles near 2π may round to that endpoint at floating-point resolution.

## Maintenance release mechanism

Use a PR against maintenance/0.2, based on v0.2.2. CI explicitly includes this
branch for PR and post-merge qualification; workflow permissions are unchanged.
The release-please workflow runs on main only. Do not merge this maintenance
version into main or dispatch main release-please to publish it.
After independent review, all checks, and specific publication authorization,
create v0.2.3 at the reviewed maintenance merge SHA and publish its GitHub release
with latest=false (0.3.0 remains the latest feature release). The existing
release-published Publish to PyPI workflow checks out that tag, runs the suite,
builds and checks distributions, verifies the tag/version match, attests them,
and publishes through the existing protected pypi environment. No permissions,
credentials, or trusted publisher settings need to change. Check for an existing
tag, release, and PyPI version before attempting publication or any retry.

## API adoption gates

A local candidate is not a verified public wheel. Core source tests must run in a
real Git checkout so Canon publisher revision tests exercise actual Git metadata.
After publication, verify wheel hash, attestation, source equality and metadata;
resolve the unchanged companion constraints without overrides. Qualify the full
API suite on Linux with required SDK dependencies and updated axis expectations.
Retain exact source/provenance checks: local overlays cannot establish PyPI
provenance. Deploy connector support for the exact old/new toolchain tuples before
API adoption, then verify mathematical calls across the supported hosts. Until
those gates pass, production stays on 0.2.2.
