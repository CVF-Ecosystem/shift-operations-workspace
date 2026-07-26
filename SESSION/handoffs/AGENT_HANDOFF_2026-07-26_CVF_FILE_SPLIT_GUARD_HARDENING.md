# Agent Handoff — CVF File-Split Guard Hardening

## Disposition

- Tranche: `CVF-FILE-SPLIT-GUARD-HARDENING-2026-07-26`
- Phase: approved `WORK_ORDER`, immediately before BUILD
- Risk: R2
- Implementation worker after G6: Claude
- Independent reviewer / commit steward: Codex
- BUILD status: **NOT STARTED**

## Authorization chain

- C1 `ab9a019`: ADR, SPEC and WORK_ORDER only.
- C1b `68b3162a4cff2c594f7ee38b6f891298af7ffefa`: metadata
  trailing-space normalization only; C1 was not amended or rewritten.
- Authorization findings closed without waiver:
  - `FSG-AUTH-F1 AMBIGUOUS_DEBT_SET`
  - `FSG-AUTH-F2 UNNECESSARY_ROUTE_SURFACE_WRITE_SCOPE`
- Re-review: `REVIEW_PASS`.
- Codex approved `CVF-FSG-WO-001` intact under operator-delegated authority.

Normative reads:

1. `docs/decisions/ADR_2026-07-26_CVF_FILE_SPLIT_GUARD_HARDENING.md`
2. `docs/specs/CVF_FILE_SPLIT_GUARD_HARDENING_SPEC.md`
3. `docs/work_orders/CVF_FILE_SPLIT_GUARD_HARDENING_WORK_ORDER.md`

## Verified authorization baseline

- Project `HEAD == origin/main ==
  68b3162a4cff2c594f7ee38b6f891298af7ffefa` before C2.
- Full suite: `369 passed, 1 warning`.
- Repository validator, session-state and current file-size guard: PASS.
- Doctor: `PASS WITH NOTE (24 passed, 1 warning)`; only the bounded legacy
  catalog-kit note.
- Hidden core HEAD/origin/manifest:
  `27137db4d9aa2aea931ddd2507185d5c24943080`, clean.
- Assessment remains untracked and untouched, SHA-256
  `168ea2c7a67a31bae50c9e4dbe78c2273a692f3a82a1074585e1bdb89b70fde2`.
- No provider call, secret read or PostgreSQL run occurred.

## Authorized result

The hard executable limits become:

- Python: 300 lines;
- TypeScript/TSX/JavaScript/JSX: 200 lines.

Oversized executable legacy debt may remain only when exact path, line count
and SHA-256 match the tracked baseline. Any content edit forces a split below
the hard limit. Executable exceptions are prohibited.

Seven C3-touched Python files above 300 must be split now. Only these four
legacy paths may enter the baseline:

1. `scripts/generate_catalog.py`
2. `scripts/run_identity_live_governance_evidence.py`
3. `tests/cvf/test_customer_request_vertical.py`
4. `tests/cvf/test_shift_close_governance.py`

## BUILD boundary

C3 is limited to the exact 24 paths in Work Order section 3.

Read-only evidence surfaces:

- `scripts/testing/validate_repository.py`
- `.githooks/pre-commit`
- `.github/workflows/ci.yml`
- `Makefile`

They must remain byte-identical.

No API/OpenAPI/schema/migration/CVF-control behavior change is allowed.
No provider call, secret read or PostgreSQL run is allowed.

## Mandatory G6

After this C2 commit is pushed, Claude must rehydrate canonical continuity,
this handoff and all three authorization artifacts, declare
`IMPLEMENTATION_WORKER`, then verify:

1. `HEAD == origin/main` at the actual post-C2 commit.
2. No tracked modifications.
3. Only the preserved assessment is untracked with the exact SHA above.
4. Core HEAD/origin/manifest are identical and core is clean.
5. Doctor is 24 PASS, zero FAIL and only the bounded legacy warning.
6. Root suite passes; record the actual count as BUILD baseline.
7. `check_file_size.py --warn` reproduces the starting debt set.
8. Work Order audit finds no required 25th path.

Any mismatch is a stop condition.

## Return checkpoint

Claude implements without staging, committing or pushing, then stops at:

`READY_FOR_INDEPENDENT_BUILD_REVIEW`

The return must include the exact changed set, line-count/digest inventory,
test-node preservation evidence, focused/full suites, validators, catalog,
doctor, diff check and all negative probes required by the Work Order.

Codex remains the independent reviewer and owns all commit/push actions.

## Next after closure

Only after this tranche reaches FREEZE may a distinct PostgreSQL live
round-trip tranche open. Phase 1 is not closed by this guard work.
