# Work Order Amendment 7 — P3-A Acknowledgment-Lineage and Remaining-Gate Resume

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-7-2026-08-04`
- Parent Work Order SHA-256: `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
- Consumed Amendment 6 SHA-256: `57c8322d82126b4202bbbe5bbbd6df6b3a3aae27ba5a28e1e67b8e6832fe4317`
- Amendment 6 authorization review SHA-256: `cd85418046d45acc261f42595cb1e215350b91235c763f829545896ca8548250`
- Corrected BUILD review SHA-256: `ccc6c4c25fc00000be34d443ffdb4d59c665f1436641e3f89b06b4906480b405`
- SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- BUILD diff base: `b93e403cf0ab6d659de0706c058d1cd7250e75d0`
- Amendment 6 acknowledgment checkpoint: `65b47e4a1b42d4ad41424f4c616bfb3f65790e0f`
- Amendment 6 authority checkpoint: `e4ac4594383d73a9aa581c93ca75347af4502ca6`
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Status: `AMENDMENT_CANDIDATE_PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Provider/network/remote-ingest calls: `0/0/0`

## Trigger and retained stop truth

The Amendment 6 fresh exact R2 acknowledgment was recorded and pushed at
`65b47e4a1b42d4ad41424f4c616bfb3f65790e0f`. The one Amendment 6 invocation
then stopped at the first preflight assertion: the worker hard-coded the
incorrect full checkpoint SHA
`65b47e4e36e3f42f07b615e9cddeeb969f9afae1` instead of the actual pushed
checkpoint. No later preflight assertion, probe, repair edit, test or gate ran.
The failed preflight was not retried. Zero provider/network/remote-ingest calls
occurred during the invocation.

Amendment 6 and its R2 are consumed. The exact dirty BUILD candidate is
unchanged. This amendment corrects only the acknowledgment-lineage binding;
DESIGN, SPEC, corrected BUILD-review findings F2-F6, repair scope and claim
boundary do not change.

## Exact retained binding

Using typed ordinal case-sensitive sorting and UTF-8 records
`path + NUL + lowercase_file_sha256 + LF`:

- exact BUILD path count: `28`;
- exact current manifest SHA-256:
  `c9e021d3f58bc996daac0d1ec3d21513419d465ab948555b7b62f18d62183d4e`;
- source/test path count: `10`;
- immutable source/test manifest SHA-256:
  `addb052c9bafb6cd977435268304d43396b304d65ea730db0060890447ab7352`;
- protected path count: `25`;
- protected-25 manifest SHA-256:
  `513ba54f7af8b0b44fd4143009aa87bb21faa19c82adc671c99c01fe2676dda1`;
- staged path count: `0`.

Current repair-surface hashes remain registry
`d3b848506f788efd658cf2be9ac05c2e81a60c45450c34cb0a157a68d3859f38`,
catalog `6b5ad6a2220da94457fe2a39fd2732210d2531127fd24b54840d4904ea933e92`
and knowledge manifest
`461e6b5a4f72ba9f86e71c1562455176392c30e14d838a6fcef09cf62e6bb429`.

Any preflight mismatch stops the continuation.

## Exact repair-touch ceiling — 3 paths

Only these paths may change:

1. `docs/catalog/MODULE_REGISTRY.json`
2. `docs/catalog/MODULE_CATALOG.md`
3. `knowledge/manifest.json`

The other 25 BUILD paths, including all ten source/test paths, are byte-
immutable. No new BUILD path may be created. Final diff remains exact 28.

## Ordered continuation

Run once in this exact order, stopping on the first non-zero command or
contract failure:

1. verify actual pushed authority lineage from Git, the bound artifact hashes,
   empty staged set, exact-28, immutable source/test and protected-25 digests;
   the acknowledgment checkpoint must equal
   `65b47e4a1b42d4ad41424f4c616bfb3f65790e0f`;
2. run the same seven-case dedicated public-invariant/fail-stop/disclosure
   probe once, in one PowerShell process with
   `PYTHONPATH=packages/refinery-bridge/src;tests/unit`; cover zero-quality
   ready, unbound fingerprint, invalid offsets, disposition mismatch, policy
   drift, stage unavailable and sanitized unexpected exception;
3. restore only `cvf-application-profile.status` from `partial` to
   `contract-only`, keep `refinery-bridge.status=partial`, then run
   `python scripts/generate_catalog.py --write` once;
4. update only the `docs/catalog/MODULE_REGISTRY.json` SHA-256 source pin in the
   active `project-context` entry of `knowledge/manifest.json`;
5. run `python scripts/check_project_knowledge.py` once;
6. run the focused Knowledge Pack unit/local-helper rehearsal once;
7. run catalog `--check` once;
8. run the full non-live pytest suite once;
9. run session-state, file-size, repository, JSON/YAML, forbidden import/I/O,
   secret and diff checks once;
10. verify final exact 28 paths, exact three repair touches, unchanged
    source/test and protected-25 digests and empty staged set.

The Amendment 5 focused `53 passed` evidence is retained and not rerun. The
failed Amendment 5 probe and Amendment 6 preflight are not retried or relabeled.
No standalone inventory/search command is authorized.

## Stop and claim boundary

This continuation permits zero provider, network and remote-ingest calls and no
retry. A pass yields only a dirty exact 28-path deterministic-local BUILD
candidate pending fresh independent BUILD review. It authorizes no BUILD
commit/push, self-review, FREEZE, runtime caller, persistence, `data_scope`,
retrieval/RAG, learning, production or Phase 3 completion claim.

## Required review and fresh R2

An independent reviewer must return
`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no waiver, bound to this
Amendment SHA, the actual acknowledgment checkpoint, exact 3/25/28 paths,
source/test digest, corrected probe environment, remaining gates and zero-call/
no-retry boundary. After the reviewed authority checkpoint is committed/pushed,
the operator must send:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-7-2026-08-04,
> Work Order Amendment SHA-256 `<exact_sha256>`, đúng 3 repair paths và final
> exact 28 BUILD paths, zero provider/network/remote-ingest calls.

The acknowledgment authorizes one continuation invocation only and no retry.
