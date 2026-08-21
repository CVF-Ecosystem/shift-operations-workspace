# P4-A AI Gateway - Worker Return

- Tranche: `P4A-AI-GATEWAY-2026-08-20`
- Execution base: `a1aeb60f3b4f7ab10959c9b1ab79b5293dec13dd`
- Worker HEAD at start: `cfb43a2a6916ea30824c656edbdde3de88c31a0e`
  (first parent `a1aeb60...`, staged empty, worktree clean, Core/manifest/binding
  equal `7d9f360a3df11ac998972728000785799399c02b`, doctor 24 PASS + 1 bounded
  legacy-catalog warning)
- Active role: `REPAIR_WORKER` (amended from the original `IMPLEMENTATION_WORKER`
  pass; this document now reflects the original BUILD, repair round 1, and the
  ratified P4A Amendment 2 / repair round 3)
- Disposition: **`READY_FOR_REVIEW`**

## Repair pass summary (amends the original BUILD)

Independent REVIEW returned `REVIEW_CHANGES_REQUIRED` with findings
`P4A-REV-F1` through `P4A-REV-F6` in
`docs/decisions/P4A_AI_GATEWAY_COMPLETION_REVIEW_2026-08-20.md` (reviewer-owned,
read-only to this pass). `P4A-REV-F1` through `P4A-REV-F5` are repaired below,
inside the original 40 worker-owned paths only. `P4A-REV-F6` (runtime matrix:
CPython `>=3.12`/Pydantic `2.10.6`) is unresolved - no package was installed
and no compliant pre-existing environment was available; see the R1 entry
below. No provider call was made during this repair pass; the retained live
receipt from the original BUILD was not altered or rerun, per the reviewer's
explicit instruction.

## Final unstaged status paths (exact 40 worker-owned, staged zero)

```
$ git status --porcelain --untracked-files=all | wc -l
41
$ git diff --cached --name-only
(empty)
```

41 = the 40 worker-owned paths (all touched across both passes) plus the
reviewer-owned 41st path (`docs/decisions/P4A_AI_GATEWAY_COMPLETION_REVIEW_2026-08-20.md`,
untouched by this worker). Verified by direct set comparison against the
DESIGN's numbered 40-path list: zero worker-touched paths outside that list.
Nothing was staged, committed, or pushed at any point in either pass.

## Requirement-by-requirement evidence (R1-R15)

- **R1** - `ai_gateway` imports cleanly; strict Pydantic 2.10.6 models;
  `packages/ai-gateway/pyproject.toml` declares `pydantic==2.10.6` only, no
  app/ledger/provider-SDK/network-client/hidden-Core dependency. Verified by
  `tests/unit/test_p4a_gateway_dependency_boundaries.py` (AST-scans every
  module's imports against a forbidden-root list; asserts no `socket` import
  and no network-capable `urllib` submodule - `urllib.parse`, used by
  `context.py` for endpoint-origin canonicalization added in this repair
  pass, is pure structural parsing with no I/O and is explicitly distinguished
  from `urllib.request`/`urllib.error`). **P4A-REV-F6, unresolved by this
  repair pass**: the only usable interpreter in this environment remains
  CPython 3.11.9 with pydantic 2.10.3 (not the declared `>=3.12`/`2.10.6`
  floor). CPython 3.13.12 exists on the machine but has no dependencies
  installed; installing packages is unauthorized both by the original Work
  Order and by this repair's stop boundary. All 179 focused tests and the
  full suite pass on 3.11.9/2.10.3; this repair pass made no attempt to
  resolve F6, per its "finish code repairs without installing anything"
  instruction.
- **R2** - All contracts in `models.py` use `StrictModel`
  (`extra="forbid", strict=True, frozen=True`); `ProviderResult.usage` uses
  `Field(default_factory=dict)`, not a mutable default (proven distinct-object
  by `TestStrictness::test_provider_result_usage_default_is_not_shared`).
- **R3** - `AIGateway.execute` is the sole dispatch point.
  `test_gateway_invokes_the_real_cvf_runtime_functions` monkeypatches
  `service.assert_placement_allowed`/`assert_within_budget`/`assert_not_terminated`
  and asserts call order `placement -> budget -> termination -> dispatch`.
  `test_gate_functions_are_the_cvf_runtime_originals` asserts the imported
  names are the *same objects* (`is`, not `==`) as `cvf_runtime`'s, proving
  this is a real call site and not a reimplementation.
