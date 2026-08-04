# P3-A Refinery Work Order Amendment 23 — Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk / phase: `R2 / WORK_ORDER`
- Amendment reviewed:
  `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_23.md`
- Reviewed SHA-256:
  `98825deb5c9b68f3c2112020255820991dbe86b136ce8dc69fa2353d2ad00d63`
- Provider/network/remote-ingest calls during review: `0/0/0`
- Findings: `NONE`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 23 is a necessary, sufficient and non-expansive execution-
infrastructure correction for the consumed A22 runner timeout. It changes
only the outer command ceiling from the failed 120-second value to a minimum
of 600 seconds and requires `PYTHONUNBUFFERED=1` plus step markers. It does
not change the exact-two payload, dynamic acknowledgment topology, ASCII R2
binding, candidate scope, gate order, stop-first/no-retry semantics or
zero-call boundary.

This PASS is authorization-review evidence only. It is not repair authority,
BUILD evidence, a BUILD commit, independent BUILD review, FREEZE or
later-lane authority.

## Consumed A22 timeout truth

Canonical memory, active state, compatibility mirror and active handoff agree
that A22 is consumed. Its single outer runner had a 120-second ceiling and was
terminated while pytest warning output was active, returning exit `124`; the
stdout flush raised `OSError 22`. No conclusive per-step PASS markers or
complete result transcript survived, so no A22 repair or gate result is
retained or relabeled.

Read-only post-stop verification reproduces the fail-closed state:

- no pytest process remains;
- both repair paths remain at their original raw CRLF pre-hashes and counts;
- the dirty candidate remains exact32 and staged paths remain zero;
- no retry, provider, network or remote-ingest call occurred.

A22 and its review reproduce at:

- Work Order:
  `59ba66ea9bb48032f50a910f3919fe20cd373123e6de22543bb33ef2d7315e3e`;
- authorization review:
  `8da89d4f56c1233fdd231082b4463645da61732977516848364080e959eb4dff`.

Current pushed topology independently reproduces:

- `HEAD == origin/main == e3da80bcc32b8218b6e867d89d60ed2e1a53b1d1`;
- `HEAD^ == b226ac7d3df6a9bf9fab3a6496960d4ed3accd3a`, the committed
  A22 authority checkpoint;
- `HEAD` changes exactly the canonical state, mirror, memory and active-
  handoff acknowledgment paths;
- canonical state committed at `HEAD` contains exact A22 R2,
  `freshR2Accepted=true`, `invocationConsumed=false` and
  `acknowledgmentCheckpointStatus=PENDING_COMMIT_PUSH`.

A22 and its R2 grant no retry authority.

## Fresh A23 R2 and retained ASCII binding

The exact required one-line human acknowledgment is:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-23-2026-08-04, Work Order Amendment SHA-256 98825deb5c9b68f3c2112020255820991dbe86b136ce8dc69fa2353d2ad00d63, đúng 2 repair paths và final exact 32 BUILD/continuity paths, zero provider/network/remote-ingest calls.

Independent construction from the fixed template and reviewed A23 hash gives
`272` Unicode code points. SHA-256 over exactly its UTF-8 bytes, with no
leading/trailing whitespace and no newline, reproduces:

`2a86746c566de613701372f90c436651f6770cef54e86b51ea2cfe1ebd0daffa`

The future runner must retain A22's reviewed binding: read canonical state
from committed `HEAD`, parse `freshR2Acknowledgment`, encode that JSON string
as UTF-8, hash it and compare only with the lowercase ASCII digest above. No
Vietnamese expected literal, stdin transport, guessed acknowledgment commit
or self-hash is permitted. Dynamic `HEAD == origin/main`, parent-authority
and exact-four-path topology remains the commit-lineage proof.

## Reproduced exact scope and byte bindings

Before this review artifact was created, the authoring worktree was exact35:
all exact32 retained candidate paths plus exactly A23, canonical state and its
compatibility mirror. Staged paths were zero.

| Binding | Reproduced result |
|---|---|
| Exact candidate paths | `32` |
| Stable paths excluding memory/handoff | `30` |
| Stable30 manifest | `f9bcbbc6e0bed42283c7aad994f6b1563311bcb216954e80c81016ad8734e056` |
| Exact repair paths | `2` |
| Protected stable paths | `28` |
| Protected28 manifest | `0b87e6d8eec3d551d1106d1a5475bc45d845ecd0c39f9807786c5632e5f4e09e` |
| Staged paths | `0` |

