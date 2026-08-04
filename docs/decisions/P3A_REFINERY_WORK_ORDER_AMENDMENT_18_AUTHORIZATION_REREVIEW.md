# P3-A Refinery Work Order Amendment 18 — Fresh Authorization Re-review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization re-review)
- Risk / phase: `R2 / WORK_ORDER`
- Amended A18 SHA-256 reviewed:
  `8e08d75cb7f7676d7fcfc18c701087ef3923089427d04acfd40a6f14115a0c2b`
- Frozen execution-sheet SHA-256 reviewed:
  `4f30176b16f82fe9c8789747106e86b6cc1ae0913d4d1bfc351a898e56e5616d`
- Initial changes-required review SHA-256:
  `d72136737ec3afe428b8390b1c3f60e4c7c3dff2c42f12670113af81465ec55c`
- Review baseline:
  `HEAD == origin/main == f775b7c4b3d32872c24fc5b8518109c8797e5764`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REREVIEW_CHANGES_REQUIRED`

The amended Work Order now SHA-binds a real frozen execution sheet. Its atomic
exact-nine patch contexts are present and unique, its source/status/pin repair
is technically correct, and its resulting `IMPLEMENTATION_STATUS.json` hash
reproduces exactly. This materially repairs the original findings.

The repair is not complete. `A18-AUTH-F1` remains open because the sheet does
not contain the exact preflight, four-case probe or final-audit programs and
omits explicit promised static/security commands. `A18-AUTH-F2` remains open
because the exact four-function matrix tests only a before-window record, not
the separately required after-window exclusion. A new lineage finding also
blocks the advertised exact-seven checkpoint: a fresh re-review artifact is
now mandatory in addition to the still-untracked, SHA-bound initial review.

Open findings: `A18-AUTH-F1`, `A18-AUTH-F2`, `A18-AUTH-F3`.
Waivers: `NONE`.

No authority checkpoint, fresh R2, repair invocation, BUILD commit, self-review,
FREEZE or later-lane action is authorized by this disposition.

## Consumed A17 and immutable candidate

The initial review's consumed-A17 conclusion remains valid: pushed A17
preflight passed; its first post-preflight read-inventory command failed parsing
at `foreach($p in$paths)` before it read a file; repair touches remained `0/9`;
the invocation stopped without retry and made zero calls.

Before this re-review artifact was created, the preparation worktree contained
exact `37` dirty paths: exact32 plus amended A18, frozen sheet, initial review
and canonical/mirror state. Excluding those five governance paths reproduces
exact32. Excluding the two volatile continuity front doors gives stable30;
excluding exact9 gives protected21. Staged paths are zero.

| Binding | Expected | Reproduced | Result |
|---|---:|---:|---|
| Exact BUILD/continuity paths | `32` | `32` | `PASS` |
| Staged paths | `0` | `0` | `PASS` |
| Stable paths | `30` | `30` | `PASS` |
| Stable-30 manifest | `a50cebb5f4f4b2e6b6ae79bc56ebc70ac17c1fdd28b7242267a17e96e9c6a436` | same | `PASS` |
| Protected paths | `21` | `21` | `PASS` |
| Protected-21 manifest | `68cbd2430a85e1cafc5a79b46a72d6479a9c2b0a09629cfb387f78c78d7a6070` | same | `PASS` |

All nine repair files still reproduce the exact A18 pre-hashes recorded in the
initial review: output `62333c0a…d9a`, protection `d909c740…a3f5`, pipeline
`69a55e2e…71bf`, tests `d99c48ef…dc8` / `1d6ac9bd…2e88` /
`8a250312…7104` / `1fc79f95…768`, status `0403f617…f10` and manifest
`b7c0d5cc…2cc9`.

Canonical memory is `316` lines with unchanged `243/6a055880…ac6` suffix.
The active handoff is exactly `600` lines with unchanged `2/46f46615…b357`
suffix. Archives remain `335/e218cbc1…f86` and `394/c50d4bfd…d44`; links
resolve and file-size guard passes. Any subsequent governance update must
compact only volatile A18 preamble text and preserve the stable suffix/archive
pointer before a checkpoint can be considered.

## Frozen patch applicability and technical assessment

The execution-sheet SHA matches A18. Every patch anchor occurs exactly once in
the current target set; every old replacement line is present. The payload
touches all and only the named nine paths in one `apply_patch` transaction.

The concrete source changes correctly implement the bounded repair:

- result-level owner/link validation rejects unsafe fallback provenance;
- candidate normalization, terminology, classification and redaction versions
  bind to the corresponding ordered stage receipts while existing quality and
  fingerprint binds remain;
- a quarantined public result requires `route.sink_available is True`;
- the pipeline keeps chronological internal selection and derives sorted unique
  public ids; duplicate receipt ids/count and failed-stage safe ids then agree;
- no dedupe algorithm, receipt model, contract, API or protected path changes.

The typed fingerprint substitution used by the canonical test independently
raises `ValidationError` on the current strict models. The status patch applies
all five intended field replacements, still parses as JSON and produces exact
SHA-256
`9d9d7d2ff387365ce018cc51de07a24d1eb3a21c08cb723feb3d74e114ae5eb6`.
The frozen manifest patch changes only the matching project-context status pin
to that value.

The patch adds exactly four `test_*` functions, one to each authorized test
module; with the accepted baseline `53`, the intended collection is `57`.
Source files would remain within 300 lines, and the patch needs no tenth repair
path. These parts are `PASS` as authorization design, not executed BUILD proof.

## A18-AUTH-F1 — frozen execution sequence remains incomplete

Status: `OPEN`; waiver: `NONE`.

The sheet freezes the atomic patch and eleven direct commands, but its
preflight, four-case probe and final audit are prose only. It says they use
Python `assert`, yet provides no exact program bytes, stdin body or digest.
Therefore a worker would still have to synthesize those three governed steps
after R2, contrary to A18's no-synthesis rule.

The listed direct commands also do not explicitly supply the Work Order's
promised YAML parse, forbidden-import/I/O and secret/security checks. A generic
repository validator cannot silently substitute for named gates unless the
frozen artifact identifies and verifies that exact coverage.

Required repair: freeze byte-exact, executable preflight, four-case probe and
final-audit programs in the sheet. Freeze every static/security command or
explicitly bind each requirement to a named validator check. The preflight must
include amended A18/sheet/review/R2 lineage, exact32/staged0/stable30/
protected21, nine pre-hashes, both archives/suffixes/links and all four line
ceilings. The final audit must mechanically fail on any scope or binding drift.

## A18-AUTH-F2 — four-function matrix is still incomplete

Status: `OPEN`; waiver: `NONE`.

The four named functions now cover the F1 reproductions, typed golden hashes,
cross-type rejection, deterministic permutations, inclusive start/end records,
one before-window rejection, disclosure surfaces and stable invalid-union
bytes. The canonical substitution was also directly checked during review.

However, the initial finding required both sides of the window boundary. The
pipeline function constructs only
`bounds.window_start.replace(year=2025)` and never supplies a record strictly
after `window_end`. Thus “out-of-window rejection” is not a complete
before/after boundary matrix, even though the collected-function count is four.

Required repair: add an after-window rejection assertion to the same frozen
pipeline function so the function count remains exactly four and total remains
57. Freeze the exact focused command's `57` collection requirement as a
contract check, not only an expected human observation.

## A18-AUTH-F3 — exact-seven checkpoint omits required re-review evidence

Status: `OPEN`; waiver: `NONE`.

Amended A18 advertises exact seven paths: A18, initial review, sheet, canonical
state, mirror, memory and handoff. The initial review is still untracked and is
directly SHA-bound by A18, so it cannot be omitted. This fresh re-review is the
only artifact that can close F1/F2 and supply the final authorization
disposition, so it also cannot be omitted. A valid future PASS checkpoint is
therefore exact eight, not exact seven.

Required repair: amend A18's checkpoint count and enumeration to include both
the initial review and the fresh re-review artifact. Any successor re-review
must preserve the explicit audit chain and enumerate the final exact set.

## Checkpoint and R2 disposition

No checkpoint or fresh R2 wording is issued while F1–F3 remain open. After the
sheet/A18 repairs and another fresh independent PASS, the minimum durable
authority checkpoint is exact eight governance paths:

1. `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_18.md`
2. `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_18_EXECUTION_SHEET.md`
3. `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_18_AUTHORIZATION_REVIEW.md`
4. `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_18_AUTHORIZATION_REREVIEW.md`
5. `SESSION/ACTIVE_SESSION_STATE.json`
6. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
7. only new A18/review governance preamble hunks in
   `SESSION/SESSION_MEMORY.md`
8. only new A18/review governance preamble/compaction hunks in
   `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`

If the next fresh disposition is recorded in a new successor artifact rather
than updating this re-review, that successor becomes an additional mandatory
lineage path unless the reviewed checkpoint contract is explicitly repaired
without losing any failed-review audit. Cached staging must exclude all repair,
archive and historical hunks; preserve exact32 dirty, staged zero and the
stable bindings; and keep the handoff at or below 600. Fresh exact R2 may be
specified only by the future PASS artifact.
