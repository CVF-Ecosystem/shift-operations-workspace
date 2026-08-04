# P3-A Refinery Work Order Amendment 18 — Authorization Re-review 2

## Final normalized-suffix verification — PASS

- Verification date: `2026-08-04`
- Role: `REVIEWER` (independent authorization re-review)
- Risk / phase: `R2 / WORK_ORDER`
- A18 SHA-256 reviewed:
  `2b11f8198a206a2c5df94e83b36ac6029c4829496d04717ef86058c483240d2a`
- Frozen execution-sheet SHA-256 reviewed:
  `deff7d1ae7289a4af3a07d8696fb02a47a3411d4a5ba7fa936b5afcab523e2f3`
- Prior in-place review SHA-256:
  `e0a374410073164167f8ffbb3e2c15eeb131b998f8d17b7cb407317d213c8b88`
- Provider/network/remote-ingest calls: `0/0/0`
- Findings: `NONE`
- Waivers: `NONE`

### Current disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REREVIEW_PASS`

`A18-AUTH-F1`, `A18-AUTH-F2` and `A18-AUTH-F3` are all
`CLOSED_WITHOUT_WAIVER`. No authorization finding remains.

The requested A18/sheet hashes and every checkpoint-owned artifact hash
reproduce. All four frozen PowerShell fences parse with zero errors and all
four Python here-string bodies compile. The retained atomic patch has one
begin/end envelope, exactly nine unique target paths, applicable unique
anchors, both before-window and after-window exclusions inside its payload,
and no stray repair fragment. The exact probe and ordered direct gates remain
fail-stop/no-retry and make zero provider/network/remote-ingest calls.

The canonical authority map contains exactly 32 final dirty paths, exactly
nine repair paths and `freshR2Accepted=false`. The preparation worktree has
exact39: all exact32 candidate paths plus exactly seven governance-only paths;
staged paths are zero. Stable30 reproduces
`a50cebb5f4f4b2e6b6ae79bc56ebc70ac17c1fdd28b7242267a17e96e9c6a436`,
protected21 reproduces
`68cbd2430a85e1cafc5a79b46a72d6479a9c2b0a09629cfb387f78c78d7a6070`,
and all nine repair pre-hashes reproduce.

Archive bindings reproduce at
`335/e218cbc150d03bd9c42f623f972e43ee33ee00b530882195e2c8c145ab918f86`
and
`394/c50d4bfd7c7745fa1bb3e5758eddb57c905f5d10fac5da5fda8707f63aee0d44`.
Normalized UTF-8 suffixes reproduce at
`243/6a055880ab97e542fa122ff6cbe3025d993aa521d3b4e9098abf82fa97237ac6`
and
`2/46f46615b06dff42a2c44b55321e30c862881146a58a98549fe06f06aaceb357`.
Each continuity front door contains exactly one `archive/...` Markdown target;
each target resolves relative to its document parent to the corresponding
hash-bound archive. Both front doors and both archives remain at or below 600
lines. The frozen preflight and final audit now encode the reviewed current
truth and the complete scope/protected/suffix/link boundary.

### Exact-nine checkpoint authorized next

The next COMMIT_STEWARD move is one governance-only partial-staged checkpoint
containing exactly:

1. `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_18.md`
2. `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_18_EXECUTION_SHEET.md`
3. `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_18_AUTHORIZATION_REVIEW.md`
4. `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_18_AUTHORIZATION_REREVIEW.md`
5. `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_18_AUTHORIZATION_REREVIEW_2.md`
6. `SESSION/ACTIVE_SESSION_STATE.json`
7. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
8. only the new A18/review governance preamble hunks in
   `SESSION/SESSION_MEMORY.md`
9. only the new A18/review governance preamble/compaction hunks in
   `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`

The checkpoint must update the authority map to this review's final SHA,
preserve all exact32 candidate hunks unstaged, leave staged zero after commit,
reproduce all bindings, and keep the handoff at or below 600. It authorizes no
repair invocation by itself.

### Exact fresh R2 wording

After that checkpoint is pushed, the required fresh human acknowledgment is
exactly:

> Tôi phê duyệt R2 cho
> P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-18-2026-08-04, Work Order Amendment
> SHA-256 2b11f8198a206a2c5df94e83b36ac6029c4829496d04717ef86058c483240d2a,
> đúng 9 repair paths và final exact 32 BUILD/continuity paths, zero
> provider/network/remote-ingest calls.

No repair, gate, BUILD commit, self-review, FREEZE or later-lane action may run
before both the exact-nine checkpoint and that fresh exact R2 are complete.

## Prior final link-boundary verification (preserved)

- Verification date: `2026-08-04`
- Role: `REVIEWER` (independent authorization re-review)
- Risk / phase: `R2 / WORK_ORDER`
- A18 SHA-256 reviewed:
  `0b0100605ab4bef3f8f24e196464ca2c31e0b46e4aebffdb4c1e16c238d1b320`
- Frozen execution-sheet SHA-256 reviewed:
  `2569944ca8f62a06d3e3b25fdfe4a3b578723239003edff695072ff536209df6`
- Prior in-place review SHA-256:
  `b24c56af36b18becccbfd7f513079654dffcb1930c8a4f3ce9d38b1db9a0f96e`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

### Current disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REREVIEW_CHANGES_REQUIRED`

The link-extraction code is structurally correct, but the invocation fails
earlier on a stale canonical-memory suffix marker/binding. `A18-AUTH-F1`
therefore remains `OPEN`; F2/F3 remain `CLOSED_WITHOUT_WAIVER`; waiver `NONE`.

The requested A18/sheet hashes and all five authority-map artifact hashes
reproduce. The map contains 32 exact-scope paths, nine repair paths and
`freshR2Accepted=false`. All four frozen PowerShell fences parse with zero
errors; all four Python here-string bodies compile; the atomic payload has
exactly nine unique targets and retains both window exclusions. Stable30,
protected21 and all nine repair pre-hashes reproduce.

The first executable blocker is in both the preflight and final audit:

```python
memory.index(b'## Historical continuity from 2026-07-22')
```

Current canonical `SESSION/SESSION_MEMORY.md` line 78 begins
`Historical continuity from 2026-07-22...`, without the frozen `## ` prefix.
Independent read-only execution of the frozen lookup raises
`ValueError: subsection not found`. The actual 243-line suffix beginning at
the present marker hashes to
`f7105ae9e9a304f1ee4a2c84d71b55d3f4e99852983980a2a0f0cd51dab41e00`,
not the sheet's frozen
`6a055880ab97e542fa122ff6cbe3025d993aa521d3b4e9098abf82fa97237ac6`.
Stop-first execution therefore terminates during preflight, before the patch
and before the newly added Markdown-link assertions.

Required repair: reconcile the canonical memory bytes and the frozen marker,
line count and suffix hash to one exact current truth, without changing the
protected BUILD candidate or silently rewriting archived history. Then retain
the new regex extraction and verify that each resolved link is the intended
hash-bound archive. Update this same review artifact in place after a fresh
independent verification.

No checkpoint, fresh R2 wording, repair invocation, BUILD commit, self-review,
FREEZE or later-lane action is authorized.

## Prior final fresh verification after scope-audit repair (preserved)

- Verification date: `2026-08-04`
- Role: `REVIEWER` (independent authorization re-review)
- Risk / phase: `R2 / WORK_ORDER`
- A18 SHA-256 reviewed:
  `87d8fea07877b6998cd17e2bbfade35bbc9cb19f9ad35d0e500feabf24a4d402`
- Frozen execution-sheet SHA-256 reviewed:
  `94bb35749b1c28b07c256b77f99803fa7f16ab5c572319defee800ec13308ff0`
- Prior in-place review SHA-256:
  `21c0030ea479c2771f4a27e644446fcc81a62f69be236d3f175420d06c36b7c7`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

### Current disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REREVIEW_CHANGES_REQUIRED`

`A18-AUTH-F2` and `A18-AUTH-F3` remain
`CLOSED_WITHOUT_WAIVER`. The exact32/exact9/protected21/suffix portion of
`A18-AUTH-F1` is repaired, but the archive-link subfinding remains `OPEN`;
waiver `NONE`.

