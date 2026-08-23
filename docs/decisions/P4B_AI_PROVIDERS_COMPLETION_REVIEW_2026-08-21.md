# P4-B AI Provider Foundation — Independent Completion Review

- Tranche: `P4B-AI-PROVIDERS-2026-08-21`
- Role: `REVIEWER`
- Review date: `2026-08-22`
- Execution base / HEAD: `319c6a809ef29134a0de8c4a9923bb18669c349c`
- Disposition: `REVIEW_FAIL / REPAIR_REQUIRED`
- Open findings: `P4B-REV-F1..F6`
- Waivers: `NONE`

## Verified baseline

- Work Order changed set: exact `50/50`, missing/unexpected `0/0`, staged `0`.
- Focused P4-B suite: `147 passed`.
- Full suite: `2634 passed, 128 skipped, 2 known warnings`.
- Session, Project Knowledge and repository validators: PASS.
- BUILD/live provider calls observed by reviewer: `0`; the non-consuming
  `--refusals-only` runner stopped at import/model selection before dispatch.

Green baseline tests do not close the adversarial contract gaps below.

## Findings

### P4B-REV-F1 — HIGH — mock exclusion is not load-bearing

`ProviderModeService` never consumes `ProviderAdapterRegistry`. A valid
`MockProviderAdapter` can be registered directly in P4-A `ProviderRegistry`,
submitted under `EXTERNAL_AI`, called once, and returned as
`EXTERNAL_ACCEPTED`. The P4-B receipt carries neither provider kind nor
`evidence_eligible=false`, so it is indistinguishable from an evidence-eligible
external result. Reviewer probe: `MOCK_THROUGH_SERVICE EXTERNAL_ACCEPTED ...
HAS_EVIDENCE_FLAG False`.

Repair must make registry-owned provider kind/evidence eligibility
load-bearing before gateway delegation. Mock/test-only targets must refuse
with zero gateway/provider calls regardless of caller labels or which P4-A
registry contains the adapter. Add the exact adversarial integration test.

### P4B-REV-F2 — HIGH — successful mode output is discarded

`ProviderModeService.execute` returns only `ProviderModeReceiptV1`. A
`RULES_MATCHED` evaluation and an accepted gateway output are validated and
then discarded; callers receive no result body. This contradicts SPEC R3/R5's
output semantics and leaves the provider foundation unusable.

Repair with a strict result envelope that separates releasable output from
the sanitized receipt. Bind output presence to terminal outcome, deep-copy
local output, preserve accepted gateway output, and prove receipt output
digest equality. Refusal/non-accepted outcomes must carry no output.

### P4B-REV-F3 — HIGH — external identity/placement binding is incomplete

The outer request has no provider id, model id, placement or context digest.
`_identity_mismatch` checks only task, mode and output schema, so SPEC R6's
provider/model/placement/relevant-digest comparisons cannot occur.
`ProviderMetadataV1.placement` is also an arbitrary string; reviewer created
and registered placement `mars`, contrary to canonical P4-A `Placement` reuse.

Repair the outer contract with explicit canonical binding facts, compare all
R6 fields before delegation, use P4-A enum identity, and bind them to the
load-bearing P4-B registry entry. Every mismatch must be zero-call.

### P4B-REV-F4 — HIGH — public boundaries are not reconstruction-safe

Reviewer probes proved:

- `MockAuthorizationV1.model_construct(purpose="PRODUCTION_USE",
  evidence_eligible=True)` is accepted by `MockProviderAdapter` because it
  checks only `isinstance`;
- a top-level constructed request containing `object()` raises `TypeError`
  instead of reaching R2's typed terminal outcome;
- non-finite float `NaN` passes the claimed JSON-only validator;
- exact fact matching treats JSON boolean `true` as integer `1` because it
  uses Python equality without type equality.

Repair every public trust boundary by reconstructing from primitive dumps,
reject non-finite numbers and bool/number type confusion, and return the
specified fail-closed terminal result without partial work.

### P4B-REV-F5 — HIGH — receipt model and published schema permit drift

An unknown mode produces a valid Pydantic `REQUEST_INVALID` receipt whose
`ai_mode="BOGUS"` is rejected by the published JSON schema. Conversely, the
model accepted `ai_mode=NO_AI/outcome=RULES_MATCHED` with no rule/output
digest, and accepted `EXTERNAL_NOT_ACCEPTED` with `gateway_calls=0`.

