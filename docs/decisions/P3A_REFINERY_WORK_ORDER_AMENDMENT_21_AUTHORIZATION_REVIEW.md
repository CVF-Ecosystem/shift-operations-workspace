# P3-A Refinery Work Order Amendment 21 — Authorization Review

## Fresh re-review of amended A21 — PASS

- Re-review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization re-review)
- Risk / phase: `R2 / WORK_ORDER`
- Amended A21 SHA-256 reviewed:
  `f6fa72b3a8e7a19654c6181242b2b2a7bb5ce20523d9913a84f38094afa4040c`
- Initial review SHA-256:
  `4d9f5f91c386fddfedb36e7faa8caff889b205e04e4cbc8267268796b34f8d49`
- Provider/network/remote-ingest calls during re-review: `0/0/0`
- Findings: `NONE`
- Waivers: `NONE`

### Current disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REREVIEW_PASS`

`A21-AUTH-F1` is `CLOSED_WITHOUT_WAIVER`. No open authorization finding
remains. The amended topology is executable, non-self-referential and binds
the acknowledgment checkpoint by dynamic Git structure plus exact committed
canonical content, without any expected, guessed or embedded future
acknowledgment hash.

### Executable acknowledgment topology

The amended preflight requires all of the following after the future A21 R2
checkpoint is pushed:

1. dynamically verify `HEAD == origin/main`;
2. read committed canonical state with
   `git show HEAD:SESSION/ACTIVE_SESSION_STATE.json`;
3. verify exact A21 `freshR2Accepted=true`, exact fresh R2 text, bound A21 and
   review hashes, `invocationConsumed=false` and
   `acknowledgmentCheckpointStatus=PENDING_COMMIT_PUSH`;
4. verify `HEAD^` equals the `authorityCheckpointCommit` recorded in that
   committed state;
5. verify `git diff-tree HEAD^ HEAD` contains exactly:
   - `CVF_SESSION/ACTIVE_SESSION_STATE.json`;
   - `SESSION/ACTIVE_SESSION_STATE.json`;
   - `SESSION/SESSION_MEMORY.md`;
   - `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`.

This is mechanically feasible and closes the self-hash defect. The commit
hash is actual dynamic `HEAD`; it is not stored inside that same commit. The
committed state instead binds the exact acknowledgment content, reviewed
authority parent and pre-push status. Current pushed A20 history independently
reproduces this topology as a concrete analog:

- `HEAD == origin/main == d5e4a7bb6a5f96933be28260384fec5e544c0bc5`;
- `HEAD^ == 227a385045bc7a8db0a67d9a5e26cbce27d8ccf6`;
- diff-tree is exactly the same four acknowledgment paths listed above;
- canonical state committed at `HEAD` contains A20
  `freshR2Accepted=true`, the exact R2 text, bound A20/review hashes,
  `authorityCheckpointCommit=227a3850…ccf6`,
  `invocationConsumed=false` and `PENDING_COMMIT_PUSH`.

No uncommitted state and no post-push self-hash receipt is used as execution
authority.

### Reproduced retained evidence

The amended A21 hash matches both the requested byte binding and canonical
state. Before this in-place re-review update, the worktree was exact36: all
exact32 candidate paths plus exactly amended A21, this review, canonical state
and mirror. Staged paths were zero.

| Binding | Reproduced result |
|---|---|
| Exact candidate paths | `32` |
| Stable paths | `30` |
| Stable30 manifest | `f9bcbbc6e0bed42283c7aad994f6b1563311bcb216954e80c81016ad8734e056` |
| Exact repair paths | `2` |
| Protected paths | `28` |
| Protected28 manifest | `0b87e6d8eec3d551d1106d1a5475bc45d845ecd0c39f9807786c5632e5f4e09e` |
| Staged paths | `0` |

Registry remains raw
`9447544840c4f526d1d39769b63b84c4223ce689e2061e36a9416f9a4a741013`
with `626` CRLF and no lone LF; catalog remains raw
`49a082972cbd4955e5932ed39f90390cb3bf281ca34dbe5a988498d2f9aaf995`
with `324` CRLF and no lone LF. Read-only normalization reproduces required
post-hashes `1c1463d9…d727` and `32fe4ecb…484`, leaving zero CR bytes.

`knowledge/manifest.json` remains immutable at
`cbf115da32e5ad9418f1d91678d2ec2f875e174ee434f5762648325f63da4f80`;
the generator remains immutable at
`fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b`.
All retained A18 output/archive/suffix/link/line bindings reproduce. Memory is
`331` lines and the active handoff is `595`, below the 600-line ceiling.

