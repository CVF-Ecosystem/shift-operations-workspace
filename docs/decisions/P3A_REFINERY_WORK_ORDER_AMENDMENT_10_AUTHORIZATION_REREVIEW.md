# P3-A Refinery Work Order Amendment 10 — Fresh Authorization Re-review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent fresh re-review)
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Repaired Amendment 10 SHA-256: `c801af1bbd946a5eae7b575899460b35d86c2f7376427081d8475ffb132cc3b0`
- Initial Amendment 10 review SHA-256: `43dad00859cb906e446c1e6875dafedbc522e1374c070da195adcf22aa947a14`
- Consumed Amendment 9 SHA-256: `417a11af86915cca0249e3559236f498fc96f7e60c8363376b4493f26aefca0e`
- Amendment 9 authorization review SHA-256: `6b7819f41d769c0304b495d26319d64619944b5d869fd92ee0fc9115f3786c46`
- Amendment 9 authority checkpoint: `422890062dbf5ee28346311abb6a2a4b13dee5f9`
- Amendment 9 acknowledgment checkpoint: `be63d4505e8b79e96e849090f34462b9918ed550`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_REVIEW_CHANGES_REQUIRED`

The repaired Amendment 10 closes the initial review's sole finding,
`A10-AUTH-F1`, without waiver: its four current repair-input hashes reproduce,
and the pending continuity entries no longer embed the Amendment's own SHA.
Fresh re-review nevertheless finds a distinct residual lifecycle defect,
`A10-AUTH-F2`: the required post-review human R2 acknowledgment must be
recorded in the active handoff before BUILD, which necessarily invalidates the
raw handoff pre-hash that A10 requires at BUILD preflight.

Open authorization findings: `A10-AUTH-F2`. Waivers: `NONE`.

Amendment 10 must not receive an authority checkpoint or fresh R2 in its
current form. No repair, gate, stage, BUILD commit/push, self-review, FREEZE,
or later-lane action is authorized by this re-review.

## A10-AUTH-F1 closure

The initial review correctly rejected stale continuity pre-hashes and the
self-reference created when the pending-A10 entries embedded A10's SHA. The
repaired continuity entries now identify Amendment 10 only by path/id. A search
of both raw repair front doors finds neither the repaired full/abbreviated A10
SHA nor the superseded full/abbreviated candidate SHA.

The repaired Work Order binds the exact raw bytes now present:

| Repair input | Bound SHA-256 | Reproduced | Result |
|---|---|---|---|
| `packages/refinery-bridge/src/refinery_bridge/pipeline.py` | `932c39a86855f4b1634df8eb7465d0d8fdb1ab576108497f808d127835b02c8c` | same | `PASS` |
| `packages/refinery-bridge/src/refinery_bridge/protection.py` | `51011c1efa2292c18b0a4dfa00f76301d003bf52403223c24ef5c5230417c623` | same | `PASS` |
| `SESSION/SESSION_MEMORY.md` | `d9ebb7a9ed717eeb713b1cc180081fb3a58d89b8238ec90f00394156e29b2581` | same | `PASS` |
| `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md` | `ad578290725279d5a093db387e3ec67fb4c24407f8948ac4dd3d22618fa0edeb` | same | `PASS` |

Because changing the Work Order no longer changes either continuity preimage,
the raw bindings are stable and the original self-reference is eliminated.

## A10-AUTH-F2 — required R2 continuity transition invalidates preflight

The raw handoff binding is stable only at the present pending-review state.
After an authorization PASS, Amendment 10 itself requires a fresh exact human
R2 acknowledgment before the continuation. The project's Mandatory
Continuity Rehydration protocol also requires that acknowledgment to be
recorded in the active handoff before BUILD begins. Adding that record changes
`SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md` away from bound raw
SHA-256 `ad578290725279d5a093db387e3ec67fb4c24407f8948ac4dd3d22618fa0edeb`.
The Amendment then requires the stale hash to match during the first BUILD
preflight and mandates an immediate stop.

The current scope offers no compliant alternate path: the active-handoff
pointer may not change, the handoff is one of the six repair paths, and no
seventh continuity path is authorized. Omitting the acknowledgment record
would violate the mandatory tranche-transition protocol; updating the bound
hash after acknowledgment would require another Work Order/review cycle and
would recur for any additional required handoff synchronization.

Required repair: bind a deterministic stable pre-repair representation that
explicitly accommodates only the mandatory review/R2 continuity append while
still detecting every unauthorized byte change, or separate the authority
record from the repair preimage through an explicitly authorized canonical
handoff transition. The revised design must make the exact post-R2 preflight
reproducible without changing the six-path/final-32 ceiling unless a separately
reviewed scope change is necessary. No waiver, debt entry, skipped handoff
acknowledgment, or preflight exception is acceptable.

## Consumed truth and retained binding

Independent Git and continuity checks confirm:

- `HEAD == origin/main == be63d4505e8b79e96e849090f34462b9918ed550`;
- Amendment 9's exact immutable preflight passed;
- its first gate, the singular file-size guard, reported exactly
  `pipeline.py 304 > 300`, session memory `616 > 600`, and active handoff
  `724 > 600`;
- execution stopped immediately, the command was not retried, later gates did
  not run, and provider/network/remote-ingest calls were `0/0/0`.

Using typed `string[]` path collections, ordinal ordering, UTF-8, and records
encoded as `path + NUL + lowercase_file_sha256 + LF`, the re-review reproduced:

| Binding | Expected | Reproduced | Result |
|---|---:|---:|---|
| Exact retained BUILD paths | `28` | `28` | `PASS` |
| Retained exact-28 manifest | `267232b323f8708ed389852576e79362a45db5be9aa99bb3bd559757ad5b0791` | same | `PASS` |
| Immutable existing-candidate paths | `26` | `26` | `PASS` |
| Protected-26 manifest | `8e297a25e51f53d1575e9a6ffd1147f8d61e7369f12b4a1583853c3602001b20` | same | `PASS` |
| Staged paths | `0` | `0` | `PASS` |
| Both proposed archive paths | absent | absent | `PASS` |

## Repair and verification contract

The six-path ceiling is exact. `pipeline.py` and `protection.py` already belong
to the retained 28; modifying the two continuity front doors and creating two
archives adds four paths, yielding final exact 32. The other 26 retained BUILD
paths remain byte-immutable.

The source move is behavior-preserving and proportionate: move the exact closed
`StageReason -> QuarantineReason` mapping to `protection.py`, import it back
under `_quarantine_reason`, and remove only the resulting unused enum import.
`pipeline.py` starts at 304 lines and `protection.py` at 241, so the move can
bring both below 300 without compression, assertion deletion, debt, catalog
metric change, contract change, test change, or behavioral expansion. Existing
focused tests cover quarantine/fallback/failed-result routing and the retained
focused `53` suite is required once after this source move.

The archive rotations are lossless and bounded. The memory block begins at the
unique `2026-07-22 (P-FIX-6)` entry and ends immediately before the unique
continuity-drift heading. The handoff block begins at the unique
`## Intake boundary` heading and continues through end-of-file. Verbatim moves,
short archive headers, resolving relative pointers, unchanged canonical
active-state/handoff pointers, and final line-count/link/integrity checks keep
all four Markdown surfaces below 600 lines without deleting history.