- **R4** - `TestZeroAttemptRefusals` parametrizes NO_AI, RULES_ONLY, no
  evidence, malformed/wrong-classification context, unregistered
  provider/model, unavailable budget and active kill switch; every case
  asserts `provider.calls == 0`, `gateway.physical_attempts == 0`,
  `receipt.provider_attempts == 0`.
- **R5** - `context.py::assert_context_admissible`: PUBLIC external requires
  `redaction_applied`; INTERNAL external requires `minimization_proven` (the
  exact P4-A1 `NOT_PROVEN` handoff shape is refused, not mutated or
  relabelled - `test_internal_without_minimization_refused`); CONFIDENTIAL/
  RESTRICTED are refused for the external placement outright.
- **R6** - `UsageLedger` reserve/commit/release under `threading.Lock()`;
  `TestConcurrency::test_concurrent_reservations_cannot_over_reserve` runs 40
  competing threads against a cap sized for exactly 10 and asserts exactly 10
  granted / 30 refused with zero over-reservation. Double
  commit/release/commit-after-release all raise `UsageLedgerError`. **P4A-REV-F2
  repaired**: (a) unit conversion - `cvf_runtime.budget` reads USD floats but
  `BudgetFacts`/the ledger carry integer USD-millis; conversion now happens
  only at the two adapter boundaries (`context.py::cost_policy_of` for the
  policy dict, `service.py`'s `BudgetState` construction for `spent_*`), never
  inside ledger arithmetic. (b) cumulative accounting - `UsageLedger.reserve`
  now projects caller-supplied prior spend PLUS this ledger's own
  already-committed cost PLUS its outstanding reservations PLUS the new
  estimate; the prior version omitted the ledger's own committed total, so
  sequential requests against a static caller-supplied snapshot could each
  pass independently. Reviewer's exact probe reproduced and fixed
  (`test_sequential_commits_are_counted_against_the_cap`: 5-millis cap, three
  sequential 3-millis requests - only the first is now admitted, versus all
  three admitting and committing 9 before the repair). 8 new tests added
  (`tests/unit/test_p4a_gateway_usage.py`): sequential-commit, outstanding-
  reservation-before-commit, exact-boundary (ledger's own `>` semantics vs.
  `cvf_runtime.budget`'s separate `>=` post-check, both independently
  verified), release-frees-capacity, caller-plus-ledger spend, monthly-cap,
  and two unit-conversion-helper tests.
- **R7** - `test_timeout_records_attempt_and_attempts_cancel` uses a
  30-second-delay fake provider against a 1-second gateway timeout to force a
  genuine `asyncio.wait_for` timeout (not a same-result false pass); asserts
  one attempt, `cancel_request` invoked, reservation released, no retry.
- **R8** - `self._physical_attempts` increments immediately before
  `provider.generate_structured_output`; capped at 1 by
  `GatewayReceipt._bounded_facts` validator (`provider_attempts: 0..1`
  Pydantic field constraint plus a model-level cross-check).
- **R9** - `validation.py` is a dependency-free JSON-Schema subset (no
  `jsonschema` runtime dependency, keeping R1 pure); invalid output raises
  `OutputSchemaError` and is never accepted -
  `test_invalid_output_keeps_one_attempt_and_releases`. **P4A-REV-F1
  repaired**: `pattern` and `oneOf` are now genuinely enforced (previously
  silently ignored, so a caller-declared constraint widened acceptance
  instead of narrowing it), and every schema/subschema is recursively
  checked for unsupported keywords *before* any value is matched, so an
  unrecognized constraint at any nesting level fails closed rather than
  being silently skipped. 24 new adversarial tests added
  (`tests/unit/test_p4a_gateway_validation.py`): matching/non-matching/
  invalid-regex `pattern`; zero/one/multiple-match `oneOf` (exact JSON
  Schema semantics, not any-of); malformed schema shapes (`properties`/
  `items`/`oneOf` not the expected type); unsupported keywords nested inside
  properties, items, and oneOf branches.
- **R10** - `GatewayReceipt` fields are exactly digests/safe
  identifiers/gate outcomes/timestamps; `test_receipt_contains_no_context_or_output_body`
  asserts a planted secret-shaped string and the raw context body are both
  absent from `receipt.model_dump_json()`. **P4A-REV-F3 repaired (receipt
  binding)**: `context_digest` is now recomputed from the actual dispatched
  `request.context` and compared against the caller's declared value
  (`context.py::assert_context_digest_matches`, called as part of gate 3, the
  earliest point after AI-mode admission) - a caller can no longer declare a
  clean digest while dispatching different real content.
  `endpoint_origin` is canonicalized to a bare `scheme://host[:port]` string
  inside `AIGateway.__init__` itself (`canonicalize_endpoint_origin`), not
  trusted from the caller; userinfo/credentials in the input are rejected
  outright rather than silently stripped. Reviewer's exact probe reproduced
  and fixed: a context-digest mismatch, and an origin carrying userinfo, path,
  query and a secret-shaped value, are both now refused before reaching a
  receipt. 10 new tests added (`tests/unit/test_p4a_gateway_context.py`):
  matching/mismatched/empty-vs-nonempty digest binding; bare-origin
  passthrough; path/query/fragment stripping; userinfo-bearing origin
  rejection; non-http scheme rejection; empty-origin passthrough (for
  pre-dispatch refusal receipts with no endpoint yet); port preservation.
- **R11** - `ProviderRegistry.register`/`resolve` are explicit; unregistered
  provider/model fails closed (`test_unregistered_model_fails_closed`);
  swapping an implementation is a registry operation only
  (`test_replacing_provider_does_not_require_core_change`). The live runner's
  `_LiveDashScopeProvider`/evidence adapter does not change P4-B from open.
  **P4A-REV-F3 repaired (identity binding)**: a returned `ProviderResult`
  claiming a different `provider_id`/`model_id` than the registered/dispatched
  request is now rejected (`context.py::assert_provider_identity_matches`,
  checked in `service.py::_dispatch` immediately after a result is returned,
  before schema validation) - a receipt can no longer record false
  provenance. 3 new tests added covering matching identity, mismatched
  provider id, and mismatched model id.
- **R12** - Every fake-provider test module's docstring states "NOT
  GOVERNANCE PROOF"; the live run (R13) is cited as the governance proof.
- **R13** - See "Live evidence" below.
- **R14** - `docs/implementation/EXECUTION_ROADMAP.md` P3-B and P4-A entries,
  `IMPLEMENTATION_STATUS.json` `p4a_ai_gateway` block, `docs/cvf/CVF_CONTROL_MAPPING.md`
  data_scope/cost/termination rows, and `docs/cvf/PROVIDER_GOVERNANCE.md` all
  state `BUILD_COMPLETE_PENDING_REVIEW` / "real library caller, no application
  caller" - never `CLOSED_BOUNDED`, never Phase 3 `6/6`. P4-B, P4-A2, app
  callers, durability and deployment are stated as remaining open in every
  touched surface; this repair pass changed no truth-surface wording, only
  code, tests, catalog metrics, and the Project Knowledge pin below.
- **R15** - See file-count section above and command log below. Catalog was
  regenerated twice during this repair pass (`generate_catalog.py --write`)
  as F1-F3's code additions changed `packages/ai-gateway` LOC; each
  regeneration's `MODULE_REGISTRY.json` hash change was propagated to its
  `knowledge/manifest.json` source pin in the same pass, so the two stay
  consistent at final HEAD.

## Commands and exit codes (repair pass, final HEAD)

```
$ python -m pytest -q tests/unit/test_p4a_gateway_models.py tests/unit/test_p4a_gateway_registry.py tests/unit/test_p4a_gateway_usage.py tests/unit/test_p4a_gateway_context.py tests/unit/test_p4a_gateway_validation.py tests/unit/test_p4a_gateway_receipts.py tests/unit/test_p4a_gateway_dependency_boundaries.py tests/contract/test_p4a_ai_gateway_schema.py tests/integration/test_p4a_gateway_live_evidence_support.py
179 passed in 2.77s
exit code: 0

$ python -m pytest -q
2022 passed, 128 skipped, 1 failed in ~273s
exit code: 1 (one pre-existing, base-identical failure; see below)

$ python scripts/generate_catalog.py --check
CATALOG VERIFY: PASS
exit code: 0

$ python scripts/check_session_state.py
SESSION STATE: PASS
exit code: 0

$ python scripts/check_project_knowledge.py
PROJECT KNOWLEDGE: PASS
exit code: 0

$ python scripts/check_file_size.py
FILE SIZE GUARD: PASS
exit code: 0

$ python scripts/testing/validate_repository.py
repository validation passed (catalog + session state + file-size checks)
exit code: 0

$ powershell -ExecutionPolicy Bypass -File "..\.Controlled-Vibe-Framework-CVF\scripts\check_cvf_workspace_agent_enforcement.ps1" -ProjectPath "."
RESULT: PASS WITH NOTE (24 passed, 1 warning - bounded legacy-catalog, pre-existing)
exit code: 0

$ git diff --check
(no output; only routine core.autocrlf line-ending warnings)
exit code: 0

$ git diff --cached --name-only
(empty)

$ git status --porcelain --untracked-files=all | wc -l
41 (40 worker-owned + 1 reviewer-owned completion review, untouched by this worker)
```

No provider/network/product-API call was made by this repair pass. No
package was installed. No new path was created outside the original 40.

## Pre-existing failure (verified NOT caused by this BUILD or this repair)

One test identity fails both at the execution base `a1aeb60` (confirmed via
`git stash` + rerun, three times across the original BUILD and this repair
pass) and at final worker HEAD:

- `tests/unit/test_project_knowledge_pack.py::test_repository_pack_passes_with_exact_eligible_set` -
  hardcodes `today=date(2026, 8, 10)`. This is a fixed historical clock
  inside a test file outside the 40-path ceiling; no file this Work Order or
  this repair authorizes touching can change it. Per P4A-REV-F5's explicit
  instruction, this failure is reported, not silently edited or relabeled.

**F5 resolved the rest of the Project Knowledge surface.** Before this repair,
`python scripts/check_project_knowledge.py` failed with
`KPK_CONTINUITY_CHANGED:GOVERNANCE_BOUNDARIES.md` and
`KPK_ELIGIBILITY_MISMATCH:GOVERNANCE_BOUNDARIES.md`, and
`tests/integration/test_project_knowledge_ingest_rehearsal.py` had 1 failure
and 8 errors, because the original BUILD edited
`docs/cvf/PROVIDER_GOVERNANCE.md` - a source pin of the `GOVERNANCE_BOUNDARIES.md`
Project Knowledge entry - without refreshing that entry's pin (only the
Project Context entry's pins were refreshed). Root cause confirmed by
recomputing SHA-256 for all seven of that entry's source pins: only
`docs/cvf/PROVIDER_GOVERNANCE.md` differed from its recorded pin. Repair:
updated that one pin and the entry's `reviewedAt` date (and the top-level
manifest date, already current) in `knowledge/manifest.json`.
`check_project_knowledge.py` now returns `PASS`, and the ingest rehearsal
suite now passes in full (85 passed, 0 failed, 0 errors).

