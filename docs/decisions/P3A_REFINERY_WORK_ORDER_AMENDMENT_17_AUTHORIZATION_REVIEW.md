# P3-A Refinery Work Order Amendment 17 — Independent Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk / phase: `R2 / WORK_ORDER`
- Amendment 17 SHA-256:
  `01e6392dfc72c257d121091466e221431e5cb43c2ed8e2dd211499dddcef1a7c`
- Parent Amendment 16 SHA-256:
  `076032a3f1c5ed3943c574a894dff90cb887ec8b36d78af37e7d3f96427f3162`
- Amendment 16 review SHA-256:
  `e6ffe5e0c45abdd9eeaa2fb4e1ba031260243c8a34df748d55cc8feb49c44879`
- Review baseline:
  `HEAD == origin/main == 2141f306ebe1509ea606a7db9965b1e64dfa91b5`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 17 accurately consumes the failed A16 invocation and corrects only
its PowerShell parser defect. Canonical multiline, whitespace-separated syntax
with parse-before-execute is sufficient to remove the compressed-token failure
without changing any assertion, file operation, repair surface or later gate.

The exact-nine repair scope/final exact32 candidate, staged zero, stable30,
protected21, nine pre-hashes, archive/suffix identities, four Markdown ceilings,
ordered stop-first/no-retry gates and zero-call claim remain unchanged and
non-expansive.

Open authorization findings: `NONE`. Waivers: `NONE`.

This PASS does not authorize continuation by itself. The exact-six governance
checkpoint must be pushed, then a fresh exact human R2 for Amendment 17 must
authorize the one permitted invocation.

## Consumed A16 invocation

Canonical continuity and Git lineage consistently record:

- A16 authority review `e6ffe5e0…4879` and fresh R2 authority
  `fa3237b5…9ed3` were pushed before the acknowledgment checkpoint;
- acknowledgment checkpoint
  `2141f306ebe1509ea606a7db9965b1e64dfa91b5` is pushed and is both `HEAD` and
  `origin/main`;
- the first preflight command failed PowerShell parsing at compressed
  `foreach($p in$a)` before any assertion or file operation executed;
- no file, repair, probe, test or later gate ran; the exact-nine touch count is
  `0/9`, the staged set remains empty, no retry occurred and calls remained
  zero.

A16 and its fresh R2 are therefore consumed by their first invocation and
cannot be retried or repurposed.

## Fresh immutable-binding reproduction

Before this review artifact was created, the authority-preparation worktree
contained exact `35` dirty paths: the exact32 BUILD/continuity candidate plus
A17 and the canonical/mirror state paths. Excluding those three governance
paths reproduces exact32. Excluding the two volatile continuity front doors
from exact32 reproduces stable30; excluding A15's exact nine repair paths from
stable30 reproduces protected21. Staged paths are zero.

Using ordinal case-sensitive sorting and UTF-8 records encoded as
`path + NUL + lowercase_file_sha256 + LF`:

| Binding | Expected | Reproduced | Result |
|---|---:|---:|---|
| Dirty BUILD/continuity paths | `32` | `32` | `PASS` |
| Staged paths | `0` | `0` | `PASS` |
| Stable paths | `30` | `30` | `PASS` |
| Stable-30 manifest | `a50cebb5f4f4b2e6b6ae79bc56ebc70ac17c1fdd28b7242267a17e96e9c6a436` | same | `PASS` |
| Protected paths | `21` | `21` | `PASS` |
| Protected-21 manifest | `68cbd2430a85e1cafc5a79b46a72d6479a9c2b0a09629cfb387f78c78d7a6070` | same | `PASS` |

All nine repair pre-hashes reproduce exactly:

| Path | SHA-256 |
|---|---|
| `packages/refinery-bridge/src/refinery_bridge/output_models.py` | `62333c0a2fb0734e50b6a3b564af6303c3488db8e14ec4ac97b86db624b0bd9a` |
| `packages/refinery-bridge/src/refinery_bridge/protection.py` | `d909c740e1a2e93859ca47a596c3dac2afaf740648044523b5d5e9de3e58a3f5` |
| `packages/refinery-bridge/src/refinery_bridge/pipeline.py` | `69a55e2e7ad3b115176ae853f2756d3115f69aa12d0d1f7a6088ab15bb8371bf` |
| `tests/unit/test_refinery_models.py` | `d99c48ef9fa7b8a29d762c28965ed719039adcd5d2ec5d15ceb2158703732dc8` |
| `tests/unit/test_refinery_canonical.py` | `1d6ac9bdcec387e3c5dcd0e8d259275d5fd08d1b1be2aec6dddba31b99f22e88` |
| `tests/unit/test_refinery_pipeline.py` | `8a2503128927333d33e439a29d562724b5ab45460ea882a6ce02a2a83a7f7104` |
| `tests/unit/test_refinery_adversarial.py` | `1fc79f95f928656988736c10e9456550c61f2836a36662f344935ae87acdb768` |
| `IMPLEMENTATION_STATUS.json` | `0403f6170dbcab9fc912ea63b003f1d8325a71f36fc408887c23445cfcaacf10` |
| `knowledge/manifest.json` | `b7c0d5ccc70284a07453f80b37e51f8f5feed04dedea393497d9f16ef9ff2cc9` |

