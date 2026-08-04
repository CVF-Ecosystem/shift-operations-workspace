# Agent Handoff — P3-A Refinery

## Disposition

- Tranche: `P3-A-REFINERY-2026-08-03`
- Parent: Project Knowledge Pack closure `107c8fa`
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Active role: `COMMIT_STEWARD`
- Status: `AMENDMENT_14_AUTHORIZATION_REVIEW_PASS_PENDING_PARTIAL_CHECKPOINT_AND_FRESH_R2`
- INTAKE commit: `32cb7f233f40fcfb3736f0f26487a36231c7d24e`
- INTAKE review: `INTAKE_REVIEW_PASS` at `558b193`

## Current truth

`refinery-bridge` is contract-only. Its YAML omits roadmap-required quarantine,
provenance, data-quality and fallback results; submodules have no runtime code
or tests. `data_scope` is callable but has no runtime caller and does not verify
minimization evidence. The existing normalized fixture invents an unsupported
`11h40 → 23:40` conversion and is not golden truth.

## Corrected independent BUILD review and Amendment 4

Independent review artifact
`docs/decisions/P3A_REFINERY_BUILD_INDEPENDENT_REVIEW.md` SHA-256
`ccc6c4c25fc00000be34d443ffdb4d59c665f1436641e3f89b06b4906480b405`
returns `REVIEW_CHANGES_REQUIRED`, no waiver. Its original manifest-drift F1
is explicitly retracted: typed ordinal reproduction passes exact 28 BUILD / 26
retained paths and digest `c7c1761c…01b8`; focused tests pass 31. The corrected
failure is a public-invariant probe that accepts zero-quality ready output, an
unbound candidate fingerprint and invalid offsets. The review also retains the
non-executable R27 label matrix, missing fail-stop paths, safe-boundary gaps and
unrelated `cvf-application-profile` catalog mutation findings.

First authorization review `42eb1c29…03ef8` failed only because the initial
Amendment candidate recorded a culture-sensitive protected-15 digest while
promising ordinal sorting; it otherwise found the 13-path scope sufficient and
non-expansive. No waiver. Corrected Work Order Amendment 4 binds the retained
exact-28 manifest `e43e53e4…c4eae`, protects 15 paths under typed ordinal
digest `ce531fb7…44784`, and authorizes exactly 13 repair paths while final BUILD
remains exact 28. It permits zero provider/network/remote-ingest calls.
DESIGN/SPEC remain unchanged. Fresh independent authorization re-review and a
fresh exact human R2 literal are mandatory before repair; no candidate edit,
stage, commit, push, self-review or FREEZE authority exists yet.

Fresh authorization re-review updated the review artifact to SHA-256
`e18217e6c41a958fdd3dc38f0e334c9153e4521929ca1b8758f33a7f856bb320`
and returned `WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no open findings
and no waiver. Corrected Amendment SHA-256 is
`0f79fcc75ae468c0c56a2db39d821738e0b863bf94710f2eebcbf845020fd0dd`.
COMMIT_STEWARD must commit/push only the corrected BUILD review, Amendment 4,
its authorization review and four continuity paths while preserving all 28
BUILD paths unstaged. Then stop for the fresh exact R2 literal; repair remains
prohibited until that acknowledgment is accepted.

## Fresh Amendment 4 human R2 acknowledgment

Accepted verbatim on 2026-08-03:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-4-2026-08-03,
> Work Order Amendment SHA-256
> 0f79fcc75ae468c0c56a2db39d821738e0b863bf94710f2eebcbf845020fd0dd,
> đúng 13 repair paths và final exact 28 BUILD paths, zero
> provider/network/remote-ingest calls.

It binds exactly one repair invocation with no retry. COMMIT_STEWARD must
commit/push only this four-path acknowledgment checkpoint while all 28 BUILD
paths remain unstaged. The acknowledgment is consumed only after that push and
the first authorized repair path changes. REPAIR_WORKER then follows Amendment
4 in exact order, stops at the first failure, makes zero provider/network/
remote-ingest calls and yields at most a dirty exact 28-path candidate pending
fresh independent BUILD review. No BUILD commit, self-review, FREEZE or
later-lane authority.

## Consumed Amendment 4 continuation and failure

Acknowledgment checkpoint `9dd0900486d961f53bf673a22133bd78f7cccbad`
was pushed. Preflight reproduced exact-28 `e43e53e4…c4eae`, protected-15
`ce531fb7…44784`, all authority hashes, HEAD/origin and empty staged set.

REPAIR_WORKER changed exactly the five authorized source paths named in
Amendment 5. Before any focused test, a read-only inventory command returned
non-zero because the Windows `rg` invocation passed unsupported literal glob
`tests/unit/test_refinery*`. Stop-first/no-retry was honored. No focused test,
probe, catalog write, knowledge update, full suite or later gate ran. Zero
provider/network/remote-ingest calls occurred; no BUILD commit/push occurred.

Amendment 4 and its R2 are consumed. Amendment 5 binds the retained exact-28
digest `c785597e…ce17a`, unchanged protected-15 `ce531fb7…44784`, the same
exact 13 repair paths and final exact 28 paths. Independent authorization
review, authority checkpoint and fresh exact R2 are mandatory before further
BUILD edits or tests.

Independent Amendment 5 authorization review SHA-256
`3b5d9a01b6c96f8f84f5010d583c0f36433bd8ffba51ff1a50a5e312e96fd7f8`
returned `WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no findings and no
waiver, bound to Amendment SHA-256
`44c2576895356e8cb83a7df1d99c945e3a5a354a11e7655521e5288e54e07726`.
It reproduced exact-28/protected-15 and all five partial-source hashes, and
confirmed the same 13-path scope, ordered gates, no retry of the failed `rg`
command and zero-call boundary. COMMIT_STEWARD must commit/push only Amendment
5, its review and four continuity paths while BUILD stays unstaged, then stop
for fresh exact R2. No further BUILD edit/test or closure authority yet.

## Fresh Amendment 5 human R2 acknowledgment