`tests/integration/test_catalog_drift_detection.py::test_check_passes_on_unmodified_repository`
failed transiently twice during this session (once during the original BUILD,
once again during this repair pass, both times because F1-F3's code additions
changed `packages/ai-gateway` LOC without a catalog regeneration) and was
resolved both times by rerunning `generate_catalog.py --write`; it passes at
final worker HEAD and is not a residual failure.

## Live evidence

- Selected model: `qwen3.7-max-2026-05-17` (from
  `packages/ai-providers/alibaba/model-quota-catalog.json` via
  `select_model.py`, unmodified).
- All 6 mandated refusal cases (`NO_AI`, `NO_EVIDENCE`,
  `P4A1_INTERNAL_WITHOUT_MINIMIZATION`, `RESTRICTED_EXTERNAL_PLACEMENT`,
  `BUDGET_EXCEEDED`, `KILL_SWITCH_ACTIVE`) ran first and each produced
  `provider_attempts=0`, `adapter_calls=0`, `gateway_attempts=0`.
- Exactly one physical HTTPS POST followed, to
  `https://ws-remplsp27g5oicq1.ap-southeast-1.maas.aliyuncs.com` (safe origin
  only - scheme+host, no path/query/credential).
- HTTP status: `200`. `provider_attempts: 1`. Structured output
  `{"status": "ok", "checked": 1}` passed the exact caller schema. Usage
  committed (`actual_tokens: 278`). No retry was attempted or needed.
