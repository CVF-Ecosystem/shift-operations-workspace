# P3-A Refinery Work Order Amendment 22 — Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk / phase: `R2 / WORK_ORDER`
- Amendment reviewed:
  `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_22.md`
- Reviewed SHA-256:
  `59ba66ea9bb48032f50a910f3919fe20cd373123e6de22543bb33ef2d7315e3e`
- Provider/network/remote-ingest calls during review: `0/0/0`
- Findings: `NONE`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 22 is a necessary, sufficient and non-expansive correction to the
consumed A21 preflight. It replaces only the transport-sensitive direct
Unicode equality with a SHA-256 comparison over the UTF-8 encoding of the
acknowledgment value parsed from committed canonical JSON. The expected
digest is lowercase ASCII. Exact-two normalization, final exact32, all
immutable bindings and the remaining one-shot gate order are unchanged.

This PASS is authorization-review evidence only. It is not repair authority,
BUILD evidence, a BUILD commit, independent BUILD review, FREEZE or
later-lane authority.

## Consumed A21 truth and pushed topology

Canonical memory, active state, compatibility mirror and handoff agree that
A21 is consumed. Its dynamic topology and committed-state checks passed. The
next Python preflight assertion, line 12 of the consumed invocation, directly
compared the committed Vietnamese acknowledgment with a Unicode literal that
had crossed the PowerShell-to-Python stdin boundary and returned false.
Execution stopped before normalization. Both repair files remain at their
reviewed raw CRLF bindings; all later assertions and gates were `NOT_RUN`;
there was no retry, repair touch, provider, network or remote-ingest call.

A21 and its final review reproduce at:

- Work Order:
  `f6fa72b3a8e7a19654c6181242b2b2a7bb5ce20523d9913a84f38094afa4040c`;
- final authorization review:
  `98874fb2829b7109199f94b006a2c2ae4a39a5b8a4a1febd8ad83cbbc4453abe`.

Current Git topology independently reproduces:

- `HEAD == origin/main == 7daf89e7d3637c1268074f6a941bee7066863cad`;
- `HEAD^ == e78317f0eddf9a20a476cd6520b411d7dd81ab32`, the committed
  A21 `authorityCheckpointCommit`;
- both commits exist and are ancestors of `origin/main`;
- `git diff-tree HEAD^ HEAD` contains exactly the canonical state, mirror,
  memory and active-handoff acknowledgment paths;
- canonical state committed at `HEAD` contains exact A21 R2,
  `freshR2Accepted=true`, `invocationConsumed=false` and
  `acknowledgmentCheckpointStatus=PENDING_COMMIT_PUSH`.

Independent hashing of that committed A21 acknowledgment reproduces
`5a42f8d4b957617424e0bba693c9f5f31aa3b99f9711824a74f1525b9f7e1bf4`.
This confirms correct canonical content and isolates the failure to the
direct transported literal comparison. A21 and its R2 grant no retry.

## Exact fresh A22 acknowledgment and ASCII binding

The exact required one-line human acknowledgment is:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-22-2026-08-04, Work Order Amendment SHA-256 59ba66ea9bb48032f50a910f3919fe20cd373123e6de22543bb33ef2d7315e3e, đúng 2 repair paths và final exact 32 BUILD/continuity paths, zero provider/network/remote-ingest calls.

Independent construction from the fixed template and reviewed A22 hash gives
`272` Unicode code points. SHA-256 over exactly its UTF-8 bytes, with no
leading/trailing whitespace and no newline, reproduces:

`c8a976f2ae0e352708a08e9e4adcd9d985cfa65b38923b8d18bafe8f61d6d10c`

