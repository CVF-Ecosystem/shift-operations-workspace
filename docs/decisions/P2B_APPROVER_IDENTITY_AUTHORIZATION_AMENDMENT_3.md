# P2-B Approver Identity Reconciliation — Authorization Amendment 3

- Amendment id: `P2B-APPROVER-IDENTITY-AUTHORIZATION-AMENDMENT-3`
- Tranche: `P2B-APPROVER-IDENTITY-RECONCILIATION`
- Status: **PROPOSED — addressed pending independent review.** Nothing below
  is "resolved" or "closed" until independent re-review returns `REVIEW_PASS`
  and this amendment is committed (as **C2b**, §3) and re-reviewed again.
- Amends: `docs/decisions/ADR_2026-07-23_P2B_APPROVER_IDENTITY_RECONCILIATION.md`,
  `docs/specs/P2B_APPROVER_IDENTITY_RECONCILIATION_SPEC.md`,
  `docs/work_orders/P2B_APPROVER_IDENTITY_RECONCILIATION_WORK_ORDER.md`. Those
  three files carry only short operative pointers/requirements; this document
  carries the rationale, the finding table, evidence, and transition history.
- Context: independent review examined the **uncommitted C3 BUILD
  implementation** (built against the SPEC as it stood after C1b). **C2**
  (pre-BUILD continuity) already landed at
  `cdbbe5b1d79c772f3523d4bb0e5d4ab639e501ce` — this amendment does not touch,
  rewrite, or recreate C2. C3 itself remains uncommitted and paused; this
  amendment changes only what the resumed C3 must additionally satisfy.

## 1. Findings (stable identities — do not renumber)

| Finding | Description |
|---|---|
| **F14** | Full-suite/OpenAPI allowlist conflict — this tranche's authorized API changes invalidate the pinned P1-B-era OpenAPI golden hash in `tests/unit/test_operations_domain_serialization.py`, which sits outside the 39-path C3 ceiling. |
| **F15** | Post-hoc self-approval false denial — the quorum matcher can compute one arbitrary perfect matching and reject the whole quorum because *that* matching happens to be confirmer-only, even when a different, non-confirmer-only matching exists over the same receipts. |
| **F16** | Incomplete six-field receipt-scope matching — `list_approval_receipts_for` filters only `record_type, record_id, action, target_version`, omitting `risk_class`/`payload_digest` from the match. |
| **F17** | Pinned API status/response-shape mismatch — the three new endpoints' actual HTTP responses are not verified exactly against SPEC §5.4 (extra/missing fields, status-code-only checks). |
| **F18** | Incomplete AC-22 **and** AC-23 coverage. Subdivided: **F18a** — AC-22's dual-backend atomic-rollback failure-injection is not proven independently on each backend. **F18b** — AC-23's permutation coverage is proven only at the algorithm level (`test_gates_unit.py`), not at service/HTTP level for both R3 and R4 on both backends. |
| **F19** | InMemory/SQL receipt-uniqueness mismatch — `InMemoryLedger.add_approval_receipt` does not enforce the `(record_type, record_id, action, target_version, approver_id)` key SqlLedger's real UNIQUE constraint enforces, breaking R2.4 idempotency on that backend. |
| **F20** | Live evidence bypasses verified JWT and lacks an overall outcome — the evidence runner establishes approver identity via a manually constructed `Principal(...)`, not a real, verified JWT through the authenticated-request path, and the receipt has no single, explicit, top-level `Overall outcome: PASS/FAIL/BLOCKED` line. |

## 2. Rationale and required behaviour, per finding

**F14.** The golden hash is a P1-B-era snapshot asserting "the API contract is
unchanged" — a claim this tranche's authorized, deliberate contract changes
(new `POST /approvals`, `POST /tasks/creation-intents`,
`GET /tasks/creation-intents/{intent_id}`, `extra="forbid"` on the three
governed inputs) necessarily break. This is a false failure, not a
regression, but the test file sits outside the 39-path ceiling, so touching
it requires an explicit ceiling amendment rather than silent widening.
**Required:** raise the C3 ceiling to 40 paths, admitting exactly one
narrowly-scoped edit — updating the golden hash constant and adding new
exact-shape assertions for the three new endpoints/schemas only. No
pre-existing, unrelated assertion (for an endpoint/schema this tranche does
not touch) may be loosened, weakened, or removed.

**F15.** The self-approval guard (R3.4) must be evaluated **within** the same
order-invariant matching search (R3.6) that decides role-authority quorum,
not as a separate post-hoc check applied to whichever matching a naive search
happens to return first. **Required:** the gate is satisfied iff there
**exists** a perfect matching whose distinct matched approvers are not the
confirmer alone — even if a *different* perfect matching over the same
receipts (one that happens to route every seat through the confirmer) would
not satisfy R3.4. A matcher that finds only a confirmer-only matching and
stops, without searching for a non-confirmer-only alternative that exists, is
non-compliant. R3.3/R3.4 are not weakened by this — a quorum still cannot be
satisfied by the confirmer alone.

**F16.** "Matching the target's current scope" (R5.1) means the complete
six-field tuple `(record_type, record_id, action, target_version, risk_class,
payload_digest)`, not the four-field subset the implementation currently
filters on. A receipt whose first four fields match but whose `risk_class` or
`payload_digest` does not match the target's current value must not count
toward quorum — filtering on four fields is a latent correctness gap, even
though today's Event/Task scopes rarely change `risk_class` post-creation.

