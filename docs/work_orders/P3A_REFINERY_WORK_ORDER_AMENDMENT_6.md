# Work Order Amendment 6 — P3-A Probe-Environment and Remaining-Gate Resume

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-6-2026-08-03`
- Parent Work Order SHA-256: `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
- Consumed Amendment 5 SHA-256: `44c2576895356e8cb83a7df1d99c945e3a5a354a11e7655521e5288e54e07726`
- Amendment 5 authorization review SHA-256: `3b5d9a01b6c96f8f84f5010d583c0f36433bd8ffba51ff1a50a5e312e96fd7f8`
- Corrected BUILD review SHA-256: `ccc6c4c25fc00000be34d443ffdb4d59c665f1436641e3f89b06b4906480b405`
- SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- BUILD diff base: `b93e403cf0ab6d659de0706c058d1cd7250e75d0`
- Amendment 5 acknowledgment checkpoint: `0e809031f69ef497e8bfc411c5ce0ed0b37e7871`
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Status: `AMENDMENT_CANDIDATE_PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Provider/network/remote-ingest calls: `0/0/0`

## Trigger and retained stop truth

Amendment 5 preflight passed. REPAIR_WORKER completed the bounded source/test
repair step, then the focused Refinery command ran once and passed `53` tests.
The next dedicated stdin probe returned non-zero before executing any probe
case because plain `python -` did not inherit pytest's configured package path
and raised `ModuleNotFoundError: refinery_bridge`. Stop-first/no-retry was
honored. The probe was not rerun. Catalog/knowledge/full/later gates were
`NOT_RUN`; zero provider/network/remote-ingest calls occurred.

The source/test candidate is retained without adopting the failed probe as
evidence. Amendment 5 and its R2 are consumed. DESIGN, SPEC and findings F2-F6
do not change.

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

Current repair-surface hashes are registry
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

1. verify pushed authority lineage, bound hashes, empty staged set, exact-28,
   immutable source/test and protected-25 digests;
2. run the same seven-case dedicated public-invariant/fail-stop/disclosure
   probe once, but in the same PowerShell process first set
   `PYTHONPATH=packages/refinery-bridge/src;tests/unit`; the probe must cover
   zero-quality ready, unbound fingerprint, invalid offsets, disposition
   mismatch, policy drift, stage unavailable and sanitized unexpected
   exception; this is a fresh Amendment 6 command, not an Amendment 5 retry;
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

The Amendment 5 focused `53 passed` evidence is retained and not rerun. Its
failed stdin probe is not retried or relabeled. No standalone inventory/search
command is authorized.

## Stop and claim boundary

This continuation permits zero provider, network and remote-ingest calls and no
retry. A pass yields only a dirty exact 28-path deterministic-local BUILD
candidate pending fresh independent BUILD review. It authorizes no BUILD
commit/push, self-review, FREEZE, runtime caller, persistence, `data_scope`,
retrieval/RAG, learning, production or Phase 3 completion claim.

## Required review and fresh R2

An independent reviewer must return
`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no waiver, bound to this
Amendment SHA, exact 3/25/28 paths, source/test digest, corrected probe
environment, remaining gates and zero-call/no-retry boundary. After the
reviewed authority checkpoint is committed/pushed, the operator must send:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-6-2026-08-03,
> Work Order Amendment SHA-256 `<exact_sha256>`, đúng 3 repair paths và final
> exact 28 BUILD paths, zero provider/network/remote-ingest calls.

The acknowledgment authorizes one continuation invocation only and no retry.