The exact-two binary payload and ordered continuation are unchanged: verify
both raw files before either binary write; immediately verify posthash/scope/
protected bindings; then run knowledge, focused, catalog, full and remaining
repository/static/security gates; run the complete final audit last. Every
step remains one-shot, stop-first/no-retry and zero
provider/network/remote-ingest/POST calls. Retained A18 passes are not rerun,
and the consumed A20 preflight failure is not retried or relabeled.

### Exact next authority boundary

COMMIT_STEWARD may next partial-stage, commit and push exactly six governance
paths/hunks:

1. `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_21.md`;
2. `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_21_AUTHORIZATION_REVIEW.md`;
3. `SESSION/ACTIVE_SESSION_STATE.json`;
4. `CVF_SESSION/ACTIVE_SESSION_STATE.json`;
5. only amended-A21/re-review governance preamble hunks in
   `SESSION/SESSION_MEMORY.md`;
6. only amended-A21/re-review governance preamble/compaction hunks in
   `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`.

The checkpoint must preserve exact32 unstaged, protected28 and every byte
binding, keep the handoff at or below 600, and finish staged zero. It grants no
repair authority by itself.

After that authority checkpoint is pushed, the exact fresh human R2 is:

> Tôi phê duyệt R2 cho
> P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-21-2026-08-04, Work Order Amendment
> SHA-256 f6fa72b3a8e7a19654c6181242b2b2a7bb5ce20523d9913a84f38094afa4040c,
> đúng 2 repair paths và final exact 32 BUILD/continuity paths, zero
> provider/network/remote-ingest calls.

The subsequent acknowledgment commit must change exactly the four continuity
paths listed in the topology above and commit exact R2 state with
`PENDING_COMMIT_PUSH`. Only then may one `REPAIR_WORKER` run the A21
continuation once. No BUILD commit, self-review, FREEZE, P3-B/P3-C, retrieval,
RAG, learning or production claim is authorized.

## Initial CHANGES_REQUIRED review (preserved)

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk / phase: `R2 / WORK_ORDER`
- Amendment reviewed:
  `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_21.md`
- Reviewed SHA-256:
  `9d2c836272a62e60f6646141b6f953a3069f1da15a0276ef75a72e69b652bd8b`