Repair exact cross-field grammar for every terminal outcome, canonicalize how
unknown input mode is represented, require/forbid provider/model/rule/output
facts and exact counters as applicable, and keep Pydantic plus JSON Schema
mutually exhaustive. Add negative tests for every mismatch.

### P4B-REV-F6 — MEDIUM — parked live checkpoint runner is not runnable

Independent `scripts/run_p4b_ai_providers_live_evidence.py --refusals-only`
returned `LIVE_EVIDENCE_BLOCKED: no eligible model (ModuleNotFoundError)`
because `alibaba.select_model` is not importable from the runner's paths.
Even after that repair, the admitted branch is an unconditional blocked stub
and explicitly requires further code changes. This contradicts the worker
return claim that the separately authorized checkpoint can run without a
fresh BUILD.

Repair the rehearsal/refusal flow so it needs neither a credential nor live
model selection, and implement the already-authorized evidence mechanics for
exactly one future admitted call using the stable existing P4-A adapter
pattern. Do not execute the consuming branch during repair.

## Repair disposition

All six findings are within the existing exact-50 Work Order paths and
objective. A separate `REPAIR_WORKER` may perform repair round 1 without path
expansion, provider/network use, install, database, commit, push or deployment.
Path 51 remains reviewer-owned and must not be edited by the repair worker.
Return `READY_FOR_REREVIEW` with exact probes and full evidence; do not claim
FREEZE or request live authority yet.

## Rereview round 1 — 2026-08-22

- Role: `REVIEWER`
- Worker return reviewed: `READY_FOR_REREVIEW`
- Disposition: `REREVIEW_FAIL / RESIDUAL_REPAIR_REQUIRED`
- Closed without waiver: `P4B-REV-F2`, `P4B-REV-F3`
- Partial: `P4B-REV-F1`, `P4B-REV-F4`, `P4B-REV-F5`
- Open: `P4B-REV-F6`
- Waivers: `NONE`

The repaired baseline is green: exact changed set `51/51` including this
reviewer-owned path, missing/unexpected `0/0`, staged `0`; focused P4-B
`199 passed`; full suite `2686 passed, 128 skipped, 2 known warnings`.
Independent `--refusals-only` rehearsal also passed all four required cases
with zero gateway/provider attempts and exit `0`. These results do not close
the adversarial gaps below.

### P4B-REV-F1-R1 — HIGH — provider eligibility and kind still do not gate dispatch

The service now resolves the P4-B registry, but it rejects only `MOCK` and a
placement mismatch. Independent probes registered otherwise-valid metadata
for the requested pair and obtained `EXTERNAL_ACCEPTED` with one gateway call
for each of:

- `kind=EXTERNAL_GATEWAY, evidence_eligible=False`;
- `kind=RULES_ONLY, evidence_eligible=True`;
- `kind=NO_AI, evidence_eligible=True`.

Repair must permit external delegation only when registry-owned metadata is
exactly `kind=EXTERNAL_GATEWAY` and `evidence_eligible=True`; every other
combination must refuse before the gateway with exact zero-call tests.

### P4B-REV-F4-R1 — HIGH — two public reconstruction boundaries remain open

`ProviderAdapterRegistry.register` stores an attached model instance without
primitive-dump reconstruction. A `ProviderMetadataV1.model_construct` value
with `kind="BOGUS"` and `placement="mars"` was registered and resolved.
Likewise, `ProviderModeService.execute` only catches digest failure rather
than revalidating the whole request. A constructed request containing the
JSON-invalid tuple `facts={"x": (1, 2)}` remained digestible and returned
`AI_MODE_DISABLED` instead of `REQUEST_INVALID`.

Repair both public boundaries by reconstructing from primitive dumps before
reading or storing fields. Invalid metadata must raise the documented typed
registration error without mutation; invalid top-level requests must return
the typed zero-work `REQUEST_INVALID` result. Add the exact bypass probes.

### P4B-REV-F5-R1 — HIGH — receipt grammar still admits impossible facts

Both `ProviderModeReceiptV1` and the published Draft 2020-12 schema accepted
all four independent negative probes:

- `RULES_NO_MATCH` carrying `rule_id="ghost"`;
- `RULES_MATCHED` with `rules_evaluated=0`;
- `EXTERNAL_NOT_ACCEPTED` with one gateway call but no provider/model ids;
- `EXTERNAL_IDENTITY_MISMATCH` carrying `ai_mode=UNKNOWN`.

Repair model and schema together so each outcome requires and forbids the
exact rule/provider/output facts and counter relationships that can actually
be emitted. Add paired model/schema rejection tests for these shapes and the
adjacent outcome matrix.

