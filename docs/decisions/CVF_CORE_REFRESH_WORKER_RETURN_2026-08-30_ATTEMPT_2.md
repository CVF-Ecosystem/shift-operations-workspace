# CVF Core Refresh Target Rebase — Attempt 2 Worker Return

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-2026-08-30`
- Role: `IMPLEMENTATION_WORKER`
- Status: `BUILD_RETURNED_FOR_INDEPENDENT_REVIEW`
- Outcome: `FAILURE_ROLLED_BACK`
- Completion findings/waivers: worker does not own them

## Result

Zero-effect preflight passed. The reconciler and initializer each ran exactly
once and initially produced five-way target equality at
`d7860138350130d6d105826ce186f1beeaba3c2d`; the initializer doctor passed 24
checks with one bounded legacy-catalog warning. All `17/17` workspace-root
targets were `NO_CHANGE`, and the sanctioned original network sequence was
exactly three operations.

Fresh downstream-synchronization conformance then failed: the generated corpus
contained all `7` positives, `686` one-fact mutations and `40` temporal cases,
but the repository matcher rejected
`REVIEW_TARGET_MOVEMENT_ROLLED_BACK_VALID` while the independent closed-object
validator accepted it. I treated this as `DOWNSTREAM_SYNCHRONIZATION:P3` and
did not retry or adjust the evidence into success.

Preservation-first rollback completed. The failed target Core remains retained
inside the attempt-2 evidence directory. Old clean Core `a7a797d...`, all
`17/17` roots, `2/2` pins, `9/9` shared carriers and `1/1` binding were
restored. The single rollback verifier returned exit `1` with the expected
`BEHIND_PUBLIC_REMOTE` result (`23/25` checks passed and one bounded warning).

## Command and effect accounting

- Reconciler: one invocation, exit `0`, one public clone.
- Pin bridge: one scoped two-file bridge, later restored.
- Initializer: one invocation, exit `0`, including the bounded doctor.
- Original sanctioned network prefix: `3` operations.
- Rollback verifier: one invocation, expected stale-Core exit `1`.
- Reconciliation retry, provider, credential, install, product, database,
  deployment, commit and push counts: `0`.
- Protected assessment contacts and broad downstream untracked inventories:
  `0`.

## Evidence and boundary

The semantic receipt is
`docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-30_ATTEMPT_2.json`.
Preimages, the preserved target Core, transcripts, checkpoints and the failed
conformance summary are under
`D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\_cvf-core-backups\CVF-CORE-REFRESH-2026-08-30-ATTEMPT-2-EVIDENCE`.

P4-E remains byte-preserved at `DESIGN_REVIEW_PASS`. This worker return proves
only a bounded deterministic failed target-rebase attempt and complete
rollback. It is not tranche closure and does not prove AI-governance behavior,
provider behavior, product/runtime adoption, deployment or production
readiness.

## Next governed move

A distinct `INDEPENDENT_COMPLETION_REVIEWER` reviews the immutable worker
receipt, return and contained evidence. No retry, retarget, commit/push or P4-E
SPEC is authorized.
