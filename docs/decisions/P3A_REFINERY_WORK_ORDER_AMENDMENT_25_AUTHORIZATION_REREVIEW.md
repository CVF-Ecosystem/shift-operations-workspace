# P3-A Refinery Work Order Amendment 25 — Authorization Re-review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization re-review)
- Risk / phase: `R2 / WORK_ORDER`
- Corrected amendment reviewed:
  `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_25.md`
- Reviewed SHA-256:
  `ff2671a05b732bf6b687bcd65daae32f8895dd669ea63a25ae63c885e2e33cf7`
- Initial review SHA-256:
  `5a222a068ac54f035d303bd32030f41147c918f8dbdf449a573e1757621629f6`
- Provider/network/remote-ingest calls during re-review: `0/0/0`
- Findings: `NONE`
- Closed findings: `A25-AUTH-F1` (`CLOSED_WITHOUT_WAIVER`)
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REREVIEW_PASS`

Corrected Amendment 25 is necessary, sufficient and non-expansive for the
consumed A24 repository-validator stop. It authorizes exactly one
repository-owned debt-pin path, binds the literal-only raw-byte result, retains
valid A24 evidence without an unnecessary full-suite rerun, and preserves all
source, test, catalog, knowledge and continuity candidate bytes.

This PASS is authorization-review evidence only. It is not repair authority,
BUILD evidence, a BUILD commit, self-review, FREEZE or later-lane authority.
The one repair invocation remains prohibited until a governance-only authority
checkpoint is pushed and the exact fresh A25 R2 acknowledgment is accepted.

## A25-AUTH-F1 closure

The initial review correctly found that the original post-hash silently
included whole-file LF normalization while the authority allowed only one
literal replacement. The corrected Work Order closes the finding without
waiver:

- current debt-registry SHA-256:
  `26e0929059d4d1c1e851dc75cfb775e306c86c10c5b7e1f6f1a7285e55f76b52`;
- current raw layout: `1587` bytes, exactly `29` CRLF sequences and zero
  lone-LF sequences;
- old generator SHA occurrences: exactly `1`;
- new generator SHA occurrences: exactly `0`;
- replacing only
  `fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b`
  with
  `6a04502d0ef35e69225a5cb1fbd652c18db4d23814219c0e0cdb27792735b9b6`
  preserves `1587` bytes and exactly `29` CRLF sequences, leaves zero old and
  exactly one new occurrence, and produces SHA-256
  `a647cb498ef800ef2b4ce8e6491741fec9ceb82d001e04f3e459d57ced6f9f4e`.

The corrected pre/post hashes, explicit no-normalization rule, repair step and
immediate post-audit now describe the same byte-exact operation. Any newline
change is a first failure, not an authorized alternate repair. The file-size
debt entry's retained `lineCount=313` matches the current generator, whose
current SHA is exactly the newly bound value above.

## Scope and manifest reproduction

Before this re-review artifact was created, the worktree had exactly `38`
dirty paths: the retained exact34 candidate plus canonical state, compatibility
mirror, corrected A25 Work Order and initial A25 review. Excluding those four
governance-authoring paths reproduces all and only the retained `34` candidate
paths. Staged paths are exactly zero, and the debt registry remains clean.

The final exact35 is exactly the retained exact34 plus
`docs/reference/FILE_SPLIT_DEBT_BASELINE.json`. The repair set contains exactly
that one path. Excluding canonical memory, active handoff and that repair path
leaves exactly `32` protected paths. Applying the reviewed ordinal manifest
algorithm reproduces:

`9399529ae64ea63170ea94549ce1809618a8c79f60ab3149d86e9b4e4bb79cac`

The four A24 output hashes remain unchanged:

| Path | Current SHA-256 |
|---|---|
| `scripts/generate_catalog.py` | `6a04502d0ef35e69225a5cb1fbd652c18db4d23814219c0e0cdb27792735b9b6` |
| `tests/integration/test_catalog_drift_detection.py` | `820e4f3bd5b299f341e511e15ecb0de2de7a3e49b28a68f1aa83eabd5aee791d` |
| `docs/catalog/MODULE_REGISTRY.json` | `1c1463d992a8ffe362059db3efded0a7a90664aebdbcec06bb9b13b922b7d727` |
| `docs/catalog/MODULE_CATALOG.md` | `32fe4ecbb7f7b493ba1536975d81aa95a895ca1424309dd580f232b8ee1bb484` |

## Retained evidence and no-rerun boundary

Canonical memory, active state, compatibility mirror and active handoff agree
that A24 acknowledgment checkpoint
`86ee107b34e049d9b718f042bbfff35fdb0927b8` is pushed and A24 is consumed.
They retain exact-four/post-audit PASS, catalog-drift `5 passed`, project
Knowledge PASS, focused Knowledge Pack `86 passed`, catalog check PASS, full
non-live `1597 passed / 128 skipped`, and session-state PASS. Repository
validation then stopped at the stale file-size debt SHA; later gates were
`NOT_RUN`, with no retry or provider/network/remote-ingest call.

No full-suite rerun is needed for this one metadata-pin edit: every byte covered
by source, test, catalog and Knowledge behavior gates is protected, while the
file-size guard and repository validator that consume this debt pin are run
once after the edit. The remaining static/security/diff gates and final
exact35/exact1/protected32 audit follow in the same stop-first invocation.

## Fresh R2 and authority boundary

The exact proposed acknowledgment is:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-25-2026-08-04,
> Work Order Amendment SHA-256
> ff2671a05b732bf6b687bcd65daae32f8895dd669ea63a25ae63c885e2e33cf7,
> đúng 1 repair path và final exact 35 BUILD/continuity paths, zero
> provider/network/remote-ingest calls.

Constructed as one line with no leading/trailing whitespace or newline, it has
`271` Unicode code points. SHA-256 over its exact UTF-8 bytes reproduces:

`b453d8adf30fb0d48246c9234ba6d4857fffc2e9c9055141ccc413ee5aa736bc`

`HEAD == refs/remotes/origin/main ==
86ee107b34e049d9b718f042bbfff35fdb0927b8`. The future runner must verify the
dynamic authority/acknowledgment topology and ASCII digest from committed
state; it must not guess a future commit hash or transport a Vietnamese
expected literal through stdin.

The ordered invocation is one-shot, stop-first and no-retry. It allows zero
provider/network/remote-ingest/POST calls, no full-suite rerun, no alternate
fix, no BUILD commit, no self-review, no FREEZE and no later-lane expansion.
Any first failure consumes the invocation and requires another reviewed
amendment plus fresh R2.

## Continuity and workspace checks

The workspace doctor returns PASS WITH NOTE (`24` passed, one bounded legacy
catalog warning). `python scripts/check_session_state.py` returns PASS.
Canonical state and compatibility mirror agree on WORK_ORDER, active handoff,
parked checkpoint, active role and updated date; both identify corrected A25 as
pending re-review. The active handoff is `595` lines, within the `600`-line
ceiling. Subsequent authority continuity must compact as needed rather than
exceed that ceiling.

## Exact next move

`COMMIT_STEWARD` may partial-stage, commit and push only the corrected A25 Work
Order, this re-review, the unchanged initial review, synchronized canonical
state/mirror, and bounded governance preamble hunks while preserving exact34
unstaged and the debt path clean. Then stop for the exact fresh A25 R2 above.
No debt repair is authorized before that acknowledgment is accepted.
