# P4-A3 Application Memory — Worker Return

- Tranche: `P4A3-APPLICATION-MEMORY-2026-08-21`
- Role: `IMPLEMENTATION_WORKER` -> `REPAIR_WORKER` (rounds 1 and 2)
- Execution base / HEAD: `422661f48d2c36f8a210f1fc517c6209f4269a0d`
- Risk: `R2`
- Status: `READY_FOR_REREVIEW_ROUND_2`
- Provider / network / install / database / commit / push / deployment: `0/0/0/0/0/0/0`

## What was built (round 0) and repaired (round 1)

SPEC R1-R12 implemented within the exact 50-path ceiling:

- Pure package `packages/application-memory` (11 files): strict frozen models
  with closed enums (R1), UUID ids / lowercase SHA-256 digests / UTC timestamps
  / bounded NFC content (R2), SESSION 8h / WORKING 24h TTL policy with
  `now >= expires_at` (R3), closed purpose/classification with RESTRICTED
  fail-closed (R4), authenticated owner/shift/scope + positive source
  revalidation bound to type/id/version/content/provenance digests (R5),
  append-only deep-copy-isolated store with zero-mutation refusals (R6),
  atomic correction/tombstone lineage with race fail-closed (R7), fixed read
  order + 1..50 limit + sanitized omission (R8), self-recomputed sanitized
  receipts (R9), no workspace/provider/HTTP/env/db/Core import (R10).
- One no-route application composition
  `workspace_api.application.application_memory.build_application_memory`.
- Evidence mechanics only: `scripts/_p4a3_application_memory_live_evidence_support.py`
  and `scripts/run_p4a3_application_memory_live_evidence.py`.

## Repair round 1 (P4A3-REV-F1..F4)

All four findings resolved in one consolidated pass, within the same 50-path
union; no path 51, no provider/network/install/database/commit/push/deployment.

- **P4A3-REV-F1 (cross-shift source binding):** the application revalidator is
  now bound to the verified target shift; `_record_source_facts` independently
  requires every shift-owned operational source's `shift_id` to equal the bound
  `shift_id` (mismatch/unbound -> `None` -> `SOURCE_REVALIDATION_FAILED`).
  `tests/integration/test_p4a3_memory_application_composition.py` adds
  same-shift positive and cross-shift negative cases.
- **P4A3-REV-F2 (reconstruct untrusted inputs/results):**
  `ApplicationMemory._coerce_request` and `_coerce_revalidation` reconstruct
  `AdmissionRequestV1`/`SourceRevalidationV1` through normal Pydantic
  validation at their trust boundaries; a `model_construct` bypass, malformed
  nested source, naive timestamp, wrong result type, or a raising callback all
  fail closed as `REQUEST_INVALID`/`SOURCE_REVALIDATION_FAILED` with zero
  mutation and no raw-exception leak. `tests/unit/test_p4a3_memory_service.py`
  adds the adversarial probes.
- **P4A3-REV-F3 (store ingress/output isolation):** the store reconstructs
  every entry through normal validation before admit/correct (rejecting bad
  digest, invalid UTC/expiry, malformed nested source and forged lineage), and
  `get()`/`snapshot()` return independently deep-copied values so no returned
  alias mutates internal state. `MemoryEntryV1` now enforces
  `expires_at_utc >= created_at_utc`. `tests/unit/test_p4a3_memory_store.py`
  adds forged-entry and `object.__setattr__` isolation probes.
- **P4A3-REV-F4 (closed receipt grammar):** the receipt model enforces the
  exact positive mapping `ADMIT->ADMITTED / READ->READ_COMPLETE /
  CORRECT->CORRECTED / DELETE->DELETED`, required and forbidden/surplus fields
  per outcome, `predecessor_entry_id == tombstoned_entry_id` for correction,
  and zero-mutation/no-stale-positive-payload for negative receipts. The JSON
  contract adds `allOf` `if/then` operation->final_outcome constraints.
  `tests/unit/test_p4a3_memory_receipts.py` adds the mismatched/surplus/
  missing-field adversarial tests.

## Repair round 2 (P4A3-REV-F3a / P4A3-REV-F4a)

Resolved both residual findings in one pass; F1/F2 accepted unchanged.

- **P4A3-REV-F3a (entry TTL invariant):** `MemoryEntryV1` now requires
  `expires_at_utc > created_at_utc` and enforces the layer ceiling in the entry
  invariant itself (`SESSION <= 8h`, `WORKING <= 24h`). The authoritative TTL
  constants moved to `models.py` (`SESSION_MAX_TTL_SECONDS`,
  `WORKING_MAX_TTL_SECONDS`, `LAYER_MAX_TTL_SECONDS`) so the invariant can
  enforce them without a models<->policy cycle; `policy.py` re-imports them.
  Store reconstruction therefore rejects forged entries outside these bounds
  before mutation. `tests/unit/test_p4a3_memory_models.py` adds zero-TTL /
  SESSION 8h / 8h+1s / WORKING 24h / 24h+1s boundary tests;
  `tests/unit/test_p4a3_memory_store.py` adds a recomputed-digest 9h-SESSION
  forged-entry probe proving zero state mutation (TTL invariant, not stale digest).