The future runner must read
`SESSION/ACTIVE_SESSION_STATE.json` from committed `HEAD`, parse
`freshR2Acknowledgment`, encode that JSON string as UTF-8, hash it and compare
only with the lowercase ASCII digest above. Its expected-value source and
command text must contain no Vietnamese acknowledgment literal. It must not
pipe either the literal or committed JSON through Python stdin, and must not
compare with an acknowledgment-commit literal or attempt a self-hash. An
ASCII-only `python -c` program reading `git show` through a subprocess is one
valid implementation. Dynamic `HEAD == origin/main`, parent-authority and
exact-four-path topology remains the commit-lineage proof.

## Reproduced exact scope and byte bindings

Before this review artifact was created, the authoring worktree was exact35:
all exact32 retained candidate paths plus exactly A22, canonical state and its
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

The exact-two bindings reproduce from raw bytes:

| Path | Raw SHA-256 | CRLF / lone LF / CR | Required LF SHA-256 |
|---|---|---:|---|
| `docs/catalog/MODULE_REGISTRY.json` | `9447544840c4f526d1d39769b63b84c4223ce689e2061e36a9416f9a4a741013` | `626 / 0 / 626` | `1c1463d992a8ffe362059db3efded0a7a90664aebdbcec06bb9b13b922b7d727` |
| `docs/catalog/MODULE_CATALOG.md` | `49a082972cbd4955e5932ed39f90390cb3bf281ca34dbe5a988498d2f9aaf995` | `324 / 0 / 324` | `32fe4ecbb7f7b493ba1536975d81aa95a895ca1424309dd580f232b8ee1bb484` |

Read-only CRLF-to-LF replacement reproduces both required post-hashes and
leaves zero CR bytes. `knowledge/manifest.json` remains immutable at
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
both actual Markdown archive links resolve. Memory is `334` lines and the
active handoff is `594`, within the 600-line ceiling.

## Payload, ordering and stop boundary

The A21-reviewed binary payload remains mandatory: read and validate both raw
files before either write; then write only the two LF-normalized byte arrays.
Immediately verify post-hashes, zero CR, exact32, protected28 and immutable
bindings. Run the Knowledge validator, focused two-file suite, catalog check,
full non-live suite, remaining repository/static/security gates and complete
final audit in the retained order, with the final audit last.

Every assertion, payload and gate is one-shot and stop-first/no-retry. A18
probe `4/4`, Refinery `57`, pre-repair Knowledge validator/`86` and file-size
PASS remain retained without rerun. A21 is not retried or relabeled. No
provider/network/remote-ingest/POST call, alternate payload, helper, BUILD
commit, self-review, FREEZE, waiver, debt or later-lane expansion is
authorized.

## Exact next authority boundary

COMMIT_STEWARD may next partial-stage, commit and push exactly six governance
paths/hunks:

1. `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_22.md`;
2. `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_22_AUTHORIZATION_REVIEW.md`;
3. `SESSION/ACTIVE_SESSION_STATE.json`;
4. `CVF_SESSION/ACTIVE_SESSION_STATE.json`;
5. only A22/review governance preamble hunks in
   `SESSION/SESSION_MEMORY.md`;
6. only A22/review governance preamble/compaction hunks in
   `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`.

The checkpoint must preserve exact32 candidate hunks unstaged, protected28
and every byte binding, retain the stable suffix/archive links, keep the
handoff at or below 600 lines and finish staged zero. It grants no repair
authority by itself.

After that authority checkpoint is pushed, the human must provide the exact
fresh A22 acknowledgment above. The acknowledgment checkpoint must change
exactly the four continuity paths, commit the exact R2 value with
`freshR2Accepted=true`, `invocationConsumed=false` and
`PENDING_COMMIT_PUSH`, and be pushed. Only then may one `REPAIR_WORKER` run
the A22 continuation once under the ASCII-only digest rule. Any mismatch or
first failed assertion/gate consumes that invocation and requires a fresh
governed disposition.

This review makes no BUILD PASS, P3-A closure, runtime wiring, provider,
remote-ingest, persistence, data-scope, retrieval/RAG, learning, production
or Phase 3 completion claim.