Accepted verbatim on 2026-08-03:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-5-2026-08-03,
> Work Order Amendment SHA-256
> 44c2576895356e8cb83a7df1d99c945e3a5a354a11e7655521e5288e54e07726,
> đúng 13 repair paths và final exact 28 BUILD paths, zero
> provider/network/remote-ingest calls.

It binds one continuation invocation with no retry. COMMIT_STEWARD must
commit/push only this four-path acknowledgment checkpoint while BUILD remains
unstaged. The acknowledgment is consumed only after that push and the first
authorized repair edit. REPAIR_WORKER then follows Amendment 5 in exact order,
does not run or replace the failed Amendment 4 inventory command, stops at the
first failure and makes zero provider/network/remote-ingest calls. No BUILD
commit, self-review, FREEZE or later-lane authority.

## Consumed Amendment 5 continuation and failure

Checkpoint `0e809031f69ef497e8bfc411c5ce0ed0b37e7871` was pushed.
Preflight passed. The source/test repair step completed, and the focused
Refinery suite passed `53`. The next dedicated stdin probe returned non-zero
before running cases because plain `python -` lacked pytest's configured
package path and could not import `refinery_bridge`. It was not retried.
Catalog, knowledge, full-suite and later gates were NOT_RUN. Zero provider/
network/remote-ingest calls and no BUILD commit/push occurred.

Amendment 5/R2 are consumed. Amendment 6 binds exact-28 `c9e021d3…183d4e`,
immutable source/test `addb052c…b7352`, protected-25 `513ba54f…6dda1`, and
authorizes only registry/catalog/knowledge-manifest touches. Independent review,
authority checkpoint and fresh exact R2 are mandatory before the corrected
probe or any remaining gate.

## Amendment 6 authorization review PASS

`docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_6.md` SHA-256
`57c8322d82126b4202bbbe5bbbd6df6b3a3aae27ba5a28e1e67b8e6832fe4317`
binds the retained exact-28 digest `c9e021d3…183d4e`, immutable source/test-10
digest `addb052c…b7352`, protected-25 digest `513ba54f…6dda1`, exactly three
repair paths and final exact 28 BUILD paths. It corrects only the environment
for the never-executed seven-case probe, retains the focused `53 passed`, then
bounds the registry/catalog/knowledge-manifest repair and remaining local
gates. It permits zero provider/network/remote-ingest calls and no retry.

Independent REVIEWER returned
`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no findings and no waiver,
in `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_6_AUTHORIZATION_REVIEW.md`
SHA-256 `cd85418046d45acc261f42595cb1e215350b91235c763f829545896ca8548250`.

COMMIT_STEWARD may commit/push only Amendment 6, its review and the four
continuity paths while preserving all exact 28 BUILD paths unstaged. Then stop
for fresh exact R2. No corrected probe, catalog/knowledge edit, test/gate,
BUILD commit, self-review, FREEZE or later-lane authority yet.

## Fresh Amendment 6 human R2 acknowledgment

Accepted verbatim on 2026-08-04:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-6-2026-08-03,
> Work Order Amendment SHA-256
> 57c8322d82126b4202bbbe5bbbd6df6b3a3aae27ba5a28e1e67b8e6832fe4317,
> đúng 3 repair paths và final exact 28 BUILD paths, zero
> provider/network/remote-ingest calls.

COMMIT_STEWARD must commit/push only this four-path acknowledgment checkpoint
while preserving all exact 28 BUILD paths unstaged. After that push,
REPAIR_WORKER runs the ordered Amendment 6 continuation once, stops at the
first non-zero command or contract failure, does not retry and makes zero
provider/network/remote-ingest calls. No BUILD commit, self-review, FREEZE or
later-lane authority.

## Consumed Amendment 6 invocation and failure

Acknowledgment checkpoint `65b47e4a1b42d4ad41424f4c616bfb3f65790e0f`
was pushed. The one Amendment 6 invocation stopped at its first preflight
assertion because the worker hard-coded incorrect full SHA
`65b47e4e36e3f42f07b615e9cddeeb969f9afae1` instead of the actual checkpoint.
The failed preflight was not retried. No probe, repair edit, test or later gate
ran. The exact dirty candidate is unchanged, the staged set is empty, and zero
provider/network/remote-ingest calls occurred during the invocation.

Amendment 6/R2 are consumed. Amendment 7 at
`docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_7.md` SHA-256
`8712b18a43a35555573bce36f3fe6afd1b91b9709036dce1f1663dddd4c5c965`
corrects only the acknowledgment-lineage binding. It retains exact-28
`c9e021d3…183d4e`, immutable source/test-10 `addb052c…b7352`, protected-25
`513ba54f…6dda1`, exactly three repair paths, final exact 28 and the corrected
probe environment/remaining gates. Independent authorization review,
authority checkpoint and fresh exact R2 are mandatory before any continuation.

## Amendment 7 authorization review PASS

Independent REVIEWER returned
`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no findings and no waiver,
in `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_7_AUTHORIZATION_REVIEW.md`
SHA-256 `4f55a537bfb356f399ab3722b71af56771091049f8b2b7e2851fac1dd4fe72fc`.
The review reproduced the actual acknowledgment/authority lineage, unchanged
exact-28/source-test-10/protected-25 digests, all three repair-surface hashes,
empty staged set, corrected probe environment, ordered remaining gates and
zero-call/no-retry boundary. Findings and waivers are `NONE`.

COMMIT_STEWARD must commit/push only Amendment 7, its review and the four
continuity paths while preserving all exact 28 BUILD paths unstaged. Then stop
for fresh exact R2. No continuation, BUILD commit, self-review, FREEZE or
later-lane authority yet.

## Fresh Amendment 7 human R2 acknowledgment

Accepted verbatim on 2026-08-04:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-7-2026-08-04,
> Work Order Amendment SHA-256
> 8712b18a43a35555573bce36f3fe6afd1b91b9709036dce1f1663dddd4c5c965,
> đúng 3 repair paths và final exact 28 BUILD paths, zero
> provider/network/remote-ingest calls.

