# Agent Handoff — P2-D Offline Queue and Polling Realtime

## Disposition

- Tranche: `P2D-OFFLINE-REALTIME-2026-08-02`
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Active role: `SESSION_SYNC_STEWARD / COMMIT_STEWARD`
- Status: `REVIEW_PASS / APPROVED — BUILD NOT STARTED`

## Settled predecessor

P2-C is `FREEZE / CLOSED_BOUNDED`: C3d BUILD
`e120a7f7d004d1c7860b27f1b425f8202a7f7bc7` and C4 truth sync
`1f3646aba7d2bc4becea6c156475360331133f29` are pushed. P2-C authority does
not carry into P2-D. Phase 2 remains `IN PROGRESS`.

## Fresh P2-D control chain

- INTAKE: `docs/decisions/INTAKE_2026-08-02_P2D_OFFLINE_REALTIME.md`
- DESIGN: `docs/decisions/ADR_2026-08-02_P2D_OFFLINE_REALTIME.md`
- SPEC: `docs/specs/P2D_OFFLINE_REALTIME_SPEC.md`
- WORK_ORDER: `docs/work_orders/P2D_OFFLINE_REALTIME_WORK_ORDER.md`
- AUTHORIZATION REVIEW:
  `docs/decisions/P2D_WORK_ORDER_AUTHORIZATION_REVIEW.md`

The reviewed exact 49-path BUILD is frontend/evidence-only. It authorizes a
navigation-only service worker, actor-bound bounded queue for exactly three
existing CAS transitions, fail-stop replay, one serialized refresh coordinator
per tab and authenticated foreground polling. It does not authorize backend,
OpenAPI, migration, dependency/lockfile, CI, roadmap or continuity edits.

## Authorization disposition

Independent review closed `P2D-AUTH-F1` through `F5` and re-review finding
`P2D-AUTH-REREVIEW-F6` without waiver. Final disposition is
`REVIEW_PASS / APPROVED` with exactly 49 unique paths and accurate NEW/existing
labels. No implementation test, browser run, PostgreSQL run or provider call
was used or claimed during authorization.

## Next governed move

Authorization package `7437b70e9005341b4ebf0f287b92411a110798b0` is
`REVIEW_PASS / APPROVED` and pushed. This continuity-only successor is the
separate pre-BUILD checkpoint and pins that commit as the exact BUILD parent.
The receiving `IMPLEMENTATION_WORKER` must rehydrate this handoff, declare the
role transition, verify clean `HEAD == origin/main`, run fresh G6 and record
baselines before the first source edit. Any failure is `BLOCKED_G6`.

BUILD and provider calls remain prohibited until that checkpoint and G6 pass.
The later worker changes only the exact 49 BUILD paths, does not stage/commit/
push/self-review/FREEZE, and stops at `READY_FOR_INDEPENDENT_P2D_BUILD_REVIEW`.

## Claim boundary

P2-D remains open. No offline/realtime governance behavior, full-shift exit,
Phase 2 completion, push transport, cross-tab/request exactly-once, production
readiness or post-Phase-2 capability is claimed by this authoring package.