### P4B-REV-F6-R1 — MEDIUM — admitted evidence path remains a blocked stub

The refusal-only half is repaired and independently verified. The admitted
branch still unconditionally prints `LIVE_EVIDENCE_BLOCKED` and exits `1`;
the worker return explicitly says a future worker must wire real dispatch.
That does not satisfy F6's already-authorized requirement to implement the
future one-call evidence mechanics without executing them during repair.

Repair the runner/support path using the stable existing P4-A evidence-only
HTTPS adapter pattern, with an exact one-attempt budget, sanitized receipt,
secret scan and testable dependency seams. Keep the consuming branch
unexecuted. No credential value may be read or printed during repair tests.

## Repair round 2 disposition

These residuals preserve the existing objective, risk, external-effect class,
artifact classes and commit owner. A separate `REPAIR_WORKER` may perform
repair round 2 inside the original exact-50 worker union and must not edit
this reviewer-owned path 51 or create path 52. No provider/network call,
install, database, commit, push or deployment is authorized. Return
`READY_FOR_REREVIEW_ROUND_2` with the exact adversarial probes, focused/full
tests and repository gates. This is repair round 2, so the round-three cost
checkpoint has not been reached.

## Rereview round 2 — 2026-08-22

- Role: `REVIEWER`
- Worker return reviewed: `READY_FOR_REREVIEW_ROUND_2`
- Disposition: `REVIEW_COST_ESCALATION_REQUIRED`
- Closed without waiver: `P4B-REV-F1-R1`, prior `P4B-REV-F2/F3`
- Residual: `P4B-REV-F4-R2`, `P4B-REV-F5-R2`, `P4B-REV-F6-R2`
- Waivers: `NONE`

The repaired baseline remains green: exact changed set `51/51`, missing and
unexpected `0/0`, staged `0`; focused P4-B `220 passed, 1 warning`; full
suite `2707 passed, 128 skipped, 3 known warnings`; repository gates PASS.
The prior F1 eligibility/kind probes now refuse with zero calls, the exact
constructed-request probe returns `REQUEST_INVALID`, and all four F5-R1
receipt examples are rejected. The remaining gaps are below.

### P4B-REV-F4-R2 — HIGH — primitive registry input escapes as raw AttributeError

`ProviderAdapterRegistry.register` calls `metadata.model_dump(...)` inside a
handler that catches only `pydantic.ValidationError`. Passing an untrusted
primitive mapping therefore raises raw `AttributeError` instead of the
documented typed `DuplicateProviderRegistrationError`. The registry remains
unmutated, but the public boundary is not reconstruction-safe for primitive
input and contradicts the worker return's “invalid metadata raises the
documented typed registration error” claim.

Repair by accepting the untrusted input at the runtime boundary, obtaining a
primitive dump only when applicable, and feeding it through
`ProviderMetadataV1.model_validate`; normalize every invalid-input failure to
the documented typed error without mutation. Test mapping, arbitrary object,
constructed model and valid model inputs.

### P4B-REV-F5-R2 — HIGH — outcome grammar is still not exact

Both Pydantic and Draft 2020-12 schema accepted all six independent shapes:

- `EXTERNAL_IDENTITY_MISMATCH` carrying an `output_digest`;
- `EXTERNAL_IDENTITY_MISMATCH` carrying `rules_evaluated=7` and a
  `ruleset_digest`;
- `EXTERNAL_ACCEPTED` carrying rule counters/ruleset facts;
- `EXTERNAL_NOT_ACCEPTED` carrying an `output_digest`;
- `RULES_NO_MATCH` without the ruleset digest the service always emits;
- `RULES_SCHEMA_INVALID` without the ruleset digest the service always emits.

The repair must encode the complete emitted-shape matrix, not another
probe-specific patch: every external outcome has zero rule counters and no
rule/ruleset facts; non-accepted external outcomes have no output digest;
rules outcomes require a ruleset digest; identity-mismatch provider/model
facts are both present or both absent; accepted external output/provider/model
facts and attempt counters are exact; disabled/invalid invariants remain
unchanged. Pydantic and schema must reject the same negative matrix and accept
every real service-emitted shape.

### P4B-REV-F6-R2 — MEDIUM — PASS receipt is decided before evidence invariants