- Receipt: `docs/decisions/P4A_AI_GATEWAY_LIVE_EVIDENCE_RECEIPT.md`. **P4A-REV-F4
  correction**: the original hash recorded here
  (`8dd2c54731225c6d7498d2baeb6ba6c498394665c9a6c0fcc53f6695181210b7`) was
  computed at write time by `write_receipt()`, before this working tree's Git
  line-ending normalization (`core.autocrlf`) rewrote the checked-out file's
  bare `\n` to `\r\n` on the next Git operation that touched it. The retained
  file itself was NOT altered or rerun by this repair - only this recorded
  reference is corrected to match the file's current, canonicalization-stable
  bytes: SHA-256 `7a2b6e8a468e625d1cd65d515c3c857d9638183cabce2f3c42812739817396b7`
  (CRLF line terminators, as Git now stores and checks out this path). Any
  future recomputation on a fresh checkout with the same `core.autocrlf`
  setting will reproduce this corrected hash; recomputing on a checkout that
  preserves bare LF will reproduce the original one. Both values verifiably
  hash the same content, differing only in line-ending representation - this
  is a continuity/tooling artifact, not a change to the retained evidence.
- Explicit secret-scan result: `NONE` (script-internal `scan_for_secrets`) and
  independently reverified by this worker with a manual `grep` of the literal
  `ALIBABA_API_KEY` value against the receipt file (0 matches) and a scan for
  `Bearer `/`sk-`/`api_key`/`Authorization:` markers (only the safe field name
  `"credential_env_var": "ALIBABA_API_KEY"` present, which is explicitly
  permitted - env-var *name*, never the value).

