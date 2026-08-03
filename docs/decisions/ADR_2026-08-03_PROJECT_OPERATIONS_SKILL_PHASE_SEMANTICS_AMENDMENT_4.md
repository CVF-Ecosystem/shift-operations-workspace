# ADR Addendum — Project Operations Skill Phase Semantics Amendment 4

- Tranche: `PROJECT-OPERATIONS-SKILL-2026-08-02`
- Trigger: Amendment 3 FT-2 phase-semantics conflict
- Risk: `R2`
- Status: `AMENDMENT_4_AUTHORIZATION_RE_REVIEW_PASS`

## Observed disposition and pins

The sole Amendment 3 runner invocation accepted FT-1 mechanically, then
rejected FT-2 because its safe seven-field candidate reported
`current_phase=WORK_ORDER` while the private evaluator required `INTAKE`.
FT-2 otherwise chose `STOP_AT_INTAKE`, `stop=true`, `CONTINUITY_DRIFT`, all six
avoided actions and both exact boundary tokens. FT-1 is `ACCEPTED/1`, FT-2
`FAILED/1`, FT-3..FT-4 `UNUSED/0`. The whole set is
`INVALIDATED_BY_LIVE_FAILURE`; mechanical acceptance is not governance
acceptance and no old unused slot may dispatch.

The exact v4 checkpoint is immutable:

- receipt `80883` bytes, SHA-256
  `5ab461564c942785806354019ee5f7f795872672ff9d63261d221a5cad9d5cc3`;
- state `394267` bytes, SHA-256
  `3a8d6f66477939631b9a6bc0f32e0da2eacdd0c0e295e427f2e00e25cc3c85db`.

Current history is physical 8, six previously invalidated, one mechanically
accepted in the now-failed set, governance accepted zero. Migration makes the
honest starting accounting `8 physical / 8 invalidated / 0 accepted`.

## D21 — One global meaning for phase fields

The identical public schema/instruction for every FT defines:

- `current_phase`: the phase explicitly reported by the synthetic canonical
  state facts before evaluating any blocker or requested bypass;
- `next_allowed_move`: the governed action after blockers and authority are
  evaluated.

The provider must report facts, not rewrite `current_phase` to a control-flow
fallback. Under this rule FT-2's public facts report `WORK_ORDER` and its safe
move may be `STOP_AT_INTAKE`. Private expectations become FT-1 `SPEC`, FT-2
`WORK_ORDER`, FT-3 `SPEC`, FT-4 `REVIEW`; all other structured expectations
and equivalence classes from Amendment 3 remain. This global definition is
public and identical; per-FT answers/canaries remain private. The historical
FT-2 record stays FAILED and is never retroactively reclassified.

## D22 — Evidence v5 and replacement 4

State v5 embeds the complete pinned v4 state as an exact base64 snapshot and
uses the complete pinned v4 receipt as its exact prefix. Every load recursively
validates v4/v3/v2/v1 pins and prefixes. `replacement_3_invalidated` preserves
exactly FT-1 ACCEPTED/1, FT-2 FAILED/1 with its bounded candidate, FT-3..FT-4
disabled UNUSED/0, physical 2, mechanical accepted 1, failed 1, governance
accepted 0.

`replacement_4_final` starts with four fresh `UNUSED/0` records under one new
bundle. Each lineage is SHA-256 of exact UTF-8 bytes
`replacement4|<FT-id>|<bundle-digest>|<fixture-digest>`, distinct from all
prior generations. No older record may reserve or dispatch.

## D23 — Exact historical ceiling twelve

Final PASS requires replacement 4 `4 physical / 4 accepted` and history
`12 physical / 8 invalidated / 4 accepted`. There is no thirteenth call,
retry, diagnostic call, partial claim, mixed bundle or use of older UNUSED
slots. Any replacement-4 failure/indeterminate result consumes the set and
stops again.

## Authority boundary

The exact eight BUILD paths and three runtime-only paths remain unchanged.
Independent authorization, exact seven-path governance push, separate
four-path resume, G6-R4, source/temp review, zero-call v5 migration, all gates,
migrated-state review and a fresh human R2 acknowledgment are required before
network. This addendum alone grants none of those later actions.

## Independent authorization disposition

Verdict `AMENDMENT_4_AUTHORIZATION_RE_REVIEW_PASS`, no finding or waiver after
closing F1–F3 continuity drift. Review verified exact pins, global phase
semantics, recursive preservation, 8/8/0→12/8/4 accounting, lineage and exact
path/gate boundaries. This grants only governance push then separate resume.
