# Completion Review — P4-A AI Gateway

- Tranche: `P4A-AI-GATEWAY-2026-08-20`
- Phase: `REVIEW`
- Reviewer: current `ORCHESTRATOR/REVIEWER`, independent from the external
  `IMPLEMENTATION_WORKER`
- Initial disposition: `REVIEW_CHANGES_REQUIRED`
- Findings: `P4A-REV-F1` through `P4A-REV-F6`
- Waivers: `NONE`
- Provider calls made by reviewer: `0`

## Recomputed evidence

- Exact worker changed set: `40/40`; paths outside ceiling: `0`; staged: `0`.
- Focused suite: `142 passed`.
- Full suite: `1976 passed, 128 skipped, 2 failed, 8 errors`; exit `1`.
- Session, catalog, file-size, repository validator and doctor: PASS; doctor
  retains only the bounded `24/1` legacy-catalog warning.
- Project Knowledge: FAIL with
  `KPK_CONTINUITY_CHANGED:GOVERNANCE_BOUNDARIES.md` and
  `KPK_ELIGIBILITY_MISMATCH:GOVERNANCE_BOUNDARIES.md`.
- Live receipt records one prior worker call; reviewer made no provider call.

## Consolidated findings

### P4A-REV-F1 — JSON Schema validation fails open

`validation.py` accepts outputs that violate unsupported caller constraints.
Independent probes showed both `pattern` and `oneOf` violations return
accepted. Ignoring an unknown keyword does widen acceptance, contrary to the
module comment and SPEC R9's exact-schema contract.

Repair: validate the schema itself and validate output with Draft 2020-12
semantics (the repository already carries `jsonschema` as a development
dependency), or reject every unsupported keyword recursively. Add negative
tests for `pattern`, `oneOf`, malformed schemas, nested unsupported keywords,
and format/constraint behavior selected by the repaired contract.

### P4A-REV-F2 — Budget units and cumulative accounting are incorrect

Gateway facts are integer USD-millis, while `cvf_runtime.BudgetState` and its
policy keys are USD floats. The adapter passes millis without conversion. The
ledger also omits already committed cost from later projected daily/monthly
spend. A reviewer probe with a 5-millis cap admitted and committed three
sequential 3-millis requests (committed total 9), violating SPEC R6.

Repair: convert millis to USD only at the cvf-runtime adapter boundary; keep
ledger arithmetic integer. Include committed plus reserved usage in each
projection, define/reset the process-lifetime period semantics honestly, and
add sequential-commit, exact-boundary, daily/monthly, unit-conversion, and
actual-over-estimate tests.

### P4A-REV-F3 — Receipts do not bind the actual dispatched facts

The gateway trusts caller-supplied `context_digest` instead of recomputing it
from `request.context`; accepts a `ProviderResult` whose provider/model differs
from the registered request; and trusts arbitrary `endpoint_origin`. A probe
accepted all three mismatches and persisted an origin containing userinfo,
path, query, and a secret-like value. This violates SPEC R10/R11 and makes a
receipt capable of false provenance or secret leakage.

Repair: recompute and compare/bind the actual canonical context; reject result
provider/model mismatch; validate and canonicalize endpoint origin inside the
library to scheme + host only; constrain all safe identifiers. Add adversarial
tests covering each mismatch and secret-bearing origin.

### P4A-REV-F4 — Live receipt hash is not reproducible

Worker return records SHA-256
`8dd2c54731225c6d7498d2baeb6ba6c498394665c9a6c0fcc53f6695181210b7`,
while the current receipt bytes recompute to
`7a2b6e8a468e625d1cd65d515c3c857d9638183cabce2f3c42812739817396b7`.

Repair: do not alter or rerun the retained receipt. Correct the worker-return
hash and document byte/line-ending canonicalization. The old receipt remains
historical evidence for the pre-repair source only.

### P4A-REV-F5 — Required Project Knowledge/full-suite gates do not pass