COMMIT_STEWARD must commit/push only this four-path acknowledgment checkpoint
while preserving all exact 28 BUILD paths unstaged. After that push,
REPAIR_WORKER runs the ordered Amendment 7 continuation once, stops at the
first non-zero command or contract failure, does not retry and makes zero
provider/network/remote-ingest calls. No BUILD commit, self-review, FREEZE or
later-lane authority.

## Consumed Amendment 7 invocation and failure

Acknowledgment checkpoint `9742c3bede7658ab9c56724ad0ad58d23a9a5e9d`
was pushed. Amendment 7 preflight passed actual authority lineage, artifact
hashes, staged-empty and exact 10/25/28 bindings. The next stdin probe collected
test node ids but stopped before executing any test case because its guessed
selector could not find a node containing `zero_quality`. It was not retried.
No repair edit, test case or later gate ran; zero provider/network/
remote-ingest calls occurred during the invocation.

Amendment 7/R2 are consumed. Amendment 8 at
`docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_8.md` SHA-256
`4401af42da2f4da8c0f1bb856e624684f4309eb6c00f6f0407270331d1dd3347`
replaces guessed selectors with an exact direct seven-case stdin probe. It
retains unchanged exact-28 `c9e021d3…183d4e`, source/test-10
`addb052c…b7352`, protected-25 `513ba54f…6dda1`, exactly three repair paths,
final exact 28 and the remaining gates. Independent authorization review,
authority checkpoint and fresh exact R2 are mandatory before continuation.

## Amendment 8 authorization review PASS

Independent REVIEWER returned
`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no findings and no waiver,
in `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_8_AUTHORIZATION_REVIEW.md`
SHA-256 `6c324b4931947b7ee55068140524dce8575a47b2f7797c7db2635b8815e9fd87`.
The review reproduced the consumed Amendment 7 truth, exact-28/source-test-10/
protected-25 digests, three repair-surface hashes and empty staged set. It
inspected immutable source/tests and confirmed all seven direct cases are
distinct, executable, ordered, counted and disclosure-safe with required
restoration. Findings and waivers are `NONE`.

COMMIT_STEWARD must commit/push only Amendment 8, its review and four
continuity paths while preserving all exact 28 BUILD paths unstaged. Then stop
for fresh exact R2. No continuation, BUILD commit, self-review, FREEZE or
later-lane authority yet.

## Fresh Amendment 8 human R2 acknowledgment

Accepted verbatim on 2026-08-04:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-8-2026-08-04,
> Work Order Amendment SHA-256
> 4401af42da2f4da8c0f1bb856e624684f4309eb6c00f6f0407270331d1dd3347,
> đúng 3 repair paths và final exact 28 BUILD paths, zero
> provider/network/remote-ingest calls.

COMMIT_STEWARD must commit/push only this four-path acknowledgment checkpoint
while preserving all exact 28 BUILD paths unstaged. After that push,
REPAIR_WORKER runs the ordered Amendment 8 continuation once, stops at the
first non-zero command or contract failure, does not retry and makes zero
provider/network/remote-ingest calls. No BUILD commit, self-review, FREEZE or
later-lane authority.

## Consumed Amendment 8 invocation and failure

Acknowledgment checkpoint `132003c80fa073b28ebe7026e201ac1db5537eb0`
was pushed. Preflight, exact direct probe 7/7, the three-path catalog/knowledge
repair, knowledge validator, focused Knowledge Pack `86`, catalog check, full
non-live `1593 passed, 128 skipped` and session-state all passed. The next
command used nonexistent `scripts/check_file_sizes.py` and returned non-zero
before file-size/repository/JSON-YAML/import-I/O/secret/diff/final gates. It
was not retried. Zero provider/network/remote-ingest calls occurred.

Amendment 8/R2 are consumed. Amendment 9 at
`docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_9.md` SHA-256
`417a11af86915cca0249e3559236f498fc96f7e60c8363376b4493f26aefca0e`
binds immutable post-repair exact-28 `267232b3…0791`, source/test-10
`addb052c…b7352`, protected-25 `513ba54f…6dda1`, all completed repair hashes,
zero repair paths and the singular tracked `scripts/check_file_size.py` plus
remaining static/final gates. Independent authorization review, authority
checkpoint and fresh exact R2 are mandatory before continuation.

## Amendment 9 authorization review PASS

Independent REVIEWER returned
`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no findings and no waiver,
in `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_9_AUTHORIZATION_REVIEW.md`
SHA-256 `6b7819f41d769c0304b495d26319d64619944b5d869fd92ee0fc9115f3786c46`.
The review reproduced retained Amendment 8 evidence, immutable post-repair
exact-28/source-test-10/protected-25 and repair hashes, empty staged set, zero
repair paths, the singular tracked file-size script, repository validator,
inline static contract and zero-call/no-retry boundary. Findings and waivers
are `NONE`.

COMMIT_STEWARD must commit/push only Amendment 9, its review and four
continuity paths while preserving all exact 28 BUILD paths unstaged. Then stop
for fresh exact R2. No verification continuation, BUILD commit, self-review,
FREEZE or later-lane authority yet.

## Fresh Amendment 9 human R2 acknowledgment

Accepted verbatim on 2026-08-04:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-9-2026-08-04,
> Work Order Amendment SHA-256
> 417a11af86915cca0249e3559236f498fc96f7e60c8363376b4493f26aefca0e,
> đúng 0 repair paths và final exact 28 BUILD paths, zero
> provider/network/remote-ingest calls.

The operator also requested proactive finding handling. This does not expand
the zero-path invocation: COMMIT_STEWARD must push only this four-path
acknowledgment checkpoint, then REPAIR_WORKER runs Amendment 9 once, stops at
the first failure and does not retry. Any finding routes to a fresh scoped
amendment, independent review and fresh R2. No BUILD edit/commit, self-review,
FREEZE or later-lane authority.

## Consumed Amendment 9 invocation and file-size findings

Acknowledgment checkpoint `be63d4505e8b79e96e849090f34462b9918ed550`
was pushed and exact immutable preflight passed. The fresh file-size gate then
failed on `pipeline.py` 304/300, session memory 616/600 and this active handoff
724/600. Execution stopped; no retry or later gate ran, and zero provider/
network/remote-ingest calls occurred.

