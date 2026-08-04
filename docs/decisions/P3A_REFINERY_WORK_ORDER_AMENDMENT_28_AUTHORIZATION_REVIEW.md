# P3-A Refinery Work Order Amendment 28 — Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk / phase: `R2 / WORK_ORDER`
- Amendment reviewed:
  `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_28.md`
- Reviewed SHA-256:
  `793dfe4f99f8bd8a4ec22977e1e0ca1a7af18d264b7fd91c9a10507c14da8db0`
- Provider/network/remote-ingest calls during review: `0/0/0`
- Findings: `NONE`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 28 is necessary, sufficient and non-expansive. It authorizes only
the two missing leading ASCII spaces in the already-dirty
`knowledge/manifest.json`, preserves the final exact35 candidate, and resumes
only the A27 gates that never ran after its immediate manifest post-hash stop.
Independent raw-byte simulation reproduces the required manifest and stable33
post-hashes exactly.

This PASS is authorization-review evidence only. It performs no repair and
grants no BUILD commit, self-review, FREEZE or later-lane authority.

## Consumed A27 truth

A27 authority checkpoint
`b2a593df9e999476f97125cf9eecf7aa8bfc5711` and acknowledgment checkpoint
`bbf02b674ec097c96351f7c6c13907e7dd87535a` are pushed. Current
`HEAD == origin/main == bbf02b674ec097c96351f7c6c13907e7dd87535a`.

A27 preflight passed and its atomic exact2 patch produced the reviewed status
post-hash
`18b21d8d263ff0518389ab413550b006661d9fabee83cb373320235a6d9ab404`.
The manifest contains the correct new pin exactly once but with eight leading
ASCII spaces. Its immediate required post-hash assertion failed, execution
stopped without retry, and all later JSON/Knowledge/session/repository/security/
final gates remained `NOT_RUN`. No provider/network/remote-ingest call occurred.
A27 and its R2 are therefore consumed and do not authorize a retry.

## Exact35 and immutable bindings

The canonical A26 `finalExact35Paths` list contains 35 unique paths and exactly
matches the retained candidate. The staged set is empty. Excluding canonical
memory and active handoff gives exact33; excluding those two plus the sole A28
repair path gives exact32 protected paths.

| Binding | Required | Reproduced | Result |
|---|---|---|---|
| Work Order SHA-256 | `793dfe4f99f8bd8a4ec22977e1e0ca1a7af18d264b7fd91c9a10507c14da8db0` | same | PASS |
| Candidate paths | `35` | `35` | PASS |
| Repair paths | `1` | `knowledge/manifest.json` only | PASS |
| Staged paths | `0` | `0` | PASS |
| Manifest pre-hash | `1988ab40737f9f6e2e695c145c2c7a197962b902211f963ef76a8eec2acfbd46` | same | PASS |
| Protected32 | `a23aa562f08c2154c96d3b7664589c1c05c1861e77eaab23b2074b3020673cca` | same | PASS |
| Stable33 pre | `a480733e3565d3ed6b51773a0fef1e725025618afeb176e266ebfae0ad76d7a2` | same | PASS |

The status file remains at the exact reviewed A27 post-image. All other
exact35 paths, including source, tests, contracts, fixtures, catalogs, debt
registry, archives and status, are byte-protected by A28.

## Independent two-space simulation

The reviewer read `knowledge/manifest.json` as raw bytes and verified:

- the exact eight-space line containing the reviewed status pin occurs once;
- the corresponding ten-space line occurs zero times;
- replacing only the two leading ASCII spaces yields valid JSON;
- no value, field, ordering, line ending or other byte changes.

The simulated output reproduces:

| Binding | Required | Reproduced | Result |
|---|---|---|---|
| Manifest post-hash | `251ca93f47a6527a0d941b7cbd371130a041fb21154ab269a05153b7751844a4` | same | PASS |
| Stable33 post | `f6ed2c05f7db2737d5d668568eaaf0ea93e22dd66ba19120b10330aab27ee5ff` | same | PASS |
| Eight/ten-space post-count | `0 / 1` | `0 / 1` | PASS |
| Protected32 | unchanged | unchanged | PASS |

The simulation was memory-only; no repository file was written.

## Scope, gates and stop boundary

The one-path/two-byte repair is the minimum sufficient change. Immediate
post-hash, occurrence, exact35, protected32, stable33 and staged0 assertions
precede every resumed gate. The remaining two JSON parses, project Knowledge
validator/focused suite, session, file-size, repository, local secret/diff and
final audits are proportionate. Full and Refinery suite reruns are correctly
excluded because their source/test/contract/fixture/catalog bytes remain
protected.

The invocation is one-shot, stop-first and no-retry. It permits zero provider,
network, remote-ingest or POST calls and no status/source/test/catalog/fixture
edit, alternate fix, BUILD commit, self-review, FREEZE, waiver or later lane.
Any first failure consumes A28 and requires new reviewed authority plus R2.

## Exact fresh R2

The exact proposed acknowledgment is this one line with no leading/trailing
whitespace or newline:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-28-2026-08-04, Work Order Amendment SHA-256 793dfe4f99f8bd8a4ec22977e1e0ca1a7af18d264b7fd91c9a10507c14da8db0, đúng 1 repair path và final exact 35 BUILD/continuity paths, zero provider/network/remote-ingest calls.

- Unicode code points: `271`
- SHA-256 over exact UTF-8 bytes:
  `b870ed3c5410f85799caf4e8a5e62abebe162ca3b7682470954afeb1f0ecc45e`

This matches canonical pending authority. The acknowledgment is not yet
accepted and grants nothing until the governance-only authority checkpoint is
pushed and the operator sends the exact line above.

## Exact next move

`COMMIT_STEWARD` may commit/push only A28, this review and bounded continuity
authority updates while preserving exact35 unstaged. Then stop for the exact
fresh R2 above. No repair or later action is authorized before its acceptance.

## Claim boundary

This review authorizes only the bounded one-path indentation repair process.
It proves no provider behavior, remote ingestion, runtime `data_scope`,
retrieval/RAG, production readiness, BUILD completion, P3-A closure or Phase 3
completion.