The continuation order is fail-closed: authority/binding/archive-absence
preflight; exactly six repairs; file-size; focused Refinery `53`; catalog
`--check` with no mutation; full non-live suite; session/repository/static
checks; and final exact-32/six-touch/protected-26/semantic/archive/staged audit.
The later repository validator's internal file-size check is part of that
aggregate validator, not a retry of Amendment 9's consumed invocation.

No debt entry, exception, waiver, provider call, network call, remote ingest,
retry, catalog write, unrelated edit, BUILD commit/push, self-review, or later
lane is authorized. Retained Amendment 8 direct probe `7/7`, three-path
catalog/knowledge repair, project-knowledge validation, focused Knowledge Pack
`86`, and its catalog write/check evidence are not rerun.

## Claim boundary and next governed move

A successful continuation yields only a dirty exact 32-path deterministic-local
BUILD/continuity repair candidate pending fresh independent BUILD review. It
does not establish a runtime caller, persistence, `data_scope`, retrieval/RAG,
learning, production, P3-A closure, FREEZE, or Phase 3 completion.

WORK_ORDER_AUTHOR must repair A10-AUTH-F2 without waiver and submit another
corrected Amendment 10 for fresh independent authorization review. The next
review must demonstrate that the exact handoff preflight remains valid after
the mandatory review/R2 acknowledgment is recorded. Only a later review PASS,
committed/pushed authority checkpoint, and fresh exact R2 may authorize one
no-retry continuation invocation.