Per the operator's proactive-finding instruction, the Amendment 10 candidate
at `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_10.md` authorizes
exactly six repair paths/final exact 32 BUILD/continuity paths: a
semantic-preserving helper move plus lossless continuity rotation into two
bounded archives. It uses no waiver or debt entry. Independent authorization
review, authority checkpoint and fresh exact R2 are mandatory before repair.

Initial independent review
`docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_10_AUTHORIZATION_REVIEW.md`
SHA-256 `43dad00859cb906e446c1e6875dafedbc522e1374c070da195adcf22aa947a14`
returned only `A10-AUTH-F1`: the memory/handoff pre-hashes were stale and
self-referential because pending continuity embedded A10's own SHA. The
pending entries now omit that SHA. Their final raw hashes must be bound into
the Work Order and receive fresh independent re-review before checkpoint/R2.

Fresh re-review
`docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_10_AUTHORIZATION_REREVIEW.md`
SHA-256 `4ed7b30f48f876337cbedd63074098104f6f9b4f1a979e4a54d3fd532f546b7f`
closed F1 but returned residual `A10-AUTH-F2`: a mandatory future R2 append
changes the raw whole-file handoff hash before BUILD. A10 now binds only the
normalized UTF-8 archive-source blocks by fixed markers: memory 331 lines SHA
`d7d902ea…348e`, handoff 390 lines SHA `d8b6f8d8…ec14`. Review/R2 preamble
append cannot change those blocks; any drift within history to be archived
still fails. Git lineage continues to restrict authority/R2 checkpoint paths.
Fresh independent re-review is required before checkpoint/R2.

Independent authorization re-review 2
`docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_10_AUTHORIZATION_REREVIEW_2.md`
SHA-256 `f06ca38053b6315922513b0f646c7c5e8cda69f9beb0ad072d4fc21409c23944`
returns `WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no finding/waiver,
for amended Work Order SHA `6c396f1fc6faad345a5ae12d3d928e515d4c5bbf46a14b9743015740e1b2634b`.
F1/F2 are closed. COMMIT_STEWARD must commit/push only the Work Order, three
review artifacts and four continuity paths while exact-28 BUILD remains
unstaged and both archive-source block digests remain unchanged. Then stop for
the exact fresh Amendment 10 R2; no repair, gate, BUILD commit or FREEZE yet.

## Fresh Amendment 10 human R2 acknowledgment

Accepted verbatim on 2026-08-04:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-10-2026-08-04,
> Work Order Amendment SHA-256
> 6c396f1fc6faad345a5ae12d3d928e515d4c5bbf46a14b9743015740e1b2634b,
> đúng 6 repair paths và final exact 32 BUILD/continuity paths, zero
> provider/network/remote-ingest calls.

Authority checkpoint `14139b9b38d18f31d34a2a2e9c1a2a02415b47af` is pushed.
This R2 binds exactly one ordered continuation with no retry. COMMIT_STEWARD
must push only this four-path acknowledgment checkpoint while exact-28 BUILD
remains unstaged. REPAIR_WORKER then verifies the exact Amendment 10 preflight,
performs only the six-path repair and runs each ordered gate once, stopping on
the first failure with zero provider/network/remote-ingest calls. No BUILD
commit, self-review, FREEZE or later-lane authority.

## Amendment 10 consumed and Amendment 11 candidate

Acknowledgment checkpoint `9b1e34df7661a6a9877046ac65f770c772d1495b`
was pushed. Amendment 10 preflight passed. Before any repair edit, local atomic
patch construction raised `TypeError: Cannot read properties of undefined
(reading 'split')` while expanding `data.memoryBlock`; `apply_patch` was never
called. Execution stopped without retry. All 28 retained BUILD paths are
unchanged, both archives remain absent, every post-repair gate is `NOT_RUN`,
and provider/network/remote-ingest calls are zero.

Amendment 11 at
`docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_11.md` SHA-256
`fe59ef90d61fddba14f15f61d7f69260542b4d8852a9b2110d80e0ef5dd84287`
retains exact six repair paths/final exact 32 and corrects only patch transport:
each block must be read independently as UTF-8/base64, decoded and verified
before one atomic `apply_patch`. Independent authorization review, bounded
checkpoint and fresh exact R2 are required. No repair/gate/BUILD commit/
FREEZE or later-lane authority exists yet.

Independent Amendment 11 authorization review
`docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_11_AUTHORIZATION_REVIEW.md`
SHA-256 `4979d8b607b1605da378fab6ed6fb5db798e6977c577e5dea7a8954f8ca61503`
returns `WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no finding/waiver.
It reproduces consumed Amendment 10 truth, exact28/protected26/Python/block
bindings and accepts the corrected independently decoded/verified UTF-8/base64
transport before one atomic six-path patch. COMMIT_STEWARD must push only A11,
its review and four continuity paths with BUILD unstaged, then stop for fresh
exact Amendment 11 R2. No repair/gate/BUILD commit/FREEZE yet.

## Fresh Amendment 11 human R2 acknowledgment

Accepted verbatim on 2026-08-04:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-11-2026-08-04,
> Work Order Amendment SHA-256
> fe59ef90d61fddba14f15f61d7f69260542b4d8852a9b2110d80e0ef5dd84287,
> đúng 6 repair paths và final exact 32 BUILD/continuity paths, zero
> provider/network/remote-ingest calls.

Authority checkpoint `c88a752734fe2cc87b6b1028c3efb5cc702340fd` is pushed.
This R2 binds one ordered continuation and no retry. Push only this four-path
acknowledgment checkpoint with BUILD unstaged, then transfer to REPAIR_WORKER.

## Amendment 11 consumed and Amendment 12 candidate

Acknowledgment `f56456f1bdeed4874dfc81378073d4eacf4de2b8` was pushed.
The first preflight command failed PowerShell parsing on `foreach($x in$p)`.
No assertion, repair or later gate ran; no retry and zero calls. Amendment 12
at `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_12.md` SHA-256
`a16c32a5c351d4fabb06ad64f24d0f3ad3bcc3dda5194e978d8abf1e3b627918`
retains exact six/final32 and corrects only canonical multi-line preflight
syntax. Independent review/checkpoint/fresh R2 required; no repair authority.

