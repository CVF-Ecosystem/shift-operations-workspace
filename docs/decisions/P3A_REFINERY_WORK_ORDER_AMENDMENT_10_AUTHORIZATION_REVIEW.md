# P3-A Refinery Work Order Amendment 10 — Independent Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Amendment 10 SHA-256: `ee9a62709ae96c8d6918795c6cf7e976d32f58b01bd25db2bdbba91af2256f8b`
- Consumed Amendment 9 SHA-256: `417a11af86915cca0249e3559236f498fc96f7e60c8363376b4493f26aefca0e`
- Amendment 9 authorization review SHA-256: `6b7819f41d769c0304b495d26319d64619944b5d869fd92ee0fc9115f3786c46`
- Amendment 9 authority checkpoint: `422890062dbf5ee28346311abb6a2a4b13dee5f9`
- Amendment 9 acknowledgment checkpoint: `be63d4505e8b79e96e849090f34462b9918ed550`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_REVIEW_CHANGES_REQUIRED`

Open authorization findings: `A10-AUTH-F1`. Waivers: `NONE`.

Amendment 10 must not receive an authority checkpoint or fresh R2 in its
current form. Its exact continuity preflight cannot pass against the current
canonical repair inputs. No repair, gate, stage, commit/push of BUILD paths,
self-review, or later-lane action is authorized by this review.

## A10-AUTH-F1 — continuity pre-hashes are stale and self-referential

Amendment 10 requires all four repair pre-hashes to match before any repair.
The two Python hashes match, but both continuity hashes do not:

| Repair input | Amendment 10 binding | Independently reproduced | Result |
|---|---|---|---|
| `packages/refinery-bridge/src/refinery_bridge/pipeline.py` | `932c39a86855f4b1634df8eb7465d0d8fdb1ab576108497f808d127835b02c8c` | same | `PASS` |
| `packages/refinery-bridge/src/refinery_bridge/protection.py` | `51011c1efa2292c18b0a4dfa00f76301d003bf52403223c24ef5c5230417c623` | same | `PASS` |
| `SESSION/SESSION_MEMORY.md` | `314c37d168972c1db80580826421f347bdcbf515aef7acce3c83452fac75cf33` | `db0b111cfeb7c55977c5fdccfff40ac9594bb6b19944b7c9c2589e41f8311dbe` | `FAIL` |
| `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md` | `0e01855dd4d35f401b4d721745848e193d00c103b17e9e366b3c6046a3bf4aef` | `03449ca3674b61b9c18bc0e707323ddfc2949be180e35ab6705d4c3c92da3a6d` | `FAIL` |

The mismatch is explained by post-authorship continuity synchronization. The
memory front door is now 617 lines after adding the Amendment 9 consumed/A10
candidate entry; the active handoff is now 740 lines after its disposition and
new 16-line consumed/A10 section were updated. The retained Amendment 9 guard
findings correctly describe their earlier 616-line and 724-line states, but
those earlier bytes are no longer the proposed Amendment 10 repair inputs.

Blindly replacing the two values in Amendment 10 is not a stable repair. The
active handoff currently embeds Amendment 10's full SHA-256. Changing a
pre-hash changes the Amendment SHA, which then requires changing the handoff,
which changes its pre-hash again. The memory also embeds an abbreviated
Amendment SHA. This is a self-reference cycle, not merely a typo.

Required repair: revise the authority/preimage design so the two continuity
repair inputs do not embed a hash that depends on their own hashes. One bounded
option is to make their pending-A10 entries identify the amendment without its
exact SHA, then compute and bind the resulting stable raw pre-hashes in the
revised Amendment. Equivalent deterministic normalization/exclusion is
acceptable only if it is explicitly specified and independently reproducible.
After repair, update the Amendment SHA and continuity consistently, then submit
the corrected artifact for fresh independent authorization review. Do not use
a waiver, debt entry, or a preflight exception.

## Retained truth and binding reproduction

Git truth is consistent with the consumed Amendment 9 record:

- `HEAD == origin/main == be63d4505e8b79e96e849090f34462b9918ed550`;
- `422890062dbf5ee28346311abb6a2a4b13dee5f9` is the Amendment 9 authority
  review commit and `be63d4505e8b79e96e849090f34462b9918ed550` is its pushed
  R2 acknowledgment checkpoint;
- the Amendment 9 exact immutable preflight passed;
- the fresh singular file-size guard then reported exactly
  `pipeline.py 304 > 300`, session memory `616 > 600`, and active handoff
  `724 > 600`;
- execution stopped there; the command was not retried, later gates did not
  run, and provider/network/remote-ingest calls were `0/0/0`.

Using typed `string[]` collections, ordinal ordering, UTF-8, and records
encoded as `path + NUL + lowercase_file_sha256 + LF`, the reviewer reproduced:

| Binding | Expected | Reproduced | Result |
|---|---:|---:|---|
| Exact retained BUILD paths | `28` | `28` | `PASS` |
| Retained exact-28 manifest | `267232b323f8708ed389852576e79362a45db5be9aa99bb3bd559757ad5b0791` | same | `PASS` |
| Immutable existing-candidate paths | `26` | `26` | `PASS` |
| Protected-26 manifest | `8e297a25e51f53d1575e9a6ffd1147f8d61e7369f12b4a1583853c3602001b20` | same | `PASS` |
| Staged paths | `0` | `0` | `PASS` |
| Memory archive absent | required | absent | `PASS` |
| Handoff archive absent | required | absent | `PASS` |

The dirty repository also contains the normal Amendment/continuity governance
surfaces outside the exact retained BUILD subset. No additional
implementation/test/fixture/contract/catalog/status/knowledge path expands the
28-path BUILD candidate.

## Six-path repair contract assessment

Apart from A10-AUTH-F1, the proposed repair is bounded and technically
sufficient:

- the arithmetic is exact: the two Python repair paths already belong to the
  retained 28; the modified memory/handoff plus two new archives add four, so
  the final repair candidate would contain exactly 32 BUILD/continuity paths;
- the other 26 retained BUILD paths remain byte-immutable;
- moving the closed `StageReason -> QuarantineReason` helper mapping from the
  304-line `pipeline.py` to the 241-line `protection.py`, importing it back
  under `_quarantine_reason`, and removing only the newly unused
  `QuarantineReason` pipeline import can preserve behavior while bringing both
  files below 300 lines;
- the current tests exercise quarantine reasons, failed-result routing,
  fallback, policy drift, redaction failures, dedupe failures, stage
  invariants, and stage-unavailable behavior, so the retained focused `53`
  suite is proportionate after the move;
- because the function is moved rather than added and no code file is added,
  the source split can preserve catalog file/LOC metrics exactly;
- the memory archive boundary is unambiguous (current lines 46 through 376)
  and bounded; the handoff archive boundary is unambiguous (current line 351
  through end-of-file) and bounded. Title/preservation note plus verbatim
  blocks keep each archive below 600 lines, while pointers keep both canonical
  front doors below 600 and leave canonical state/handoff pointers unchanged.

The ordered checks are fail-closed and non-expansive: corrected stable
preflight; exactly six repair paths; file-size; focused Refinery; catalog
check with no mutation; full non-live suite; session/repository/static checks;
and final exact-32/six-touch/protected/archive/staged audit. No waiver or debt
mechanism is allowed. The aggregate repository validator's internal file-size
check is part of that later validator, not a retry of the failed Amendment 9
invocation.

Retained Amendment 8 direct probe `7/7`, catalog/knowledge repair, project
knowledge validation, and focused Knowledge Pack `86` remain no-rerun
evidence. The continuation still permits zero provider, network, and
remote-ingest calls and no retry, and its successful claim would remain only a
dirty deterministic-local candidate pending independent BUILD review.

## Next governed move

WORK_ORDER_AUTHOR must repair A10-AUTH-F1 without waiver, produce stable and
reproducible continuity preimages, and issue a corrected Amendment 10 artifact.
A new independent authorization review is required. Only a review PASS followed
by a committed/pushed authority checkpoint and a fresh exact R2 acknowledgment
may authorize one no-retry continuation invocation.