- **P4A3-REV-F4a (positive receipt field grammar):** ADMIT/ADMITTED and
  CORRECT/CORRECTED now require layer/purpose/classification, entry_id/
  entry_digest_sha256, source/provenance digests and expires_at_utc (plus
  predecessor==tombstoned and `tombstone_reason=CORRECTED` for correction);
  READ/READ_COMPLETE forbids entry/source/lifecycle fields; DELETE/DELETED
  forbids entry/source/classification/expiry/read/predecessor; every positive
  write requires `omitted_count=0`; negative receipts require zero mutation and
  zero omitted count with no positive payload. The JSON contract adds `allOf`
  `if/then` required/forbidden-field constraints per positive outcome.
  `tests/unit/test_p4a3_memory_receipts.py` and
  `tests/contract/test_p4a3_application_memory_schema.py` add missing/surplus
  adversarial tests with independently recomputed hashes.

## Reviewer probes now fail closed

Round-1 and round-2 reviewer probes, all rejected/isolated:

| Probe | Result after repair |
|---|---|
| `RECEIPT_MISMATCH_ACCEPTED ADMIT READ_COMPLETE` | rejected |
| `FORGED_CALLBACK_ACCEPTED ADMITTED 1` | `SOURCE_REVALIDATION_FAILED`, zero mutation |
| `CROSS_SHIFT_SOURCE_ACCEPTED ADMITTED` | `SOURCE_REVALIDATION_FAILED`, zero mutation |
| `FORGED_ENTRY_ACCEPTED <bad digest> expiry_before_creation=True` | rejected at store ingress |
| `OUTPUT_ALIAS_MUTATES_STORE poisoned digest_matches=False` | isolated (digest preserved) |
| F3a zero TTL (`expires_at_utc == created_at_utc`) | rejected |
| F3a SESSION expiry at created + 9h | rejected |
| F4a ADMIT/ADMITTED with only entry_id+entry_digest | rejected |
| F4a READ/READ_COMPLETE carrying layer/purpose/classification/source/provenance/expiry | rejected |

## Evidence (exact commands and results)

Interpreter: `C:\Users\DELL\AppData\Local\cvf-p4a-py313-venv\Scripts\python.exe`
(Python 3.13.12, Pydantic 2.10.6).

| Check | Result |
|---|---|
| Focused P4-A3 (12 files + amended `test_operations_domain_boundary.py`) | `182 passed` |
| Affected P3-C / P4-A1 / P4-A2 regressions (22 files) | `362 passed, 1 warning` (known P4-A1 Pydantic serializer warning) |
| Full repository suite `python -m pytest -q` | `2494 passed, 128 skipped, 2 warnings` (both warnings pre-existing/bounded: short HMAC-key and P4-A1 Pydantic serializer) |
| Catalog `python scripts/generate_catalog.py --check` | `CATALOG VERIFY: PASS` (26 modules, 30032 LOC) |
| Session `python scripts/check_session_state.py` | `SESSION STATE: PASS` |
| Knowledge `python scripts/check_project_knowledge.py` | `PROJECT KNOWLEDGE: PASS` |
| File size `python scripts/check_file_size.py` | `FILE SIZE GUARD: PASS` |
| Repository `python scripts/testing/validate_repository.py` | `repository validation passed` |
| `git diff --check` | exit `0` (LF→CRLF line-ending notices only) |
| Staged set `git diff --cached --name-only` | empty |
| Changed JSON parse | PASS (7 changed JSON files all parse) |
| Secret scan (changed files) | clean; only pre-existing `Bearer` documentation text in `IMPLEMENTATION_STATUS.json`/`docs/cvf/CVF_CONTROL_MAPPING.md` (not introduced by this worker) |
| Workspace doctor | `RESULT: PASS WITH NOTE (24 passed, 1 warning(s))` — sole warning is the bounded legacy `LEGACY_PROJECT: governed downstream catalog kit not present` note |
| Exact changed set | 50 paths (same 50-path union), unexpected/missing 0/0 |

## Claim boundary

This worker return proves a bounded, provider-neutral, process-local
session/working application memory over synthetic/local evidence. It does NOT
prove episodic/semantic memory, durable persistence, a public API/UI, an
operational-corpus recall path, a production provider adapter, deployment or
production readiness. The DESIGN's "admitted memory reaches the provider at
most once" checkpoint remains a separate post-review operator authority and
was not exercised here.

## Stop

Returns `READY_FOR_REREVIEW_ROUND_2`. Independent REVIEW (path 51) and FREEZE
belong to the reviewer/closer, not this worker. No commit, push, or deployment
was made.