Independent Amendment 12 review
`docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_12_AUTHORIZATION_REVIEW.md`
SHA-256 `6b807775c665c98d089be047ab81d6dd9a953759cca1906b6a32474c53aa9d32`
returns authorization PASS, no finding/waiver, for A12 SHA
`a16c32a5c351d4fabb06ad64f24d0f3ad3bcc3dda5194e978d8abf1e3b627918`.
Push only A12, review and four continuity paths with BUILD unstaged, then stop
for fresh exact A12 R2. No repair/gate/BUILD commit/FREEZE yet.

## Fresh Amendment 12 human R2 acknowledgment

Accepted verbatim: Amendment `a16c32a5c351d4fabb06ad64f24d0f3ad3bcc3dda5194e978d8abf1e3b627918`,
exactly 6 repair paths/final exact 32 BUILD/continuity paths, zero provider/
network/remote-ingest. Authority `82071ee8f8fb0615e763d20789c52c7db7a5b594`
is pushed. Push only four acknowledgment paths, then one no-retry continuation.

## Amendment 12 consumed and Amendment 13 candidate

Ack `bf9daaf3feb108c8f9fd63352e5d80ddfec7e717` pushed; preflight PASS.
Step 2 verified both base64 blocks but V8 lacked `TextDecoder`, so `apply_patch`
was never called. No retry, 0/6 touches, archives absent and zero calls.
Amendment 13 at `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_13.md`
SHA `332895d89799ec724031057cf265b1c84e6a62a8510b6f86363a4fe309f9da50`
retains exact6/final32 and substitutes strict pure-JS UTF-8 scalar decoding.
Independent review/checkpoint/fresh R2 required; no repair authority.

Independent Amendment 13 authorization review
`docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_13_AUTHORIZATION_REVIEW.md`
SHA `c9719ab585e33f6b74f9ea0e3e182e681ffa1a5f9fa952e73892294e502d36a7`
returns PASS, no finding/waiver, for A13 SHA
`332895d89799ec724031057cf265b1c84e6a62a8510b6f86363a4fe309f9da50`.
Push only A13, review and four continuity paths with BUILD unstaged, then stop
for fresh exact A13 R2. No repair/gate/BUILD commit/FREEZE yet.

## Fresh Amendment 13 human R2 acknowledgment

Accepted verbatim for Amendment
`332895d89799ec724031057cf265b1c84e6a62a8510b6f86363a4fe309f9da50`,
exactly six repair/final exact 32 BUILD/continuity paths, zero provider/network/
remote-ingest. Authority `af691d049ca37288d99a09ac0df790018e3fc31c` is
pushed. Push only four acknowledgment paths, then one no-retry continuation.

## Amendment 13 consumed and Amendment 14 candidate

Ack `20f3f73c5fdd9d3704823c8191f067f57422be76` pushed. Preflight,
atomic six-path repair and file-size gate passed. A read-only `rg` inventory
then failed on Windows-invalid wildcard literals; no retry, later gates not
run and zero calls. Amendment 14 at
`docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_14.md` SHA
`a1a76cbfa979855cf64d650ccca5ede807470b12bf5e9930a7cc7a1cb15bbe17`
authorizes zero repair touches/final exact32 and explicit five-file focused
suite. Independent review, partial-staged checkpoint and fresh R2 required.

Independent Amendment 14 review
`docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_14_AUTHORIZATION_REVIEW.md`
SHA `f50ffde1259973cca317d091e8ce13bc8622a9cf44265b9de4d9207e34d916d1`
returns PASS, no finding/waiver, for A14 SHA
`a1a76cbfa979855cf64d650ccca5ede807470b12bf5e9930a7cc7a1cb15bbe17`.
Push exact six authority paths using partial staging for only memory/handoff
governance hunks; preserve all exact32 repair hunks dirty/unstaged. Then stop
for fresh exact A14 R2. No continuation/BUILD commit/FREEZE yet.


## Intake boundary

P3-A may design only a deterministic local, fail-closed transformation boundary
that preserves source linkage, refuses ambiguity/fabrication, separates
sensitivity from topic classification, emits quarantine/data-quality receipts
and produces no context candidate on failure. It does not own confirmed truth,
raw persistence, external ingest, provider calls, retrieval/RAG, P3-B/P3-C,
learning or production behavior.

## Evidence boundary

No provider call is needed or authorized for INTAKE. Future deterministic local
claims may use contract/unit evidence. Any future claim about actual AI/provider
governance requires a separately approved real-provider call and sanitized
receipt under AGENTS.md.

## Design candidate

ADR `docs/decisions/ADR_2026-08-03_P3A_REFINERY.md` resolves the eight INTAKE
decisions with a pure local package, versioned text-field provenance, fixed
fail-closed stages, syntax-only normalization, caller-scoped advisory dedupe,
separate sensitivity/topic fields, versioned redaction, typed no-candidate
outcomes, strict 100/100 control-coverage admission and minimal
`ContextCandidateV1`. The current fixture remains a negative case.

## Retained DESIGN review

Independent review returned `REVIEW_FAIL`, no waiver:

- F1 dedupe tuple/window/collision mechanics underspecified;
- F2 quarantine/source ownership and no-sink semantics underspecified;
- F3 stage failure/quality/disposition mapping ambiguous;
- F4 candidate schema and digest preimage not reproducible.

The ADR repairs all four: fingerprints are SHA-256+SHA-512+length over bounded
scope/window records; quarantine has explicit distinct owners/route and closed
reasons; nine receipts plus precedence make candidate absence total; and
ContextCandidateV1 has an exact canonical JSON preimage/fingerprint.

Independent re-review returned `DESIGN_REVIEW_PASS`, no waiver, bound to ADR
SHA-256 `57ec06fc72e6ec2baad95079cdeff7eabfe7eb2837841dfc7c11cdba256e696e`.
Any ADR byte change requires fresh review.

## SPEC candidate

