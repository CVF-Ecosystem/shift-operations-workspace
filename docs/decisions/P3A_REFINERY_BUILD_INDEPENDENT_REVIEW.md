# P3-A Refinery BUILD Independent Review

> **Correction history — fresh re-review:** The original review incorrectly
> reported retained-manifest drift because its PowerShell collection was not a
> strongly typed `string[]`; the intended ordinal comparer was therefore not
> applied as assumed. A fresh invocation explicitly used
> `[StringComparer]::Ordinal` over a typed string array and reproduced the bound
> digest exactly. Original F1 and the stop-first disposition based on it are
> retracted. The disposition below is the corrected disposition and rests only
> on independently confirmed implementation/coverage defects F2-F6.

- Review date: `2026-08-03`
- Role: `REVIEWER` (independent from BUILD/repair authorship)
- Risk: `R2`
- Control-chain phase: `REVIEW`
- BUILD diff base: `b93e403cf0ab6d659de0706c058d1cd7250e75d0`
- Parent Work Order SHA-256: `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
- Work Order Amendment 1 SHA-256: `587412712cc6d98b6c7e85cba99d9d650d38097ed316e09992243d07ea965546`
- Work Order Amendment 2 SHA-256: `0f47068a71d59dc553ffdf459e52c5e622325fabff9015a16db73249ea3614c4`
- Work Order Amendment 3 SHA-256: `30896c92b12beb8b5f6d153eb8ea4cc642b80004a0c4b400cd61f91dccc6e0f4`
- SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`REVIEW_CHANGES_REQUIRED`

The candidate cannot pass independent BUILD review. The corrected immutable
binding and focused tests pass, but a reviewer probe confirms that public model
construction accepts contradictory results and invalid receipt offsets that
the SPEC requires it to reject. Stop-first/no-retry was applied at that first
fresh evidence failure. No later evidence command was run.

This review makes no runtime, provider, remote-ingest, persistence,
`data_scope`, retrieval/RAG, learning, production, Phase 3 completion, commit,
or FREEZE claim.

## Authority and scope review

The parent DESIGN, SPEC, Work Order, Amendments 1-3, and their independent
authorization reviews were read and compared with the complete candidate.
The intended contract is a deterministic, local, fail-stop nine-stage
pre-admission pipeline with safe receipts, deterministic canonicalization,
exact-source dedupe, quarantine precedence, candidate admission only after all
nine stages pass, and bounded knowledge/catalog truth.

The dirty BUILD set, after excluding the separately governed continuity paths,
contains exactly these 28 paths:

1. `docs/catalog/MODULE_CATALOG.md`
2. `docs/catalog/MODULE_REGISTRY.json`
3. `fixtures/refinery/normalized_message.json`
4. `fixtures/refinery/qualified_time_message.json`
5. `IMPLEMENTATION_STATUS.json`
6. `knowledge/manifest.json`
7. `knowledge/PROJECT_CONTEXT.md`
8. `packages/refinery-bridge/contracts/refinery_contract.yaml`
9. `packages/refinery-bridge/pyproject.toml`
10. `packages/refinery-bridge/README.md`
11. `packages/refinery-bridge/src/refinery_bridge/__init__.py`
12. `packages/refinery-bridge/src/refinery_bridge/canonical.py`
13. `packages/refinery-bridge/src/refinery_bridge/controls.py`
14. `packages/refinery-bridge/src/refinery_bridge/dedupe.py`
15. `packages/refinery-bridge/src/refinery_bridge/enums.py`
16. `packages/refinery-bridge/src/refinery_bridge/input_models.py`
17. `packages/refinery-bridge/src/refinery_bridge/normalization.py`
18. `packages/refinery-bridge/src/refinery_bridge/output_models.py`
19. `packages/refinery-bridge/src/refinery_bridge/pipeline.py`
20. `packages/refinery-bridge/src/refinery_bridge/protection.py`
21. `packages/refinery-bridge/src/refinery_bridge/receipt_models.py`
22. `pyproject.toml`
23. `tests/unit/_refinery_fixtures.py`
24. `tests/unit/test_refinery_adversarial.py`
25. `tests/unit/test_refinery_canonical.py`
26. `tests/unit/test_refinery_contract.py`
27. `tests/unit/test_refinery_models.py`
28. `tests/unit/test_refinery_pipeline.py`

The two Amendment 3 knowledge additions are exactly
`knowledge/PROJECT_CONTEXT.md` and `knowledge/manifest.json`; removing them
leaves the expected 26 path names. The knowledge text remains bounded to
`BUILD_CANDIDATE_PENDING_INDEPENDENT_REVIEW` and denies the prohibited expanded
claims. The registry and generated catalog remain `partial`, with SHA-256
values `d3b848506f788efd658cf2be9ac05c2e81a60c45450c34cb0a157a68d3859f38`
and `6b5ad6a2220da94457fe2a39fd2732210d2531127fd24b54840d4904ea933e92`
respectively. The staged set was empty.

## Findings

### F1 — RETRACTED: original manifest-drift finding was reviewer error

The original invocation produced
`88cbac9731a1dc6154792806e3cf763b134a87e19b6c69dba54240c57ac38336`
because the PowerShell collection was not strongly typed and did not receive
the ordinal sorting semantics the reviewer believed it had applied. That was a
review-method defect, not candidate drift.

The fresh invocation used a typed `string[]` and
`[Array]::Sort(..., [StringComparer]::Ordinal)`. It reproduced exact BUILD
count `28`, retained count `26`, and manifest SHA-256
`c7c1761c699494658b6d8853e1ebcc1703f5be52d6855a6be1ddb7478be601b8`.
Registry/catalog hashes also reproduced and the staged set remained empty.
F1 is invalidated in full and supplies no part of the corrected disposition.

### F2 — HIGH: public result construction does not enforce SPEC invariants

Source inspection of `output_models.py` found that `RefineryResultV1` checks
stage order, orphan `NOT_RUN`, later-stage `NOT_RUN`, and coarse receipt
presence, but does not bind the public result's quality receipt, candidate
fingerprint/provenance, disposition receipt, and first-failure reason back to
the stage receipts and canonical candidate. Contradictory public results can
therefore pass model construction even though R20/R21/R24 and AC02/AC04 require
those combinations to be rejected. This also weakens the claimed canonical
receipt and disposition boundary.

The fresh reviewer probe constructed a valid pipeline result and then showed
that public validation accepts both `CANDIDATE_READY` with a zero-total quality
receipt and a syntactically valid but unrelated all-zero candidate
fingerprint. These are executable confirmations, not source-only inferences.

### F3 — HIGH: the required 28-case adversarial matrix is a label count, not 28 independent cases

`test_refinery_adversarial.py` declares 28 unique strings in `MATRIX_CASES` and
tests only the length and uniqueness of those labels. It does not parameterize
or execute 28 corresponding cases. The executable tests do not independently
cover the full R27 matrix, including policy drift, terminology overlap/cycle,
control-version substitution, sensitivity monotonicity, unexpected invariant
fallback, disclosure through exception/log/snapshot, and the qualified-time
fixture through the pipeline. R27 and AC08 are therefore not demonstrated.

### F4 — HIGH: declared fail-stop reasons have no complete execution path

`POLICY_DRIFT`, `STAGE_UNAVAILABLE`, and unexpected invariant fallback reasons
exist in enums/contracts, but the reviewed pipeline does not provide complete
paths that emit and test them. Exception handling is stage-specific and does
not establish a total sanitized `STAGE_INVARIANT_ERROR` fallback for arbitrary
unexpected stage failures. This falls short of R10/R13/R14 and the fail-stop
claim.

### F5 — MEDIUM: receipt and safe-string boundaries are under-constrained

Direct public construction does not consistently apply the repository's safe
string policy to receipt identifiers, control versions, links, candidate
identifiers/topics, and related output fields. `safe_offsets` are not checked
for bounds/order/non-overlap, and receipt helpers sort/de-duplicate some
collections instead of rejecting duplicate boundary input. This leaves R4,
R5, and R17 only partially implemented.

The fresh reviewer probe independently confirmed that `StageReceiptV1`
accepts `safe_offsets=((9, 2), (-1, 500000))`, including reversed, negative,
out-of-bounds, and overlapping ranges.

### F6 — MEDIUM: catalog registry includes an unrelated semantic status change

The candidate diff against the bound BUILD base changes
`cvf-application-profile` from `contract-only` to `partial` in addition to the
authorized `refinery-bridge` status change. Amendment 2 expressly limited its
manual registry edit to `refinery-bridge` and prohibited alteration of other
registry fields. The resulting aggregate catalog counts therefore include an
unexplained non-P3-A semantic mutation.

## Evidence ledger

| Order | Evidence | Result |
|---:|---|---|
| 1 | Fresh typed ordinal exact-set/binding check; registry/catalog hashes; staged count | `PASS`: exact `28/26`; digest `c7c176…01b8`; registry `d3b848…9f38`; catalog `6b5ad6…3e92`; staged `0` |
| 2 | Focused refinery pytest, one invocation | `PASS`: `31 passed` |
| 3 | Public result/receipt invariant probe, one invocation | `FAIL`: accepted `CANDIDATE_READY_WITH_ZERO_QUALITY`, `UNBOUND_CANDIDATE_FINGERPRINT`, and `INVALID_SAFE_OFFSETS` |
| 4 | Knowledge validator and focused knowledge tests | `NOT_RUN — stop-first after order 3` |
| 5 | Catalog check | `NOT_RUN — stop-first after order 3` |
| 6 | Full non-live pytest suite | `NOT_RUN — stop-first after order 3` |
| 7 | Session, file-size, repository, JSON/YAML, static, secret, and diff checks | `NOT_RUN — stop-first after order 3` |

Earlier BUILD-worker evidence is not adopted as independent reviewer evidence.
Its reported passes cannot cure the independently reproduced model-invariant
failure or the source and coverage findings above.

## Required disposition

Return to governed repair/work-order handling. The retained manifest needs no
repair: its binding is valid. At minimum, repair must correct the public model
invariants and executable adversarial coverage, resolve the missing fail-stop
paths and receipt bounds, and remove or separately authorize the unrelated
registry mutation. A fresh independent BUILD review is required after repair.
No waiver is granted.
