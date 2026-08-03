# Work Order Amendment 2 — Project Operations Skill Live Failure Repair

- Parent: `PROJECT_OPERATIONS_SKILL_WORK_ORDER.md` + Amendment 1
- Trigger: consumed Amendment 1 FT-1 replacement lineage
- Risk: `R2`
- Status: `AMENDMENT_2_AUTHORIZATION_RE_REVIEW_PASS — GOVERNANCE PUSH THEN SEPARATE RESUME/G6-R2 REQUIRED`

## 1. Exact BUILD ceiling

The final changed set remains exactly these eight paths:

1. `skills/operate-shift-workspace/SKILL.md`
2. `skills/operate-shift-workspace/agents/openai.yaml`
3. `tests/unit/test_project_operations_skill_contract.py`
4. `scripts/run_project_operations_skill_live_evidence.py`
5. `scripts/_project_operations_skill_live_evidence_support.py`
6. `tests/unit/test_project_operations_skill_live_evidence.py`
7. `docs/decisions/PROJECT_OPERATIONS_SKILL_FORWARD_TEST_RECEIPT.md`
8. `docs/decisions/PROJECT_OPERATIONS_SKILL_LIVE_EVIDENCE_STATE.json`

Only paths 4-8 are expected to change after authorization; paths 1-3 require
no-op inspection. No ninth final path, install, catalog/provider-config edit or
new runtime path is authorized. Runtime-only paths stay exactly:

- `docs/decisions/.PROJECT_OPERATIONS_SKILL_LIVE_EVIDENCE.lock`
- `docs/decisions/.PROJECT_OPERATIONS_SKILL_LIVE_EVIDENCE_STATE.json.tmp`
- `docs/decisions/.PROJECT_OPERATIONS_SKILL_FORWARD_TEST_RECEIPT.md.tmp`

## 2. Immutable pre-repair checkpoint

G6-R2 must verify receipt `49817` bytes / SHA-256
`9334ab2e6b51bcbd7017c75628e1b0e723d2089463ea352c9dbe51b5874f2c6a`
and state `110062` bytes / SHA-256
`71e4f42fbf921561f52066d707b98464599c02a11da2d0706eb33a561f7e6c8c`.
It must also validate history 5, FT-1 FAILED/1, FT-2..FT-4 UNUSED/0, exact
original v1 preservation, zero runtime residue and zero staged files.

## 3. Authorized implementation order after resume

1. Add the same public six-label enum to every serialized response schema;
   retain private per-FT required subsets and canaries only in evaluator data.
2. Introduce evidence v3 with exact v2 snapshot/prefix preservation,
   immutable `replacement_1_invalidated` and fresh `replacement_2_final`.
   Each final lineage is SHA-256 of exact UTF-8
   `replacement2|<FT-id>|<bundle-digest>|<fixture-digest>`; require four
   distinct keys, one uniform bundle, no attempt-id input and no equality with
   any v1/Amendment 1 lineage.
3. Add v3 identity, transition, anti-rollback, receipt and exact 9/5/4
   accounting validation; block all old-set dispatch and tenth-call routes.
4. Expand non-network tests for SPEC B4; preserve all Amendment 1 probes.
5. Run focused/full/quick-validation/repository/diff/secret/doctor gates.
6. Independently review source and temp migration probes before repo migration.
7. Migrate pinned repo evidence once with zero provider calls; verify final set
   four `UNUSED/0`, history 5/5/0 and all prefixes/snapshots.
8. Re-run all non-network gates and independent migrated-state pre-call review.
9. After explicit human R2 acknowledgment, run the live runner once for exactly
   four final calls. On any failure stop; never rerun.
10. Run post-call gates, exact-parent rollback rehearsal and independent final
    BUILD review. Only final `REVIEW_PASS` transfers commit ownership.

## 4. Provider-call and accounting authority

After every gate above, exactly four new physical calls are authorized: one
fresh `replacement_2_final` lineage per FT. The historical ceiling becomes
exactly nine. Final PASS is 4/4 for the new set and 9/5/4 overall. Amendment 1
FT-2..FT-4 are disabled despite being UNUSED. No retry, batch, shared context,
partial claim, fifth final call or tenth historical call exists.

## 5. Roles and commits

Independent `AUTHORIZATION_REVIEWER` must review this ADR/SPEC/Work Order and
the path/call/accounting feasibility. After PASS, `SESSION_SYNC_STEWARD` stages,
commits and pushes exactly these seven governance-authoring paths:

1. `docs/decisions/ADR_2026-08-03_PROJECT_OPERATIONS_SKILL_LIVE_FAILURE_AMENDMENT_2.md`
2. `docs/specs/PROJECT_OPERATIONS_SKILL_SPEC_AMENDMENT_2.md`
3. `docs/work_orders/PROJECT_OPERATIONS_SKILL_WORK_ORDER_AMENDMENT_2.md`
4. `SESSION/SESSION_MEMORY.md`
5. `SESSION/ACTIVE_SESSION_STATE.json`
6. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
7. `SESSION/handoffs/AGENT_HANDOFF_2026-08-02_PROJECT_OPERATIONS_SKILL.md`

No BUILD path may enter that commit. After push, a separate resume checkpoint
may change and commit exactly paths 4-7 above, setting BUILD/REPAIR_WORKER and
G6-R2-first authority; it may include no Amendment doc or BUILD path.
`REPAIR_WORKER` may change only the exact eight BUILD paths after that resume
commit is pushed and G6-R2 passes. `REVIEWER` remains independent;
`COMMIT_STEWARD` receives the eight-path BUILD only after final `REVIEW_PASS`.
C4 remains separate.

## 6. Stop conditions

Stop on pin mismatch, lost nested evidence, public leakage of a private subset,
old-set dispatch, mixed bundle, invalid state accepted, receipt rollback,
preflight mutation/call, failed gate, secret/raw output, runtime residue,
replacement failure, possible retry/tenth call, missing independent review or
missing human R2 acknowledgment.

Authorization re-review passed without waiver. It authorizes only the exact
seven-path governance commit/push followed by the exact four-path resume
checkpoint. No repair, migration, provider call or FREEZE is authorized before
that pushed resume and G6-R2 sequence.
