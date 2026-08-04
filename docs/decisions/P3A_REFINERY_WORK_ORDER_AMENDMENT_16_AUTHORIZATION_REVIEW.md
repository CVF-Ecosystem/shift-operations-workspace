# P3-A Refinery Work Order Amendment 16 — Independent Authorization Review

> **Correction history — fresh bounded re-review:** The initial review at
> SHA-256
> `f74b3af9bd8cc29627e6d186bc4842f6ca3659979361839c389a0ef348d36728`
> returned changes required for only `A16-AUTH-F1`: the active handoff was 602
> lines, above the retained 600-line ceiling and outside the exact-nine repair
> scope. No checkpoint, R2, repair, stage, commit or push followed. The
> governance preamble was compacted without changing the stable handoff suffix,
> archive pointer or BUILD candidate; amended A16 also makes the four-Markdown
> ceiling a pre-repair assertion. This fresh re-review records F1 closure and
> supersedes only the initial disposition.

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk / phase: `R2 / WORK_ORDER`
- Amendment 16 SHA-256 reviewed:
  `076032a3f1c5ed3943c574a894dff90cb887ec8b36d78af37e7d3f96427f3162`
- Superseded initial Amendment 16 SHA-256:
  `b253c568a27aba5cb1140481f74d2787062481075bd082c25c78a2bb982c6b2b`
- Parent Amendment 15 SHA-256:
  `19e1369d52d1fa65a5bff674fe8a24116767ffcbcf7b84de7340d2fccaced28c`
- Amendment 15 authorization review SHA-256:
  `738a08b767b730c0efe2ee42cc124538f470e073d930b1f6b62b3e4a6275dadb`
- Review baseline:
  `HEAD == origin/main == a6e82e1696825e966fe3164854b56a6d05fdbed9`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 16 correctly records the consumed Amendment 15 invocation and fixes
the archive-path identity that caused its first preflight failure. The exact
32/staged-zero candidate, stable 30, protected 21, nine repair pre-hashes,
archive identities and retained suffixes all reproduce. The nine-path repair
scope and ordered zero-call/no-retry gates remain substantively sufficient and
non-expansive.

The governance-only compaction reduces the current active handoff to `579`
lines while preserving its stable two-line suffix, archive pointer and BUILD
candidate. Amended A16 explicitly checks the canonical memory, active handoff
and both archives are each at most 600 lines in preflight, before any repair.
The previously impossible final line gate is therefore executable and bounded.

`A16-AUTH-F1`: `CLOSED_WITHOUT_WAIVER`.
Open authorization findings: `NONE`. Waivers: `NONE`.

This PASS does not authorize repair by itself. The exact-six governance-only
authority checkpoint must be pushed and a fresh exact Amendment 16 human R2
must authorize the one permitted invocation.

## Consumed Amendment 15 invocation

Git and canonical continuity reproduce the bounded failure sequence:

- acknowledgment checkpoint
  `a6e82e1696825e966fe3164854b56a6d05fdbed9` is pushed and is both `HEAD` and
  `origin/main`;
- the first preflight passed authority lineage, artifact hashes, exact 32,
  staged zero, stable 30, protected 21 and all nine repair pre-hashes;
- it then stopped on the nonexistent memory-archive literal
  `SESSION/archive/SESSION_MEMORY_P3A_REFINERY_PRE_ROTATION_2026-08-04.md`;
- no repair path changed, no probe/test/later gate ran, no retry occurred and
  provider/network/remote-ingest calls remained zero.

The candidate bytes and all nine pre-hashes remain unchanged, so Amendment 15
and its fresh R2 are consumed at that failed first invocation and cannot be
reused.

## Fresh binding reproduction

The authority-preparation worktree contains exact `36` dirty paths: the exact
32 BUILD/continuity candidate plus Amendment 16, this review and the canonical/
mirror state paths. Excluding those four governance paths reproduces exact 32. Excluding
the two volatile continuity front doors from exact 32 reproduces stable 30.
Excluding Amendment 15's exact nine repair paths from stable 30 reproduces
protected 21. The staged set is empty.

Ordinal case-sensitive sorting and UTF-8 records encoded as
`path + NUL + lowercase_file_sha256 + LF` reproduce:

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

## Archive identity and retained-boundary review

Amendment 16 supplies the correct canonical identities and exact bytes:

| Archive | Lines | SHA-256 | Result |
|---|---:|---|---|
| `SESSION/archive/SESSION_MEMORY_2026-07-22_TO_2026-07-31.md` | `335` | `e218cbc150d03bd9c42f623f972e43ee33ee00b530882195e2c8c145ab918f86` | `PASS` |
| `SESSION/handoffs/archive/AGENT_HANDOFF_2026-08-03_P3A_REFINERY_FOUNDATION.md` | `394` | `c50d4bfd7c7745fa1bb3e5758eddb57c905f5d10fac5da5fda8707f63aee0d44` | `PASS` |

Both relative archive pointers resolve. The immutable memory suffix remains
`243` lines / `6a055880ab97e542fa122ff6cbe3025d993aa521d3b4e9098abf82fa97237ac6`.
The immutable handoff suffix remains `2` lines /
`46f46615b06dff42a2c44b55321e30c862881146a58a98549fe06f06aaceb357`.

The memory front door is `309` lines, the active handoff is `579`, and both
archives are `335/394`; all four are below `600`. The repository file-size
guard independently returns `FILE SIZE GUARD: PASS`.

## A16-AUTH-F1 closure — active-handoff line ceiling

Status: `CLOSED_WITHOUT_WAIVER`; waiver: `NONE`.

Amendment 15 and Amendment 16 require the final line audit to retain all four
Markdown surfaces at or below `600` lines. The repair meets the finding without
expanding the BUILD repair set: only the volatile governance preamble was
compacted before checkpoint, and the current handoff is `579` lines. The
stable two-line suffix still hashes to `46f46615…b357`; the relative foundation
archive pointer resolves; the foundation archive remains `394/c50d4bfd…d44`;
and exact32/stable30/protected21 plus every nine-path pre-hash remain unchanged.

Amended A16 now makes all four line ceilings an explicit pre-repair assertion
alongside exact archive/suffix hashes. Any authority/R2 preamble growth that
crosses the ceiling stops the invocation before repair. This closes F1 without
an exception, debt entry, tenth repair path or waiver.

## Scope, gates and claim boundary

With F1 closed, Amendment 16 is sufficient and non-expansive. It changes only
the failed archive-path literal and retains Amendment 15's exact nine already-
dirty repair paths. Those paths remain sufficient for the four final-review
defects, AC-03/05/06/07 evidence, implementation-status truth and the derived
knowledge-manifest pin. The protected 21, contracts, fixtures, archives,
catalog and project-context surfaces remain immutable.

The continuation order is fail-closed: corrected preflight; exact-nine repair;
four-case direct probe; explicit five-file focused suite with at least 57
cases; knowledge validation/focused suite; file-size and non-mutating catalog
check; full non-live suite; repository/static checks; final exact-scope,
integrity and claim-boundary audit. Every step runs once, stops at the first
failure and permits zero provider/network/remote-ingest calls.

PASS can yield only a dirty exact-32 deterministic-local candidate pending
fresh independent BUILD review. It cannot authorize BUILD commit, self-review,
FREEZE, runtime activation, provider/ingest/persistence or a P3-A/Phase-3 claim.

## Exact authority checkpoint and fresh R2

The authority checkpoint must partial-stage and push exactly these six
governance paths while preserving the exact-32 candidate dirty and unstaged:

1. `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_16.md`
2. `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_16_AUTHORIZATION_REVIEW.md`
3. `SESSION/ACTIVE_SESSION_STATE.json`
4. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
5. only the new A16/review governance preamble hunks in
   `SESSION/SESSION_MEMORY.md`
6. only the new A16/review governance preamble hunks in
   `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`

The cached diff must exclude every BUILD repair, rotation/archive, source and
historical-continuity hunk. After push, staged paths must be zero and all
exact-32/stable-30/protected-21/archive/suffix bindings must reproduce.

Only then may the operator supply this fresh exact acknowledgment:

> Tôi phê duyệt R2 cho
> P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-16-2026-08-04, Work Order Amendment
> SHA-256 `076032a3f1c5ed3943c574a894dff90cb887ec8b36d78af37e7d3f96427f3162`, đúng 9 repair paths và final
> exact 32 BUILD/continuity paths, zero provider/network/remote-ingest calls.

That future R2 may authorize exactly one invocation, with no retry. Its
four-path acknowledgment checkpoint must contain only canonical state, mirror
and the new R2 preamble hunks in memory/handoff. No other path is authorized.
