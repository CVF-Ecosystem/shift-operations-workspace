# P3-A Refinery Work Order Amendment 25 — Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk / phase: `R2 / WORK_ORDER`
- Amendment reviewed:
  `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_25.md`
- Reviewed SHA-256:
  `12de43b4fc9a2093d4292f590d0bf025d2263d303b4235d788208da0cd35e704`
- Provider/network/remote-ingest calls during review: `0/0/0`
- Findings: `A25-AUTH-F1`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_CHANGES_REQUIRED`

Amendment 25 is not executable as written. Its one repair path and intended
debt-pin update are sufficient, but its asserted exact-one byte-change boundary
contradicts its required post-hash. The amendment must be corrected and receive
a fresh independent re-review before any authority checkpoint, R2
acknowledgment or repair invocation.

This disposition is authorization-review evidence only. It authorizes no
repair, BUILD action, commit, push, provider/network/remote-ingest call,
waiver, self-review, FREEZE or later-lane work.

## Finding A25-AUTH-F1 — Post-hash silently includes whole-file newline normalization

Severity: `BLOCKING`  
Waiver: `NONE`

The current debt registry has SHA-256
`26e0929059d4d1c1e851dc75cfb775e306c86c10c5b7e1f6f1a7285e55f76b52`,
contains exactly `29` CRLF sequences and zero lone-LF sequences, contains the
old generator SHA exactly once, and contains the new generator SHA zero times.

Replacing only the authorized 64-byte ASCII SHA literal while preserving every
other byte produces:

`a647cb498ef800ef2b4ce8e6491741fec9ceb82d001e04f3e459d57ced6f9f4e`

It does not produce the amendment's required post-hash
`499ddd1724e45861fcfac95d70b4dd620ef5e0f2c92b5206a7264b1518371560`.
That declared hash is reproduced only after the literal replacement plus
conversion of all `29` CRLF sequences to LF, removing `29` carriage-return
bytes from the file.

This conflicts with all three current authority statements:

- "The only authorized byte change is one literal replacement";
- "No debt fields ... may otherwise change";
- step 2 requires one `apply_patch` for the exact one-line replacement, with
  no separately declared newline-normalization operation.

The author must choose and bind one byte-exact behavior:

1. retain the exact-one literal replacement and correct the required post-hash
   to `a647cb498ef800ef2b4ce8e6491741fec9ceb82d001e04f3e459d57ced6f9f4e`; or
2. explicitly authorize CRLF-to-LF normalization of this same one repair path,
   preserve the current `499ddd1724e45861fcfac95d70b4dd620ef5e0f2c92b5206a7264b1518371560`
   post-hash, and update the repair/post-audit wording accordingly.

Either correction changes the Work Order bytes and therefore requires a new
Work Order SHA-256, a recomputed exact fresh-R2 UTF-8 digest, continuity sync,
and fresh independent authorization re-review. No waiver is appropriate
because the present runner cannot simultaneously satisfy its post-hash and its
exact-change boundary.

## Checks that otherwise pass

### Consumed A24 and retained evidence

Canonical memory, active state, compatibility mirror and active handoff agree
that A24 acknowledgment checkpoint
`86ee107b34e049d9b718f042bbfff35fdb0927b8` is pushed and A24 is consumed.
They retain exact-four/post-audit PASS, catalog-drift `5 passed`, project
Knowledge PASS, focused Knowledge Pack `86 passed`, catalog check PASS, full
non-live `1597 passed / 128 skipped`, and session-state PASS. Repository
validation then stopped at the stale file-size-debt entry; later gates were
`NOT_RUN`, with no retry or provider/network/remote-ingest call.

Retaining the full suite without rerun is sufficient for this bounded metadata
repair because all source, tests, catalogs, knowledge artifacts and candidate
continuity bytes covered by those gates remain protected, while the file-size
guard and repository validator are explicitly rerun after the debt-pin change.
This sufficiency conclusion remains conditional on repairing A25-AUTH-F1 and
preserving the corrected byte-exact scope.

### Scope and manifest reproduction

Before this review artifact was created, the authoring worktree had exactly
`37` dirty paths: the retained exact34 candidate plus canonical state, its
compatibility mirror and the A25 Work Order. Removing those three governance
authoring paths reproduces all and only the `34` retained candidate paths.
The final exact35 is exactly that set plus
`docs/reference/FILE_SPLIT_DEBT_BASELINE.json`; the repair set contains exactly
that one path.

Excluding canonical memory, the active handoff and the one repair path leaves
exactly `32` protected paths. The reviewed ordinal manifest algorithm
reproduces:

`9399529ae64ea63170ea94549ce1809618a8c79f60ab3149d86e9b4e4bb79cac`

The four retained A24 output hashes also reproduce:

| Path | Current SHA-256 |
|---|---|
| `scripts/generate_catalog.py` | `6a04502d0ef35e69225a5cb1fbd652c18db4d23814219c0e0cdb27792735b9b6` |
| `tests/integration/test_catalog_drift_detection.py` | `820e4f3bd5b299f341e511e15ecb0de2de7a3e49b28a68f1aa83eabd5aee791d` |
| `docs/catalog/MODULE_REGISTRY.json` | `1c1463d992a8ffe362059db3efded0a7a90664aebdbcec06bb9b13b922b7d727` |
| `docs/catalog/MODULE_CATALOG.md` | `32fe4ecbb7f7b493ba1536975d81aa95a895ca1424309dd580f232b8ee1bb484` |

### Authority, stop and call boundaries

`HEAD == refs/remotes/origin/main ==
86ee107b34e049d9b718f042bbfff35fdb0927b8`; staged paths are exactly zero.
The dynamic-topology requirement, one-invocation/no-retry stop rule, prohibition
on BUILD commit/self-review/FREEZE, and zero provider/network/remote-ingest/POST
boundary are otherwise sufficient and non-expansive.

The exact proposed A25 acknowledgment is `271` Unicode code points and its
UTF-8 SHA-256 correctly reproduces
`a451b79f8fb85c7126b56a6149d73127f4917375960cc3ae07a8f6eed94a6d18`.
It must not be requested or accepted against this rejected Work Order hash.

### Continuity and workspace checks

The workspace doctor returns PASS WITH NOTE (`24` passed, one bounded legacy
catalog warning). `python scripts/check_session_state.py` returns PASS; the
canonical phase is WORK_ORDER, the active handoff pointer agrees, and the
compatibility mirror identifies A25 as pending independent review. The active
handoff is `596` lines, within the `600`-line ceiling. Because only four lines
of headroom remain, any later continuity update must compact rather than append
past the ceiling.

## Required next move

`WORK_ORDER_AUTHOR` must close `A25-AUTH-F1` without waiver by selecting one of
the two byte-exact alternatives above, update the Work Order and synchronized
continuity, and request a fresh independent authorization re-review. The debt
registry must remain untouched until that re-review passes, a governance-only
authority checkpoint is pushed, and a fresh exact R2 acknowledgment is
accepted.
