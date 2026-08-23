# P4-B AI Provider Foundation — Worker Return

- Tranche: `P4B-AI-PROVIDERS-2026-08-21`
- Role: `IMPLEMENTATION_WORKER` (original BUILD), then `REPAIR_WORKER`
  (repair round 1), then `REPAIR_WORKER` again (repair round 2), then
  `REPAIR_WORKER` again (repair round 3, Amendment 1), then `REPAIR_WORKER`
  again (repair round 4, Amendment 2)
- Execution base: `319c6a809ef29134a0de8c4a9923bb18669c349c` (unchanged)
- Interpreter: `C:\Users\DELL\AppData\Local\cvf-p4a-py313-venv\Scripts\python.exe`
  — Python `3.13.12`, Pydantic `2.10.6`
- Disposition: `READY_FOR_REREVIEW_ROUND_4` (superseding round 3's
  `READY_FOR_REREVIEW_ROUND_3` after independent rereview round 3 closed
  F4-R2/F6-R2 but retained sole residual `P4B-REV-F5-R3`, returning
  `REVIEW_COST_ESCALATION_REQUIRED`; the operator explicitly authorized
  Amendment 2 for one bounded repair round 4 limited to that finding)

## Repair round 1 (2026-08-22) — role transition `REVIEWER -> REPAIR_WORKER` (condensed; superseded by rounds 2-3)

The independent completion review (path 51) returned `REVIEW_FAIL` with six
findings, all resolved. Detail is condensed here since rounds 2-3 are
authoritative for current state; every source-file/test-name citation is
preserved for traceability.

- **F1 (mock exclusion not load-bearing)**: `ProviderModeService.__init__`
  (`service.py`) gained `registry: ProviderAdapterRegistry | None = None`
  defaulting to a fresh EMPTY registry (never "no check"); `_finish_
  external_ai` calls `self._registry.resolve(...)` before any gateway
  dispatch — unregistered refuses `PROVIDER_NOT_REGISTERED`, `MOCK` kind
  refuses `MOCK_PROVIDER_NOT_EVIDENCE_ELIGIBLE`, placement disagreement
  refuses `REGISTRY_PLACEMENT_MISMATCH`, all zero-call. Tests: `tests/unit/
  test_p4b_provider_registry.py::TestRegistryIsLoadBearingInService::
  test_registered_mock_kind_is_refused_zero_call_even_though_registered`,
  `test_a_mock_adapter_registered_only_in_a_different_p4a_registry_is_still_
  refused`, `test_default_registry_refuses_everything_as_unregistered`.
- **F2 (successful output discarded)**: `execute` now returns
  `ProviderModeResultV1` (`models.py`) pairing `output` with the sanitized
  receipt via `build_result()` (deep-copy isolated); validators bind output
  presence to terminal outcome and `output_digest` equality. Tests: `tests/
  unit/test_p4b_rules_only.py::TestProviderModeResultV1` (`test_rules_
  matched_requires_non_null_output`, `test_refusal_outcome_forbids_output_
  body`, `test_output_digest_mismatch_is_rejected`, `test_build_result_
  deep_copy_isolates_output`) and `TestServiceIntegration::test_output_
  digest_in_receipt_matches_returned_output`/`test_rules_only_output_is_
  isolated_from_internal_ruleset_state`.
- **F3 (identity/placement binding incomplete)**: `ProviderModeRequestV1`
  gained `provider_id`/`model_id`/`placement`/`context_digest`;
  `_identity_mismatch` compares ALL of task_type/ai_mode/output_schema/
  provider_id/model_id/placement/context_digest, unset outer fact = a
  mismatch; `ProviderMetadataV1.placement` types as P4-A's canonical
  `Placement` enum (was free-form `str`). Tests: `tests/unit/
  test_p4b_provider_service.py::TestExternalIdentityBinding::test_identity_
  binding_fact_mismatch_is_zero_call_refusal` (parametrized over all six
  facts), `test_outer_binding_facts_missing_entirely_is_zero_call_refusal`;
  `test_p4b_provider_models.py::TestProviderModeRequestV1::test_rejects_
  non_enum_placement_string`; `test_p4b_provider_registry.py::
  TestRegistration::test_rejects_arbitrary_placement_string_at_registration`.