**F17.** Every schema pinned in SPEC §5.4 is exact and exhaustive: a response
must contain precisely the listed fields, no more, no fewer. Verification
must diff the response body's key set against the pinned schema exactly — a
passing HTTP status code alone is not evidence of contract compliance.

**F18a.** AC-22's failure-injection proof (intent + `task.creation_intent.
create` audit committing atomically, or neither on injected failure) must run
as an independent, explicit case **per backend** — InMemory and SQL each
individually asserted — mirroring AC-19's existing pattern exactly. A single
test parametrized to silently exercise only one backend does not satisfy this
AC.

**F18b.** AC-23's permutation coverage (every ordering of a valid quorum's
receipts PASSes) must run at the **service/HTTP level**, for **both** R3 and
R4 quorums, on **both** backends — in addition to, never instead of, the
existing algorithm-level unit coverage in `test_gates_unit.py`. Covering only
one risk class, only one backend, or only the algorithm level does not
satisfy this AC.

**F19.** `InMemoryLedger.add_approval_receipt` must enforce the identical
uniqueness key SqlLedger's `UNIQUE(record_type, record_id, action,
target_version, approver_id)` constraint enforces: a matching insert must
return the existing receipt (feeding R2.4's idempotent `200` path on **both**
backends), never create a second row. This mirrors the backend-symmetry
principle R9.6 already established for `add_task`'s duplicate-`task_id`
rejection.

**F20.** Every approver identity in the live-evidence run must be established
by minting a real JWT (`create_access_token`) and driving it through the
actual authenticated-request path (`get_principal`, e.g. via an HTTP
`Authorization` header) — a manually constructed `Principal(user_id=...,
role=...)` object standing in for that verification step does not satisfy
AC-16. The receipt document must additionally carry one explicit, top-level
line labeled `Overall outcome: PASS` / `FAIL` / `BLOCKED`, distinct from the
existing per-case and per-call outcome fields.

## 3. Post-C2 amendment lifecycle (this amendment's own commit path)

This amendment is authored and reviewed as its own authorization-repair
round, distinct from C1b and from C3 (which remains paused, uncommitted,
unmodified by this round):

- **G7** — Independent review of this uncommitted amendment (the four files
  listed in the header) → `REVIEW_PASS` / `REVIEW_CHANGES_REQUIRED`.
- **G7b** — COMMIT_STEWARD commits and pushes **C2b** — exactly the four
  paths in the header, zero implementation/test/migration/catalog/continuity
  paths — only after **G7** returns `REVIEW_PASS`.
- **G7c** — Independent re-review of the pushed C2b and explicit operator
  approval. Nothing beyond this amendment is authorized to change as a result
  of G7c; it does not re-open F1–F13 or the already-committed C1/C1b/C2.
- **G7d — repair-resumption gate.** Before C3 may be touched again:
  `HEAD == origin/main` at C2b; nothing staged; the three canonical
  authorization files and this amendment are clean (match the committed
  C2b tree exactly); the paused C3 changed set and the one preserved
  untracked assessment file are the **only** remaining worktree changes; and
  Claude explicitly declares the **REPAIR_WORKER** role before making any
  further edit to C3's source/test/migration content. **G7d does not demand
  an absolututely-clean worktree the way the original G6 did** — BUILD had
  already started before these findings surfaced, so the paused C3 diff is
  expected and permitted at G7d; G6 itself is unchanged and remains the gate
  that ran once, before BUILD's first edit.

WORK_ORDER §7/§8/§10 carry the authoritative gate text and commit-plan row;
this section records the rationale for why they exist.

## 4. Historical C2 correction

The WORK_ORDER's C2 allowlist (§11) named a handoff file with the wrong date
(`2026-07-23`). C2 already landed at `cdbbe5b1d79c772f3523d4bb0e5d4ab639e501ce`
under the corrected name
`SESSION/handoffs/AGENT_HANDOFF_2026-07-26_P2B_APPROVER_IDENTITY_RECONCILIATION.md`.
This amendment corrects the WORK_ORDER's own record of that fact; it does
**not** rewrite, amend, or recreate the C2 commit itself.

## 5. Cross-reference — where each finding's operative requirement lives

| Finding | Operative requirement |
|---|---|
| F14 | WORK_ORDER §3.11 (40-path ceiling, narrow authorization); SPEC R7.3 |
| F15 | SPEC R3.7 |
| F16 | SPEC R5.1 (amended) |
| F17 | SPEC §5.4 (amended), §9 |
| F18a | SPEC AC-22 (amended), WORK_ORDER §6 |
| F18b | SPEC AC-23 (amended), WORK_ORDER §6 |
| F19 | SPEC R8.2a |
| F20 | SPEC AC-16 (amended), §7 (amended) |

## 6. Boundaries unchanged

No PostgreSQL live testing is introduced or required by this amendment or by
this P2-B tranche generally — SQLite + `operations_ledger.tables.metadata` +
schema parity remain the verification mechanism (ADR §4.5, SPEC AC-20);
PostgreSQL stays **NOT LIVE VERIFIED**. No change to auth issuance/refresh/
revocation, admin provisioning, lanes 3–4 (incidents/handovers, frontend), or
the claim boundary in ADR §7.1/§8.2. F1–F13 are not reopened.
