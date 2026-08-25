# Work Order Amendment 1 — P4-C path 67 Knowledge source pins

- Tranche: `P4C-INTEGRATION-EDGE-2026-08-23`
- Phase: `WORK_ORDER`
- Risk ceiling: `R2`
- Parent Work Order raw SHA-256:
  `d9d2f139a3bec12674200266a93f8667cb054f7edffd7bacb8eff1eefb6ebea2`
- DESIGN amendment review: `DESIGN_AMENDMENT_REVIEW_PASS`, `NONE/NONE`
- SPEC amendment review: `SPEC_AMENDMENT_REVIEW_PASS`, `NONE/NONE`
- BUILD: `STOPPED_PENDING_AUTHORIZATION_REVIEW`

## Authorized ceiling amendment

The original 66 unique BUILD paths remain byte-for-byte authorized. Add:

67. `knowledge/manifest.json`

The final P4-C BUILD changed-set union must contain exactly 67 unique paths.
No other path is authorized.

## Sole path-67 operation

The `REPAIR_WORKER` may replace only the following three SHA string values in
existing `sourcePins` entries, after recomputing each named source:

| Source | Current SHA | Required SHA |
|---|---|---|
| `docs/catalog/MODULE_REGISTRY.json` | `3505654ae154ebca22daea6fbe632d365a648902bac1f459a245de4aa5e30e36` | `4a7c621126cc1237bc8ec43bc67dba69ca1ccfc94a402ac65a8131d18fe5710f` |
| `AGENTS.md` | `afce67b2e37fd3072a45b942d4d1d33491726d4d182c8cd4b0f600c8992b5770` | `6b2629d21f49b6841ffccad3dd1912dca50b5ea9a9eb6c6c2a1edf56c1b3fecf` |
| `.cvf/manifest.json` | `8cd22f2a2129f9d57b61b8587c24d5164935034d2fc59d011f511b205ec9c0da` | `2f319767aadce1da76650bfe4b682ad993d664746157dd4b80a49a85f6f8d79a` |

Every other byte in path 67 is protected, including the pre-existing settled
Core-refresh delta for `IMPLEMENTATION_STATUS.json`. The worker must not edit
Knowledge metadata, validators, tests, catalog outputs, invariant artifacts,
runtime source or governance/review/continuity artifacts.

## Evidence and commands

Before editing, record exact source hashes, staged set zero and Core
`HEAD == origin/main == manifest == AGENTS == 9c01832930226f2f770eafa346e01279160f22cb`.
After the edit, run:

1. `python scripts/check_project_knowledge.py`
2. `python -m pytest -q tests/unit/test_project_knowledge_pack.py`
3. the retained P4-C focused suite and full non-live suite;
4. `python scripts/check_invariant_families.py --json`
5. `python scripts/check_session_state.py`
6. `python scripts/generate_catalog.py --check`
7. `python scripts/check_file_size.py`
8. `python scripts/testing/validate_repository.py`
9. workspace doctor, `git diff --check`, exact-67 scope check, staged-zero and
   secret/disclosure scan.

Existing disposable-local PostgreSQL evidence may be retained unless a
reviewer identifies a causal database regression; no new database effect is
introduced by the JSON pin repair.

## Roles and effects

- `REPAIR_WORKER`: performs only the three replacements and returns evidence.
- `INDEPENDENT_COMPLETION_REVIEWER`: recomputes hashes, scope and tests; the
  worker cannot self-approve.
- Commit/push ownership remains unassigned.

Provider calls, external HTTP, credentials, installs, deployment, commit and
push remain zero. This deterministic pin repair does not itself support a CVF
governance-behavior claim.

## Stop conditions

Stop on any fourth pin/value change, path 68, source-hash movement, test or
guard failure, Core drift, protected assessment access, secret exposure, or
need for any external effect. Do not weaken a guard.

## Disposition

`READY_FOR_INDEPENDENT_AUTHORIZATION_REVIEW`. BUILD remains stopped.
