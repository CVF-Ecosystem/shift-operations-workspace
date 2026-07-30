# Agent Handoff — Message Admission and Trust Repair

## Disposition

- Tranche: `MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30`
- Control-chain phase: `FREEZE`
- Risk: `R2`
- Active role: `ORCHESTRATOR`
- Implementation worker: `Claude Code 2.1.215`
- Status: `FREEZE / CLOSED_BOUNDED — C3 PUSHED`

## Settled predecessor

`SHIFT-CREATE-ADMISSION-REPAIR-2026-07-29` is `FREEZE /
CLOSED_BOUNDED`:

- C3 `3f9e456d129075e347d986af3b31d35f4d00afb9`;
- C4 `56e2f3ba871541e1fb80302cf7aa39b1b84a623b`;
- `SCR-BUILD-REV-F1..F3` closed without waiver;
- `HEAD == origin/main` was clean before this intake opened.

Do not reopen or batch predecessor work into this tranche.

## Intake evidence

Source inspection and ephemeral local probes independently confirmed:

- anonymous `POST /messages` returns HTTP 200;
- caller-controlled `sender_id` and `source="INTERNAL"` are accepted
  unchanged;
- the router calls `ledger.add_message(...)` directly;
- InMemoryLedger persists the message with zero audit records;
- SqlLedger message persistence raises `NotImplementedError`;
- Integration Edge verifies HMAC and deduplicates its generic webhook but
  does not yet persist a raw envelope, canonicalize, map sender identity,
  route to a shift/fallback queue, or hand a canonical message to
  workspace-api;
- the minimal operations-domain/database Message shape and Canonical Message
  Contract are materially different.

No provider call, external webhook, secret read, Docker/PostgreSQL run,
production data access, stage, commit, or push occurred during the probe.

## DESIGN decision

Canonical ADR:
`docs/decisions/ADR_2026-07-30_MESSAGE_ADMISSION_TRUST_REPAIR.md`.

The existing `POST /messages` is classified as an authenticated internal-user
command only:

- require verified JWT and `message.create` at minimum role `operator`;
- derive `sender_id` from `principal.user_id` and fix source to `INTERNAL`;
- treat legacy sender/source fields only as optional matching assertions;
- route through one MessageService transaction that persists the message and
  exact actor-bound audit;
- reject unknown/frozen shifts and prove InMemory/SQLite/PostgreSQL parity;
- use the existing minimal table/domain model, with no migration and no claim
  of Canonical Message Contract equivalence.

External ingestion is a separate, later Integration Edge tranche. It requires
dedicated service identity, verified canonical provenance, raw-envelope
ownership, dedupe/replay, identity mapping and shift-or-fallback routing.
Provider payload and external canonical envelopes must never use the internal
`POST /messages` route.

No Integration Edge, canonical schema, channel adapter, identity-mapping,
conversation-routing, quarantine, attachment or fallback implementation is
included in this tranche.

## DESIGN findings disposition

- `MAR-INTAKE-F1 ENTRYPOINT_CLASSIFICATION`;
- `MAR-INTAKE-F2 SENDER_AUTHORITY`;
- `MAR-INTAKE-F3 EDGE_TO_CORE_HANDOFF`;
- `MAR-INTAKE-F4 MODEL_CONTRACT_DRIFT`;
- `MAR-INTAKE-F5 ROUTING_AND_SHIFT_BINDING`;
- `MAR-INTAKE-F6 DURABLE_PARITY`;
- `MAR-INTAKE-F7 GOVERNANCE_ACTIONS`;
- `MAR-INTAKE-F8 FAILURE_AND_HTTP_CONTRACT`;
- `MAR-INTAKE-F9 LIVE_EVIDENCE`.

All nine findings are resolved architecturally by the ADR. Their behavior and
exact HTTP/test contracts must be frozen in SPEC before any work order or
implementation can exist.

## Next governed move

SPEC `MESSAGE_ADMISSION_TRUST_REPAIR_SPEC.md` is `REVIEW_PASS` after
`MAR-SPEC-REV-F1..F3` closed without waiver. Work Order
`MESSAGE_ADMISSION_TRUST_REPAIR_WORK_ORDER.md` is authorization
`REVIEW_PASS` after `MAR-WO-AUTH-F1..F3` closed without waiver.
Amendment 1 closes `MAR-PREBUILD-F1 C2_G6_ORDER_CYCLE` without waiver: C2
records the G6 requirement, then G6 runs from pushed C2 and its result belongs
in the worker return/build receipt.

Operator assignment is acknowledged: Claude Code `2.1.215` is the sole
`IMPLEMENTATION_WORKER`/bounded `REPAIR_WORKER`; Codex remains independent
reviewer, commit steward and closer. Authorization commits:

- C1 `a01e64af022289e0bbc5ad9142a4ef9099e80345`;
- Amendment 1 `9d60508`.