`docs/specs/P3A_REFINERY_SPEC.md` binds immutable parent ADR
`57ec06fc…e696e` and Amendment 1 `dc091f2b…f0e4a` into R1-R30 and AC-01 through
AC-12. It fixes the nine-stage order, three typed fingerprint preimages, closed
failure/disposition schemas, 100/100 control-coverage admission, deterministic
and disclosure properties, synthetic fixture matrix and zero-I/O claim boundary.

## Retained SPEC review and repair

Independent review of SPEC SHA-256 `3471bc9b…e8511` returned `REVIEW_FAIL`, no
waiver. F1 found wrong normative R-number references; F2 found the stage-reason
vocabulary open; F3 found orphan `NOT_RUN` was not rejected; F4 found the
dual-digest-equal/length-different collision case ambiguous.

The repaired candidate changes only those findings: fingerprint preimages now
bind R19/R23 and missing context binds R21; `StageReason` and permitted
stage/outcome pairs are closed; the receipt language is exactly `PASS^9` or
`PASS* FAIL NOT_RUN*`; and collision is unequal full triples with either digest
equal, with explicit acceptance vectors. The failed receipt remains immutable.

## Retained SPEC re-review

Independent re-review of repaired SPEC `f836f5d3…49ffc` closed F1-F4 exactly,
then returned `REVIEW_FAIL`, no waiver, for F5-F7. F5 shows an invalid or
disclosure-unsafe envelope cannot construct the parent-mandated non-null safe
provenance result without echoing or fabrication. F6 shows ready `UNIQUE` and
`REDACTED_TEXT_MATCH` outcomes have no typed public field. F7 shows ENVELOPE,
DEDUPE and CANDIDATE_ADMISSION receipt versions have no normative source.

Because F5 changes a parent DESIGN invariant, the tranche returns to DESIGN.
Amendment 2 must define a pre-admission rejection union branch, executed-stage
typed dedupe status, and one exact version source for every stage. The existing
SPEC is retained as a failed candidate and may change only after Amendment 2
receives independent review pass.

## Design Amendment 2 candidate

`docs/decisions/ADR_2026-08-03_P3A_REFINERY_AMENDMENT_2.md` resolves only
F5-F7. It makes the public output a closed union with a provenance-free,
disclosure-safe `PreAdmissionRejectionV1` for structurally unconstructible
input; adds typed `dedupe_status` with exact outcome/nullability rules; and maps
nine explicit control versions to the nine receipts. It also makes exact-source
matching a DEDUPE failure so duplicate disposition and later `NOT_RUN` receipts
are mechanically consistent. Parent candidate/dedupe preimages stay unchanged.

Independent review returned `DESIGN_AMENDMENT_REVIEW_PASS`, no waiver, bound to
Amendment 2 SHA-256 `393ca069c6ead96bfc7de52f453952cf12dcab1799fbbdccb5836668632291dc`.
F5-F7 are closed at DESIGN. Any byte change requires fresh DESIGN re-review.

## Repaired SPEC candidate

SPEC SHA-256 `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
retains F1-F4 and binds reviewed Amendment 2: structural invalid input returns
the exact provenance-free pre-admission branch; admitted fingerprint mismatch
uses safe locally recomputed provenance; `dedupe_status` is typed with
exact-source fail-stop semantics; and every receipt has one exact mapped
`control_version`. The fixture/acceptance matrix covers both union branches,
version substitution, public dedupe status and no-fabrication disclosure.

Fresh independent final review returned `SPEC_REVIEW_PASS`, no waiver, bound to
SPEC SHA-256 `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`.
F1-F7 and all R1-R30/AC-01..12 are closed. Any SPEC byte change requires fresh
review.

## Work Order candidate

`docs/work_orders/P3A_REFINERY_WORK_ORDER.md` SHA-256
`3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
authorizes exactly 26 mandatory BUILD paths only after independent authorization
review and fresh exact human R2 acknowledgment. BUILD has zero
provider/network/remote-ingest calls, stops at the first failed gate with no
retry, and cannot activate any runtime/later-lane claim.

Independent review returned `WORK_ORDER_AUTHORIZATION_REVIEW_PASS`, no waiver,
bound to Work Order `3a2bf12e…bcd3c5`. It confirms the 26-path split is
sufficient/non-expansive and the zero-call/no-retry boundary is executable. This
pass is not BUILD authority.

## Fresh human R2 acknowledgment

Accepted verbatim on 2026-08-03:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-2026-08-03, Work Order SHA-256
> 3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5,
> đúng 26 BUILD paths, zero provider/network/remote-ingest calls.

It binds exactly one invocation. Clean pushed authority baseline is
`72a712d51ad53c2de38f0784b257c42428f80738`; Work Order/SPEC hashes match and
the worktree was clean at acceptance. The acknowledgment is not consumed until
this four-path continuity checkpoint is committed/pushed and the first BUILD
path is changed. No retry, provider/network/remote-ingest call or expansion.

## Consumed BUILD invocation and failure

Pre-BUILD checkpoint `b93e403cf0ab6d659de0706c058d1cd7250e75d0` was clean and
pushed. The acknowledgment was consumed when the first authorized BUILD path
changed. BUILD remained at zero provider/network/remote-ingest calls.

- Gate 1 models/canonical/contract: PASS, 15 tests.
- Gate 2 pipeline/adversarial: PASS, 16 tests.
- Gate 3 full non-live suite: FAIL, 3 failed / 1560 passed / 128 skipped / 8 errors.
- Gate 4 and all later gates: NOT RUN by stop-first/no-retry rule.
- BUILD diff at stop: 25 of 26 authorized paths; generated
  `docs/catalog/MODULE_CATALOG.md` was correctly not written after gate 3 failed.

The failure exposes two Work Order defects, not authority to repair them:

1. full suite includes catalog-drift enforcement but the Work Order orders
   catalog generation only after the full suite, making that test fail before
   the authorized generator step;
2. changing `IMPLEMENTATION_STATUS.json` invalidates the closed Knowledge Pack's
   `PROJECT_CONTEXT.md` eligibility/source pin, while the Work Order includes no
   knowledge manifest/context repair paths.

