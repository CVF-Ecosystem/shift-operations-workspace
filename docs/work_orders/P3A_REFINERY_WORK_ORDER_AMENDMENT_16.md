# Work Order Amendment 16 — P3-A Preflight Archive-Path Correction

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-16-2026-08-04`
- Parent Amendment 15 SHA-256: `19e1369d52d1fa65a5bff674fe8a24116767ffcbcf7b84de7340d2fccaced28c`
- Amendment 15 authorization review SHA-256: `738a08b767b730c0efe2ee42cc124538f470e073d930b1f6b62b3e4a6275dadb`
- Failed Amendment 15 acknowledgment checkpoint: `a6e82e1696825e966fe3164854b56a6d05fdbed9`
- Risk / phase: `R2 / WORK_ORDER`
- Status: `AUTHORIZATION_REVIEW_CHANGES_REQUIRED_F1_REPAIRED_PENDING_REREVIEW`
- Provider/network/remote-ingest calls: `0/0/0`

## Trigger and consumed invocation

The Amendment 15 R2 authorized one no-retry invocation. Its first preflight
command verified authority lineage, Amendment/review artifacts, exact32,
staged zero, stable30, protected21 and all nine repair pre-hashes. It then
returned non-zero before any repair edit because the local worker supplied the
nonexistent memory-archive literal
`SESSION/archive/SESSION_MEMORY_P3A_REFINERY_PRE_ROTATION_2026-08-04.md`.

Stop-first/no-retry was honored. No repair, probe, test or later gate ran; all
nine repair pre-hashes and every exact32 byte remain unchanged. The invocation
made zero provider/network/remote-ingest calls. Amendment 15 and its R2 are
consumed and cannot be retried.

## Sole correction

The canonical retained archive identities are:

| Path | Lines | SHA-256 |
|---|---:|---|
| `SESSION/archive/SESSION_MEMORY_2026-07-22_TO_2026-07-31.md` | 335 | `e218cbc150d03bd9c42f623f972e43ee33ee00b530882195e2c8c145ab918f86` |
| `SESSION/handoffs/archive/AGENT_HANDOFF_2026-08-03_P3A_REFINERY_FOUNDATION.md` | 394 | `c50d4bfd7c7745fa1bb3e5758eddb57c905f5d10fac5da5fda8707f63aee0d44` |

Amendment 16 corrects only the first literal above. It preserves Amendment
15's exact nine repair paths, repair pre-hashes, final exact32, stable30
`a50cebb5f4f4b2e6b6ae79bc56ebc70ac17c1fdd28b7242267a17e96e9c6a436`,
protected21
`68cbd2430a85e1cafc5a79b46a72d6479a9c2b0a09629cfb387f78c78d7a6070`,
archive hashes, suffix hashes, required implementation repair, exact four-case
probe, acceptance/status repair and claim boundary without modification.

## Authorization finding repair

Initial independent review artifact
`docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_16_AUTHORIZATION_REVIEW.md`
at SHA-256
`f74b3af9bd8cc29627e6d186bc4842f6ca3659979361839c389a0ef348d36728`
returned `A16-AUTH-F1`, no waiver: the active handoff was 602 lines, so the
retained final line gate was impossible outside the exact nine repair paths.

F1 is repaired only in the governance preamble before checkpoint: compact the
current A15/A16 summary without changing the stable two-line handoff suffix,
archive pointer or any BUILD/rotation hunk. The active handoff must be at most
600 lines before authorization re-review and remain so through checkpoint/R2.
This governance-only compaction is not a tenth repair path and must be included
only as the authorized partial handoff hunk in the authority checkpoint.

## Ordered continuation

Run once, with no retry, and stop at the first non-zero command or contract
failure:

1. repeat Amendment 15 preflight using exactly the two canonical archive paths
   above and the pushed Amendment 16 authority/R2 lineage; explicitly prove
   `SESSION/SESSION_MEMORY.md`, the active handoff and both archive Markdown
   files are each at most 600 lines, while archive/suffix hashes remain exact;
2. edit exactly Amendment 15's nine repair paths;
3. run the exact four-case direct probe once;
4. run the explicit five-file focused Refinery suite once, requiring all tests
   pass and at least 57 collected cases;
5. run project-knowledge validation and focused Knowledge Pack suite once;
6. run file-size and catalog `--check` once without catalog mutation;
7. run the full non-live pytest suite once;
8. run session/repository/JSON-YAML/import-I/O/secret/diff checks once;
9. run the final exact32/exact-nine/protected21/source/archive/suffix/link/line/
   staged/claim-boundary audit once.

No provider/network/remote-ingest call, BUILD commit, self-review, FREEZE,
waiver, debt entry, path expansion or later-lane action is authorized. PASS
yields only a dirty exact32 deterministic-local candidate pending fresh
independent BUILD re-review.

## Required authorization and fresh R2

Independent authorization review, a governance-only authority checkpoint and
a fresh exact human R2 are mandatory. The R2 must name Amendment 16 SHA,
exactly nine repair paths, final exact32 BUILD/continuity paths and zero
provider/network/remote-ingest calls. It authorizes one invocation only.