The worker changed `docs/cvf/PROVIDER_GOVERNANCE.md`, a source pin of
`GOVERNANCE_BOUNDARIES.md`, but refreshed only the Project Context pins.
`python scripts/check_project_knowledge.py` is explicitly required by SPEC,
not optional. The resulting pin drift caused the integration errors. One
frozen-date Project Knowledge unit failure also exists at the base and cannot
be called PASS; it requires an explicit baseline disposition or a separately
authorized test-path repair.

Repair: refresh the authorized governance-boundary pin/date/eligibility facts
so the Project Knowledge command and integration rehearsal pass. Report the
remaining base-identical frozen-date test separately; do not edit an
unauthorized test path or relabel exit `1` as PASS.

### P4A-REV-F6 — Required runtime matrix is unverified

BUILD ran on CPython `3.11.9` with Pydantic `2.10.3`; SPEC R1 requires Python
`>=3.12` and exact Pydantic `2.10.6`. CPython `3.13.12` exists locally but has
no Pydantic installed. Packaging metadata alone is not execution evidence.

Repair/evidence: finish code repairs without installing anything. Then provide
a compliant pre-existing environment, or obtain separate authority for the
minimum package-install external effect and rerun the focused/full required
checks under Python 3.13.12/Pydantic 2.10.6. Do not widen network authority
silently.

## Repair authority and stop boundary

A separate agent may transition to `REPAIR_WORKER` and repair F1–F5 only in
the original 40 worker-owned paths. This reviewer-owned file is read-only to
the repair worker. No provider call, retry, install, new path, commit, push, or
deployment is authorized. Return an amended worker-return section with exact
evidence and `READY_FOR_REREVIEW`.

Because F1–F3 materially change the code path covered by the retained live
receipt, final governance acceptance will require a fresh post-repair provider
proof. The original Work Order authorized exactly one call and it has been
consumed. A replacement call requires a separately approved evidence
amendment after local repairs pass.

## Claim boundary

BUILD is not accepted. P4-A, P3-B and Phase 3 remain open. The retained live
receipt proves only the pre-repair worker state and must not be cited as proof
of repaired/final source.

## Independent rereview — repair round 1

- Disposition: `REVIEW_CHANGES_REQUIRED_ROUND_2`
- Reviewer provider calls / installs: `0 / 0`
- Exact status: worker paths `40/40`, reviewer path `1/1`, staged `0`.
- Focused suite: `179 passed`.
- Full suite: `2022 passed, 128 skipped, 1 failed`; exit `1`.
- Catalog, session, Project Knowledge, file-size, repository validator,
  diff-check and doctor: PASS; doctor retains only the bounded `24/1` warning.

### Finding dispositions

- `P4A-REV-F2`: **CLOSED**. The independent 5-millis probe now admits once
  then refuses twice; cumulative accounting and millis-to-USD conversion pass.
- `P4A-REV-F3`: **CLOSED**. Mismatched context is zero-call refused;
  mismatched provider/model is rejected after one attempt; unsafe userinfo is
  rejected; persisted endpoint origin excludes path/query.
- `P4A-REV-F4`: **CLOSED**. Current receipt bytes recompute to the corrected
  `7a2b6e8a...` hash and the worker return records the line-ending distinction.
- `P4A-REV-F5a` (introduced Project Knowledge drift): **CLOSED**.
  `check_project_knowledge.py` and all 85 ingest-rehearsal tests pass.
- `P4A-REV-F1`: **OPEN, repair round 2**. Keyword-name recursion is fixed,
  but the meta-contract does not validate the value shape of every supported
  keyword. Independent probes accepted malformed schemas containing a
  list-valued subschema `type`, plus string-valued `additionalProperties`,
  `minimum`, `minLength`, and `required`. Invalid constraints are therefore
  still silently ignored or misinterpreted.
- `P4A-REV-F5b` (baseline full-suite disposition): **OPEN AUTHORITY
  CHECKPOINT**. The frozen-date failure is base-identical, but SPEC requires
  the full-suite command to pass and no waiver exists. Its test path is outside
  the 40-path ceiling; repair or acceptance amendment requires new authority.
