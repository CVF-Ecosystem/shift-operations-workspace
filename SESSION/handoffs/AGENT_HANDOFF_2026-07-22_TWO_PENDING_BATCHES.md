# Agent Handoff — 2026-07-22 (Two pending uncommitted batches — checkpoint)

Provider-neutral handoff. Continues from
[`AGENT_HANDOFF_2026-07-22_P2A_CUSTOMER_REQUEST.md`](AGENT_HANDOFF_2026-07-22_P2A_CUSTOMER_REQUEST.md).

- **Mode:** cvf_enforcement_buildout
- **Active role for this handoff's author:** REPAIR_WORKER (bootstrap-continuity
  batch). Next required role: independent REVIEWER (of the repaired
  bootstrap-continuity batch).
- **Startup ack:** mode=cvf_enforcement_buildout; active handoff=this file;
  next allowed move=see "Next allowed move" below; parked
  checkpoint=bootstrap-continuity commit plus final session sync pending;
  customer_request is committed at `0429c4a`; every P2-A(remaining)/P2-B/P2-C
  item stays parked until continuity records both batch commits.

## Why this handoff exists

Two separate, unrelated-to-each-other batches of work are currently
**uncommitted** in this working tree at the same time. A prior version of
`SESSION/ACTIVE_SESSION_STATE.json`'s `next_allowed_move` still described only
the P2-A-CUSTOMER-REQUEST tranche as the checkpoint and implicitly allowed
moving straight to P2-A(remaining)/P2-B/P2-C — which would be wrong while two
batches sit undispositioned. This handoff and the `next_allowed_move` update
that points here correct that.

## Batch 1 — customer_request repair (committed)

Five findings from an independent review of the P2-A-CUSTOMER-REQUEST tranche
(InMemory alias-bypass, source_message_id backend divergence, malformed
promised_at 500, schema-parity status-CHECK one-directional gap, missing
domain_lock negative test) were repaired by a REPAIR_WORKER pass. A second
independent review confirmed:

- 35/35 targeted tests passed
- Full suite: 149 passed
- Repository validation: PASS
- Catalog verification: PASS
- Session-state checker: PASS
- No blocking code defect found

**Disposition: `COMMITTED_REVIEW_PASS` at `0429c4a`.** This batch is done,
independently reviewed, and committed separately. Do not modify this code
again unless a new regression is demonstrated. Files touched by this batch (unchanged by the
bootstrap-continuity work below):
`apps/workspace-api/src/workspace_api/api/customer_requests/router.py`,
`apps/workspace-api/src/workspace_api/application/customer_request_service.py`,
`apps/workspace-api/src/workspace_api/infrastructure/repository.py`,
`docs/catalog/MODULE_CATALOG.md`, `docs/catalog/MODULE_REGISTRY.json`,
`docs/cvf/CVF_CONTROL_MAPPING.md`,
`packages/operations-ledger/src/operations_ledger/ledger.py`,
`packages/operations-ledger/src/operations_ledger/sql_ledger.py`,
`tests/integration/test_schema_parity_types_and_checks.py`,
`tests/cvf/test_customer_request_repair.py` (new).

## Batch 2 — bootstrap-continuity backfill (independent review: CHANGES_REQUIRED, then repaired)

A separate task audited and backfilled this project onto the CVF Project
Bootstrap Continuity Contract (`.cvf/manifest.json`, `.cvf/policy.json`,
`AGENTS.md`, `CVF_SESSION_MEMORY.md` pointer, `docs/INDEX.md`,
`knowledge/README.md`, `docs/specs/README.md`, `docs/work_orders/README.md`,
`docs/CVF_BOOTSTRAP_LOG_2026-07-22.md`, plus additive-only merges into
`CONTRIBUTING.md` and `SESSION/ACTIVE_SESSION_STATE.json`). An independent
review returned `REVIEW_CHANGES_REQUIRED` with five findings:

1. Unresolved `{{CVF_CORE_PATH}}` template tokens in `AGENTS.md` — repaired,
   now resolves `cvfCorePath` from `.cvf/manifest.json` instead of a
   hardcoded or literal-token path.