The requested A18 and sheet hashes reproduce. The canonical authority map has
exactly 32 `exact32Paths`, exactly nine `repairPaths`, the requested artifact
hashes and `freshR2Accepted=false`. All four frozen PowerShell fences parse
with zero errors and all four embedded Python here-string bodies compile. The
atomic payload remains applicable by its unique retained anchors, touches only
the nine authorized paths, and contains both before-window and after-window
tests. The final audit now asserts final dirty scope equals the checkpoint-owned
exact32 array, repair count equals nine, protected count equals 21 and its
manifest reproduces
`68cbd2430a85e1cafc5a79b46a72d6479a9c2b0a09629cfb387f78c78d7a6070`;
it also reproduces both stable suffix hashes. Those repairs pass review.

The final archive-link requirement is still not executable. Both preflight and
final audit assert only that two hard-coded archive paths are files. Neither
program reads the Markdown link at
`SESSION/SESSION_MEMORY.md` nor the Markdown link at
`SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`, extracts its
relative target, resolves it against the front door's parent directory and
asserts that the resolved file is the hash-bound archive. A broken or changed
Markdown link therefore survives while both hard-coded `Path(...).is_file()`
assertions still pass. This does not close the expressly required archive-link
resolution boundary.

Required repair: freeze a parse-safe final assertion that extracts each exact
Markdown archive-link target from its front door, resolves it relative to that
front door, and proves that it resolves to the already hash-bound memory and
handoff archive respectively. Preserve the fixed archive hashes/line counts,
exact32/exact9/protected21/suffix checks and every closed F2/F3 repair. Then
update this same artifact in place for another independent disposition.

No checkpoint, fresh R2 wording, repair invocation, BUILD commit, self-review,
FREEZE or later-lane action is authorized. Canonical
`p3a_amendment_18_authority.freshR2Accepted` must remain `false`.

## Prior fresh verification after F1/F2/F3 repair (preserved)

- Verification date: `2026-08-04`
- Role: `REVIEWER` (independent authorization re-review)
- Risk / phase: `R2 / WORK_ORDER`
- A18 SHA-256 reviewed:
  `972c89e680030a8b823c3b01fa70a3599cf9edf17f5f7ed7e78598122c3a1f6a`
- Frozen execution-sheet SHA-256 reviewed:
  `1a048d79f64cc395a56322b006b649baab340286f3b86a66e4722601344d3dfa`
- Prior content SHA-256:
  `e0ff5ef0c8c81f7caaae4f48959f1a23cf5649f1cf6fe483a106a1cb8394aabe`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

### Current disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REREVIEW_CHANGES_REQUIRED`

`A18-AUTH-F2` and `A18-AUTH-F3` are
`CLOSED_WITHOUT_WAIVER`. `A18-AUTH-F1` remains `OPEN`; waiver `NONE`.

The amended A18 and execution-sheet bytes match the requested hashes. All four
frozen PowerShell blocks parse with zero parser errors and all three embedded
Python here-string bodies compile. Both before-window and after-window
rejection cases are now inside the single `*** Begin Patch` / `*** End Patch`
payload, with no stray copy after it. A18 also names the required exact-nine
checkpoint, including this in-place `REREVIEW_2` path. These facts close F2
and F3 without waiver.

F1 is not closed because the frozen final audit does not prove the promised
final exact-nine/scope boundary. It checks staged zero, checks that each of the
nine repair hashes merely differs from its pre-hash, pins the expected
`IMPLEMENTATION_STATUS.json` hash and manifest source pin, checks Python line
limits, archive hashes/line counts, and continuity line ceilings. It does not
recompute final `git status --porcelain=v1 -uall` and assert equality to the
frozen exact32 set. It also does not recompute the final protected21 manifest
or the two stable continuity suffix hashes, and it does not resolve the
Markdown archive links. Consequently an extra dirty path or a protected,
suffix, or link-boundary mutation can survive the last gate while the final
audit still exits zero. This contradicts A18's required final
`exact32/exact9/protected21/archive/suffix/line/staged` audit and the sheet's
claim of a final exact9/scope audit.