- **F4 (public boundaries not reconstruction-safe, 4 gaps)**: (1)
  `MockProviderAdapter.__init__` forces `MockAuthorizationV1.model_validate`
  on the primitive dump, rejecting a `model_construct` bypass — test
  `test_p4b_mock_provider.py::TestAuthorizationIsStructurallyRequired::
  test_adapter_rejects_model_construct_bypassed_authorization`; (2)
  `execute`'s first step wraps `digest_of(...)` in `try/except Exception`,
  converting an unhandled `TypeError` (non-JSON `facts` value crashing
  `json.dumps`) to typed `REQUEST_INVALID` — test `test_p4b_no_ai.py::
  TestFailClosedOnUnexpectedException::test_model_construct_bypassed_non_
  json_facts_is_request_invalid_not_a_raw_typeerror`; (3) `errors.py::
  _assert_json_only` checks `math.isfinite` per float leaf — tests
  `test_p4b_provider_models.py::TestBoundedJson::test_rejects_nan`/
  `test_rejects_positive_and_negative_infinity`/`test_accepts_finite_
  float`; (4) `rules_only.py::_facts_match` requires `type(actual) is
  type(expected)` (closing `True == 1`) — test `test_p4b_rules_only.py::
  TestWinnerSelection::test_string_vs_int_fact_does_not_coerce_match`.
- **F5 (receipt/schema permit drift)**: `models.py` adds
  `VALID_RECEIPT_AI_MODES`/`canonical_receipt_ai_mode()` (unknown mode
  canonicalized to `"UNKNOWN"` before receipt build, never echoed raw);
  `ProviderModeReceiptV1` gained a closed-vocabulary validator and exact
  cross-field grammar per outcome; `provider_modes.schema.json` hand-edited
  to mirror it with `allOf`/`if`/`then`. Tests: `test_p4b_provider_
  modes_schema.py::TestReceiptAiModeVocabulary`,
  `TestPydanticAndSchemaAgreeOnDrift`, `TestAdditionalGrammarRules`,
  `TestRoundTripEveryTerminalOutcome` (all eight outcomes).
- **F6 (parked runner not runnable, refusals-only fixed; admitted branch a
  deliberate stub)**: root cause — `alibaba/select_model.py` lives at
  `packages/ai-providers/alibaba/`, not under `src/`, and neither
  live-evidence script added `packages/ai-providers` to `sys.path`. Fixed
  the path AND moved the `alibaba.select_model` import to strictly after
  the `--refusals-only` early exit (a fixed `REHEARSAL_MODEL_ID` label is
  used instead), making refusals-only genuinely credential/model-selection-
  independent. Verified by running it (4/4 zero-call cases, exit 0).
  `scripts/_p4b_ai_providers_live_evidence_support.py` gained real,
  testable admitted-path mechanics (`build_admitted_external_request()`,
  `_CountingAdmittedProvider`) for a future worker, never invoked by
  `main()` this round. Tests: `test_p4b_provider_live_evidence_support.py::
  TestAdmittedPathMechanics`.

**File-size guard repair**: moved bounded-JSON helpers from `models.py`
into leaf module `errors.py` (re-exported unchanged); condensed the
grammar validator into a `_require(condition, message)` helper; relocated
`TestRegistryIsLoadBearing[InService]`/`TestReceiptAiModeGrammar`/
`TestProviderModeResultV1` to their most-thematic files; parametrized four
mismatch tests into one, preserving every case as its own pytest id. Result:
`FILE SIZE GUARD: PASS`.

**Verification**: consolidated review of all six findings against real
source before any fix; focused P4-B suite (12 files, 199 items) **199
passed**; P4-A/A2/A3 regression **698 passed**; full suite **2686 passed,
128 skipped, 2 known warnings**; catalog/session/knowledge/file-size/
repository/diff/staged/exact-path (51/51, `comm -23` empty)/secret-scan
(only the documented synthetic `sanitize("Bearer abcdef01234567890")`
literal) gates PASS; workspace doctor `PASS WITH NOTE`; `--refusals-only`
rehearsal exit 0.

**Repair round 1 disposition (superseded)**: `READY_FOR_REREVIEW` at the
time — all six findings resolved; F6's admitted branch a deliberate,
reported stub. Independent rereview round 1 closed F2/F3 without waiver
but returned `REREVIEW_FAIL / RESIDUAL_REPAIR_REQUIRED` with four
residuals, repaired in round 2 below.

## Repair round 2 (2026-08-22) — role transition `REVIEWER -> ORCHESTRATOR -> REPAIR_WORKER`

The independent rereview at
`docs/decisions/P4B_AI_PROVIDERS_COMPLETION_REVIEW_2026-08-21.md` (path 51,
reviewer-owned, unedited by this repair — see its "Rereview round 1"
section) returned `REREVIEW_FAIL / RESIDUAL_REPAIR_REQUIRED` with four
residual findings: `P4B-REV-F1-R1`, `P4B-REV-F4-R1`, `P4B-REV-F5-R1`,
`P4B-REV-F6-R1`. Entry-state verification confirmed HEAD unchanged at
`319c6a809ef29134a0de8c4a9923bb18669c349c`, exactly 51 changed paths, staged
empty, before any edit.

### F1-R1 — HIGH — provider eligibility and kind still do not gate dispatch — RESOLVED

Round 1's gate only rejected `kind=MOCK`; the reviewer's three probes
(`EXTERNAL_GATEWAY`+`evidence_eligible=False`; `RULES_ONLY`+`True`;
`NO_AI`+`True`) each reached `EXTERNAL_ACCEPTED` with one gateway call.

