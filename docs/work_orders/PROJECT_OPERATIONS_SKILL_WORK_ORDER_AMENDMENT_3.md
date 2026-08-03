# Work Order Amendment 3 — Project Operations Skill Semantic Repair

- Parent: `PROJECT_OPERATIONS_SKILL_WORK_ORDER.md` + Amendments 1 and 2
- Trigger: consumed Amendment 2 FT-1 replacement lineage
- Risk: `R2`
- Status: `AMENDMENT_3_AUTHORIZATION_REVIEW_PASS — GOVERNANCE PUSH THEN SEPARATE RESUME/G6-R3 REQUIRED`

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

Only paths 4-8 are expected to change; paths 1-3 receive no-op inspection.
The only runtime paths remain the existing lock and two `.tmp` files. No ninth
final path, install, catalog/provider-config edit or new runtime path exists.

## 2. Immutable G6-R3 checkpoint

Before any BUILD edit, G6-R3 must verify:

- receipt `60182` bytes / SHA-256
  `d6b92e9ff84215e472e111b78feef87ddd22ee1ff3f1dc18bba4c72bb649775f`;
- state `268577` bytes / SHA-256
  `95b7ceb737bd549027eac8ad7e74dfb7f2fb66eef87544f4ebb284630f92155b`;
- history physical 6, invalidated 5, accepted 0; replacement-2 FT-1
  `FAILED/1`, FT-2..FT-4 `UNUSED/0`;
- exact nested v2/v1 preservation, zero runtime residue, zero staged paths,
  and exactly the same eight untracked BUILD paths.

## 3. Authorized implementation sequence after pushed resume

1. Replace prose-sensitive output/evaluation with SPEC C1's uniform public
   structured schema and deterministic private equality/membership matrix.
2. Add SPEC C2's bounded `candidate_response` retention without retaining raw
   envelopes or weakening FAILED/no-retry behavior.
3. Introduce v4 with exact v3 snapshot/prefix and recursive v2/v1 preservation,
   immutable replacement 2 and fresh `replacement_3_final`. Compute each
   lineage from exact UTF-8
   `replacement3|<FT-id>|<bundle-digest>|<fixture-digest>`.
4. Enforce exact v4 identity, transition, anti-rollback, receipt and 10/6/4
   accounting; block all older dispatch and eleventh-call routes.
5. Expand non-network tests for SPEC C5 and retain every prior failure probe.
6. Run focused/full/quick/repository/diff/secret/doctor gates.
7. Obtain independent source/temp-migration review before repository migration.
8. Migrate once with zero provider calls; verify v4 starts at history 6/6/0,
   replacement 3 four `UNUSED/0`, and all snapshots/prefixes exact.
9. Repeat all gates and obtain independent migrated-state pre-call review.
10. Ask for a new explicit human R2 acknowledgment; prior approvals do not
    authorize the Amendment 3 ceiling.
11. Invoke the live runner once for exactly four calls. Stop on the first
    failure and never rerun.
12. Run post-call gates, exact-parent rollback rehearsal and independent final
    BUILD review. Only `REVIEW_PASS` transfers commit ownership.

## 4. Provider-call and accounting authority

Only after every pre-call gate may four new physical calls be made: one fresh
replacement-3 lineage per FT. The final ceiling is exactly ten physical calls
and final PASS is replacement 3 `4/4`, overall `10/6/4`. No older unused call,
retry, shared context, partial claim, fifth replacement-3 or eleventh historical
call is authorized.

## 5. Roles and exact commits

Independent `AUTHORIZATION_REVIEWER` reviews the Amendment 3 ADR/SPEC/Work
Order, feasibility, paths and call/accounting ceiling. After PASS,
`SESSION_SYNC_STEWARD` commits and pushes exactly these seven governance paths:

1. `docs/decisions/ADR_2026-08-03_PROJECT_OPERATIONS_SKILL_SEMANTIC_CONTRACT_AMENDMENT_3.md`
2. `docs/specs/PROJECT_OPERATIONS_SKILL_SPEC_AMENDMENT_3.md`
3. `docs/work_orders/PROJECT_OPERATIONS_SKILL_WORK_ORDER_AMENDMENT_3.md`
4. `SESSION/SESSION_MEMORY.md`
5. `SESSION/ACTIVE_SESSION_STATE.json`
6. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
7. `SESSION/handoffs/AGENT_HANDOFF_2026-08-02_PROJECT_OPERATIONS_SKILL.md`

No BUILD path enters that commit. A separate pushed resume changes exactly the
four continuity paths 4-7, setting BUILD/REPAIR_WORKER and G6-R3-first
authority. Only then may `REPAIR_WORKER` touch the same eight BUILD paths.
`REVIEWER` stays independent and `COMMIT_STEWARD` receives them only after
final review PASS. C4 and later queue items remain separate.

## 6. Stop conditions

Stop on any pin/history/path mismatch, lost nested evidence, private-answer
leak, unsafe diagnostic retention, old-set dispatch, mixed bundle, invalid
state accepted, receipt rollback, preflight call/mutation, failed gate,
secret/envelope retention, runtime residue, replacement failure, possible
retry/eleventh call, missing independent review or missing fresh human R2
acknowledgment.

Authorization review passed without finding or waiver. It authorizes only the
exact seven-path governance commit/push followed by the exact four-path resume
checkpoint. No BUILD edit, migration or provider call is authorized before the
pushed resume and G6-R3 sequence.