## Findings, deviations, repairs - original BUILD pass

1. **File-size guard breach during BUILD, self-repaired within the same 40
   paths.** `service.py` (534 lines), `run_p4a_gateway_live_evidence.py` (405
   lines) and `test_p4a_gateway_receipts.py` (308 lines) each exceeded the
   300-line `.py` hard limit, which forbids the exception registry entirely.
   Repair: relocated `GateRecorder`/`ReceiptBuilder`/policy-adapter functions
   from `service.py` into `errors.py` (both already-authorized paths; no new
   file); relocated request-builder functions and `run_refusals` from the
   runner into `_p4a_gateway_live_evidence_support.py` (also already
   authorized); compacted the receipts test's parametrize table. Final sizes:
   `service.py` 299, `errors.py` 297, `run_p4a_gateway_live_evidence.py` 288,
   `_p4a_gateway_live_evidence_support.py` 297,
   `test_p4a_gateway_receipts.py` 295 - all under 300. No logic, assertion, or
   test coverage was dropped; `run_refusals` gained an injected
   `provider_factory` parameter so the support module does not need to define
   provider classes itself, and `tests/integration/test_p4a_gateway_live_evidence_support.py`
   was updated to call the relocated functions directly instead of importing
   them from the runner (a local `_GuardProvider` fake, explicitly marked "NOT
   GOVERNANCE PROOF", replaces the runner's `_RefusalGuardProvider` for that
   one test).
2. **`docs/implementation/EXECUTION_ROADMAP.md` also breached the 600-line
   `.md` hard limit** after the R14 bounded-truth edits (610 lines). `.md`
   files may in principle use the exception registry, but the baseline is
   explicitly "not a general exception mechanism" per
   `docs/reference/FILE_SIZE_GUARD.md`; repaired by compacting the new P3-B/
   P4-A entries and two stale historical paragraphs (one still describing the
   already-superseded P4-A1 state) without dropping any commit hash, evidence
   figure, or claim-boundary statement. Final: 600 lines exactly.
3. **`packages/ai-gateway/contracts/provider_interface.py` previously declared
   a different `AIProvider` method surface** (`classify()`, `extract_entities()`,
   `summarize()`, `estimate_cost()`, `report_usage()` alongside
   `generate_structured_output()`/`health_check()`/`cancel_request()`) and a
   `ProviderResult.usage: dict = {}` mutable default. SPEC/DESIGN specify only
   the three-method protocol and forbid mutable defaults; the file is now a
   thin re-export of `ai_gateway.provider.AIProvider` and
   `ai_gateway.models.ProviderRequest`/`ProviderResult`, which are the single
   canonical strict definitions. `docs/cvf/PROVIDER_GOVERNANCE.md`'s contract
   listing was corrected to match.