Fix: `packages/ai-providers/src/ai_providers/service.py::
ProviderModeService._finish_external_ai` now refuses unless
`metadata.kind is ProviderKind.EXTERNAL_GATEWAY and metadata.
evidence_eligible is True` — both exact — reason code
`PROVIDER_NOT_EXTERNAL_GATEWAY_EVIDENCE_ELIGIBLE`, strictly subsuming the
old MOCK-only check.

Tests, `tests/unit/test_p4b_provider_registry.py::
TestRegistryIsLoadBearingInService`:
`test_wrong_kind_or_eligibility_combination_is_zero_call_refusal`
(parametrized over the three exact reviewer combinations, zero-call
refusal) and `test_exact_external_gateway_and_evidence_eligible_true_
proceeds_to_gateway` (inverse-positive: both exact reaches
`EXTERNAL_ACCEPTED`). Two pre-existing tests' expected reason code was
updated to the new, more general string (same assertion proved).

### F4-R1 — HIGH — two public reconstruction boundaries remain open — RESOLVED

1. **Registry stored an unreconstructed instance**: the reviewer's
   `ProviderMetadataV1.model_construct(kind="BOGUS", placement="mars")` was
   registered/resolved. Fix: `registry.py::ProviderAdapterRegistry.register`
   now calls `ProviderMetadataV1.model_validate(metadata.model_dump(
   mode="python"))` BEFORE reading/storing any field (same discipline round
   1 applied to `MockAuthorizationV1`), raising
   `DuplicateProviderRegistrationError` with the registry left unchanged.
   Test: `test_p4b_provider_registry.py::TestRegistration::
   test_model_construct_bypassed_metadata_is_rejected_without_mutation`.
2. **`execute` only caught digest failure**: the reviewer's
   `facts={"x": (1, 2)}` stayed "digestible" (`json.dumps` serializes a
   tuple like a list) but fell through to `AI_MODE_DISABLED` instead of
   `REQUEST_INVALID`. Fix: `service.py::execute`'s top-level guard now does
   `ProviderModeRequestV1.model_validate(request.model_dump(mode="python"))`
   — full reconstruction, not just a digest attempt — before any dispatch;
   failure returns `REQUEST_INVALID` (reason `REQUEST_NOT_REVALIDATABLE`,
   renamed from `REQUEST_NOT_DIGESTIBLE`). Test:
   `test_p4b_no_ai.py::TestFailClosedOnUnexpectedException::
   test_model_construct_bypassed_tuple_facts_is_request_invalid_not_ai_
   mode_disabled` (exact reviewer repro, asserts `REQUEST_INVALID`, never
   `AI_MODE_DISABLED`).

### F5-R1 — HIGH — receipt grammar still admits impossible facts — RESOLVED

Both the model and schema accepted all four reviewer probes:
`RULES_NO_MATCH`+`rule_id="ghost"`; `RULES_MATCHED`+`rules_evaluated=0`;
`EXTERNAL_NOT_ACCEPTED` with a gateway call but no ids;
`EXTERNAL_IDENTITY_MISMATCH`+`ai_mode=UNKNOWN`.

Fix — general rules in `errors.py::assert_receipt_grammar` (relocated from
`models.py` for file-size budget, called by `ProviderModeReceiptV1.
_counters_match_outcome`): `rule_id` present iff a rule actually matched
(`RULES_MATCHED`/`RULES_SCHEMA_INVALID`); `rules_evaluated >= 1` whenever
`rule_id` is present; `provider_id`/`model_id` present whenever
`gateway_calls >= 1` (covers `EXTERNAL_NOT_ACCEPTED` too);
`EXTERNAL_IDENTITY_MISMATCH` requires the exact `ai_mode="EXTERNAL_AI"`
(never the `UNKNOWN` sentinel). `provider_modes.schema.json` gained
matching `if/then` conditionals for each rule, and narrowed
`EXTERNAL_IDENTITY_MISMATCH`'s `ai_mode` enum to `["EXTERNAL_AI"]`.

Tests, `tests/contract/test_p4b_provider_modes_schema.py::
TestReviewerImpossibleShapesRejectedByBothLayers`: paired
`_rejected_by_pydantic`/`_rejected_by_schema` tests for all four reviewer
shapes (8 tests) plus four `_still_valid` adjacent-legitimate-shape tests
proving no overtightening. All pre-existing round-trip/drift tests still
pass unmodified.

### F6-R1 — MEDIUM — admitted evidence path remains a blocked stub — RESOLVED