- Provider/network/remote-ingest calls during review: `0/0/0`
- Findings: `A21-AUTH-F1`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_CHANGES_REQUIRED`

A21 correctly retains the exact-two LF payload, exact32 candidate and all
immutable byte/scope/gate boundaries, but its replacement acknowledgment
lineage rule is not executable. The proposed pushed canonical-state source is
self-referential when it is required to contain the hash of the same commit
that contains that state. `A21-AUTH-F1` remains open with no waiver.

No authority checkpoint, fresh R2, repair, later gate, BUILD commit,
self-review, FREEZE or later-lane action is authorized from this disposition.

## Consumed A20 truth and pushed lineage

Canonical memory, active state, mirror and handoff agree that A20 is consumed.
Its two Git lineage commands passed. The next Python preflight stopped at line
13 because an unreviewed runner literal guessed
`d5e4a7b78d56713acde35ba33a562da1d72d274e` instead of the pushed
acknowledgment commit
`d5e4a7bb6a5f96933be28260384fec5e544c0bc5`. No catalog byte changed; later
preflight assertions and all later gates remained `NOT_RUN`; no retry,
provider, network or remote-ingest call occurred.

A20 and its review reproduce at:

- Work Order:
  `58b576d779dec3e3b1a934f24f2b90e4b18910d5594c383c20f4eb8d3d6a38d4`;
- review:
  `8711138128b52140c79c9f3fc2107bad95ec046b9cc345257c4be028ff6dfbc4`.

The exact authority checkpoint
`227a385045bc7a8db0a67d9a5e26cbce27d8ccf6` and exact acknowledgment
checkpoint `d5e4a7bb6a5f96933be28260384fec5e544c0bc5` both exist and are ancestors
of pushed `origin/main`. Current
`HEAD == origin/main == d5e4a7bb6a5f96933be28260384fec5e544c0bc5`.
The acknowledgment commit's parent is the authority checkpoint, matching the
required two-commit topology.

## Independently reproduced retained evidence

Before this review artifact was created, the authoring worktree was exact35:
all exact32 retained candidate paths plus exactly A21, canonical state and its
compatibility mirror. Staged paths were zero.

| Binding | Reproduced result |
|---|---|
| A21 SHA-256 | `9d2c836272a62e60f6646141b6f953a3069f1da15a0276ef75a72e69b652bd8b` |
| Exact candidate paths | `32` |
| Stable paths | `30` |
| Stable30 manifest | `f9bcbbc6e0bed42283c7aad994f6b1563311bcb216954e80c81016ad8734e056` |
| Exact repair paths | `2` |
| Protected paths | `28` |
| Protected28 manifest | `0b87e6d8eec3d551d1106d1a5475bc45d845ecd0c39f9807786c5632e5f4e09e` |
| Staged paths | `0` |

The exact-two raw and normalized bindings remain unchanged:

| Path | Raw SHA-256 | CRLF / lone LF | Required LF SHA-256 |
|---|---|---:|---|
| `docs/catalog/MODULE_REGISTRY.json` | `9447544840c4f526d1d39769b63b84c4223ce689e2061e36a9416f9a4a741013` | `626 / 0` | `1c1463d992a8ffe362059db3efded0a7a90664aebdbcec06bb9b13b922b7d727` |
| `docs/catalog/MODULE_CATALOG.md` | `49a082972cbd4955e5932ed39f90390cb3bf281ca34dbe5a988498d2f9aaf995` | `324 / 0` | `32fe4ecbb7f7b493ba1536975d81aa95a895ca1424309dd580f232b8ee1bb484` |

Both raw files contain no lone LF. Replacing only CRLF with LF in memory
reproduces both required post-hashes and leaves zero CR bytes.
`knowledge/manifest.json` remains immutable at
`cbf115da32e5ad9418f1d91678d2ec2f875e174ee434f5762648325f63da4f80`;
the generator remains immutable at
`fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b`.
All retained A18 output/archive/suffix/link/line bindings reproduce. The active
handoff is `594` lines, below its 600-line ceiling.

The retained exact-two payload and gate sequence remain sufficient: both
files are read and verified before any binary write; posthash/scope/protected
checks immediately follow normalization; knowledge, catalog, full and
repository/static/security gates retain their reviewed order; final audit is
last. All remain one-shot, stop-first/no-retry and zero
provider/network/remote-ingest/POST calls.

## A21-AUTH-F1 — future acknowledgment hash cannot be read from itself

Status: `OPEN`; waiver: `NONE`.

A21 requires the future A21 acknowledgment commit hash to be read from the
“pushed canonical state” and then compared to actual `HEAD`/`origin/main`.
That cannot be satisfied by the acknowledgment commit itself: a Git commit's
hash depends on the tree containing the canonical-state bytes, so those bytes
cannot already contain that same commit's hash.

Current A20 history demonstrates the issue directly. The pushed A20
acknowledgment commit is `d5e4a7bb…0bc5`, but:

```text
git show HEAD:SESSION/ACTIVE_SESSION_STATE.json
  -> acknowledgmentCheckpointStatus = PENDING_COMMIT_PUSH
```

Only the current uncommitted post-failure state says
`PUSHED_d5e4a7bb…0bc5`. Reading that working-tree value would not establish
that it was pushed, and it would leave canonical state as an extra dirty path,
contradicting A21's final exact32 boundary.

Required repair: define one executable, non-self-referential topology. The
minimal option is to verify dynamically that `HEAD == origin/main`, prove
`HEAD^` is the pushed A21 authority checkpoint, and inspect the canonical
state committed at `HEAD` for exact `freshR2Accepted=true`, exact A21 R2 text,
bound A21/review hashes, the authority-checkpoint value, and the expected
pre-push acknowledgment status. The runner then uses actual `HEAD` as the
acknowledgment commit without any guessed or embedded hash. Alternatively,
authorize a distinct later receipt commit that records the acknowledgment
hash and make the runner verify that explicitly different commit topology.

A21 must freeze one of those rules and receive fresh independent review. It
must not require a commit to contain its own hash, and it must not source
authority from uncommitted state.

## Claim and next-authority boundary

The exact-two binary normalization remains technically approved as retained
design, but it is not executable authority while F1 is open. WORK_ORDER_AUTHOR
may change only the A21 lineage contract and the bounded governance continuity
needed to describe it; no catalog, manifest, generator, source, test or other
exact32 byte may change. After repair, a fresh independent review must
reproduce the unchanged exact2/exact32/stable30/protected28 bindings and the
new executable lineage topology before any checkpoint or R2 request.

This review makes no BUILD PASS, P3-A closure, runtime wiring, provider,
remote-ingest, persistence, data-scope, retrieval/RAG, learning, production or
Phase 3 completion claim.