The exact-two raw and read-only normalized bindings reproduce:

| Path | Raw SHA-256 | CRLF / lone LF / CR | Required LF SHA-256 |
|---|---|---:|---|
| `docs/catalog/MODULE_REGISTRY.json` | `9447544840c4f526d1d39769b63b84c4223ce689e2061e36a9416f9a4a741013` | `626 / 0 / 626` | `1c1463d992a8ffe362059db3efded0a7a90664aebdbcec06bb9b13b922b7d727` |
| `docs/catalog/MODULE_CATALOG.md` | `49a082972cbd4955e5932ed39f90390cb3bf281ca34dbe5a988498d2f9aaf995` | `324 / 0 / 324` | `32fe4ecbb7f7b493ba1536975d81aa95a895ca1424309dd580f232b8ee1bb484` |

Read-only CRLF-to-LF replacement leaves zero CR bytes and reproduces both
required post-hashes. `knowledge/manifest.json` remains immutable at
`cbf115da32e5ad9418f1d91678d2ec2f875e174ee434f5762648325f63da4f80`;
the generator remains immutable at
`fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b`.

Retained archive hashes/line counts remain
`e218cbc150d03bd9c42f623f972e43ee33ee00b530882195e2c8c145ab918f86/335`
and
`c50d4bfd7c7745fa1bb3e5758eddb57c905f5d10fac5da5fda8707f63aee0d44/394`.
Normalized memory/handoff suffixes reproduce at
`6a055880ab97e542fa122ff6cbe3025d993aa521d3b4e9098abf82fa97237ac6`
and
`46f46615b06dff42a2c44b55321e30c862881146a58a98549fe06f06aaceb357`;
both actual archive links resolve. Memory is `337` lines and the active
handoff is `594`, within the 600-line ceiling.

## Runner ceiling, ordering and stop boundary

A minimum 600-second outer ceiling is sufficient and proportionate for the
same bounded local continuation that previously reached the full pytest stage
before the 120-second orchestration ceiling. It provides five times the failed
ceiling without adding a command, payload, retry or provider call.
`PYTHONUNBUFFERED=1` and explicit step markers make completed output available
incrementally and reduce the risk that a later transport failure erases the
location of the first failure. They do not convert partial output into PASS:
only a completed zero-exit step may be retained.

The runner must set the environment variable before launch and configure the
actual outer tool/command timeout to at least 600 seconds. An inner timeout or
a textual assertion of 600 seconds is insufficient. If that outer ceiling is
still exceeded, the A23 invocation is consumed and requires a new governed
disposition; it must not be extended or retried in place.

The A22-reviewed all-reads-before-any-write binary payload remains mandatory.
After exact-two normalization, immediate posthash/zero-CR/exact32/protected28
checks precede the Knowledge validator, focused suite, catalog check, full
non-live suite, remaining repository/static/security gates and final complete
audit, in that order. The final audit remains last. Every step is one-shot,
stop-first/no-retry. No provider/network/remote-ingest/POST call, alternate
payload, helper, BUILD commit, self-review, FREEZE, waiver, debt or later-lane
expansion is authorized.

## Exact next authority boundary

COMMIT_STEWARD may next partial-stage, commit and push exactly six governance
paths/hunks:

1. `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_23.md`;
2. `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_23_AUTHORIZATION_REVIEW.md`;
3. `SESSION/ACTIVE_SESSION_STATE.json`;
4. `CVF_SESSION/ACTIVE_SESSION_STATE.json`;
5. only A23/review governance preamble hunks in
   `SESSION/SESSION_MEMORY.md`;
6. only A23/review governance preamble/compaction hunks in
   `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`.

The checkpoint must preserve exact32 candidate hunks unstaged, protected28
and every byte binding, retain stable suffixes/archive links, keep the handoff
at or below 600 lines and finish staged zero. It grants no repair authority by
itself.

After that authority checkpoint is pushed, the human must provide the exact
fresh A23 acknowledgment above. Its acknowledgment checkpoint must change
exactly the four continuity paths, commit exact R2 state with
`freshR2Accepted=true`, `invocationConsumed=false` and
`PENDING_COMMIT_PUSH`, and be pushed. Only then may one `REPAIR_WORKER` launch
one A23 outer runner under the reviewed timeout/unbuffered contract.

This review makes no BUILD PASS, P3-A closure, runtime wiring, provider,
remote-ingest, persistence, data-scope, retrieval/RAG, learning, production
or Phase 3 completion claim.
