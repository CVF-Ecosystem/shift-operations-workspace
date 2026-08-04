# P3-A Refinery Work Order Amendment 24 — Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk / phase: `R2 / WORK_ORDER`
- Amendment reviewed:
  `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_24.md`
- Reviewed SHA-256:
  `cc4d481d128b07566628871a01667ddbc1d1a45c2bd4b65c20241290b1bef51a`
- Provider/network/remote-ingest calls during review: `0/0/0`
- Findings: `NONE`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 24 is a necessary, sufficient and non-expansive repair for the
consumed A23 full-suite failure. It makes the two canonical generator writes
platform-stable, makes the catalog-drift fixture restore exact original bytes,
and restores the two catalog artifacts to their already-reviewed LF bytes.
The exact four-path repair produces final exact34 without changing catalog
meaning, metrics, knowledge pins or any protected candidate byte.

This PASS is authorization-review evidence only. It is not repair authority,
BUILD evidence, a BUILD commit, independent BUILD review, FREEZE or
later-lane authority.

## Consumed A23 truth

Canonical memory, active state, compatibility mirror and active handoff agree
that A23 is consumed. Its retained markers establish PASS for preflight,
exact-two normalization and immediate post-audit, project Knowledge
validation, focused Knowledge Pack `86`, and catalog `--check`. The full
non-live suite then completed with exactly `2 failed / 1587 passed / 128
skipped / 8 errors`. The reported failures/errors carry
`KPK_ELIGIBILITY_MISMATCH` and `KPK_SOURCE_PIN_DRIFT` for
`PROJECT_CONTEXT.md`. Execution stopped at that full-suite failure; all later
gates were `NOT_RUN`. There was no retry, provider, network or remote-ingest
call.

A23 and its review reproduce at:

- Work Order:
  `98825deb5c9b68f3c2112020255820991dbe86b136ce8dc69fa2353d2ad00d63`;
- authorization review:
  `af32aff2af5003df5dfcc9131b25204f3f63baff9655560949da1ac1052d2ce8`.

Current pushed topology independently reproduces:

- `HEAD == origin/main == 9a62662f2f5578ce04f10e9146afe015dca2bd8e`;
- `HEAD^ == cd24315b9e10435abb9224cda75fa2d2c9a64052`, the committed
  A23 authority checkpoint;
- `HEAD` changes exactly the canonical state, mirror, memory and active-
  handoff acknowledgment paths;
- canonical state committed at `HEAD` contains exact A23 R2,
  `freshR2Accepted=true`, `invocationConsumed=false` and
  `acknowledgmentCheckpointStatus=PENDING_COMMIT_PUSH`.

A23 and its R2 grant no retry authority.

## Root cause and patch semantics

Post-stop read-only inspection finds both catalogs restored to the original
CRLF pre-hashes. This is consistent with the full-suite ordering and source:
the catalog-drift fixture snapshots LF catalogs using `read_text()` and later
restores the decoded strings using `write_text()` with the platform default
newline behavior. On Windows that teardown translates LF back to CRLF. The
Knowledge tests run later and correctly reject those byte-changed source pins.
The generator's two `write_text()` calls carry the same platform-dependent
write behavior.

The exact A24 patch is sufficient:

- adding `newline="\n"` to both generator writes keeps the generated registry
  and Markdown byte-stable at LF on Windows and other supported platforms;
- `Path.write_text` in the current interpreter exposes the `newline`
  parameter; `newline="\n"` writes LF without platform translation;
- changing the fixture backups to `read_bytes()` and teardown to
  `write_bytes()` restores exactly the bytes that existed before each
  negative probe, independent of platform newline rules;
- the negative probes themselves remain unchanged and still mutate real files
  temporarily, so test strength is not reduced;
- the reviewed patch changes no line count and adds no file. Generator/test
  LOC and code-file metrics therefore remain unchanged, and LF normalization
  changes only catalog line endings, not rendered content or metrics.

In-memory application of the exact diff independently reproduces the required
source/test hashes:

| Path | Pre SHA-256 | Required post SHA-256 | Lines before/after |
|---|---|---|---:|
| `scripts/generate_catalog.py` | `fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b` | `6a04502d0ef35e69225a5cb1fbd652c18db4d23814219c0e0cdb27792735b9b6` | `313 / 313` |
| `tests/integration/test_catalog_drift_detection.py` | `72e57f9ed304e358a977c514e1baa2648af155bea48b93bda00d2799322d9fa8` | `820e4f3bd5b299f341e511e15ecb0de2de7a3e49b28a68f1aa83eabd5aee791d` | `97 / 97` |

The patch must be applied once as the single exact two-source `apply_patch`
defined by A24. No alternate edit, refactor, formatter or helper is permitted.

## Fresh A24 R2 and ASCII binding

The exact required one-line human acknowledgment is:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-24-2026-08-04, Work Order Amendment SHA-256 cc4d481d128b07566628871a01667ddbc1d1a45c2bd4b65c20241290b1bef51a, đúng 4 repair paths và final exact 34 BUILD/continuity paths, zero provider/network/remote-ingest calls.

Independent construction from the fixed template and reviewed A24 hash gives
`272` Unicode code points. SHA-256 over exactly its UTF-8 bytes, with no
leading/trailing whitespace and no newline, reproduces:

`590b86e1e025f563f8723433044083b340af774e65d3ff9cc3b65c365d4e2f1d`

