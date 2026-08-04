# P3-A Refinery Work Order Amendment 18 — Independent Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk / phase: `R2 / WORK_ORDER`
- Amendment 18 SHA-256 reviewed:
  `227357fa076756d9a0f8adf861c728c6937891b2a8e43db9c11a71bbd437b3cf`
- Parent A17 SHA-256:
  `01e6392dfc72c257d121091466e221431e5cb43c2ed8e2dd211499dddcef1a7c`
- A17 authorization review SHA-256:
  `a0c670c6f00d6826b32338fd270378440e807f95bf58ec7177bdf9eeafe3519d`
- Review baseline:
  `HEAD == origin/main == f775b7c4b3d32872c24fc5b8518109c8797e5764`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_CHANGES_REQUIRED`

A18 correctly consumes A17, removes the failed read-inventory command and
retains a sufficient exact-nine/final-exact32 repair ceiling. Its source repair
directions for final-review F1/F2 and its exact status/pin partition for F4 are
minimal and technically feasible on the inspected current code.

Authorization nevertheless cannot pass because A18 requires a precomputed
atomic patch and direct commands from a reviewed execution sheet, but no such
sheet, payload, path or digest exists in the authority set. Separately, the
test contract's “at least four” collected cases does not enumerate a complete,
testable AC-03/05/06/07 matrix and therefore does not establish closure of F3.

Open authorization findings: `A18-AUTH-F1`, `A18-AUTH-F2`.
Waivers: `NONE`.

No authority checkpoint, fresh R2, repair, probe, gate, BUILD commit,
self-review, FREEZE or later-lane action is authorized by this disposition.

## Consumed A17 truth

Git and canonical continuity consistently establish:

- A17 authority checkpoint `6ab305610c9065dbc0590ac8727bc67e6ccdf6ba`
  and fresh-R2 acknowledgment checkpoint
  `f775b7c4b3d32872c24fc5b8518109c8797e5764` are pushed;
- A17's canonical multiline preflight passed;
- its first post-preflight command then failed PowerShell parsing at
  `foreach($p in$paths)` while preparing a read-only source/test inventory;
- parsing failed before that command read any file;
- no repair file, probe, test or later gate ran: repair touches are `0/9`,
  staged paths are zero, no retry occurred and calls remained zero.

A17 and its fresh R2 are consumed by that first invocation and cannot be
retried. All candidate bytes remain at the A15 pre-repair hashes.

## Fresh immutable-binding reproduction

Before creation of this review artifact, the authority-preparation worktree
contained exact `35` dirty paths: the exact32 BUILD/continuity candidate plus
A18 and canonical/mirror state. Excluding those three governance paths gives
exact32. Excluding only the two volatile continuity front doors gives stable30;
excluding the exact nine repair paths gives protected21. Staged paths are zero.

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

## Archive, suffix and line reproduction

| Surface | Lines | Bound SHA-256 | Result |
|---|---:|---|---|
| canonical memory / stable suffix | `315 / 243` | `6a055880ab97e542fa122ff6cbe3025d993aa521d3b4e9098abf82fa97237ac6` | `PASS` |
| active handoff / stable suffix | `596 / 2` | `46f46615b06dff42a2c44b55321e30c862881146a58a98549fe06f06aaceb357` | `PASS` |
| memory archive | `335` | `e218cbc150d03bd9c42f623f972e43ee33ee00b530882195e2c8c145ab918f86` | `PASS` |
| handoff foundation archive | `394` | `c50d4bfd7c7745fa1bb3e5758eddb57c905f5d10fac5da5fda8707f63aee0d44` | `PASS` |

Both relative archive pointers resolve. All four Markdown surfaces are at or
below `600`; the repository file-size guard returns PASS. Any future authority
or R2 preamble must compact only volatile A17/A18 governance text as necessary,
preserve the two-line suffix and archive pointer, and keep the handoff at or
below 600.

## Source and final-review repair assessment

The reviewer inspected the final F1–F4 review, all three authorized source
files, all four authorized test files, `IMPLEMENTATION_STATUS.json` and the
project-context source pins in `knowledge/manifest.json`.

The source partition is sufficient and minimal:

- F1: `output_models.py` can validate result-level owner/link safety;
  `protection.py` can bind candidate control versions to the corresponding
  stage receipts and require a quarantined route to be available. No contract,
  receipt model or API change is needed.
- F2: `pipeline.py` can retain chronological internal selection while deriving
  one sorted-unique public match-id tuple for the stage receipt, duplicate
  receipt, result and counts. The dedupe algorithm need not change.
- F4: only `IMPLEMENTATION_STATUS.json.p3a_refinery` is stale; after correcting
  it, only its exact project-context source pin changes in
  `knowledge/manifest.json`. Registry/catalog/project-context content remains
  untouched.

Current line counts leave bounded repair room: source files are `202/260/285`
and test files are `158/48/120/213`, each below the applicable 300-line limit.
The requested exact-nine atomic patch is feasible without a tenth path.

## A18-AUTH-F1 — precomputed execution material is not bound

Status: `OPEN`; waiver: `NONE`.

A18 says its invocation will use one precomputed atomic `apply_patch` and
explicit probe/gate commands copied from a reviewed execution sheet. The only
A18 artifact present is the Work Order itself. It contains neither the exact
patch payload nor the exact direct commands and identifies no execution-sheet
path, SHA-256 or authority-checkpoint member.

Consequently the reviewer cannot verify before R2 that:

- the patch touches all and only exact nine paths atomically;
- its concrete edits implement the reviewed F1–F4 contract without extra
  semantics;
- the post-preflight sequence has no PowerShell control grammar, generated
  shell, hidden inventory, selector synthesis or recovery branch;
- each probe/gate command is direct, executable and ordered exactly once.

Required repair: embed the complete canonical patch blueprint and every exact
direct probe/gate command in A18 itself, or bind a dedicated execution-sheet
artifact by path and SHA and include it in the checkpoint. The material must be
frozen before fresh review; any later byte change requires another review.

## A18-AUTH-F2 — AC-03/05/06/07 evidence contract is under-specified

Status: `OPEN`; waiver: `NONE`.

Requiring “at least four” new collected cases across four files is a count, not
a testable closure matrix. It permits four cases that omit required assertions
while still satisfying the literal threshold. A18 does not enumerate exact
case ids, inputs, recomputed bytes and expected outputs for:

- AC-03 dedupe-content golden bytes, candidate golden bytes and cross-type
  fingerprint substitution rejection;
- AC-05 repeated deterministic result bytes, stable invalid-envelope bytes and
  dedupe permutation invariance;
- AC-06 inclusive start/end edges, before/after-window exclusion, chronological
  multi-match selection and lexical public ids under permutations;
- AC-07 the complete relevant construction/receipt/exception/log/snapshot
  disclosure matrix, including all four final-review reproductions.

Required repair: the frozen A18 execution material must enumerate every case
and expected assertion, name its target authorized test file, set the exact
post-patch collected count or a strict minimum justified by that enumeration,
and bind the four-case direct probe separately from the focused suite.

## Retained gates and claim boundary

Subject to F1/F2 repair, the retained execution order is sound: immutable
preflight; one atomic exact-nine patch; direct four-case probe; explicit
five-file focused suite; local knowledge checks; file-size and non-mutating
catalog check; full non-live suite; repository/static/security checks; final
exact32/exact9/protected21/archive/suffix/line/staged audit.

The first failed parser, command or contract assertion must stop all later work
without retry. No provider/network/remote-ingest/POST/helper call, BUILD commit,
self-review, FREEZE, waiver, debt, scope expansion or later-lane action is
permitted. PASS can yield only a dirty exact32 local candidate pending fresh
independent BUILD review.

## Checkpoint disposition

No checkpoint or fresh R2 wording is issued while F1/F2 remain open. After
repair and fresh independent PASS, embed the execution material in A18 to keep
the intended checkpoint at exact six governance paths:

1. `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_18.md`
2. `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_18_AUTHORIZATION_REVIEW.md`
3. `SESSION/ACTIVE_SESSION_STATE.json`
4. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
5. only new A18/review governance preamble hunks in
   `SESSION/SESSION_MEMORY.md`
6. only new A18/review governance preamble/compaction hunks in
   `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`

If a separate execution-sheet path is chosen instead, it becomes a seventh
checkpoint path and the fresh review must enumerate it explicitly. In either
case cached staging must exclude every BUILD/repair/archive/history hunk,
preserve exact32 dirty and staged zero after push, and keep the handoff at or
below 600. Fresh exact R2 may be specified only by the future PASS artifact.