- `P4A-REV-F6`: **OPEN AUTHORITY/EVIDENCE CHECKPOINT**. Execution remains
  Python 3.11.9/Pydantic 2.10.3 rather than the SPEC runtime.

### Repair round 2 authority

A separate `REPAIR_WORKER` may repair only F1 inside the already-authorized
`validation.py` and `test_p4a_gateway_validation.py` paths. Validate the full
meta-shape of every supported keyword before matching: `type`, `properties`,
`required`, `additionalProperties`, `items`, `enum`, `oneOf`, `pattern`,
numeric bounds, and length/item bounds, rejecting booleans where numeric
integers are required. Add the reviewer probes and nested variants.

No provider call, install, new path, completion-review edit, commit, push, or
deployment is authorized. Return `READY_FOR_REREVIEW_ROUND_2`. F5b, F6, and
replacement live proof remain parked. This is repair round 2; the round-three
escalation threshold has not been reached.

## Independent rereview — repair round 2

- Disposition: `REVIEW_COST_ESCALATION_REQUIRED`
- Reviewer provider calls / installs: `0 / 0`
- Focused suite: `201 passed`.
- Session, Project Knowledge, file-size and diff checks: PASS.
- Catalog/repository validator: FAIL because the two authorized F1 files added
  46 LOC without an authorized catalog regeneration.

The assigned round-2 probes now fail closed, but the same F1 meta-schema root
cause remains incomplete. Independent probes accepted invalid schemas with
negative `minLength`/`minItems`, duplicate `required`/`enum` members,
non-string `properties` names, and non-finite numeric bounds. The first two
cases directly widen acceptance; the others show the promised complete
meta-shape validation is still not implemented.

Continuing would be repair round 3 without an independent new root cause.
Under `AGENTS.md` Governance Latency and Approval Continuity, the reviewer
therefore stops and records `REVIEW_COST_ESCALATION_REQUIRED`. No further
repair is authorized by this record.

Before work resumes, the orchestrator/operator must approve one consolidated
amendment that resolves, rather than serially rediscovers:

1. complete supported-subset meta-schema validation, including non-negative
   size bounds, unique/string member sets, string property names and finite
   numeric bounds;
2. catalog regeneration and Project Knowledge pin refresh caused by the final
   source/test LOC;
3. F5b's out-of-ceiling frozen-date test disposition;
4. F6's compliant Python/Pydantic environment and any package-install effect;
5. exactly one replacement post-repair live proof, because the retained call
   covers pre-repair source only.

P4-A, P3-B and Phase 3 remain open. No commit or push is authorized.

## Independent rereview — unapproved round-3 execution

- Disposition: `REVIEW_BLOCKED_AUTHORITY_VIOLATION`
- Reviewer provider calls / installs: `0 / 0`
- Focused P4-A suite: `210 passed`.
- Full suite: `2054 passed, 128 skipped, 1 warning`.
- Session, Project Knowledge, catalog, file-size, repository validator,
  diff-check and doctor: PASS; doctor retains only the bounded `24/1` warning.
- Staged paths: `0`.

Technical probes show the final F1 meta-shape cases now fail closed and the
formerly frozen-date test passes. However, the canonical state and handoff
still said `STOP: REVIEW_COST_ESCALATION_REQUIRED`, no consolidated amendment
or successor Work Order exists, and `tests/unit/test_project_knowledge_pack.py`
was modified outside the original 40-path worker ceiling. A chat disposition
of `READY_FOR_REVIEW` requests review; it does not retroactively grant BUILD,
install, provider-call, path-ceiling, or acceptance authority. The worker
return also remains stale: it still claims no out-of-ceiling edit and reports
the prior 179-test/frozen-date state.

Additional open evidence findings:

1. `P4A-REV-F4` is reopened: the receipt's current raw SHA-256 is
   `7ed61ca10d5267fd6512296a7ab01e956328868a12f70d6f4460ae60ff90b4ac`,
   while the completion review and worker return claim `7a2b6e8a...`.