The future runner must retain the reviewed ASCII-only binding: read canonical
state from committed `HEAD`, parse `freshR2Acknowledgment`, encode the JSON
string as UTF-8, hash it and compare only with the lowercase ASCII digest
above. No Vietnamese expected literal, stdin transport, guessed
acknowledgment commit or self-hash is permitted. Dynamic
`HEAD == origin/main`, parent-authority and exact-four-path topology remains
the commit-lineage proof.

## Reproduced scope and retained bindings

Before this review artifact was created, the authoring worktree was exact35:
all retained exact32 candidate paths plus exactly A24, canonical state and its
compatibility mirror. Staged paths were zero. The two source/test paths are
currently clean and become the only additions to final exact34 after repair.

| Binding | Reproduced result |
|---|---|
| Retained candidate paths | `32` |
| Final candidate paths | `34` |
| Final additions | generator and catalog-drift test only |
| Exact repair paths | `4` |
| Stable30 manifest | `f9bcbbc6e0bed42283c7aad994f6b1563311bcb216954e80c81016ad8734e056` |
| Protected existing stable paths | `28` |
| Protected28 manifest | `0b87e6d8eec3d551d1106d1a5475bc45d845ecd0c39f9807786c5632e5f4e09e` |
| Staged paths | `0` |

The exact-two catalog bindings reproduce from current raw bytes:

| Path | Raw SHA-256 | CRLF / lone LF | Required LF SHA-256 |
|---|---|---:|---|
| `docs/catalog/MODULE_REGISTRY.json` | `9447544840c4f526d1d39769b63b84c4223ce689e2061e36a9416f9a4a741013` | `626 / 0` | `1c1463d992a8ffe362059db3efded0a7a90664aebdbcec06bb9b13b922b7d727` |
| `docs/catalog/MODULE_CATALOG.md` | `49a082972cbd4955e5932ed39f90390cb3bf281ca34dbe5a988498d2f9aaf995` | `324 / 0` | `32fe4ecbb7f7b493ba1536975d81aa95a895ca1424309dd580f232b8ee1bb484` |

Read-only CRLF-to-LF replacement reproduces both required catalog post-hashes
and leaves zero CR bytes. `knowledge/manifest.json` remains immutable at
`cbf115da32e5ad9418f1d91678d2ec2f875e174ee434f5762648325f63da4f80`.

Retained archive hashes/line counts remain
`e218cbc150d03bd9c42f623f972e43ee33ee00b530882195e2c8c145ab918f86/335`
and
`c50d4bfd7c7745fa1bb3e5758eddb57c905f5d10fac5da5fda8707f63aee0d44/394`.
Normalized memory/handoff suffixes reproduce at
`6a055880ab97e542fa122ff6cbe3025d993aa521d3b4e9098abf82fa97237ac6`
and
`46f46615b06dff42a2c44b55321e30c862881146a58a98549fe06f06aaceb357`;
both archive links resolve. Memory is `340` lines and the active handoff is
`594`, within the 600-line ceiling.

## Ordered continuation and stop boundary

The A24 runner must retain an actual outer timeout of at least 600 seconds,
set `PYTHONUNBUFFERED=1` before launch and expose step markers. It runs once,
stops at the first non-zero or contract failure and is never retried.

The required order is: dynamic authority and all prehash/scope/protected
checks; exact atomic two-source patch; reviewed all-reads-before-any-write
binary normalization of both catalogs; all four posthashes plus final
exact34/protected28/staged0 audit; focused catalog-drift tests; Knowledge
validator; focused Knowledge Pack suite; catalog check; full non-live suite;
remaining repository/static/security gates; final complete audit last.

This ordering proves the isolation repair before Knowledge and full-suite use,
and checks final scope immediately after all four writes. A23's completed
pre-failure PASS markers are retained without relabeling or rerun except for
the newly authorized A24 gates explicitly listed above. No provider/network/
remote-ingest/POST call, alternate payload, BUILD commit, self-review, FREEZE,
waiver, debt or later-lane expansion is authorized.

## Exact next authority boundary

COMMIT_STEWARD may next partial-stage, commit and push exactly six governance
paths/hunks:

1. `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_24.md`;
2. `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_24_AUTHORIZATION_REVIEW.md`;
3. `SESSION/ACTIVE_SESSION_STATE.json`;
4. `CVF_SESSION/ACTIVE_SESSION_STATE.json`;
5. only A24/review governance preamble hunks in
   `SESSION/SESSION_MEMORY.md`;
6. only A24/review governance preamble/compaction hunks in
   `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`.

The checkpoint must preserve retained exact32 candidate hunks unstaged,
protected28 and every byte binding, keep the generator/test at their prehashes,
retain stable suffixes/archive links, keep the handoff at or below 600 lines
and finish staged zero. It grants no repair authority by itself.

After that authority checkpoint is pushed, the human must provide the exact
fresh A24 acknowledgment above. Its acknowledgment checkpoint must change
exactly the four continuity paths, commit exact R2 state with
`freshR2Accepted=true`, `invocationConsumed=false` and
`PENDING_COMMIT_PUSH`, and be pushed. Only then may one `REPAIR_WORKER` launch
one A24 outer runner under the reviewed contract.

This review makes no BUILD PASS, P3-A closure, runtime wiring, provider,
remote-ingest, persistence, data-scope, retrieval/RAG, learning, production
or Phase 3 completion claim.
