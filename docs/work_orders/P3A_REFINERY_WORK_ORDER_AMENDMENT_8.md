# Work Order Amendment 8 — P3-A Exact Direct-Probe and Remaining-Gate Resume

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-8-2026-08-04`
- Parent Work Order SHA-256: `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
- Consumed Amendment 7 SHA-256: `8712b18a43a35555573bce36f3fe6afd1b91b9709036dce1f1663dddd4c5c965`
- Amendment 7 authorization review SHA-256: `4f55a537bfb356f399ab3722b71af56771091049f8b2b7e2851fac1dd4fe72fc`
- Corrected BUILD review SHA-256: `ccc6c4c25fc00000be34d443ffdb4d59c665f1436641e3f89b06b4906480b405`
- SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- BUILD diff base: `b93e403cf0ab6d659de0706c058d1cd7250e75d0`
- Amendment 7 acknowledgment checkpoint: `9742c3bede7658ab9c56724ad0ad58d23a9a5e9d`
- Amendment 7 authority checkpoint: `dda6d1d9dc176ee2d7bc051d7cf96ea2895f14bc`
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Status: `AMENDMENT_CANDIDATE_PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Provider/network/remote-ingest calls: `0/0/0`

## Trigger and retained stop truth

The Amendment 7 fresh exact R2 acknowledgment was recorded and pushed at
`9742c3bede7658ab9c56724ad0ad58d23a9a5e9d`. Its preflight passed exact
authority lineage, artifact hashes, empty staged set and the 10/25/28 binding.
The next stdin probe first collected test node ids, then stopped before running
any test case because its guessed selector could not find a node containing
`zero_quality`. The failed probe was not retried. No repair edit, test case or
later gate ran. Zero provider/network/remote-ingest calls occurred during the
invocation.

Amendment 7 and its R2 are consumed. The exact dirty BUILD candidate is
unchanged. This amendment replaces the guessed node-id selector with an exact
direct seven-case stdin probe; DESIGN, SPEC, corrected BUILD-review findings
F2-F6, repair scope and claim boundary do not change.

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

## Exact direct seven-case probe contract

The probe is one `python -` invocation in the same PowerShell process after
setting `PYTHONPATH=packages/refinery-bridge/src;tests/unit`. It imports only
the immutable Refinery source plus `_refinery_fixtures`; it does not collect or
run pytest nodes. It executes exactly these seven named cases once each:

1. `zero_quality_ready`: build a ready result, replace its quality receipt with
   an all-zero `QualityReceiptV1`, and require `RefineryResultV1.model_validate`
   to raise `ValidationError`;
2. `unbound_fingerprint`: build a ready result, replace its candidate
   fingerprint with all-zero SHA-256/SHA-512 and byte length zero, and require
   `ValidationError`;
3. `invalid_offsets`: construct a normalization `StageReceiptV1` with offset
   `(9, 2)` and require `ValidationError`;
4. `disposition_mismatch`: build the no-context result, mutate its disposition
   to `NO_CANDIDATE_DUPLICATE`, clear quarantine receipt, inject an invented
   duplicate receipt, and require `ValidationError`;
5. `policy_drift`: temporarily replace `pipeline.classify` with a function that
   downgrades a RESTRICTED input to PUBLIC; require a typed result whose
   classification receipt reason is exactly `POLICY_DRIFT`, then restore the
   original function in `finally`;
6. `stage_unavailable`: temporarily replace `pipeline.normalize_syntax` with a
   function raising `StageUnavailableError`; require reason
   `STAGE_UNAVAILABLE`, the next receipt `NOT_RUN`, and fallback disposition,
   then restore in `finally`;
7. `sanitized_unexpected_exception`: temporarily replace
   `pipeline.conflict_reason` with a function raising
   `RuntimeError("raw-secret")`; attach an in-memory logging handler, require
   reason `STAGE_INVARIANT_ERROR`, require `raw-secret` absent from serialized
   result and captured logs, then restore the function and remove the handler
   in `finally`.

Each expected `ValidationError` must use an explicit helper that fails if no
exception is raised. The script maintains a counter/list and fails unless the
seven labels above complete once in the stated order. It prints only the seven
safe labels and `AMENDMENT_8_SEVEN_CASE_PROBE_PASS`; it must not print raw
exceptions, payloads or serialized results.

## Ordered continuation

Run once in this exact order, stopping on the first non-zero command or
contract failure:

1. verify actual pushed authority lineage from Git, bound artifact hashes,
   empty staged set, exact-28, immutable source/test and protected-25 digests;
2. run the exact direct seven-case probe above once;
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
failed Amendment 5 probe, Amendment 6 preflight and Amendment 7 selector probe
are not retried or relabeled. No standalone inventory/search or collection
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
Amendment SHA, the actual acknowledgment checkpoint, exact 3/25/28 paths,
source/test digest, exact direct probe contract, remaining gates and zero-call/
no-retry boundary. After the reviewed authority checkpoint is committed/pushed,
the operator must send:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-8-2026-08-04,
> Work Order Amendment SHA-256 `<exact_sha256>`, đúng 3 repair paths và final
> exact 28 BUILD paths, zero provider/network/remote-ingest calls.

The acknowledgment authorizes one continuation invocation only and no retry.