An independent fake-HTTPS probe confirmed the adapter performs one attempt
and refuses a second (`calls/urlopen = 1/1`), so the transport and budget
mechanics are real. However `main()` sets payload disposition to
`LIVE_EVIDENCE_PASS` from outcome alone and writes the receipt before checking
secret hits or the call-count invariant. It checks only `provider.calls`, not
`gateway.physical_attempts`, `receipt.gateway_calls` or
`receipt.provider_attempts`. An anomalous accepted result can therefore leave
a PASS-labeled receipt even though the runner subsequently exits blocked.

Repair by computing all evidence invariants first. PASS requires outcome
accepted, secret scan clean, and exact physical/adapter/gateway/receipt
counters; every failure writes or retains only `LIVE_EVIDENCE_BLOCKED` and
never a PASS artifact. Add a successful fake-transport end-to-end test plus
counter-drift and secret-hit tests proving no false PASS receipt. Do not run
the real consuming branch.

## Cost-escalation disposition

Closing these residuals would be repair round 3 without an independent new
root cause. Under the governance-latency rule, no further repair is
automatically authorized. Record `REVIEW_COST_ESCALATION_REQUIRED` and stop.
The operator must explicitly authorize a bounded Amendment/repair round 3
before any implementation edit. Until then, path 51 remains reviewer-owned,
no path 52 may be created, and provider/network call, credential use, install,
database, commit, push and deployment remain unauthorized. The later
post-review one-call checkpoint is separate and remains parked.

## Rereview round 3 — 2026-08-22

- Role: `REVIEWER`
- Worker return reviewed: `READY_FOR_REREVIEW_ROUND_3_CONTINUITY_SYNCED`
- Disposition: `REVIEW_COST_ESCALATION_REQUIRED`
- Closed without waiver: `P4B-REV-F4-R2`, `P4B-REV-F6-R2`
- Partial: `P4B-REV-F5-R2`
- Residual: `P4B-REV-F5-R3`
- Waivers: `NONE`

Independent verification matched the worker baseline: exact changed set
`51/51`, missing/unexpected `0/0`, staged `0`; focused P4-B `239 passed, 1
warning`; full suite `2726 passed, 128 skipped, 3 known warnings`; session,
Project Knowledge, catalog, file-size and repository gates PASS. F4 primitive
mapping/object/constructed-model probes now return the typed error without
mutation. F6 fake-transport success, counter-drift and secret-hit tests pass,
and the refusal rehearsal remains 4/4 zero-call.

### P4B-REV-F5-R3 — HIGH — accepted provider-attempt counter is not exact

Amendment 1 explicitly requires accepted external attempt counters to be
exact. `assert_receipt_grammar` requires one gateway call for
`EXTERNAL_ACCEPTED` but does not require `provider_attempts == 1`; the schema
has the same omission. Independent probes constructed an
`EXTERNAL_ACCEPTED` receipt with provider/model/output facts,
`gateway_calls=1`, and `provider_attempts=0`. Both Pydantic and Draft 2020-12
schema accepted it. A direct mutation of a canonical accepted JSON payload to
`provider_attempts=0` was also schema-valid.

Repair the general accepted-outcome rule in model and schema to require
`provider_attempts == 1`. Add paired Pydantic/schema negative tests and retain
the positive real-service accepted receipt test. Do not change
`EXTERNAL_NOT_ACCEPTED`, whose provider attempts may legitimately be zero or
one depending on where P4-A refused.

## Round-4 authority checkpoint

This is a residual of the same receipt-grammar root after the operator-
authorized round 3. No round 4 is automatically authorized. Record
`REVIEW_COST_ESCALATION_REQUIRED` and stop pending explicit operator authority
for this single bounded source/schema/test repair. Reviewer path 51 remains
read-only to any worker; no path 52, provider/network call, credential use,
install, database, commit, push or deployment. Post-review live authority
remains separately parked.

## Rereview round 4 — 2026-08-22

- Role: `REVIEWER`
- Worker return reviewed: `READY_FOR_REREVIEW_ROUND_4`
- Disposition: `REVIEW_PASS / LIVE_AUTHORITY_REQUIRED`
- Closed without waiver: `P4B-REV-F5-R3` and all prior findings
- Open source findings: `NONE`
- Waivers: `NONE`

Independent mutation probes confirmed that an otherwise-valid
`EXTERNAL_ACCEPTED` receipt with `provider_attempts=0` is rejected by both
Pydantic and the published Draft 2020-12 schema. The same payload with one
provider attempt is accepted by both. `EXTERNAL_NOT_ACCEPTED` remains valid
with either zero or one provider attempt, preserving the Amendment boundary.

