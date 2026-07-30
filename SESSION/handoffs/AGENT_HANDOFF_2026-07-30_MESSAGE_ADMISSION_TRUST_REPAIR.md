# Agent Handoff — Message Admission and Trust Repair

## Disposition

- Tranche: `MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30`
- Control-chain phase: `BUILD — PRE-G6`
- Risk: `R2`
- Active role: `ORCHESTRATOR / INDEPENDENT_REVIEWER / COMMIT_STEWARD`
- Implementation worker: `Claude Code 2.1.215`
- Status: `C2 PRE-BUILD ACKNOWLEDGED — G6 REQUIRED BEFORE FIRST BUILD EDIT`

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