2. `P4A-REV-F6` remains open: the exercised environment is Python 3.11.9 /
   Pydantic 2.10.3; Python 3.13.12 exists but cannot import Pydantic.
3. No replacement post-repair live provider proof exists; the retained
   receipt still covers pre-repair source only.

No technical green result is accepted as a governance `REVIEW_PASS` while
these authority and evidence defects remain. Preserve the current worktree;
do not commit, push, install, call a provider, or perform further repair until
the operator explicitly chooses ratification-and-completion or rejection /
quarantine of the unapproved changes.

## Final independent review — ratified Amendment 2

- Disposition: `REVIEW_PASS`
- Findings / waivers: `NONE / NONE`
- Reviewer provider calls / installs: `0 / 0`
- Exact changed set: DESIGN worker paths `40/40`, reviewer path `1/1`,
  ratified F5b path `1/1`; exact `42`, missing/extra `0/0`, staged `0`.
- Compliant runtime: Python `3.13.12`, Pydantic `2.10.6` at
  `C:\Users\DELL\AppData\Local\cvf-p4a-py313-venv`.
- Validation suite: `63 passed`; focused P4-A suite: `210 passed`.
- Full suite on the compliant runtime: `2054 passed, 128 skipped`, no failure.
- Real-gate identity/order probes: `2 passed`.
- Session, Project Knowledge, catalog, file-size, repository validator,
  JSON parse, diff-check and doctor: PASS; doctor retains only the bounded
  legacy-catalog note (`24/1`).

The operator explicitly ratified the final F1/catalog/F5b changes and the
F5b path-ceiling expansion. Independent recomputation confirms complete
fail-closed supported-subset meta-schema validation, catalog totals of 24
modules / 26005 LOC, and the `MODULE_REGISTRY.json` source pin
`6da02a9b9124e84676fedc42f5eb8954bb7a4b73ef37454dba8380e7b09b4522`.

F4 is closed: the replacement receipt hashes to
`c177ee398667f6f649dc94b29420da1eaaa11933c6426e67401ab087679e18b9`
after universal-newline canonicalization and
`ce86a861a8eba7a38fad2c8fae578ebac3bceabf06b9914c7fb85b6759e78105`
as raw CRLF bytes. F6 is closed by the compliant runtime run above. The
replacement receipt is valid JSON, records HTTP 200 and exactly one physical /
adapter / gateway attempt; all six refusal cases record zero attempts; the
recorded order is data-scope, cost, termination before provider dispatch; no
Bearer, Authorization-header or secret-key-value marker is persisted.

P4-A is accepted `CLOSED_BOUNDED`. P3-B closes only for this reviewed gateway /
live-evidence library call-site boundary, and Phase 3 may be recorded `6/6`
within that same boundary because the full suite and repository gates retain
all existing Phase 3 evidence. This does not prove an application/API caller,
durable accounting/audit, production provider adapter, RAG, deployment or
production readiness. P4-A2 and P4-B remain parked. Push is not authorized.

## FREEZE reconciliation recheck — 2026-08-21

Role transition: `REVIEWER → CLOSER`. Final truth-surface and continuity sync
preserved the exact ratified 42-path set with staged zero. Session state,
Project Knowledge, catalog, file-size, repository validator, changed-JSON
parse, diff-check and source-pin equality all PASS. Workspace doctor is
`PASS WITH NOTE` (`24/1`, sole bounded legacy-catalog warning); Core HEAD,
origin/main, manifest and local binding remain equal at `7d9f360a...` and the
Core worktree is clean. Receipt raw/universal hashes and compliant runtime
remain exact. No additional provider call or package install occurred during
review/FREEZE. Final disposition remains `FREEZE / CLOSED_BOUNDED`, findings /
waivers `NONE / NONE`; local closure commit is handed to `COMMIT_STEWARD`, and
push remains unauthorized.
