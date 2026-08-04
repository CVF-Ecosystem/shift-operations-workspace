# P3-A Refinery Work Order Amendment 20 — Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk / phase: `R2 / WORK_ORDER`
- Amendment reviewed:
  `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_20.md`
- Reviewed SHA-256:
  `58b576d779dec3e3b1a934f24f2b90e4b18910d5594c383c20f4eb8d3d6a38d4`
- Provider/network/remote-ingest calls during review: `0/0/0`
- Findings: `NONE`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 20 is a necessary, sufficient and non-expansive repair for the
consumed A19 newline-translation stop. It authorizes only binary LF
normalization of the two already-dirty generated catalog surfaces, retains the
exact32 candidate and every protected semantic/output binding, and orders only
the still-due gates. This PASS is authorization-review evidence only. It is not
repair authority, BUILD evidence, a BUILD commit, independent BUILD review,
FREEZE or later-lane authority.

## Governance and consumed-A19 truth

Canonical memory, state, mirror and active handoff agree on A19's consumed
disposition. A19 preflight and its exact-three write completed; the first
post-hash assertion then failed on the registry raw hash and execution stopped.
Knowledge, focused, catalog, full and later gates remained `NOT_RUN`. No retry,
provider, network or remote-ingest call occurred.

A19 and its independent review reproduce at:

- Work Order:
  `3b78afc6492c19de192cae4f86ac0cda2234055f2e984b523a100e2b5ace11f7`;
- authorization review:
  `329c345464120bd8bf6e02a7f9427f3279949831d06a56963f27f27fbde5276d`.

Its authority checkpoint
`e802d1ba8dab5452383ff7bffa50b8f0de9ea9f6` and fresh-R2 acknowledgment
checkpoint `f3539a9da41c565f4163f3c9d14aab42fb7bbdfa` are ancestors of pushed
`origin/main`; current `HEAD == origin/main == f3539a9d…bdfa`. A19 and its R2
are consumed and grant no retry authority.

## Exact authoring scope and immutable candidate

Before this review artifact was created, the authoring worktree was exact35:
all exact32 retained candidate paths plus exactly A20, canonical state and its
compatibility mirror. Staged paths were zero.

Independent ordinal/case-sensitive manifest reproduction gives:

| Binding | Reproduced result |
|---|---|
| Exact candidate paths | `32` |
| Stable paths excluding memory/handoff | `30` |
| Stable30 manifest | `f9bcbbc6e0bed42283c7aad994f6b1563311bcb216954e80c81016ad8734e056` |
| Exact repair paths | `2` |
| Protected stable paths | `28` |
| Protected28 manifest | `0b87e6d8eec3d551d1106d1a5475bc45d845ecd0c39f9807786c5632e5f4e09e` |
| Staged paths | `0` |

`knowledge/manifest.json` is already final and immutable at
`cbf115da32e5ad9418f1d91678d2ec2f875e174ee434f5762648325f63da4f80`.
Its registry source pin names the required LF registry hash. The generator is
also immutable at
`fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b`.
Both are included in protected28; neither needs nor receives a repair touch.

## Raw and normalized byte reproduction

The exact-two raw bindings and newline inventories reproduce directly from
`Path.read_bytes()`:

| Path | Raw SHA-256 | CRLF | lone LF | CR |
|---|---|---:|---:|---:|
| `docs/catalog/MODULE_REGISTRY.json` | `9447544840c4f526d1d39769b63b84c4223ce689e2061e36a9416f9a4a741013` | `626` | `0` | `626` |
| `docs/catalog/MODULE_CATALOG.md` | `49a082972cbd4955e5932ed39f90390cb3bf281ca34dbe5a988498d2f9aaf995` | `324` | `0` | `324` |

In the payload's assertions, total `LF` counts equal the corresponding CRLF
counts (`626` and `324`), proving there are no lone LF bytes. Replacing only
`CRLF` with `LF` in memory leaves zero CR bytes and independently reproduces:

| Path | Required normalized-LF SHA-256 |
|---|---|
| `docs/catalog/MODULE_REGISTRY.json` | `1c1463d992a8ffe362059db3efded0a7a90664aebdbcec06bb9b13b922b7d727` |
| `docs/catalog/MODULE_CATALOG.md` | `32fe4ecbb7f7b493ba1536975d81aa95a895ca1424309dd580f232b8ee1bb484` |

The normalized bytes are exactly the A19-reviewed generated outputs. No
semantic catalog, manifest, generator, source, test, status, continuity,
archive, contract, fixture or dependency edit is necessary. The two catalog
paths are therefore both necessary and jointly sufficient.

## Payload and ordering review

The frozen PowerShell block parses with zero errors and its Python body
compiles. AST inspection confirms the payload has two ordered top-level loops:
the first reads and validates both files and performs zero writes; only after
that loop completes does the second loop perform direct `write_bytes` calls.
Thus both raw hashes and all newline counts fail closed before either file can
be mutated, and binary writes avoid host text-newline translation. No
generator, text-mode writer, formatter, `apply_patch` or manifest edit is
present or permitted.

The remaining gate order is sound: pushed authority and all immutable/raw
bindings precede normalization; exact posthash/scope/protected checks
immediately follow it; knowledge and focused gates precede the catalog check;
the full suite precedes repository/static/security checks; the complete final
audit is last. Each command runs at most once and stops on its first non-zero
or contract failure. A18 probe `4/4`, Refinery `57`, pre-repair Knowledge
validator/`86` and file-size PASS are retained without retry. The failed A19
post-hash assertion is not relabeled or rerun.

Archive hashes and line counts remain `335/e218cbc1…f86` and
`394/c50d4bfd…d44`; normalized suffixes remain `6a055880…ac6` and
`46f46615…b357`; each actual Markdown archive target resolves to its bound
archive. Memory is `327` lines and the active handoff is `596`, so all four
continuity/archive Markdown files remain at or below 600.

## Exact next authority boundary

COMMIT_STEWARD may next partial-stage, commit and push exactly these six
governance paths/hunks:

1. `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_20.md`;
2. `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_20_AUTHORIZATION_REVIEW.md`;
3. `SESSION/ACTIVE_SESSION_STATE.json`;
4. `CVF_SESSION/ACTIVE_SESSION_STATE.json`;
5. only the new A20/review governance preamble hunks in
   `SESSION/SESSION_MEMORY.md`;
6. only the new A20/review governance preamble/compaction hunks in
   `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`.

The front-door preamble hunks are separated from the retained candidate
rotation hunks, so partial staging is feasible. Because the handoff is already
596 lines, any review acknowledgment must compact only the volatile preamble
and preserve the stable suffix. The checkpoint must retain all exact32
candidate hunks unstaged, preserve protected28 and every bound hash, keep the
handoff at or below 600, and finish with staged zero. It authorizes no repair
by itself.

After that checkpoint is pushed, the required fresh human acknowledgment is:

> Tôi phê duyệt R2 cho
> P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-20-2026-08-04, Work Order Amendment
> SHA-256 58b576d779dec3e3b1a934f24f2b90e4b18910d5594c383c20f4eb8d3d6a38d4,
> đúng 2 repair paths và final exact 32 BUILD/continuity paths, zero
> provider/network/remote-ingest calls.

Only after that exact acknowledgment is recorded and pushed may one
`REPAIR_WORKER` run the A20 continuation once. Any mismatch or failed gate
consumes the invocation and requires a fresh governed disposition. No retry,
provider/network/remote-ingest/POST call, BUILD commit, self-review, FREEZE,
P3-B/P3-C, retrieval, RAG or learning authority is granted.