Required repair: extend the exact final audit with a parse-safe, frozen check
that (1) final dirty paths equal exact32, (2) all and only exact9 carry their
authorized post-patch bytes or otherwise have exact frozen post-hash bindings,
(3) protected21 reproduces
`68cbd2430a85e1cafc5a79b46a72d6479a9c2b0a09629cfb387f78c78d7a6070`,
(4) both stable suffix hashes reproduce, and (5) the archive links extracted
from the two Markdown front doors resolve to the hash-bound archive files.
Parser-check the amended frozen block and update this same artifact in place
for another independent disposition.

No checkpoint, fresh R2, repair invocation, BUILD commit, self-review, FREEZE
or later-lane action is authorized. The canonical
`p3a_amendment_18_authority.freshR2Accepted` value must remain `false`.

## Historical prior CHANGES_REQUIRED narrative (preserved)

The material below is the prior disposition at SHA-256
`e0ff5ef0c8c81f7caaae4f48959f1a23cf5649f1cf6fe483a106a1cb8394aabe`.
It is retained as audit history and is superseded only where the fresh
verification above explicitly closes F2/F3 or narrows the remaining F1.

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization re-review)
- Risk / phase: `R2 / WORK_ORDER`
- A18 SHA-256 reviewed:
  `7cfe856176ae298c77a0d8516890fae4732a5057e535ff9c05b193a0aeb7a511`
- Frozen execution-sheet SHA-256 reviewed:
  `9985526fc825ff539aa452e2339e655b852878494375f89c3960b170315665ef`
- Initial review SHA-256:
  `d72136737ec3afe428b8390b1c3f60e4c7c3dff2c42f12670113af81465ec55c`
- First re-review SHA-256:
  `919bf51f485bdcc8060adfb0e542a57c0e508b52a24271e33872428520e1f36c`