4. Repair round count for the file-size findings: 1 round each, both with an
   independent root cause (a hard numeric gate, not a subjective judgment
   call) - no `REVIEW_COST_ESCALATION_REQUIRED` condition was reached.

## Findings, deviations, repairs - this repair pass (P4A-REV-F1..F5)

1. **File-size guard re-breached during this repair pass, self-repaired again
   within the same 40 paths.** F1-F3's new code pushed `service.py` to 334
   lines and `errors.py` to 308/309 lines mid-repair. Repair: relocated
   `_ProfileView` (renamed `CvfProfileView`, since it moved out of
   `service.py`) and the four `cvf_runtime` policy-adapter functions from
   `errors.py`/`service.py` into `context.py` (already-authorized, had the
   most headroom); relocated the new `ContextDigestMismatchError`/
   `ProviderIdentityMismatchError`/`EndpointOriginError` classes into
   `errors.py`'s existing error-class block; deduplicated a `_now()` helper
   `service.py` had redefined when `errors.py` already exported one; trimmed
   docstrings without dropping content. Final: `service.py` 299,
   `context.py` 203, `errors.py` 285 - all under 300.
2. **Self-caught test-design defect in this repair pass's own first draft,
   corrected before being counted as passing.** An initial adversarial test
   for the ledger boundary case assumed `>=`-at-cap should refuse, but the
   ledger's own `reserve()` correctly uses `>` ("would exceed"), while
   `cvf_runtime.budget.assert_within_budget`'s separate post-reservation
   check uses `>=` - two independently correct checks at different stages,
   not a single inconsistent one. The test was rewritten to assert the
   ledger's actual (correct) `>` semantics and to note that the existing
   `TestFallback::test_budget_exceeded_falls_back_with_zero_calls` test
   (already part of the original 142, still passing) already proves the
   `>=` boundary is caught end-to-end via the real `cvf_runtime` gate one
   step later - so no separate end-to-end boundary test was needed.
3. **`urllib.parse` import flagged by a pre-existing R1 dependency test.**
   `context.py`'s new `canonicalize_endpoint_origin` (F3) needs URL
   structure parsing; the test's forbidden-import check treated any
   `urllib.*` import as network-capable. Repair (in-ceiling test file):
   distinguished `urllib.parse` (pure parsing, no I/O) from
   `urllib.request`/`urllib.error` (network-capable) by checking fully
   qualified import names instead of just the top-level `urllib` root; the
   network-capable subset remains forbidden.
4. Repair round count for findings 1-3 above: 1 round each, each with an
   independent root cause discovered while implementing F1-F3 - no
   `REVIEW_COST_ESCALATION_REQUIRED` condition was reached.

No other deviation from SPEC/DESIGN/Work Order/Completion Review occurred in
either pass. No provider was contacted during this repair pass; the original
BUILD's single live call was not repeated. No retry was attempted at any
point. No path outside the 40 worker-owned paths was created, modified,
staged, or deleted; the reviewer-owned 41st path was not touched. No secret
was printed, logged, or persisted outside the one env-var-name field the
SPEC explicitly permits.

## Residual claim boundary

