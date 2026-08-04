# P3-A Refinery Work Order Amendment 10 — Authorization Re-review 2

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent fresh authorization re-review)
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Amendment 10 SHA-256: `6c396f1fc6faad345a5ae12d3d928e515d4c5bbf46a14b9743015740e1b2634b`
- Initial review SHA-256: `43dad00859cb906e446c1e6875dafedbc522e1374c070da195adcf22aa947a14`
- First re-review SHA-256: `4ed7b30f48f876337cbedd63074098104f6f9b4f1a979e4a54d3fd532f546b7f`
- Amendment 9 acknowledgment checkpoint: `be63d4505e8b79e96e849090f34462b9918ed550`
- Amendment 9 authority checkpoint: `422890062dbf5ee28346311abb6a2a4b13dee5f9`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 10 closes `A10-AUTH-F1` and `A10-AUTH-F2` without waiver. Its
normalized, marker-delimited archive-source bindings reproduce exactly and
remain invariant when the mandatory authorization-review and R2 records are
added only to the preambles. Exact Git checkpoint lineage bounds those
authority transitions, while any byte drift inside either archive-source block
changes its digest and stops BUILD preflight.

Open authorization findings: `NONE`. Waivers: `NONE`.

This PASS does not itself authorize repair. The reviewed authority checkpoint
must be committed/pushed and followed by Amendment 10's fresh exact human R2
acknowledgment before one no-retry continuation invocation may begin.

## F1/F2 closure and normalized block reproduction

The reviewer independently implemented the exact prescribed algorithm:
universal-newline normalization to LF; unique exact start/end markers;
selection of the start line through the line before the end marker, or through
EOF for the handoff; `"\n".join(selected_lines) + "\n"`; UTF-8 SHA-256.

| Archive-source block | Expected | Reproduced | Result |
|---|---|---|---|
| Memory: `**2026-07-22 (P-FIX-6):**` through before the continuity-drift heading | `331` lines / `d7d902ea4eef700310d999b1fb41ed62fefe6cf4b1a5f389ca86aae6fdfe348e` | same | `PASS` |
| Active handoff: `## Intake boundary` through EOF | `390` lines / `d8b6f8d8af9ac11856db1308ecc1e966900cc808ed0907475cd18b98b3c3ec14` | same | `PASS` |

Each marker has exactly one match and each boundary is ordered correctly. The
memory block currently begins after the volatile top/current-state preamble;
the active-handoff block begins after the complete current disposition and
Amendment 4-10 chain. Amendment 10 explicitly permits review/R2 entries only
before those markers. Therefore future mandatory review/R2 appends cannot
change either block digest, resolving F2, while inserting or editing anything
inside an archive-source block fails preflight.

The authority and acknowledgment checkpoints remain path-bounded governance
transitions whose actual pushed lineage is checked before BUILD. They cannot
silently authorize a BUILD/repair path. The normalized binding is deliberately
narrow only in ignoring the permitted preamble append; it fully binds every
byte that will be moved verbatim into each archive. F1's earlier whole-file
self-reference is absent and no hash depends on a file embedding that same
hash.

## Consumed Amendment 9 truth

Independent Git and continuity checks confirm:

- `HEAD == origin/main == be63d4505e8b79e96e849090f34462b9918ed550`;
- the Amendment 9 immutable exact-28/zero-repair preflight passed;
- the singular file-size guard then reported exactly `pipeline.py 304 > 300`,
  session memory `616 > 600`, and active handoff `724 > 600`;
- execution stopped on that first non-zero gate; it was not retried and no
  repository/static/final gate ran;
- provider/network/remote-ingest calls were `0/0/0`.

Amendment 9 and its R2 are consumed. Amendment 10's post-repair file-size run
is a fresh differently scoped gate, not a retry or relabeling of the failed
pre-repair command.

## Retained BUILD binding and repair inputs

Using typed `string[]` collections, ordinal ordering, UTF-8, and records
encoded as `path + NUL + lowercase_file_sha256 + LF`, the reviewer reproduced:

| Binding | Expected | Reproduced | Result |
|---|---:|---:|---|
| Exact retained BUILD paths | `28` | `28` | `PASS` |
| Retained exact-28 manifest | `267232b323f8708ed389852576e79362a45db5be9aa99bb3bd559757ad5b0791` | same | `PASS` |
| Immutable existing-candidate paths | `26` | `26` | `PASS` |
| Protected-26 manifest | `8e297a25e51f53d1575e9a6ffd1147f8d61e7369f12b4a1583853c3602001b20` | same | `PASS` |
| `pipeline.py` pre-hash | `932c39a86855f4b1634df8eb7465d0d8fdb1ab576108497f808d127835b02c8c` | same | `PASS` |
| `protection.py` pre-hash | `51011c1efa2292c18b0a4dfa00f76301d003bf52403223c24ef5c5230417c623` | same | `PASS` |
| Staged paths | `0` | `0` | `PASS` |
| Both proposed archive paths | absent | absent | `PASS` |

## Exact repair and archive contract

The six-path/final-32 arithmetic is exact. Both Python repair paths already
belong to the retained 28. Two modified continuity front doors plus two new
archives add four paths, producing final exact 32; the other 26 retained BUILD
paths remain byte-immutable. No seventh repair or continuity path is needed.

The semantic source move is sufficient and non-expansive. `pipeline.py` is 304
lines and `protection.py` is 241. Moving the exact closed
`StageReason -> QuarantineReason` mapping, importing it back under the existing
private alias, and removing only the newly unused enum import brings both
under 300 without changing `_failed_result`, `refine`, receipt ordering, error
routing, tests, contracts, dependencies, assertions, or catalog file/LOC
metrics. Current focused tests exercise quarantine, fallback, policy drift,
redaction, dedupe-context, invariant, and stage-unavailable paths.

The archive rotation is lossless by construction: the exact digested blocks
are moved verbatim, each archive adds only a short title/preservation note,
and each front door receives a resolving relative pointer. With a conservative
three-line header/pointer allowance, projected maxima are memory front door
`291`, memory archive `334`, active handoff `371`, and handoff archive `393`,
all below the Markdown hard limit of 600. Canonical active-state and handoff
pointers remain unchanged.

## Ordered gates and claim boundary

The continuation is fail-closed: pushed-lineage/artifact/binding/staged/archive
preflight; exactly six repairs; file-size; focused Refinery `53`; catalog
`--check` with no mutation; full non-live suite; session/repository/JSON-YAML/
import-I/O/secret/diff checks; then final exact-32/six-touch/protected-26/
semantic/archive/link/line-limit/staged audit. Each command runs once and the
first non-zero result stops the invocation. The repository validator's internal
file-size subcheck is part of that aggregate validator and not a retry of the
consumed Amendment 9 invocation.

No waiver, debt/exception entry, provider call, network call, remote ingest,
retry, unrelated edit, catalog write, BUILD commit/push, self-review, FREEZE,
or later lane is authorized. Retained Amendment 8 direct probe `7/7`, the
three-path catalog/knowledge repair, project-knowledge validation, focused
Knowledge Pack `86`, and catalog write/check evidence are not rerun.

A successful invocation yields only a dirty exact 32-path deterministic-local
BUILD/continuity repair candidate pending fresh independent BUILD review. It
does not prove a runtime caller, persistence, `data_scope`, retrieval/RAG,
learning, production, P3-A closure, or Phase 3 completion.

## Next governed move

COMMIT_STEWARD may create/push only the repaired Amendment, this re-review, and
the bounded authority/continuity preamble paths under the existing exact-path
governance discipline. All exact 28 BUILD paths remain unstaged, both bound
archive-source blocks remain unchanged, and both archives remain absent. Then
the operator must provide the exact fresh Amendment 10 R2 acknowledgment in a
separate bounded checkpoint, recorded only in the permitted preamble. That
acknowledgment authorizes one continuation invocation and no retry.