2. `CVF_SESSION_MEMORY.md` falsely claimed no `CVF_SESSION/` directory
   exists — repaired: it now states plainly that
   `CVF_SESSION/ACTIVE_SESSION_STATE.json` exists as a non-canonical
   compatibility mirror, never a second canonical source.
3. `docs/CVF_BOOTSTRAP_LOG_2026-07-22.md` contradicted the actual worktree
   (said `CVF_SESSION/` was not created, doctor result left as an unchecked
   placeholder) — repaired: now records the compatibility mirror's real
   existence/purpose and the actual doctor result (FAIL, 21/22 — see below).
4. Canonical continuity allowed moving straight to new roadmap work while
   two batches were undispositioned — repaired by this handoff and the
   `next_allowed_move`/mirror updates it accompanies.
5. The compatibility mirror had no deterministic drift check, only prose —
   repaired: `scripts/check_session_state.py` now has a
   `verify_mirror_drift()` function comparing
   `CVF_SESSION/ACTIVE_SESSION_STATE.json` against
   `SESSION/ACTIVE_SESSION_STATE.json`'s `cvf_bootstrap_continuity_contract`
   block via an explicit field mapping (field names differ between the two:
   `phaseModel` in the mirror maps to `controlChainModel` in the canonical
   block, etc.). A negative test
   (`tests/cvf/test_session_state_mirror_drift.py`) proves the check
   actually fails on injected drift.

**Disposition: `REVIEWER_ACCEPTED_PENDING_COMMIT`.** The second independent
review reproduced one remaining canonical-drift blind spot plus three bounded
quality defects. Reviewer-owned repairs now compare canonical top-level fields
to the nested contract, fail when the required mirror is absent, require exact
next-move pointer text, set the machine role to REVIEWER, and keep negative
tests entirely in disposable paths. Fresh proof: session-state PASS, mirror
drift tests 7/7 PASS, full suite 156/156 PASS, repository validation PASS,
catalog PASS, and diff hygiene PASS.

### Doctor result (recorded honestly, not marked PASS)

`scripts/check_cvf_workspace_agent_enforcement.ps1` run against this project:
**FAIL, 21/22 checks passed.** The single failing check is "CVF public core
matches origin/main":

```
DIVERGED_OR_UNRELATED_HISTORY.
Local:  f05e3dcd2fb9c82be6f886d0798ca6e87dfcfc7f
origin/main: 9f39111cd97b87ded14c06e01055a4d703d218e6
```

This is an **external publication/reconciliation dependency** of the hidden
CVF core clone against its own public remote. It is not caused by, and cannot
be fixed by, any edit inside this project. Per the mandate for this repair
task, the hidden core must not be modified, reset, or force-pushed to resolve
it — that is a separate, operator-authorized action
(`scripts/update_cvf_workspace_public_core.ps1`), not part of this project's
continuity repair.

## Next allowed move

In this exact order:

1. Commit the accepted bootstrap-continuity batch separately from `0429c4a`.
2. Synchronize this handoff and canonical/mirror session state with both
   committed SHAs.
3. Only after both batches are committed and continuity is synchronized:
   P2-A remaining domains
   (incidents/handovers — still need a new migration first), P2-B (real
   authentication), or P2-C (frontend UI) may be opened, per
   `EXECUTION_ROADMAP.md`.

**Do not implement any P2-A(remaining)/P2-B/P2-C work before both batches
above are committed**, unless the operator explicitly supersedes this
checkpoint.

## Blocked

Everything in `blocked_work` in `SESSION/ACTIVE_SESSION_STATE.json` remains
in force, plus:

- Do not alter committed customer_request batch `0429c4a` without a newly
  demonstrated regression. Commit the reviewer-accepted bootstrap-continuity
  batch separately, then perform final session sync.
- Do not push.
- Do not modify the hidden CVF core, and do not attempt to resolve the
  origin/main divergence by editing project files — it is not fixable from
  inside this project.
- Do not treat `CVF_SESSION/ACTIVE_SESSION_STATE.json` as canonical, or edit
  it without also updating `SESSION/ACTIVE_SESSION_STATE.json`'s
  `cvf_bootstrap_continuity_contract` block in the same change — run
  `python scripts/check_session_state.py` to confirm no drift before
  finishing any session that touches either file.
