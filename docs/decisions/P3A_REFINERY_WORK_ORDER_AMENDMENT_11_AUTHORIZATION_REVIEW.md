# P3-A Refinery Work Order Amendment 11 — Independent Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Amendment 11 SHA-256: `fe59ef90d61fddba14f15f61d7f69260542b4d8852a9b2110d80e0ef5dd84287`
- Consumed Amendment 10 SHA-256: `6c396f1fc6faad345a5ae12d3d928e515d4c5bbf46a14b9743015740e1b2634b`
- Amendment 10 authorization re-review 2 SHA-256: `f06ca38053b6315922513b0f646c7c5e8cda69f9beb0ad072d4fc21409c23944`
- Amendment 10 authority checkpoint: `14139b9b38d18f31d34a2a2e9c1a2a02415b47af`
- Amendment 10 acknowledgment checkpoint: `9b1e34df7661a6a9877046ac65f770c772d1495b`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 11 truthfully consumes Amendment 10's pre-edit patch-construction
failure, preserves the entire accepted six-path repair candidate, and corrects
only the transport/construction seam. Independently obtained UTF-8/base64
block payloads, mandatory decode/count/digest verification, and one six-path
`apply_patch` call remove the undefined optional-property failure while
preserving atomicity, archive integrity, fail-first/no-retry behavior, and the
zero-call boundary.

Open authorization findings: `NONE`. Waivers: `NONE`.

This PASS does not itself authorize repair. The reviewed authority checkpoint
must be committed/pushed and followed by Amendment 11's fresh exact human R2
acknowledgment before one no-retry continuation invocation may begin.

## Consumed Amendment 10 truth

Independent Git and canonical continuity checks establish:

- `HEAD == origin/main == 9b1e34df7661a6a9877046ac65f770c772d1495b`;
- `14139b9b38d18f31d34a2a2e9c1a2a02415b47af` is the pushed Amendment 10
  authorization checkpoint and `9b1e34df7661a6a9877046ac65f770c772d1495b`
  is its pushed R2 acknowledgment checkpoint;
- Amendment 10's full authority/immutable preflight passed;
- before any repair edit, atomic-patch construction raised
  `TypeError: Cannot read properties of undefined (reading 'split')` while
  expanding undefined `data.memoryBlock`;
- `apply_patch` was never called, repair touches remained exactly `0/6`, both
  archive paths remained absent, and all post-repair gates were `NOT_RUN`;
- execution stopped at that first failure, was not retried, and
  provider/network/remote-ingest calls were `0/0/0`.

Amendment 10 and its R2 are consumed. Amendment 11 does not retry or relabel
the failed construction; it provides a separately reviewed transport contract
under a fresh R2 requirement.

## Independent retained-binding reproduction

Using typed path collections, ordinal case-sensitive ordering, UTF-8, and
records encoded as `path + NUL + lowercase_file_sha256 + LF`, the reviewer
reproduced:

| Binding | Expected | Reproduced | Result |
|---|---:|---:|---|
| Exact retained BUILD paths | `28` | `28` | `PASS` |
| Retained exact-28 manifest | `267232b323f8708ed389852576e79362a45db5be9aa99bb3bd559757ad5b0791` | same | `PASS` |
| Protected existing-candidate paths | `26` | `26` | `PASS` |
| Protected-26 manifest | `8e297a25e51f53d1575e9a6ffd1147f8d61e7369f12b4a1583853c3602001b20` | same | `PASS` |
| `pipeline.py` pre-hash | `932c39a86855f4b1634df8eb7465d0d8fdb1ab576108497f808d127835b02c8c` | same | `PASS` |
| `protection.py` pre-hash | `51011c1efa2292c18b0a4dfa00f76301d003bf52403223c24ef5c5230417c623` | same | `PASS` |
| Staged paths | `0` | `0` | `PASS` |
| Both archive paths | absent | absent | `PASS` |

The exact universal-newline/LF/UTF-8 archive-block algorithm also reproduces:

| Archive-source block | Expected | Reproduced | Result |
|---|---|---|---|
| Memory P-FIX-6 through before continuity-drift heading | `331` lines / `d7d902ea4eef700310d999b1fb41ed62fefe6cf4b1a5f389ca86aae6fdfe348e` | same | `PASS` |
| Active handoff `## Intake boundary` through EOF | `390` lines / `d8b6f8d8af9ac11856db1308ecc1e966900cc808ed0907475cd18b98b3c3ec14` | same | `PASS` |

Thus no source, continuity archive block, or repair output from Amendment 10
was partially changed before its construction stop.

## Corrected atomic patch construction

The corrected contract directly addresses the failure mode and is executable:

- each block is emitted independently by a read-only local command as one
  base64 value, so arbitrary Vietnamese/Unicode text and newline content are
  transported without optional JSON properties or cross-field assumptions;
- each value is decoded as UTF-8 independently and must reproduce its exact
  normalized line count and SHA-256 before patch construction;
- marker, decode, count, digest, archive-absence, or scope mismatch stops before
  any write;
- only after both blocks pass may one patch be constructed containing all six
  file operations and sent through a single `apply_patch` call;
- one patch prevents an intentionally sequenced partial six-file repair; a
  patch rejection is the first failure and is not retried;
- shell and Python file writes remain prohibited.

The contract therefore preserves the reviewed archive bytes and eliminates
the specific `data.memoryBlock` dependency without adding a helper script,
temporary repository path, transport file, seventh repair path, or external
call.

## Exact repair scope and retained semantics

The arithmetic remains exact. `pipeline.py` and `protection.py` already belong
to the retained 28. Modifying the two canonical front doors and creating the
two archives adds four paths, so the final BUILD/continuity candidate is exact
32; the other 26 retained BUILD paths stay byte-immutable.

The source move remains semantic-preserving: relocate only the closed
`StageReason -> QuarantineReason` mapping to `protection.py`, import it back
under `_quarantine_reason`, and remove only the newly unused enum import.
`_failed_result`, `refine`, public contracts, receipts, error routing, tests,
dependencies, assertions, behavior, and catalog metrics cannot change. Moving
the helper from the 304-line pipeline into the 241-line protection module can
bring both under the 300-line hard limit without compression or debt.

The rotations remain lossless: move the two exact verified normalized blocks
verbatim, add only short archive title/preservation notes, replace each source
block with a resolving relative pointer, preserve current P3-A/disposition and
later canonical memory sections, keep canonical pointers unchanged, and
require all four Markdown files at or below 600 lines.

## Ordered gates and claim boundary

The invocation is fail-closed: pushed lineage/artifact/binding/archive absence
preflight; verified transport and one atomic six-path patch; file-size;
focused Refinery `53`; catalog `--check` without mutation; full non-live suite;
session/repository/JSON-YAML/import-I/O/secret/diff checks; then final exact-32,
six-touch, protected-26, semantic, verbatim-archive, link, line-limit, and
staged-zero audit. Each step runs once and the first failure stops execution.

All Amendment 8/9 evidence retained by Amendment 10 remains no-rerun evidence.
No provider/network/remote-ingest call, retry, waiver, debt/exception entry,
catalog write, unrelated edit, BUILD commit/push, self-review, FREEZE, or later
lane is authorized.

A pass yields only a dirty exact-32 deterministic-local BUILD/continuity
candidate pending fresh independent BUILD review. It proves no runtime caller,
persistence, `data_scope`, retrieval/RAG, learning, production, P3-A closure,
or Phase 3 completion.

## Next governed move

COMMIT_STEWARD may create/push only the Amendment 11 authority checkpoint under
the existing bounded governance discipline while preserving all exact-28 BUILD
paths unstaged and both archives absent. Then the operator must provide the
fresh exact Amendment 11 R2 acknowledgment. That acknowledgment authorizes one
continuation invocation only and no retry.