Focused P4-B verification passed `236` tests with one known Pydantic warning.
The full suite passed `2731`, skipped `128`, with three known warnings. Session,
Project Knowledge, catalog, file-size and repository gates passed; changed set
remained exact `51`, staged `0`, HEAD and `origin/main` remained
`319c6a809ef29134a0de8c4a9923bb18669c349c`, and the workspace doctor returned
`PASS WITH NOTE` (`24` pass plus the same bounded legacy-catalog warning).

The non-consuming implementation review is complete. Because this tranche
claims governed external-provider behavior, FREEZE still requires the
separately authorized real-provider checkpoint described by the Work Order:
zero-call refusal cases followed by exactly one admitted provider call, then
independent post-call review. No live/provider/network/credential authority
is inferred from this review pass.

## First post-review live checkpoint — 2026-08-22

- Disposition: `LIVE_EVIDENCE_BLOCKED / REPAIR_REQUIRED`
- Refusals: `4/4` zero-call
- Physical admitted calls: exactly `1`; no retry
- HTTP status: `200`
- Counters: adapter/gateway/receipt gateway/provider = `1/1/1/1`
- Outcome: `EXTERNAL_NOT_ACCEPTED`
- Reason: `OUTPUT_SCHEMA_INVALID`
- Secret scan: `NONE`

### P4B-LIVE-F1 — HIGH — evidence prompt/schema drift rejects a compliant response

The runner imports the canonical P4-A `CANARY_PROMPT`, which requires exactly
`{"status":"ok","checked":1}`, while P4-B support independently defines a
schema requiring only `status` and forbidding additional properties. The
provider returned HTTP 200 after the single authorized attempt, but the
prompt-required `checked` field necessarily violated the divergent P4-B
schema, so the gateway correctly refused the output. This is deterministic
runner contract drift, not a provider outage.

Repair the existing support path to reuse the canonical P4-A canary schema
paired with the imported prompt, and add a non-consuming regression test that
locks prompt/schema alignment. The consumed one-call authority is exhausted;
do not retry. A replacement live call requires separate operator authority.

## Independent P4B-LIVE-F1 repair rereview return — 2026-08-22

An independent REVIEWER returned
`READY_FOR_REPLACEMENT_LIVE_AUTHORITY`, confirming the P4B-LIVE-F1 repair
sound. The reviewer made no replacement provider call and declared no FREEZE.
The retained first receipt remains `LIVE_EVIDENCE_BLOCKED`; exactly one
replacement live call remains an explicit operator-authority checkpoint.

## Replacement live authority and retained lineage — 2026-08-22

The operator authorized exactly one replacement call using the existing
stable runtime/runner, preceded by the four zero-call refusals, with no retry,
install, database, commit, push or deployment. Before any replacement
execution, the retained first receipt was independently re-read as
`LIVE_EVIDENCE_BLOCKED`, secret scan `NONE`, canonical universal-newline
SHA-256 `a0fbde82e3cca1187dbd6ca3fabe6eb7007ae7ffafd8f51bcb370cd635b6288d`.
This lineage remains authoritative even though the runner may replace the
current receipt path with the replacement result.

## Replacement live post-call review and FREEZE — 2026-08-22

- Role route: `LIVE_EVIDENCE_WORKER -> REVIEWER -> CLOSER`
- Fresh refusals: `4/4` zero-call
- Replacement admitted calls: exactly `1`; no retry
- HTTP status: `200`
- Outcome: `EXTERNAL_ACCEPTED`
- Counters: adapter/gateway physical/receipt gateway/provider = `1/1/1/1`
- Secret scan: `NONE`
- Replacement canonical receipt SHA-256:
  `ec29426d10f68381b413e09d2a0278044790c7b91e24098079358ee333bd8097`
- Retained first BLOCKED canonical SHA-256:
  `a0fbde82e3cca1187dbd6ca3fabe6eb7007ae7ffafd8f51bcb370cd635b6288d`
- Targeted/focused/full verification: `20/237/2732` passed, `128` skipped
- Final findings/waivers: `NONE/NONE`
- Final disposition: `FREEZE / CLOSED_BOUNDED`

The replacement receipt is sanitized and binds the accepted outcome to exact
one-call accounting after all required zero-call refusals. The first BLOCKED
attempt remains preserved as historical lineage in this review; it is not
rewritten as a PASS. P4-B closes only as a provider-neutral library and
no-route application-composition foundation. This does not prove a production
vendor adapter, automatic routing/retry, durable usage/audit, public API/UI,
deployment or production readiness.
