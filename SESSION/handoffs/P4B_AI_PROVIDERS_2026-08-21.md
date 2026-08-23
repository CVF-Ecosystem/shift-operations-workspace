# Active Handoff — P4-B AI Provider Foundation

- Tranche: `P4B-AI-PROVIDERS-2026-08-21`
- Date: `2026-08-21`
- Risk: `R2`
- Phase: `FREEZE`
- Status: `CLOSED_BOUNDED`
- Execution base: `319c6a8`
- Active role: `ORCHESTRATOR`

## Authority acknowledgment

After P4-A3 was committed and pushed at `319c6a8`, the operator requested the
next tranche. The orchestrator selected roadmap-next P4-B and opened INTAKE.
No BUILD, provider/network call, install, database, commit, push or deployment
authority carries forward.

## Current boundary

Provider-mode foundation only: zero-call `NO_AI`, deterministic local
`RULES_ONLY`, test-only evidence-ineligible mock, and an external-mode boundary
that may delegate only to injected P4-A `AIGateway`. No vendor adapter or
public route is included.

## Next governed move

P4-B reached `FREEZE / CLOSED_BOUNDED`. The replacement checkpoint passed four
fresh zero-call refusals followed by exactly one HTTP 200
`EXTERNAL_ACCEPTED` call with exact `1/1/1/1` counters and secret scan NONE.
The first BLOCKED receipt lineage remains preserved in completion review.
Next governed move is fresh INTAKE for
`CROSS-AGENT-INVARIANT-LEARNING-2026-08-22`; no DESIGN or BUILD authority.

## Reviewed design summary

Role transitions declared `INTAKE_AUTHOR -> REVIEWER -> DESIGN_AUTHOR ->
REVIEWER`. P4-A remains the sole external dispatch point. `NO_AI` is a typed
zero-call refusal; `RULES_ONLY` is deterministic local evaluation; mock is
test-only/default-denied/evidence-ineligible. Live proof remains a separate
post-review checkpoint.

## Pre-BUILD control chain

Role transitions declared `ORCHESTRATOR -> INTAKE_AUTHOR -> REVIEWER ->
DESIGN_AUTHOR -> REVIEWER -> SPEC_AUTHOR -> WORK_ORDER_AUTHOR -> REVIEWER ->
ORCHESTRATOR`. INTAKE and DESIGN reviews passed, SPEC v1.0 is testable, and
the exact-50 Work Order authorization review returned `REVIEW_PASS` with
findings/waivers `NONE/NONE`. BUILD belongs only to a different worker.

## Parked checkpoints

Production provider/network integration, credentials, live call, durable
usage/audit, database, deployment, commit and push remain parked. Any final
governance-behavior claim needs separately authorized real-provider evidence;
mock output is prohibited as proof.

## IMPLEMENTATION_WORKER acknowledgment (2026-08-21)

A separate `IMPLEMENTATION_WORKER` rehydrated continuity, read the exact-50
Work Order, SPEC v1.0, DESIGN and both reviews, and acknowledges the Work
Order before editing any source path. BUILD will implement only the 50-path
ceiling: the `ai-providers` package (models, protocols, `NO_AI`, `RULES_ONLY`,
`MockProviderAdapter`, `ProviderAdapterRegistry`, `ProviderModeService`), the
no-route application composition, the rehearsal-only (never-executed) live
evidence pair, the eleven required test files, catalog/CVF-doc/continuity
truth updates, and the worker-return document at path 50. No provider/network
call, install, database, route, retry, deployment, commit or push will occur.
Worker stops at `READY_FOR_REVIEW` or a precise blocker; it does not
self-review, create path 51, or declare FREEZE.

## Independent review (2026-08-22)

Role transition declared `IMPLEMENTATION_WORKER -> REVIEWER`. Exact set was
50/50 and baseline tests remained green (focused 147; full 2634/128), but
adversarial probes opened six findings: mock exclusion not load-bearing,
successful output discarded, incomplete external binding, reconstruction/
JSON scalar fail-open cases, receipt/schema grammar drift, and a non-runnable
parked live runner. Canonical detail is reviewer-owned path 51.