The admitted branch was an unconditional `LIVE_EVIDENCE_BLOCKED` stub. Fix,
following the existing P4-A pattern
(`_p4a_gateway_live_evidence_support.py::_LiveDashScopeProvider`/
`CallBudget`) exactly: `scripts/run_p4b_ai_providers_live_evidence.py` now
defines `_CountingAdmittedProvider` (hard one-attempt `CallBudget` —
`reserve()` runs FIRST, before touching the request/body/credential, so an
exhausted budget fails closed with no other side effect; credential read
only inside `_post` at dispatch time; exactly one physical `urllib.request`
POST, no retry; sanitized `ProviderResult`) and `run_admitted_case`
(assembles the matching request/registry/gateway/provider WITHOUT invoking
them). `main()`'s admitted branch now actually dispatches through this real
mechanics instead of printing a stub, and writes a receipt plus secret
scan — but this repair never runs `main()` past `--refusals-only`.
`_p4b_ai_providers_live_evidence_support.py::run_refusals` was also fixed
to register `evidence_eligible=True` (was `False`, which the new F1-R1 gate
now refuses on its own, masking the intended `NO_GATEWAY_INJECTED` reason
for `EXTERNAL_NO_GATEWAY`) so that case again exercises its intended branch.

Tests (spies/fakes/monkeypatches only, zero I/O, zero credential
read/print), `tests/integration/test_p4b_provider_live_evidence_support.py::
TestAdmittedPathMechanics`: budget-refuses-second-reservation,
`_post`-fails-closed-with-no-credential-configured,
budget-exhausted-refuses-before-credential-read,
assembly-performs-zero-I/O, and construction-alone-touches-nothing.
`--refusals-only` re-run after the fix (below) confirms zero-call/
credential-independence, now with `EXTERNAL_NO_GATEWAY` correctly showing
`reason=NO_GATEWAY_INJECTED`.

### Round 2 file-size guard repair (incidental, within the same ceiling)

Fixes/adversarial coverage required more in-ceiling splits: the receipt
grammar rule table moved from `models.py` into `errors.py::
assert_receipt_grammar` (leaf module, no import cycle, takes the outcome's
`.value` string); the new admitted-path mechanics
(`_CountingAdmittedProvider`/`run_admitted_case`) were written directly in
`scripts/run_p4b_ai_providers_live_evidence.py` (more room there than the
support module); `TestMockDefaultDenial`/`TestProjectionsExcludeMock`
relocated from `test_p4b_provider_registry.py` to
`test_p4b_mock_provider.py`; `TestAdditionalGrammarRules` relocated from the
contract test file into `test_p4b_provider_models.py::
TestProviderModeReceiptV1`. No test assertion was deleted. Result:
`FILE SIZE GUARD: PASS`; every touched file `<= 300` lines.

### Repair round 2 verification commands, in order

1. Consolidated review of the reviewer's "Rereview round 1" section plus the
   actual current source of every touched file, before writing any fix.
