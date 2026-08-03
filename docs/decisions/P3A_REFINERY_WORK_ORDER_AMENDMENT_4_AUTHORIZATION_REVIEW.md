# P3-A Refinery Work Order Amendment 4 — Independent Authorization Review

> **Re-review history:** The first authorization review of Amendment candidate
> SHA-256 `69f512066d879aada49d9c0875f408b9666c246ae98ee5d476becadde90fc5a7`
> returned `WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_FAIL` because its
> protected-15 digest was culture-sorted. That review artifact is retained in
> this file's history at SHA-256
> `42eb1c29385297cd012e0a4818fdbb8e688e7a218e361aca9e6022cf9d903ef8`;
> the finding was valid and received no waiver. This updated artifact records a
> fresh independent re-review of corrected Amendment SHA-256
> `0f79fcc75ae468c0c56a2db39d821738e0b863bf94710f2eebcbf845020fd0dd`.

- Review date: `2026-08-03`
- Role: `REVIEWER` (independent authorization review)
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Amendment under review SHA-256: `0f79fcc75ae468c0c56a2db39d821738e0b863bf94710f2eebcbf845020fd0dd`
- Superseded Amendment candidate SHA-256: `69f512066d879aada49d9c0875f408b9666c246ae98ee5d476becadde90fc5a7`
- Superseded FAIL review artifact SHA-256: `42eb1c29385297cd012e0a4818fdbb8e688e7a218e361aca9e6022cf9d903ef8`
- Corrected BUILD review SHA-256: `ccc6c4c25fc00000be34d443ffdb4d59c665f1436641e3f89b06b4906480b405`
- SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- Parent Work Order SHA-256: `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
- Amendment 1 SHA-256: `587412712cc6d98b6c7e85cba99d9d650d38097ed316e09992243d07ea965546`
- Amendment 2 SHA-256: `0f47068a71d59dc553ffdf459e52c5e622325fabff9015a16db73249ea3614c4`
- Amendment 3 SHA-256: `30896c92b12beb8b5f6d153eb8ea4cc642b80004a0c4b400cd61f91dccc6e0f4`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

The corrected Amendment 4 closes the sole authorization finding without
waiver. Its retained exact-28 and protected-15 manifests reproduce under the
mandatory ordinal, case-sensitive algorithm; its exact 13 repair paths remain
sufficient and non-expansive for corrected BUILD-review findings F2-F6; and
its ordered stop-first/no-retry evidence and zero-call boundary are adequate.

This PASS authorizes no repair by itself. Repair remains gated on the corrected
authority and synchronized continuity being committed/pushed while all 28
BUILD paths remain unstaged, followed by the exact fresh human R2
acknowledgment required by Amendment 4.

## Authority and lineage

The corrected Amendment, corrected BUILD review, unchanged SPEC, parent Work
Order and Amendments 1-3 reproduce the SHA-256 values shown above. The
corrected BUILD review properly retracts its original manifest finding and
retains disposition `REVIEW_CHANGES_REQUIRED` only for F2-F6. Amendment 4
neither changes DESIGN or SPEC nor expands the candidate's deterministic-local
claim boundary.

An in-memory reconstruction independently removed only the new binding-history
block and restored the former protected digest. The reconstructed bytes hash to
`69f512066d879aada49d9c0875f408b9666c246ae98ee5d476becadde90fc5a7`,
exactly the superseded Amendment candidate. The corrected Amendment therefore
changes only the protected digest and transparent correction/history text; it
does not alter the repair contract, path partition, gates or claim boundary.

## Independent manifest reproduction

The reviewer used explicit typed `string[]` collections and
`[Array]::Sort(..., [StringComparer]::Ordinal)`. Each manifest record was
encoded as `path + NUL + lowercase_file_sha256 + LF` in UTF-8.

### Retained candidate

- path count: `28`
- reproduced SHA-256:
  `e43e53e4610a596d987f9f3a5c70a97ebfd35ffa4337f3bc3c8aacc9b8bc4eae`
- Amendment 4 binding:
  `e43e53e4610a596d987f9f3a5c70a97ebfd35ffa4337f3bc3c8aacc9b8bc4eae`
- result: `PASS`
- staged path count: `0`

### Protected candidate

Removing the exact 13 repair paths leaves these 15 protected paths:

1. `IMPLEMENTATION_STATUS.json`
2. `fixtures/refinery/normalized_message.json`
3. `fixtures/refinery/qualified_time_message.json`
4. `knowledge/PROJECT_CONTEXT.md`
5. `packages/refinery-bridge/README.md`
6. `packages/refinery-bridge/contracts/refinery_contract.yaml`
7. `packages/refinery-bridge/pyproject.toml`
8. `packages/refinery-bridge/src/refinery_bridge/__init__.py`
9. `packages/refinery-bridge/src/refinery_bridge/canonical.py`
10. `packages/refinery-bridge/src/refinery_bridge/dedupe.py`
11. `packages/refinery-bridge/src/refinery_bridge/enums.py`
12. `packages/refinery-bridge/src/refinery_bridge/input_models.py`
13. `packages/refinery-bridge/src/refinery_bridge/normalization.py`
14. `pyproject.toml`
15. `tests/unit/test_refinery_canonical.py`

- ordinal, case-sensitive reproduced SHA-256:
  `ce531fb7fe4b8fa7c97aa29863cf1980a8665f5d74d21fb3d17259af37644784`
- corrected Amendment 4 binding:
  `ce531fb7fe4b8fa7c97aa29863cf1980a8665f5d74d21fb3d17259af37644784`
- result: `PASS`

The first Amendment candidate's culture-sensitive binding
`dec7b368407833c5c36bbd747f6f8507242c56a532aa5e34cb9b5c2a147da3c5`
is retained only as correction history. The current binding is the explicit
typed-ordinal result and introduces no candidate-byte or path-set change.

## Thirteen-path sufficiency and scope review

Apart from the invalid protected digest, the exact 13-path ceiling is
sufficient and non-expansive:

| Review finding | Authorized repair surfaces | Assessment |
|---|---|---|
| F2 public-result invariants | `output_models.py`, `receipt_models.py`, `pipeline.py`, focused model/pipeline/contract tests | `SUFFICIENT` — canonical helpers can be consumed without modifying protected `canonical.py` |
| F3 executable R27 matrix | `_refinery_fixtures.py` plus four authorized test modules | `SUFFICIENT` — permits at least 28 named, independently executed cases without a new path |
| F4 fail-stop paths | `controls.py`, `protection.py`, `pipeline.py` and authorized tests | `SUFFICIENT` — existing closed enums/contract already contain required reason values and need not change |
| F5 safe boundaries/offsets | `controls.py`, `receipt_models.py`, `output_models.py` and authorized tests | `SUFFICIENT` — existing `validate_safe_string` may be reused without changing protected `input_models.py` |
| F6 unrelated catalog mutation | registry, generated catalog and registry pin in `knowledge/manifest.json` | `SUFFICIENT` — restores only the unrelated status while retaining `refinery-bridge=partial` |

Current line counts also leave room under the repository's 300-line Python
hard limit across the authorized source/test surfaces. No new BUILD path,
protected-file edit, runtime integration or wider architectural change is
needed to repair F2-F6.

## Gate and claim-boundary assessment

The prescribed order is appropriate: immutable preflight first; source/test
repair; focused tests; a dedicated contradiction/fail-stop/disclosure probe;
one catalog generation; one exact knowledge-pin update; knowledge, catalog,
full-suite and repository gates; then exact-set/protected-digest/staged-state
closure. It clearly requires stop-first and prohibits retry of failed or
successful commands.

The zero provider/network/remote-ingest boundary is explicit and consistent
with the deterministic-local repair. The output remains only a dirty exact
28-path BUILD candidate pending fresh independent BUILD review. It grants no
commit, push, self-review, FREEZE, runtime caller, persistence, `data_scope`,
retrieval/RAG, learning, production or Phase 3 claim.

## Finding closure and next governed move

- `A4-AUTH-R1 — PROTECTED_MANIFEST_SORT_SEMANTICS`: `CLOSED_WITHOUT_WAIVER`.
- Open authorization findings: `NONE`.
- Waivers: `NONE`.

The corrected Amendment may proceed only through its stated authority
checkpoint and fresh exact human R2 gate. That acknowledgment authorizes one
repair invocation with no retry, exact 13-path ceiling, final exact 28 BUILD
paths and zero provider/network/remote-ingest calls. It does not authorize
stage/commit/push of BUILD, self-review, FREEZE or any later lane.