## Repair round 1 (2026-08-22)

Role transition declared `REVIEWER -> REPAIR_WORKER`. All six findings
(P4B-REV-F1..F6) repaired within the existing exact-50 union, no path
expansion: registry consultation is now load-bearing before any `EXTERNAL_AI`
delegation (F1); `ProviderModeService.execute` returns a strict
`ProviderModeResultV1` envelope binding releasable output to terminal outcome
(F2); the outer request now carries explicit provider/model/placement/
context-digest facts compared against the nested request, and
`ProviderMetadataV1.placement` reuses P4-A's canonical `Placement` enum (F3);
mock-authorization reconstruction now revalidates from its primitive dump,
an unexpected top-level exception now reaches typed `REQUEST_INVALID`,
non-finite floats are rejected, and exact-fact matching is type-checked (F4,
all four sub-gaps); the receipt gained a closed `ai_mode` vocabulary and
exact cross-field grammar, matched by hand-edited conditional grammar in the
published JSON schema (F5); the live-evidence runner's `--refusals-only` path
is now credential-independent/model-selection-independent and was run once
during repair (four refusal cases, zero gateway/provider calls, exit 0) —
the admitted (consuming) branch remains an explicit unexecuted stub pending
separate authority. Four files (`models.py`, `service.py`, two test files)
required an in-ceiling split/condense to stay under the file-size guard's
300-line hard limit. Full detail with source-file/test-name citations is in
`docs/decisions/P4B_AI_PROVIDERS_WORKER_RETURN_2026-08-21.md`. Verification:
focused P4-B 199/199 (12 files after moves), P4-A/A2/A3 regression 698/698,
full suite 2686/128/2 (matches pre-repair baseline exactly), all repository
gates PASS, exactly 51 changed paths, staged 0, HEAD unchanged. Disposition
`READY_FOR_REREVIEW`. Independent REVIEWER action required next; this repair
does not self-review, edit path 51, create path 52, call any provider,
install anything, commit, push, or declare FREEZE.

## Independent rereview round 1 (2026-08-22)

Role transition declared `REPAIR_WORKER -> REVIEWER`. Exact changed set
remained 51/51 including reviewer path, staged 0; focused/full verification
passed 199/2686 with 128 skipped and two known warnings; refusal rehearsal
passed 4/4 with zero gateway/provider calls. F2 and F3 closed without waiver.
Adversarial probes retained four residuals: F1-R1 (registry kind and
`evidence_eligible` do not gate dispatch), F4-R1 (constructed metadata and a
digestible invalid top-level request bypass revalidation), F5-R1 (four
impossible receipt shapes pass both model and schema), and F6-R1 (admitted
runner branch remains an unconditional blocked stub). Canonical probes and
repair requirements are in reviewer-owned path 51.

Role transition declared `REVIEWER -> ORCHESTRATOR`. Same-scope repair round
2 is authorized within the original exact-50 worker union. A separate
`REPAIR_WORKER` must stop at `READY_FOR_REREVIEW_ROUND_2`; it may not edit
path 51, create path 52, make a provider/network call, install, use a
database, commit, push, deploy, or declare FREEZE.

## Repair round 2 (2026-08-22)