This BUILD+repair proves a bounded library call site: `AIGateway.execute`
invokes the real `cvf_runtime.data_scope`/`budget`/`termination` gates, in the
mandated order, before at most one provider dispatch, now with F1-F3's
adversarial hardening (schema fail-closed, correct unit/cumulative budget
accounting, receipt-to-dispatch binding) proven by 179 focused tests. It does
**not** prove: an application or API caller uses the gateway; durable usage or
audit accounting (the ledger is process-local, explicitly non-durable); a
production provider adapter (P4-B remains open - the live adapter is
evidence-only); RAG, vector, or hybrid retrieval (P4-A2 remains open);
deployment or production readiness; that the declared runtime matrix
(CPython `>=3.12`/Pydantic `2.10.6`, F6) has been exercised; or that P3-B or
Phase 3 is closed (both remain open pending independent RE-review and a
reviewer's own claim-boundary determination). Because F1-F3 materially
changed the code path the retained live receipt exercised, that receipt
proves only the pre-repair source, exactly as the Completion Review states;
final governance acceptance of the repaired code path requires a fresh
post-repair provider proof under a separately approved evidence amendment,
which this repair pass was explicitly not authorized to obtain.

## Repair round 3 (ratified P4A Amendment 2)

The operator ratified the round-3 F1/catalog/F5b changes and authorized
ratify-and-complete: update this worker return, close F4, install the
compliant runtime, and make exactly one replacement live call. No deployment,
commit, or push.

### F1 (final) — complete meta-schema validation

`validation.py` now validates the full value shape of every supported keyword
before matching: `type` (string + supported name), `properties` (object +
string keys), `required` (array of unique strings), `additionalProperties`
(boolean), `items` (schema), `enum` (non-empty array of unique members),
`oneOf` (non-empty array, recursive), `pattern` (string + compilable),
`minimum`/`maximum` (real finite number), and `minLength`/`maxLength`/
`minItems`/`maxItems` (non-negative integer). 9 new adversarial tests added to
`tests/unit/test_p4a_gateway_validation.py` (63 total): negative size bounds,
duplicate `required`/`enum` members, non-string property names, non-finite
numeric bounds. Every malformed schema raises `OutputSchemaError` before any
output can be accepted.

### F5b (ratified) — frozen-date test disposition

`tests/unit/test_project_knowledge_pack.py::test_repository_pack_passes_with_exact_eligible_set`
now calls `validate_pack(ROOT)` with the default UTC clock instead of the stale
`today=date(2026, 8, 10)`. This is the sole out-of-ceiling edit, now ratified.

### Catalog + Project Knowledge pin

`generate_catalog.py --write` regenerated `MODULE_REGISTRY.json` +
`MODULE_CATALOG.md` (24 modules, 26005 LOC). The `MODULE_REGISTRY.json`
source pin in `knowledge/manifest.json` was refreshed to
`6da02a9b9124e84676fedc42f5eb8954bb7a4b73ef37454dba8380e7b09b4522`.
`check_project_knowledge.py` PASS.

### F6 (closed) — compliant runtime

Compliant environment: CPython `3.13.12` + Pydantic `2.10.6` +
`pydantic-core 2.27.2` in a stable venv outside the repo:
`C:\Users\DELL\AppData\Local\cvf-p4a-py313-venv`. The standalone uv-managed
3.13.12 interpreter is externally managed and cannot be modified directly; the
venv is the compliant execution environment.
- Focused P4-A suite: `210 passed`.
- Full suite: `2054 passed, 128 skipped, 0 failed`.

### Replacement live proof (post-repair)

Exactly one replacement HTTPS POST under the compliant 3.13.12 runtime:
`LIVE_EVIDENCE_PASS`, HTTP `200`, physical calls `1`, accepted; 6 refusal cases
all zero-call; safe origin only; secret scan `NONE`. Receipt:
`docs/decisions/P4A_AI_GATEWAY_LIVE_EVIDENCE_RECEIPT.md`.

### F4 (closed) — replacement receipt hash

The replacement receipt supersedes the retained pre-repair receipt. Its
canonicalization-stable (universal-newline) SHA-256 is
`c177ee398667f6f649dc94b29420da1eaaa11933c6426e67401ab087679e18b9` (the value
`write_receipt()` computes); the raw on-disk bytes hash as
`ce86a861a8eba7a38fad2c8fae578ebac3bceabf06b9914c7fb85b6759e78105` (CRLF line
terminators from Windows text-mode write). The prior `7a2b6e8a...` /
`8dd2c547...` references above belong to the retained pre-repair receipt and
are superseded.

## Disposition

**`READY_FOR_REVIEW`.**

Ratified P4A Amendment 2 complete: F1/catalog/F5b accepted, F4 hash corrected,
F6 runtime installed and verified, and exactly one replacement post-repair live
proof recorded. No commit, no push, no deployment. The completion review
(`docs/decisions/P4A_AI_GATEWAY_COMPLETION_REVIEW_2026-08-20.md`) remains
reviewer-owned and was not modified by this worker.