## Archive, suffix and line-boundary reproduction

| Surface | Lines | SHA-256 / suffix SHA-256 | Result |
|---|---:|---|---|
| `SESSION/SESSION_MEMORY.md` | `312` total / `243` stable suffix | `6a055880ab97e542fa122ff6cbe3025d993aa521d3b4e9098abf82fa97237ac6` | `PASS` |
| active handoff | `593` total / `2` stable suffix | `46f46615b06dff42a2c44b55321e30c862881146a58a98549fe06f06aaceb357` | `PASS` |
| `SESSION/archive/SESSION_MEMORY_2026-07-22_TO_2026-07-31.md` | `335` | `e218cbc150d03bd9c42f623f972e43ee33ee00b530882195e2c8c145ab918f86` | `PASS` |
| `SESSION/handoffs/archive/AGENT_HANDOFF_2026-08-03_P3A_REFINERY_FOUNDATION.md` | `394` | `c50d4bfd7c7745fa1bb3e5758eddb57c905f5d10fac5da5fda8707f63aee0d44` | `PASS` |

Both relative archive pointers resolve and all four Markdown files are at or
below `600`. The repository file-size guard returns PASS. Any checkpoint/R2
governance update must preserve both suffix hashes and keep the active handoff
at or below 600; bounded compaction may affect only its volatile A16/A17
governance preamble, never the suffix, archive pointer or BUILD/rotation hunks.

## Syntax correction, scope and gate review

The A16 command failed before parsing, so no prior assertion or file-operation
result can be reused. A17 correctly requires one canonical multiline preflight
whose loops, conditionals, functions and operators use whitespace-separated
PowerShell grammar. Requiring a script block or file-safe multiline command to
parse before its single execution prevents recurrence of the exact compressed
token defect while leaving the substantive A16/A15 preflight unchanged.

A17 incorporates the exact A16 archive paths, all four pre-repair Markdown
ceilings, suffix/archive checks, exact32/staged0/stable30/protected21 and nine
pre-hashes. It then permits only A15's nine already-dirty repair paths and the
same four-case probe, focused five-file suite with at least 57 cases, knowledge
checks, file-size/non-mutating catalog check, full non-live suite, repository/
static/security checks and final exact-scope/integrity audit.

Each command runs once; the first parser, command or contract failure stops all
later work. No retry, provider/network/remote-ingest call, BUILD commit,
self-review, FREEZE, waiver, debt, expansion or later-lane action is allowed.
PASS yields only a dirty exact32 deterministic-local candidate pending fresh
independent BUILD review.

## Exact authority checkpoint and fresh R2

COMMIT_STEWARD must partial-stage and push exactly these six governance paths:

1. `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_17.md`
2. `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_17_AUTHORIZATION_REVIEW.md`
3. `SESSION/ACTIVE_SESSION_STATE.json`
4. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
5. only the new A17/review governance preamble hunks in
   `SESSION/SESSION_MEMORY.md`
6. only the new A17/review governance preamble/compaction hunks in
   `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`

The cached diff must exclude every BUILD repair, rotation/archive, source and
historical-continuity hunk. It must retain the handoff at or below 600 lines.
After push, staged paths must be zero and all exact32/stable30/protected21/
pre-hash/archive/suffix/line bindings must reproduce.

Only then may the operator provide this fresh exact acknowledgment:

> Tôi phê duyệt R2 cho
> P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-17-2026-08-04, Work Order Amendment
> SHA-256 `01e6392dfc72c257d121091466e221431e5cb43c2ed8e2dd211499dddcef1a7c`,
> đúng 9 repair paths và final exact 32 BUILD/continuity paths, zero
> provider/network/remote-ingest calls.

That R2 authorizes exactly one invocation and no retry. Its four-path
acknowledgment checkpoint may contain only canonical state, mirror and the new
R2 governance preamble/compaction hunks in memory/handoff, while preserving
the exact32 candidate dirty and the handoff at or below 600 lines.