Role transition declared `ORCHESTRATOR -> REPAIR_WORKER`. All four residual
findings (`P4B-REV-F1-R1`, `P4B-REV-F4-R1`, `P4B-REV-F5-R1`,
`P4B-REV-F6-R1`) repaired within the existing exact-50 union, no path
expansion: external delegation now requires registry-owned metadata to be
exactly `kind=EXTERNAL_GATEWAY` AND `evidence_eligible=True` (F1-R1);
`ProviderAdapterRegistry.register` and `ProviderModeService.execute` both
fully reconstruct/revalidate untrusted input from its primitive dump before
storing or dispatching, closing the `model_construct` registry bypass and
the JSON-invalid-tuple request bypass (F4-R1); the receipt's cross-field
grammar (now centralized in `errors.py::assert_receipt_grammar`) and the
published schema both enforce the general rules the four reviewer probes
pointed at — rule_id iff matched, rules_evaluated>=1 when matched,
provider/model ids whenever a gateway call happened, and
`EXTERNAL_IDENTITY_MISMATCH` requires the genuine `ai_mode=EXTERNAL_AI`
(F5-R1); the admitted (consuming) live-evidence branch is now real, tested
one-call mechanics (hard one-attempt budget, last-moment credential read,
one physical HTTPS POST, no retry) wired into the runner but still never
executed this round, pending separate authority (F6-R1). Full detail with
source-file/test-name citations is in
`docs/decisions/P4B_AI_PROVIDERS_WORKER_RETURN_2026-08-21.md`. Verification:
focused P4-B 220/220 (12 files), P4-A/A2/A3 regression 698/698, full suite
2707/128/3 (skips match baseline; 3rd warning is a new deliberate adversarial
test's expected Pydantic notice), all repository gates PASS, exactly 51
changed paths, staged 0, HEAD unchanged. Disposition
`READY_FOR_REREVIEW_ROUND_2`. Independent REVIEWER action required next;
this repair does not self-review, edit path 51, create path 52, call any
provider, install anything, commit, push, or declare FREEZE.

## Independent rereview round 2 (2026-08-22)

Role transition declared `REPAIR_WORKER -> REVIEWER`. Exact 51/51, staged 0,
focused 220 and full 2707/128 passed; repository gates passed. Independent
probes closed F1-R1 and confirmed the constructed-request repair plus the
four original F5 examples. Three residuals remain: F4-R2 raw `AttributeError`
for primitive registry input; F5-R2 six impossible terminal receipt shapes
accepted by model and schema; F6-R2 PASS receipt written before all evidence
invariants, without exact gateway/receipt counter gates. Canonical evidence
and the complete repair contract are in reviewer path 51.

Role transition declared `REVIEWER -> ORCHESTRATOR`. Because the next repair
would be round 3 without an independent new root cause, disposition is
`REVIEW_COST_ESCALATION_REQUIRED`. Stop pending explicit operator Amendment
authority. No implementation edit, path 52, provider/network call, credential
use, install, database, commit, push, deployment or FREEZE is authorized.

## Operator Amendment authority (2026-08-22)

Role transition declared `ORCHESTRATOR -> WORK_ORDER_AUTHOR`. The operator
explicitly authorized round 3 for only F4-R2/F5-R2/F6-R2. Amendment 1 was
recorded in the existing Work Order path with the complete repair matrix and
evidence requirements; no path 52 was created. Boundaries remain exact-50,
path 51 read-only, and zero provider/network call, credential use, install,
database, commit, push or deployment.

Role transition declared `WORK_ORDER_AUTHOR -> ORCHESTRATOR`. Next action
belongs to a separate `REPAIR_WORKER`, which must acknowledge Amendment 1,
perform only the bounded repair and stop at `READY_FOR_REREVIEW_ROUND_3`.

## Repair round 3 (2026-08-22)

Role transition declared `ORCHESTRATOR -> REPAIR_WORKER`. Acknowledged
Amendment 1 and all three residual findings (`P4B-REV-F4-R2`,
`P4B-REV-F5-R2`, `P4B-REV-F6-R2`) before any edit. All three repaired within
the existing exact-50 union, no path expansion: `ProviderAdapterRegistry.
register` now accepts untrusted input generically (`isinstance` gates the
`.model_dump()` call), feeds it through `ProviderMetadataV1.model_validate`,
and normalizes every `ValidationError` to the documented typed error with no
partial mutation, closing the raw `AttributeError` on primitive/arbitrary
input (F4-R2); the receipt cross-field grammar in
`ai_providers/errors.py::assert_receipt_grammar` was rewritten as one
general outcome-family-keyed rule set (`is_external`/`is_rules`/etc., not
per-shape patches), mirrored in `provider_modes.schema.json`'s `allOf`
conditionals, closing all six round-2 reviewer shapes plus the adjacent
matrix (F5-R2); `scripts/run_p4b_ai_providers_live_evidence.py`'s admitted
branch now computes every evidence invariant (`accepted`, secret scan,
four-way counter agreement) via `decide_admitted_disposition` before any
disposition is chosen or anything is written to disk (F6-R2). Full detail
with source-file/test-name citations is in
`docs/decisions/P4B_AI_PROVIDERS_WORKER_RETURN_2026-08-21.md`. Verification:
focused P4B suite passed, P4-A/A2/A3 regression 698/698 (unchanged
baseline), full suite 2726 passed/128 skipped/3 known warnings, all
repository gates PASS after catalog regeneration and a knowledge-manifest
pin refresh, exactly 51 changed paths, staged 0, HEAD unchanged. Disposition
`READY_FOR_REREVIEW_ROUND_3`. Independent REVIEWER action required next;
this repair does not self-review, edit path 51, create path 52, call any
provider, use a real credential, install anything, commit, push, or declare
FREEZE.

## Independent rereview round 3 (2026-08-22)

Role transition declared `ORCHESTRATOR -> REVIEWER`. Independent probes and
239/2726 baselines closed F4-R2 and F6-R2 without waiver. F5-R2 remains
partial: both Pydantic and schema accept `EXTERNAL_ACCEPTED` with
`gateway_calls=1` but `provider_attempts=0`, contrary to Amendment 1's exact
accepted-counter contract. Canonical evidence is in reviewer path 51.

Role transition declared `REVIEWER -> ORCHESTRATOR`. Disposition is
`REVIEW_COST_ESCALATION_REQUIRED`; no round 4 is authorized without explicit
operator approval. No source edit, path 52, live call, credential use,
install, database, commit, push, deployment or FREEZE is authorized.

## Amendment 2 authority acknowledgment (2026-08-22)

Role transition declared `ORCHESTRATOR -> WORK_ORDER_AUTHOR`. The operator
explicitly authorized one bounded repair round 4 for only `P4B-REV-F5-R3`.
Amendment 2 was recorded in the existing Work Order path with the existing
exact-50 worker union unchanged. Path 51 remains reviewer-owned/read-only;
path 52 and all provider/network/credential/install/database/commit/push/
deployment effects remain prohibited. Role transition declared
`WORK_ORDER_AUTHOR -> ORCHESTRATOR`; a separate `REPAIR_WORKER` may now accept
the Work Order, acknowledge it here, repair, and stop at
`READY_FOR_REREVIEW_ROUND_4`.


## Repair round 4 acknowledgment (2026-08-22)

Role transition declared `ORCHESTRATOR -> REPAIR_WORKER`. Acknowledges
Amendment 2 and its sole scope, `P4B-REV-F5-R3`: `EXTERNAL_ACCEPTED` must
require `provider_attempts == 1` in both the general Pydantic receipt
grammar and the published Draft 2020-12 JSON Schema, with paired negative
tests and retained positive coverage; `EXTERNAL_NOT_ACCEPTED` stays
untightened. Confirmed entry state before any edit: `HEAD` unchanged at
`319c6a809ef29134a0de8c4a9923bb18669c349c`, exactly 51 paths, staged 0.
Repair proceeds only within the existing exact-50 worker union; path 51
stays read-only and no path 52 is created.

## Independent rereview round 4 (2026-08-22)

Role transition declared `REPAIR_WORKER -> REVIEWER`. Independent Pydantic and
Draft 2020-12 mutation probes rejected `EXTERNAL_ACCEPTED` with zero provider
attempts, accepted the exact-one shape, and retained both zero/one forms for
`EXTERNAL_NOT_ACCEPTED`. Focused P4-B passed 236 with one known warning; full
suite passed 2731 with 128 skipped and three known warnings. Repository gates,
exact-51/staged-0/unchanged-HEAD and doctor 24/1 all passed. F5-R3 and all
prior findings are closed without waiver. Disposition:
`REVIEW_PASS / LIVE_AUTHORITY_REQUIRED`.

Role transition declared `REVIEWER -> ORCHESTRATOR`. No provider/network call
was made and no credential was consumed. The separate live checkpoint remains
authority-gated; P4-B is not yet FREEZE.

## Post-review live authority acknowledgment (2026-08-22)

The operator explicitly authorized the P4-B post-review live checkpoint:
mandated zero-call refusals followed by exactly one admitted real-provider
call using the existing stable runtime/runner and configured credential. The
credential value must never be printed or written. The runner-owned sanitized
receipt is the sole new live-evidence artifact. Install, database, commit,
push and deployment remain prohibited. Role transition declared
`ORCHESTRATOR -> LIVE_EVIDENCE_WORKER`; after the call, control must transition
to `REVIEWER -> CLOSER` for post-call review and FREEZE disposition.

## First post-review live checkpoint result (2026-08-22)

Four refusal cases passed zero-call. The sole admitted attempt returned HTTP
200 with exact `1/1/1/1` counters and secret scan NONE, but was correctly
blocked as `EXTERNAL_NOT_ACCEPTED / OUTPUT_SCHEMA_INVALID`. No retry occurred.
Role transition declared `LIVE_EVIDENCE_WORKER -> REVIEWER`; post-call review
opened `P4B-LIVE-F1`: the runner imports P4-A's prompt requiring `status` plus
`checked`, while P4-B support duplicated a status-only schema with
`additionalProperties=false`. Role transition declared `REVIEWER ->
REPAIR_WORKER` under the operator's instruction to self-handle further
findings. Repair is limited to canonical prompt/schema reuse and regression
tests; the consumed one-call authority is not renewed.

## P4B-LIVE-F1 repair return (2026-08-22)

The support module now aliases P4-A's canonical `CANARY_SCHEMA`; its fake
successful provider response and regression assertions use the exact
prompt-required `status` plus `checked` object. Targeted/focused/full tests
passed 20/237/2732 with 128 skipped and three known full-suite warnings;
catalog and file-size gates passed. No provider/network call, credential read,
install, database, commit, push or deployment occurred during repair. Role
transition declared `REPAIR_WORKER -> ORCHESTRATOR`. Disposition:
`READY_FOR_INDEPENDENT_REREVIEW_LIVE_REPAIR`; replacement live authority is
not granted or inferred.

## Independent P4B-LIVE-F1 repair rereview return (2026-08-22)

An independent REVIEWER confirmed the repair sound and returned
`READY_FOR_REPLACEMENT_LIVE_AUTHORITY`. No replacement live call was made and
no FREEZE was declared. Role transition returned control to ORCHESTRATOR;
replacement provider authority remains the sole active checkpoint.

## Replacement live authority acknowledgment (2026-08-22)

The operator authorized exactly one P4-B replacement provider call after four
fresh zero-call refusals, using the existing stable runtime/runner and
configured credential without exposing its value. No retry, install, database,
commit, push or deployment. Before execution, the retained first BLOCKED
receipt was preserved in completion-review lineage with canonical SHA-256
`a0fbde82e3cca1187dbd6ca3fabe6eb7007ae7ffafd8f51bcb370cd635b6288d` and
secret scan NONE. Role transition declared `ORCHESTRATOR ->
LIVE_EVIDENCE_WORKER`.

## Replacement live result and closure (2026-08-22)

Four fresh refusal cases passed zero-call, followed by exactly one replacement
provider attempt. It returned HTTP 200 and `EXTERNAL_ACCEPTED`, with exact
adapter/gateway/receipt counters `1/1/1/1`, secret scan NONE and canonical
receipt SHA-256
`ec29426d10f68381b413e09d2a0278044790c7b91e24098079358ee333bd8097`.
No retry occurred. Targeted/focused/full verification passed 20/237/2732 with
128 skipped. Role transitions declared `LIVE_EVIDENCE_WORKER -> REVIEWER ->
CLOSER`; final findings/waivers `NONE/NONE`, disposition `FREEZE /
CLOSED_BOUNDED`. No install, database, commit, push or deployment occurred.