After this four-path C2 is pushed, Claude must rehydrate continuity and run G6
before the first BUILD edit. If G6 passes, Claude may change exactly the 29 C3
paths in the reviewed Work Order and must return
`READY_FOR_INDEPENDENT_MESSAGE_ADMISSION_BUILD_REVIEW`.

Claude must not review, stage, commit, push or FREEZE. Codex must not implement
or silently repair Claude's BUILD.

No BUILD, source/test/permission/schema/migration edit, provider call or
Docker/PostgreSQL BUILD run is authorized before this C2 is pushed and G6
passes.

## Independent BUILD review and repair authorization

The implementation worker returned
`READY_FOR_INDEPENDENT_MESSAGE_ADMISSION_BUILD_REVIEW`. Codex independently
reviewed source, receipts and executable evidence and returned
`REVIEW_CHANGES_REQUIRED`:

- `MAR-BUILD-REV-F1 FULL_REGRESSION_AND_CEILING_GAP`;
- `MAR-BUILD-REV-F2 ENDPOINT_PORT_SECRET_LEAK`;
- `MAR-BUILD-REV-F3 REFUSAL_AUDIT_FALSE_PASS`;
- `MAR-BUILD-REV-F4 ROLLBACK_AND_POSTGRES_ASSERTION_GAPS`;
- `MAR-BUILD-REV-F5 RECEIPT_AND_CATALOG_TRUTH_DRIFT`.

Independent evidence: exact focused Work Order command `106 passed`; full
suite `782 passed / 76 skipped / 1 failed`; repository/catalog/session/
file-size/JSON/diff gates PASS; doctor PASS WITH NOTE 24/1; exact 29-path
dirty set and protected-boundary zero diff. Adversarial no-network probes
proved an invalid secret-bearing endpoint port escaped in a raw `ValueError`
and seven injected refusal audits still produced seven PASS outcomes.

Amendment 2 is pushed at `8d5c085`. It adds exactly
`tests/unit/test_shift_create_openapi_contract.py` as path 30, invalidates
the current live receipt as closure evidence, and requires fresh PostgreSQL
and provider proof only after all repaired non-live tests pass.

Claude Code `2.1.215` may now resume only as bounded `REPAIR_WORKER` against
the pushed Amendment 2 and exact 30-path ceiling. Claude must preserve the
dirty BUILD, must not stage/commit/push/review/FREEZE, and must stop at
`READY_FOR_INDEPENDENT_MESSAGE_ADMISSION_BUILD_RE_REVIEW`. Codex remains
independent reviewer and commit steward.

## C3 repair history, independent final review and FREEZE

- BUILD initially returned exactly 29 authorized paths with zero staged paths.
- Independent review returned `REVIEW_CHANGES_REQUIRED` for
  `MAR-BUILD-REV-F1..F5`; Amendment 2 `8d5c085` added only historical OpenAPI
  test path 30 and authorized bounded repair.
- Repair required multiple review rounds. F2 closed three distinct endpoint
  failure branches without waiver: parse/port failures inside `call_provider`,
  a non-numeric secret-bearing port, and finally malformed IPv6 escaping from
  `runner.main()` through `safe_endpoint_description` before the sanitized
  provider boundary.
- The final independent facade-level adversarial review verified no sentinel
  in stdout, stderr or receipt. Focused suite: `82 passed / 7 skipped`; full
  non-live suite: `789 passed / 76 skipped`.
- The prior repair-round disposable PostgreSQL 16 evidence was retained
  truthfully at `66 passed`, migrations `21/0` then `17/4`, exact cleanup. It
  was not rerun in the final F2-only round because no PostgreSQL path changed.
- Fresh provider evidence was regenerated after the final F2 fix: seven real
  HTTP/JWT refusal cases made zero provider calls; the admitted path persisted
  exactly one message and exact actor-bound audit before exactly one Alibaba
  `qwen3.7-max` call returned HTTP 200.
- Repository, catalog, session, file-size, diff and workspace-doctor gates
  passed; doctor carried only the bounded legacy warning (24/1); no
  `cvf-pg-live-*` residue remained.
- C3 `ab92f51be5b00740f2316b6e1b1c81aa186c753f` contains exactly the 30
  authorized paths, is pushed, and leaves `HEAD == origin/main`.

Disposition: `FREEZE / CLOSED_BOUNDED`.

Permitted claim only:

> Internal `POST /messages` requires a verified JWT, derives sender/source
> authority server-side, enforces `message.create`, and atomically persists a
> shift-bound internal Message with an actor-bound audit record on the proven
> backends.

External/channel ingestion, Canonical Message Contract completion,
raw-envelope/replay/identity-mapping/fallback/quarantine/attachment handling,
assignment/tenant/data_scope authorization and production PostgreSQL readiness
remain open. The next tranche must be selected by the operator and begin at
fresh INTAKE. No DESIGN, SPEC, WORK_ORDER, BUILD, provider-call, commit or
mutation authority carries forward.