The dirty failed candidate is retained exactly. No test rerun, catalog write,
source-pin repair, commit or push occurred after failure.

## Work Order Amendment 1 candidate

`docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_1.md` binds the exact
25-path failed candidate manifest digest `58e4685e…8484da`, keeps 24 paths
byte-immutable, and permits exactly four repair touches: registry, generated
catalog, Project Context and knowledge manifest. Final BUILD diff is exactly 28
paths. Corrected order generates catalog and refreshes the two changed source
pins before Knowledge Pack checks and the single full-suite rerun.

The prior independent review returned
`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, but its assertion that
`dd6e2d5c…eef5d` reproduced a case-sensitive sort is invalidated. Pre-stage
COMMIT_STEWARD validation reproduced `dd6e2d5c…eef5d` only with case-insensitive
ordering and reproduced `58e4685e…8484da` with the stated Unicode-code-point,
case-sensitive ordering. No BUILD path changed. Amendment 1 now carries the
correct digest and new SHA-256
`587412712cc6d98b6c7e85cba99d9d650d38097ed316e09992243d07ea965546`.
Fresh independent re-review returned
`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no findings and no waiver,
in artifact SHA-256
`ff85f3cc4d2b694755a0855e5b596648fc8a5fb3b92ba6f248779a356ee50174`.
It independently reproduced the exact case-sensitive 25-path digest and
re-confirmed the four repair touches, 24 protected paths, final exact 28 paths,
corrected order, zero-call and no-retry boundaries.

## Pre-stage authority validation finding

- Session state: PASS.
- File-size guard: PASS.
- `git diff --check`: PASS.
- Dirty set: exact 31 paths = six authority candidates + unchanged 25-path
  failed BUILD candidate; staged set remained empty.
- Finding: prior review's digest statement and bound value were inconsistent.
- Disposition: prior Amendment 1 review PASS invalidated, no waiver; no stage,
  commit, push, repair, test rerun, provider or remote-ingest action occurred.

## Next governed move

Fresh human R2 acknowledgment accepted verbatim on 2026-08-03:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-1-2026-08-03,
> Work Order Amendment SHA-256
> 587412712cc6d98b6c7e85cba99d9d650d38097ed316e09992243d07ea965546,
> đúng 4 repair paths và final exact 28 BUILD paths, zero
> provider/network/remote-ingest calls.

It binds exactly one continuation invocation with no retry. COMMIT_STEWARD
must commit/push only this four-path acknowledgment checkpoint while preserving
the 25 BUILD paths unstaged. The acknowledgment is consumed only after that
push and the first repair path changes. REPAIR_WORKER then follows Amendment 1
in exact order, stops at the first failure, makes zero provider/network/
remote-ingest calls and yields at most a dirty 28-path candidate pending
independent BUILD review. No BUILD commit, self-review, FREEZE or later-lane
authority.

## Consumed Amendment 1 continuation and failure

Acknowledgment checkpoint `7b4cadb8ac01e3fd4f2284b76416a83dc8cd5277`
was pushed before the continuation. Preflight confirmed HEAD/origin, immutable
baseline ancestry, parent/Amendment/SPEC hashes, empty staged set, exact 25-path
candidate digest `58e4685e…8484da` and protected-24 digest
`d61bd541…d2bec2`.

The single authorized generator run exited 0 and changed only
`docs/catalog/MODULE_REGISTRY.json` plus generated
`docs/catalog/MODULE_CATALOG.md`. The immediately required semantic check then
failed: `refinery-bridge.status` remained `contract-only`; Amendment 1 required
the generator to set computed truth to `partial`. Protected-24 digest remained
unchanged and the dirty BUILD set became exactly 26 paths.

Execution stopped at that first contract failure. `knowledge/PROJECT_CONTEXT.md`
and `knowledge/manifest.json` were not touched. Knowledge validator/focused
tests, catalog check, full suite and every later gate were NOT RUN. A subsequent
read-only snapshot command had a PowerShell parse error before reading/writing
files and was not retried. The invocation made zero provider/network/
remote-ingest calls and no retry, commit or push.

Amendment 1 and its R2 acknowledgment are consumed. The next move is a fresh
WORK_ORDER amendment that binds the retained exact 26-path candidate and
authorizes only the minimal catalog-status correction plus the still-unrun
knowledge/gate sequence. It requires independent review and fresh exact R2.

## Work Order Amendment 2 candidate

`docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_2.md` SHA-256
`0f47068a71d59dc553ffdf459e52c5e622325fabff9015a16db73249ea3614c4`
binds the exact retained 26-path candidate digest `a90307c7…e9d2`, registry
`23273fb2…65b8`, generated catalog `f814040d…e8e6` and protected-24 digest
`d61bd541…d2bec2`.

It corrects the newly proven ownership defect only: edit the single
`refinery-bridge.status` value from `contract-only` to `partial` before one
catalog render. The repair-touch ceiling remains exactly registry, catalog,
Project Context and knowledge manifest; final BUILD diff remains exact 28
paths. It then runs only the still-unrun knowledge/catalog/full/repository
gates, once each, stop-first/no-retry and zero provider/network/remote-ingest.

