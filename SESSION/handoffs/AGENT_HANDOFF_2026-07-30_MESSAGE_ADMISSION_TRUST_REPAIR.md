# Agent Handoff — Message Admission and Trust Repair

## Disposition

- Tranche: `MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30`
- Control-chain phase: `INTAKE`
- Risk: `R2`
- Active role: `ORCHESTRATOR / INTAKE_AUTHOR`
- Status: `INTAKE RECORDED — DESIGN NEXT; BUILD NOT AUTHORIZED`

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

## Required DESIGN findings

- `MAR-INTAKE-F1 ENTRYPOINT_CLASSIFICATION`;
- `MAR-INTAKE-F2 SENDER_AUTHORITY`;
- `MAR-INTAKE-F3 EDGE_TO_CORE_HANDOFF`;
- `MAR-INTAKE-F4 MODEL_CONTRACT_DRIFT`;
- `MAR-INTAKE-F5 ROUTING_AND_SHIFT_BINDING`;
- `MAR-INTAKE-F6 DURABLE_PARITY`;
- `MAR-INTAKE-F7 GOVERNANCE_ACTIONS`;
- `MAR-INTAKE-F8 FAILURE_AND_HTTP_CONTRACT`;
- `MAR-INTAKE-F9 LIVE_EVIDENCE`.

Canonical intake:
`docs/decisions/INTAKE_2026-07-30_MESSAGE_ADMISSION_TRUST_REPAIR.md`.

## Next governed move

Author DESIGN only. DESIGN must explicitly classify internal-user versus
external-channel entry points, bind sender/source authority to verified
identity/provenance, decide the Integration Edge handoff, reconcile model/
contract/persistence truth, and bound migration/fallback/quarantine scope.

No BUILD, source/test/schema/migration/contract edit, provider call,
Docker/PostgreSQL run, stage, commit, or push authority exists from this
handoff.