2. P4-B focused tests (same 12 files as round 1's command):
   **220 passed, 1 known warning** (a Pydantic serializer warning from
   dumping a deliberately `model_construct`-bypassed instance in the F4-R1
   registry test — expected, not a defect).
3. Affected P4-A/P4-A2/P4-A3 regressions (same command as round 1):
   **698 passed** (matches round 1's baseline exactly).
4. Full repository suite (`python -m pytest -q`): **2707 passed, 128
   skipped, 3 known warnings** (skips match baseline; +21 net new tests vs.
   round 1's 2686; 3rd warning is the new F4-R1 registry test's expected
   notice).
5. `python scripts/generate_catalog.py --write` then `--check` →
   `CATALOG VERIFY: PASS` (LOC changed from the fixes/adversarial additions).
6. `python scripts/check_session_state.py` → `SESSION STATE: PASS`.
7. `python scripts/check_project_knowledge.py` → `PROJECT KNOWLEDGE: PASS`
   (after recomputing raw-bytes SHA-256 pins for
   `docs/catalog/MODULE_REGISTRY.json` and `docs/cvf/PROVIDER_GOVERNANCE.md`
   in `knowledge/manifest.json`, via `Path.read_bytes()`, never text-mode).
8. `python scripts/check_file_size.py` → `FILE SIZE GUARD: PASS`.
9. `python scripts/testing/validate_repository.py` → `repository validation
   passed (catalog + session state + file-size checks)`.
10. `check_cvf_workspace_agent_enforcement.ps1 -ProjectPath "."` →
    `RESULT: PASS WITH NOTE (24 passed, 1 warning)` — same pre-existing
    bounded legacy note as round 1.
11. `git diff --check` → exit 0 (only pre-existing CRLF-autocrlf advisory
    warnings).
12. `git diff --cached --name-only` → empty (verified before/after a
    `git add -N .` / `git reset` probe used only to build the secret-scan
    diff, never leaving anything staged).
13. `git status --porcelain --untracked-files=all` → exactly **51** paths —
    the same union as round 1, verified path-for-path against the Work
    Order's ceiling via `comm -23`/`comm -13` — zero outside, zero missing.
14. Secret scan of the full working-tree diff: hits are exactly the same
    pre-existing synthetic literal round 1 already documented
    (`sanitize("Bearer abcdef01234567890")`) plus the harmless variable read
    `api_key = os.environ[self._key_env_name]` (a variable name, not a
    credential value) in the new admitted-path mechanics. No real
    credential, endpoint query, or auth header anywhere in the diff.
15. `--refusals-only` live-evidence rehearsal, run twice (before/after the
    `run_refusals` `evidence_eligible` fix under F6-R1), authorized after
    confirming by reading the code both times that the path stays
    zero-call/credential-independent and never constructs
    `_CountingAdmittedProvider`/`run_admitted_case`. Final run: all 4
    mandated refusal cases zero-call (`NO_AI`, `RULES_NO_MATCH`,
    `EXTERNAL_TASK_TYPE_MISMATCH` → `TASK_TYPE_MISMATCH`,
    `EXTERNAL_NO_GATEWAY` → `NO_GATEWAY_INJECTED`), mock output confirmed
    evidence-ineligible, exit before any provider call. No provider/network
    call was made (confirmed by code reading before each run and by the
    printed zero-call counters after).

### Repair round 2 disposition (superseded by round 3 below)

**`READY_FOR_REREVIEW_ROUND_2`** at the time. All four residual findings
(F1-R1, F4-R1, F5-R1, F6-R1) resolved with concrete source-file and
test-name evidence above; F6-R1's admitted branch is now real, tested,
one-call mechanics wired into the runner but remained deliberately
unexecuted that round, pending separate post-review authority (reported,
not hidden). Independent rereview round 2 closed `P4B-REV-F1-R1` and the
prior `F2/F3` without waiver, but returned `REVIEW_COST_ESCALATION_REQUIRED`
with three residuals (`P4B-REV-F4-R2`, `P4B-REV-F5-R2`, `P4B-REV-F6-R2`),
repaired in round 3 immediately below after explicit operator Amendment 1
authority.

## Repair round 3 (2026-08-22) — role transition `REVIEWER -> ORCHESTRATOR -> WORK_ORDER_AUTHOR -> ORCHESTRATOR -> REPAIR_WORKER`

Independent rereview round 2 (path 51, reviewer-owned, unedited) returned
`REVIEW_COST_ESCALATION_REQUIRED` with three residuals: `P4B-REV-F4-R2`,
`P4B-REV-F5-R2`, `P4B-REV-F6-R2`. The operator explicitly authorized this
bounded round as **Amendment 1**, recorded inside the existing Work Order
(no path 52). Entry-state verified: HEAD `319c6a8...`, 51 changed paths,
staged empty, before any edit. Real current source was read in full (not
trusted from prior worker-return prose) before writing any fix.

**F4-R2 (primitive registry input escapes as raw `AttributeError`) —
RESOLVED.** Root cause, reproduced live: `ProviderAdapterRegistry.register`
(`packages/ai-providers/src/ai_providers/registry.py`) called
`metadata.model_dump(mode="python")` unconditionally, so a plain dict or
`object()` raised a raw `AttributeError` instead of the documented
`DuplicateProviderRegistrationError`. Fix: `register`'s parameter is now
typed `object`; it dumps to primitive ONLY when
`isinstance(metadata, ProviderMetadataV1)` (needed because
`model_validate` does not re-run validators for an already-same-type
instance, so a `model_construct` bypass still needs the dump-then-revalidate
step), otherwise passes the raw value straight to
`ProviderMetadataV1.model_validate` (which natively accepts dict or
instance). Only `pydantic.ValidationError` is caught and normalized; no
other exception type is expected. Registry stays unmutated on every
rejection. Tests, `tests/unit/test_p4b_provider_registry.py::
TestRegistration`: `test_untyped_public_boundary_input_rejects_without_raw_
attributeerror` (parametrized: primitive mapping, `object()`, both zero
mutation, plus positive-control re-registration) and
`test_primitive_mapping_with_valid_typed_values_registers_normally`
(a correctly-typed plain dict registers). Pre-existing F4-R1
`model_construct` test still passes unmodified.

**F5-R2 (outcome grammar is still not exact) — RESOLVED, general grammar
rule.** `ai_providers/errors.py::assert_receipt_grammar` was rewritten
around outcome-FAMILY predicates derived from the real
`ProviderModeOutcome` taxonomy and every `build_receipt(...)` site in
`service.py` — not a per-outcome `if` chain patched one probe at a time:
`is_external = outcome.startswith("EXTERNAL_")` forbids ALL rule
counters/facts on every external outcome (rules and external are mutually
exclusive code paths); `is_external and not accepted_external` forbids
`output_digest` (only an accepted call could have produced output);
`is_rules = outcome.startswith("RULES_")` REQUIRES the `ruleset_digest`
`_finish_rules_only` always computes and forbids provider/model ids and
gateway/provider calls; `rule_matched` (`RULES_MATCHED`/
`RULES_SCHEMA_INVALID`) requires `rule_id` + `rules_evaluated >= 1`,
`RULES_NO_MATCH` forbids `rule_id`, only a match carries `output_digest`;
`EXTERNAL_IDENTITY_MISMATCH`'s provider/model ids are
both-present-or-both-absent as a pair; a genuine gateway attempt
(accepted/not-accepted) requires exactly one call and both ids, an
accepted one also the output digest; zero-work refusals require zero
counters and no facts. A future outcome in an existing family
automatically inherits its rules — no per-shape branch to remember. The
same family predicates are mirrored in `provider_modes.schema.json`'s
`allOf` via `pattern: "^EXTERNAL_"`/`"^RULES_"` `if` conditionals plus an
`anyOf` pair for the mismatch identity-pair rule. Fixes to pre-existing
tests that now correctly need `ruleset_digest`:
`test_p4b_provider_modes_schema.py::test_rules_no_match_round_trips`,
`test_rules_schema_invalid_round_trips`,
`test_rules_no_match_with_rule_id_ghost_rejected_by_schema`,
`test_rules_no_match_with_empty_rule_id_still_valid`;
`test_p4b_rules_only.py::TestProviderModeResultV1::
test_refusal_outcome_forbids_output_body`. New coverage: `tests/unit/
test_p4b_no_ai.py::TestF5R2CompleteGrammarMatrix::test_shape_rejected_by_
pydantic`/`test_shape_rejected_by_schema`, each parametrized over all six
reviewer shapes (`mismatch_output_digest`, `mismatch_rule_facts`,
`accepted_rule_facts`, `not_accepted_output_digest`,
`no_match_missing_ruleset_digest`,
`schema_invalid_missing_ruleset_digest`) — 12 items, both layers agree on
every one. Positive real-emitted-shape proof: `test_p4b_provider_service.py
::TestRealExternalReceiptsSatisfyGrammar::test_real_accepted_not_accepted_
and_mismatch_receipts_carry_zero_rule_facts` — receipts from real
`ProviderModeService.execute()` calls, never hand-constructed. Pre-existing
`TestRoundTripEveryTerminalOutcome`/`TestReviewerImpossibleShapesRejected
ByBothLayers` still pass unmodified.

**F6-R2 (PASS receipt decided before evidence invariants) — RESOLVED.**
Root cause: `run_p4b_ai_providers_live_evidence.py::main()`'s admitted
branch set `disposition` from `accepted` alone and wrote the receipt before
checking secret hits or `gateway.physical_attempts`/`receipt.gateway_calls`
/`receipt.provider_attempts`. Fix: new pure `decide_admitted_disposition(*,
receipt, provider, gateway, generated_at, model_id, key_env_name,
refusals)` computes, in order, `accepted`, `counters_agree` (exact
`(provider.calls, gateway.physical_attempts, receipt.gateway_calls,
receipt.provider_attempts) == (1, 1, 1, 1)`), renders the body with a
provisional BLOCKED disposition via the new `render_receipt()` (split out
of `write_receipt`, which now only writes an already-rendered document —
never a payload) and scans that real body for secrets, and only re-renders
as PASS if `accepted AND counters_agree AND not hits`. `main()` calls this
before `write_receipt`, so the write and the exit code are gated by the
identical invariants. Not executed against a real endpoint this round.
Tests, `tests/integration/test_p4b_provider_live_evidence_support.py::
TestF6R2AdmittedDispositionInvariants`, driving the REAL admitted mechanics
(`run_admitted_case`, real `ProviderModeService`/`AIGateway`/
`_CountingAdmittedProvider`) through an injected fake HTTPS transport
(`_FakeHttpResponse` monkeypatched over `urllib.request.urlopen`) and an
obviously-synthetic fake credential: `test_genuinely_successful_case_
reaches_pass` (all invariants agree → PASS embedded in the document);
`test_counter_drift_is_forced_to_blocked_never_pass` (receipt
`model_copy`-mutated to `provider_attempts=0` against real `provider.calls
== 1` → forced BLOCKED); `test_secret_hit_is_forced_to_blocked_never_pass`
(synthetic `"Bearer sk-fake-obviously-synthetic-0000000000"` injected via
`credential_env_var` → forced BLOCKED despite full acceptance/counter
agreement). No real network I/O, no real credential read/logged, `main()`
never executed.

**File-size guard**: every touched `.py` file stayed `<= 300` lines via
in-ceiling splits — `errors.py` 287/300 (rewritten grammar is net shorter
despite covering more), `registry.py` 129/300, `run_p4b_ai_providers_live_
evidence.py` 295/300 (`render_receipt`/`write_receipt` relocated to
`scripts/_p4b_ai_providers_live_evidence_support.py`, 284/300),
`test_p4b_provider_registry.py`/`test_p4b_provider_service.py` 300/300
exactly (F4-R2/F5-R2 tests added compactly; `TestObjectIdentity` relocated
to `test_p4b_provider_dependency_boundaries.py`, 182/300, with a
self-contained fixture since cross-file test-module import does not work
under this repo's pytest config — verified empirically), F5-R2's negative
matrix in `test_p4b_no_ai.py` (190/300) rather than the thematically
obvious but budget-exhausted contract test file (288/300).

**Verification**: focused P4-B suite (12 files) **239 passed, 1 known
warning** (pre-existing F4-R1 Pydantic serializer notice); P4-A/A2/A3
regression **698 passed** (unchanged baseline); full suite `python -m
pytest -q` **2726 passed, 128 skipped, 3 known warnings**;
`generate_catalog.py --write` then `--check` → PASS; `check_session_state.py`
→ PASS; `check_project_knowledge.py` initially FAILED
(`KPK_SOURCE_PIN_DRIFT:PROJECT_CONTEXT.md` — its `docs/catalog/
MODULE_REGISTRY.json` pin went stale after catalog regeneration), fixed by
recomputing that one pin via `Path.read_bytes()` (never text-mode) in
`knowledge/manifest.json`, re-ran → PASS (`PROVIDER_GOVERNANCE.md`'s
separate pin was untouched, no recompute needed); `check_file_size.py` →
PASS; `validate_repository.py` → PASS;
`check_cvf_workspace_agent_enforcement.ps1` → `PASS WITH NOTE (24 passed, 1
warning)`, same pre-existing bounded legacy note; `git diff --check` → exit
0 (same pre-existing CRLF advisories); `git diff --cached --name-only` →
empty; `git status --porcelain --untracked-files=all` → exactly **51**
paths, verified path-for-path against the ceiling via `comm -23`/`comm
-13` — zero outside, zero missing. Secret scan of the full working-tree
diff: only the pre-existing documented synthetic
`sanitize("Bearer abcdef01234567890")` plus this round's two new,
clearly-commented synthetic literals (`"sk-fake-not-a-real-credential"`,
`"Bearer sk-fake-obviously-synthetic-0000000000"`) — no real credential,
AWS-shaped key, PEM block, or endpoint-query credential anywhere.
`--refusals-only` rehearsal (the one authorized execution, confirmed
zero-call/credential-independent by reading the code first, and confirmed
it returns before `decide_admitted_disposition` is ever reached) ran once
after all edits: all 4 mandated cases zero-call, mock output confirmed
evidence-ineligible, exit code 0.

**Disposition: `READY_FOR_REREVIEW_ROUND_3`.** All three residual findings
(F4-R2, F5-R2, F6-R2) resolved with concrete source-file/test-name evidence
above, including F5-R2's general outcome-family grammar rule explained in
full. This document does not self-review, self-approve, edit path 51,
create path 52, call any provider, use a real credential, install
anything, commit, push, or declare FREEZE. HEAD remains
`319c6a809ef29134a0de8c4a9923bb18669c349c`; staged is empty; changed-set is
exactly 51 paths. Independent REVIEWER action is required next.

---

## Repair round 4 (2026-08-22) — role transition `ORCHESTRATOR -> REPAIR_WORKER`, Amendment 2

Independent rereview round 3 closed `P4B-REV-F4-R2`/`F6-R2` without waiver
and retained sole residual `P4B-REV-F5-R3`: both the general Pydantic
receipt grammar and the published Draft 2020-12 schema accepted
`EXTERNAL_ACCEPTED` with `gateway_calls=1` but `provider_attempts=0`,
contrary to Amendment 1's exact-accepted-counter contract. Disposition was
`REVIEW_COST_ESCALATION_REQUIRED`; the operator explicitly authorized
Amendment 2 for one bounded round limited to this single finding.

**Fix.** `packages/ai-providers/src/ai_providers/errors.py::
assert_receipt_grammar`'s Rule 6 (`if accepted_external:`) gained
`_require(provider_attempts == 1, ...)` alongside the pre-existing
`output_digest` requirement — `EXTERNAL_ACCEPTED` is only reachable after a
real physical dispatch, so a receipt claiming acceptance with zero attempts
is now rejected. `EXTERNAL_NOT_ACCEPTED` is untouched: it stays under the
pre-existing `gateway_attempted` branch, which requires `gateway_calls == 1`
but never constrains `provider_attempts`, so 0 or 1 both remain valid there
per the Amendment's explicit instruction. The published schema's
`EXTERNAL_ACCEPTED` `if`/`then` conditional
(`packages/ai-providers/contracts/provider_modes.schema.json`) gained
`"provider_attempts": { "const": 1 }` added to both `properties` and
`required`, mirroring the model exactly; no other conditional was touched.

**Tests.** `tests/unit/test_p4b_no_ai.py::_F5R2_CASES` gained one paired
case (`accepted_zero_provider_attempts`: an otherwise-fully-valid
`EXTERNAL_ACCEPTED` receipt with `provider_attempts=0`), automatically
covered by the existing `TestF5R2CompleteGrammarMatrix`'s parametrized
`test_shape_rejected_by_pydantic`/`test_shape_rejected_by_schema` (now 7
cases, both layers). New `TestF5R3AcceptedProviderAttemptsExact` adds: a
positive test constructing the same base with `provider_attempts=1` and
validating it against the real schema file (proves the tightened schema
still accepts the honest case); and a parametrized `provider_attempts in
(0, 1)` test proving `EXTERNAL_NOT_ACCEPTED` stays valid either way (proves
the Amendment's "do not tighten" instruction was honored, not just assumed).
Positive coverage for the real service-emitted `EXTERNAL_ACCEPTED` receipt
was already present in `tests/unit/test_p4b_provider_service.py` (round 3)
and is unaffected — rerun and still passing.

**Verification** (interpreter/version above). F5-R3-specific:
`test_p4b_no_ai.py` + `test_p4b_provider_service.py` +
`test_p4b_provider_modes_schema.py` = `74 passed`. Full P4-B focused (all 11
files): `236 passed, 1 warning` (pre-existing, unrelated to this round).
P4-A/A2/A3 regressions: unchanged from round 3, rerun as part of the full
suite below. Full repository `python -m pytest -q`: `2731 passed, 128
skipped, 3 warnings` (skips/warning count match the round-3 baseline
exactly — no regression). `generate_catalog.py --write` was required once
(errors.py/schema/test LOC changed) then `--check` PASS; the write drifted
`knowledge/manifest.json`'s `docs/catalog/MODULE_REGISTRY.json` raw-byte
pin only (recomputed via `sha256sum`, matching this repo's known
CRLF/text-mode-hash gotcha), `check_project_knowledge.py` then PASS.
`check_session_state.py`, `check_file_size.py`,
`testing/validate_repository.py`, `git diff --check` (exit 0, only
informational CRLF autocrlf notices), and the CVF workspace-agent
enforcement doctor (`RESULT: PASS WITH NOTE`, 24 passed/1 bounded legacy
warning, unchanged) all pass. Secret scan: no new credential-like values
introduced (only the pre-existing synthetic Bearer-token literal already
noted in round 1).

**Changed-set proof.** `git rev-parse HEAD` unchanged at
`319c6a809ef29134a0de8c4a9923bb18669c349c`; `git status --porcelain
--untracked-files=all | wc -l` = exactly `51`; `git diff --cached
--name-only` empty; path 51 (`docs/decisions/
P4B_AI_PROVIDERS_COMPLETION_REVIEW_2026-08-21.md`) shows only as `??`
(untracked), never modified by this round; no path 52 created. Provider/
network/credential/install/database/commit/push/deployment this round:
`0/0/0/0/0/0/0/0`. Neither live-evidence script was executed.

**Final status.** `READY_FOR_REREVIEW_ROUND_4`. This repair did not
self-review, edit path 51, create path 52, call any provider, use a real
credential, install anything, commit, push, request/execute the
post-review live call, or declare FREEZE. Independent REVIEWER action is
required next.

---

## Original BUILD record (2026-08-21, condensed, superseded by all rounds above)

Built the `ai-providers` package and its no-route application composition
per SPEC R1–R12. Original verification: focused P4-B 147 passed, full
suite 2634 passed/128 skipped, exact changed-set 50/50, staged empty.
Original disposition `READY_FOR_REVIEW`, corrected by every repair round
above, which are authoritative for all current claims and the exact-51
changed-set.

---

## Post-review live finding repair — 2026-08-22

The single authorized admitted attempt returned HTTP 200 with exact `1/1/1/1`
counters and secret scan NONE, but correctly stopped at
`EXTERNAL_NOT_ACCEPTED / OUTPUT_SCHEMA_INVALID`; no retry occurred. Independent
post-call review opened `P4B-LIVE-F1`: P4-B support duplicated a status-only
schema while the runner imported P4-A's canonical prompt requiring both
`status` and `checked`.

Role transition `REVIEWER -> REPAIR_WORKER`. The support module now aliases
P4-A's canonical `CANARY_SCHEMA`, eliminating the independent prompt/schema
copy. The fake successful-provider fixture now returns the canonical object,
and a regression test locks schema object identity plus the required
`status`/`checked` contract. Targeted live-support tests passed `20`; focused
P4-B passed `237` with one known warning; full suite passed `2732`, skipped
`128`, with three known warnings. Catalog and file-size guards passed. No
provider/network call, credential read, install, database, commit, push or
deployment occurred during repair.

Disposition: `READY_FOR_INDEPENDENT_REREVIEW_LIVE_REPAIR`. The prior call
authority is exhausted. A replacement call requires separate operator
authority after independent source rereview. P4-B is not FREEZE.