Independent authorization review returned
`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no findings and no waiver,
in `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_2_AUTHORIZATION_REVIEW.md`
SHA-256 `42026b238140d3519cc083dbc02e97f1935cf7ed2ce66e86010e5cad92eda904`.
It independently reproduced the 26-path, protected-24, registry and catalog
digests; confirmed generator behavior; and accepted the one-field correction,
four repair paths, final exact 28 paths, ordered gates and zero-call/no-retry
boundary as sufficient and non-expansive.

COMMIT_STEWARD must stage/commit/push only Amendment 2, its review and the four
continuity paths while preserving all 26 BUILD paths unstaged. Then stop for
fresh literal R2 bound to Amendment SHA `0f47068a…14c4`, four repair paths and
final exact 28 BUILD paths. No continuation/rerun/provider/network/
remote-ingest or later-lane authority yet.

## Fresh Amendment 3 human R2 acknowledgment

Accepted verbatim on 2026-08-03:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-3-2026-08-03,
> Work Order Amendment SHA-256
> 30896c92b12beb8b5f6d153eb8ea4cc642b80004a0c4b400cd61f91dccc6e0f4,
> đúng 2 repair paths và final exact 28 BUILD paths, zero
> provider/network/remote-ingest calls.

It binds one continuation with no retry. COMMIT_STEWARD must commit/push only
this four-path checkpoint while preserving all 26 BUILD paths unstaged. The
acknowledgment is consumed only after that push and the first knowledge path
changes. REPAIR_WORKER then runs Amendment 3 in exact order, stops first
failure, makes zero provider/network/remote-ingest calls and yields at most a
dirty exact 28-path candidate pending independent BUILD review. No BUILD
commit, self-review, FREEZE or later-lane authority.

## Amendment 3 continuation PASS

Acknowledgment checkpoint `3972bbb7202af63c60e49c44b3038b753bc976ac`
was pushed before continuation. Preflight reproduced exact immutable 26-path
digest `c7c1761c…01b8`, registry `d3b84850…9f38`, catalog
`6b5ad6a2…3e92`, both `partial`, and empty staged set.

REPAIR_WORKER changed exactly `knowledge/PROJECT_CONTEXT.md` and
`knowledge/manifest.json`. Only the two authorized project-context source-pin
digests changed in the manifest. Ordered evidence passed once each:

- project knowledge validator: PASS;
- focused Knowledge Pack suite and local disposable helper: `86 passed`;
- catalog check without write: PASS;
- full non-live suite: `1571 passed, 128 skipped`;
- session-state, file-size and repository validators: PASS;
- JSON/YAML parse, forbidden import/I/O, secret and diff checks: PASS;
- final exact audit: 28 BUILD paths, two repair paths, immutable-26 digest
  unchanged, context 29 lines and staged set empty.

No provider/network/remote-ingest call or retry occurred. The output is only a
dirty deterministic local BUILD candidate pending independent review. It has
no runtime caller and proves no P3-A closure, provider/ingest/persistence,
`data_scope` enforcement, retrieval/RAG, learning, production or Phase 3
completion.

ORCHESTRATOR must transfer the exact candidate to independent REVIEWER. No
BUILD edit, stage, commit, push, self-review, FREEZE or later-lane authority.

## Fresh Amendment 2 human R2 acknowledgment

Accepted verbatim on 2026-08-03:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-2-2026-08-03,
> Work Order Amendment SHA-256
> 0f47068a71d59dc553ffdf459e52c5e622325fabff9015a16db73249ea3614c4,
> đúng 4 repair paths và final exact 28 BUILD paths, zero
> provider/network/remote-ingest calls.

It binds exactly one continuation invocation with no retry. COMMIT_STEWARD
must commit/push only this four-path acknowledgment checkpoint while preserving
all 26 BUILD paths unstaged. The acknowledgment is consumed only after that
push and the single registry status value changes. REPAIR_WORKER then follows
Amendment 2 in exact order, runs every remaining command once, stops first
failure, makes zero provider/network/remote-ingest calls and yields at most a
dirty exact 28-path candidate pending independent BUILD review. No BUILD
commit, self-review, FREEZE or later-lane authority.

## Consumed Amendment 2 continuation and failure

Acknowledgment checkpoint `78ea4e58d61f75cd90ef153f5ea9f7396884bfe1`
was pushed before continuation. Preflight confirmed authority lineage, all
immutable hashes, empty staged set, exact 26-path candidate digest
`a90307c7…e9d2` and protected-24 digest `d61bd541…d2bec2`.

The one authorized registry edit changed only `refinery-bridge.status` from
`contract-only` to `partial`. The catalog generator then ran once and returned
PASS. The immediately ordered verification wrapper returned non-zero because
PowerShell rejected its script at parse time (`foreach` missing whitespace),
before any verification check executed.

Execution stopped there. The verification command was not retried.
`knowledge/PROJECT_CONTEXT.md` and `knowledge/manifest.json` were not touched;
Knowledge validator/focused tests, catalog check, full suite and later gates
were NOT RUN. Zero provider/network/remote-ingest calls occurred during the
invocation, and no BUILD commit/push occurred.

Amendment 2 and its R2 are consumed. WORK_ORDER_AUTHOR must bind the retained
exact post-generator 26-path candidate in a fresh amendment that authorizes
only the unrun verification/knowledge/gate sequence. Independent review,
authority checkpoint and fresh exact R2 are mandatory.

## Work Order Amendment 3 candidate

`docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_3.md` SHA-256
`30896c92b12beb8b5f6d153eb8ea4cc642b80004a0c4b400cd61f91dccc6e0f4`
binds exact post-generator 26-path digest `c7c1761c…01b8`, registry
`d3b84850…9f38` and catalog `6b5ad6a2…3e92`. Both catalog surfaces carry
`refinery-bridge: partial`.

All 26 candidate paths are byte-immutable. Amendment 3 prohibits catalog
`--write` and authorizes exactly `knowledge/PROJECT_CONTEXT.md` plus
`knowledge/manifest.json`; final BUILD diff remains exact 28 paths. It then
runs only never-run knowledge/catalog/full/repository gates, once each,
stop-first/no-retry and zero provider/network/remote-ingest.

Independent authorization review returned
`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no findings and no waiver,
in `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_3_AUTHORIZATION_REVIEW.md`
SHA-256 `13635fd1b58ac8f4a9a8cdf329d35ea294f55d103157a6f0bf9ab837480a9ad6`.
It reproduced all retained hashes/digest and confirmed two repair paths, final
exact 28, two pin strings only, catalog-write prohibition, ordered gates and
zero-call/no-retry as sufficient and non-expansive.

COMMIT_STEWARD must stage/commit/push only Amendment 3, its review and the four
continuity paths while preserving all 26 BUILD paths unstaged. Then stop for
fresh literal R2 bound to Amendment SHA `30896c92…e0f4`, two repair paths and
final exact 28 BUILD paths. No continuation/rerun/provider/network/
remote-ingest or later-lane authority yet.