- Review baseline:
  `HEAD == origin/main == f775b7c4b3d32872c24fc5b8518109c8797e5764`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REREVIEW_CHANGES_REQUIRED`

The amended sheet now contains concrete preflight, probe, additional gate and
final-audit sections, and the frozen probe body parses as Python. The atomic
exact-nine repair payload remains applicable and technically sound, the status
hash/pin remain exact, and all immutable candidate bindings reproduce.

F1–F3 are nevertheless not closed. The preflight/final audit omit mandatory
scope/manifests/suffix/authority assertions, the exact secret-scan command does
not parse as PowerShell, the after-window test is outside the atomic patch
payload, and exact-eight still omits this mandatory re-review-2 artifact.

Open findings: `A18-AUTH-F1`, `A18-AUTH-F2`, `A18-AUTH-F3`.
Waivers: `NONE`.

No authority checkpoint, fresh R2, repair invocation, BUILD commit,
self-review, FREEZE or later-lane action is authorized.

## Immutable reproduction

Before creation of this artifact, the preparation worktree contained exact
`38` dirty paths: exact32 plus A18, sheet, initial review, first re-review and
canonical/mirror state. Excluding those six governance paths gives exact32;
excluding the volatile memory/handoff front doors gives stable30; excluding
the exact-nine repair paths gives protected21. Staged paths are zero.

| Binding | Reproduced | Result |
|---|---:|---|
| Exact BUILD/continuity paths | `32` | `PASS` |
| Staged paths | `0` | `PASS` |
| Stable paths / manifest | `30` / `a50cebb5f4f4b2e6b6ae79bc56ebc70ac17c1fdd28b7242267a17e96e9c6a436` | `PASS` |
| Protected paths / manifest | `21` / `68cbd2430a85e1cafc5a79b46a72d6479a9c2b0a09629cfb387f78c78d7a6070` | `PASS` |

All nine pre-hashes remain the exact values bound by A18 and both prior
reviews. Archives remain `335/e218cbc1…f86` and `394/c50d4bfd…d44`; memory
suffix remains `243/6a055880…ac6`; handoff suffix remains
`2/46f46615…b357`; archive links resolve. Canonical memory is `316` lines and
the handoff is exactly `600`; file-size guard passes. Any further governance
update must compact only volatile A18 preamble text without changing the stable
suffix, pointer, archive or BUILD hunks.

## Retained patch, matrix and status assessment

The exact atomic patch is unchanged from the first re-review. Its anchors are
unique in current source and it touches all and only exact nine paths. The
source repair correctly binds public versions, route availability and safe
provenance, while retaining chronological selection and emitting lexical
unique public match ids. It changes no dedupe algorithm, receipt model,
contract, API, catalog or protected path.

The patch still adds exactly four collected test functions, one per authorized
test file, targeting a baseline `53` plus four = `57`. The candidate-to-source
typed substitution rejects on current strict models. The status replacement
still parses and hashes exactly to
`9d9d7d2ff387365ce018cc51de07a24d1eb3a21c08cb723feb3d74e114ae5eb6`;
the manifest patch changes only the matching project-context pin.

These retained parts pass authorization design review. They are not executed
BUILD evidence and do not overcome the executable defects below.

## A18-AUTH-F1 — frozen execution programs are still insufficient

Status: `OPEN`; waiver: `NONE`.

The newly frozen Python probe body compiles. The preflight and final audit,
however, do not implement the contract they claim to freeze:

- preflight does not verify the A18/sheet/review/R2 artifact hashes or pushed
  exact authority lineage;
- it does not reproduce exact32, stable30 or protected21 manifests;
- it checks archive hashes and line counts but not the two stable suffix hashes
  or relative-link resolution;
- final audit does not verify exact32, exact-nine touches, protected21, suffix
  hashes, archive links or the full claim boundary.

The added secret/security command is also not executable verbatim. Independent
PowerShell parser inspection returns three errors (`Missing expression`,
`Unexpected token ')'`, and an unterminated string) because backslash does not
escape the embedded double quotes in a PowerShell double-quoted `python -c`
argument. Stop-first execution would halt at this gate even if earlier work
passed.

Required repair: freeze executable programs that assert every named binding,
lineage and boundary; correct the secret command using PowerShell-safe quoting;
and parser-check every frozen PowerShell line before fresh review. No prose
substitution or worker synthesis is allowed.

## A18-AUTH-F2 — after-window assertion is outside the atomic patch

Status: `OPEN`; waiver: `NONE`.

The exact atomic diff still contains the before-window assertion only. The new
after-window `pytest.raises` fragment appears after the sheet's final prose,
outside the fenced `*** Begin Patch` / `*** End Patch` payload. Copying the
authorized patch byte-for-byte therefore does not add it to
`test_refinery_pipeline.py`; the focused suite would still lack the required
after-window exclusion.

Required repair: place the after-window assertion inside the pipeline hunk of
the single atomic payload, preserve exactly four collected functions/57 total,
and remove the stray non-command fragment from the end of the sheet.

## A18-AUTH-F3 — exact-eight lineage omits re-review 2

Status: `OPEN`; waiver: `NONE`.

A18's exact-eight set now includes A18, sheet, initial review, first re-review,
state, mirror, memory and handoff. Both prior reviews remain untracked and are
directly SHA-bound causal audit artifacts, so neither can be omitted. This
re-review-2 artifact is the only current disposition on the new A18/sheet bytes
and must also be durable. The correct future checkpoint is therefore exact
nine, not exact eight.

Required repair: amend A18 to name this `REREVIEW_2` path and exact-nine count.
After repairing A18/sheet, update this same re-review-2 artifact in place for a
fresh disposition so another lineage path is not created.

## Checkpoint and R2 disposition

No checkpoint or fresh R2 wording is issued while F1–F3 remain open. After
repair and an in-place fresh PASS, the minimum checkpoint is exact nine:

1. `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_18.md`
2. `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_18_EXECUTION_SHEET.md`
3. `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_18_AUTHORIZATION_REVIEW.md`
4. `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_18_AUTHORIZATION_REREVIEW.md`
5. `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_18_AUTHORIZATION_REREVIEW_2.md`
6. `SESSION/ACTIVE_SESSION_STATE.json`
7. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
8. only new A18/review governance preamble hunks in
   `SESSION/SESSION_MEMORY.md`
9. only new A18/review governance preamble/compaction hunks in
   `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`

Cached staging must exclude every repair/archive/history hunk, preserve the
exact32 candidate dirty and staged zero, reproduce all stable bindings, and
keep the active handoff at or below 600. Fresh exact R2 may be specified only
by the future PASS disposition.
