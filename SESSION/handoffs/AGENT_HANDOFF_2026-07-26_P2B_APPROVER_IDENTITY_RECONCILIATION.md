# Agent Handoff — 2026-07-26 (P2B Approver Identity Reconciliation)

## Disposition

- Tranche: `P2B-APPROVER-IDENTITY-RECONCILIATION`
- Control-chain phase: `FREEZE`
- Status: **CLOSED_BOUNDED**
- Risk: R2 — changes the load-bearing approval control and requires live
  provider-backed governance evidence
- BUILD commit: `9376ddb056ef83e7d41f45ca951b6c13a4169c7f`
  (`REVIEW_PASS`, 38 paths), pushed to `origin/main`
- Independent reviewer, commit steward and closer: Codex

## Authorization receipts

- Original C1:
  `f98f29e145fa002be070e9d44520d20f0f82dcb3`, exactly the ADR, SPEC and
  WORK_ORDER; retained unchanged.
- Authorization review revision 1: F1–F8 repaired without waiver.
- Authorization review revision 2: F9–F13 repaired without waiver:
  order-invariant quorum matching; fresh BUILD baseline; the bounded untracked
  assessment exception; exact doctor-note gate; separate C1b.
- C1b:
  `d3bb1ccce340d2a102064d57cee6136147ee5c0d`, exactly the same three
  authorization paths, independently `REVIEW_PASS`, rehearsed and pushed;
  `HEAD == origin/main` at the time of its push.
- C1b rehearsal: full suite `306 passed`; repository validator,
  `check_session_state.py`, `generate_catalog.py --check`,
  `check_file_size.py`, and `git diff --check` PASS.
- Doctor: `RESULT: PASS WITH NOTE (24 passed, 1 warning(s))`; 24 checks PASS,
  zero FAIL, sole warning
  `LEGACY_PROJECT: governed downstream catalog kit not present`.
- G1c: independent re-review of pushed C1b = `REVIEW_PASS`.
- G3: **PASS**. Codex explicitly approves the amended WORK_ORDER intact under
  the operator-delegated approval authority granted on 2026-07-26.

## Closed authorization and BUILD chain

- C1: `f98f29e145fa002be070e9d44520d20f0f82dcb3`
- C1b: `d3bb1ccce340d2a102064d57cee6136147ee5c0d`
- C2: `cdbbe5b1d79c772f3523d4bb0e5d4ab639e501ce`
- C2b authorization amendment 3:
  `62c740ad950d970861f5c084cb3bba3dec73e4e6`
- C3 BUILD after independent `REVIEW_PASS`:
  `9376ddb056ef83e7d41f45ca951b6c13a4169c7f`

The BUILD removed caller-supplied approver names and deleted
`known-principals.yaml` as runtime authority. An authenticated user now creates
a durable approval receipt through JWT-protected `POST /approvals`; current
authority is re-derived from the active `users` row. Receipts are bound to the
exact six-field scope `(record_type, record_id, action, target_version,
risk_class, payload_digest)`. Quorum matching is deterministic,
order-invariant and self-approval-safe. Task creation uses durable
`TaskCreationIntent` payload digests. Receipt, intent, mutation and audit
behavior is atomic across the in-memory and SQL ledger implementations.

## Independent review evidence

- Focused reconciliation suite: `116 passed`.
- Root full suite: `369 passed, 1 warning`.
- Repository validator, session-state check, catalog verification, file-size
  guard, migration discovery, secret scan and diff check: PASS.
- Workspace doctor: `PASS WITH NOTE (24 passed, 1 warning)`; the only warning
  is the bounded legacy catalog-kit note.
- Independent F16 probe: a non-null Event digest could not consume a null-scope
  receipt; HTTP `409`.
- Live Alibaba evidence: `qwen3.7-max`, HTTP `200`, expected token
  `CVF_APPROVAL_EVIDENCE_OK`; zero calls for every refusal and exactly one call
  after genuine JWT-backed quorum. Sanitized receipt:
  `docs/decisions/P2B_APPROVER_IDENTITY_LIVE_EVIDENCE_RECEIPT.md`.
- AC-21 revert rehearsal restored the exact parent tree and the `306 passed,
  1 warning` baseline, then removed and pruned the temporary worktree.
- Final Git truth at C3 review: `HEAD == origin/main ==
  9376ddb056ef83e7d41f45ca951b6c13a4169c7f`.

## Claim boundary

This closure fixes High Finding #4 only within the stated authenticated,
scope-bound approval-receipt boundary. It does not mean every historical
finding or every CVF control is fixed. It does not prove that production
endpoints invoke a provider; none do. It does not add refresh/revocation or an
admin provisioning flow. It does not verify PostgreSQL live: the Phase 1 exit
gate remains open until an actual migration-created PostgreSQL round-trip is
run and reviewed.

The preserved untracked assessment remains outside this tranche and untouched:
`docs/decisions/ASSESSMENT_2026-07-23_OPERATIONS_WORKSPACE_REPOSITIONING.md`,
SHA-256
`168ea2c7a67a31bae50c9e4dbe78c2273a692f3a82a1074585e1bdb89b70fde2`.

## Next governed move

Start a fresh `INTAKE` for the separate
`CVF-FILE-SPLIT-GUARD-HARDENING` tranche. It must define repository-enforced
split-file guards rather than rely on agent memory. Do not design, authorize or
implement that tranche inside this C4 closure.

After that tranche reaches its own closure, open a distinct PostgreSQL live
round-trip tranche to satisfy the Phase 1 exit gate. P2-A incidents/handovers
remains the next business-delivery lane, deferred behind those two
operator-selected governance/exit-gate moves.
