# P3-A Refinery — Independent SPEC Review

- Tranche: `P3-A-REFINERY-2026-08-03`
- Risk: `R2`
- Review role: `REVIEWER`
- Parent ADR SHA-256: `57ec06fc72e6ec2baad95079cdeff7eabfe7eb2837841dfc7c11cdba256e696e`
- Design Amendment 1 SHA-256: `dc091f2ba00334e58d8755ebfb33e5ec868bf802e8233f36e0f470a6b96f0e4a`
- DESIGN review SHA-256: `fcb8c3f96bd2ed524c2bb4457a338a3e9c7cfde4b120090091e298d30eb2ab45`
- DESIGN re-review SHA-256: `1a76e69a153de0a23911da6a735cc46ba91aaeebdceeaacaa6d921289b5c113c`
- DESIGN Amendment 1 review SHA-256: `13ea108843101265efb08b01d2096dd3ea5d05fc4943a33eb4db2d4dc8b9f99c`
- Reviewed SPEC SHA-256: `3471bc9b409d68906a50439c24a6ea2ac6cee374cf895630c75d26b9f59e8511`
- Disposition: `REVIEW_FAIL`
- Waiver: `NONE`
- Review date: `2026-08-03`

## Reviewed scope and changed-set observation

The review checked every R1–R30 requirement and AC-01 through AC-12 against
the immutable reviewed parent ADR and reviewed Design Amendment 1. It covered
schema closure, stage and quality receipts, three fingerprint preimages,
dedupe/collision behavior, total fail-closed disposition, disclosure/I/O and
claim boundaries, fixtures and phase separation.

Immediately before this receipt was created, the unstaged candidate set was
the one untracked SPEC plus four pre-existing modified continuity paths:

- `docs/specs/P3A_REFINERY_SPEC.md` (untracked candidate);
- `SESSION/SESSION_MEMORY.md`;
- `SESSION/ACTIVE_SESSION_STATE.json`;
- `CVF_SESSION/ACTIVE_SESSION_STATE.json`;
- `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`.

The staged set was empty. This reviewer added only this review path and did not
edit the SPEC, parent DESIGN artifacts or continuity.

## Findings

### F1 — Normative fingerprint and disposition references point to the wrong schemas

R8 says `dedupe_content_fingerprint` uses the exact R20 preimage and
`candidate_fingerprint` uses the exact R25 preimage. R20 actually defines
`QualityReceiptV1`; R25 defines determinism/monotonic properties. The intended
preimages are R19 (`DedupeContentV1`) and R23 (`ContextCandidateV1`). A literal
implementation of R8 cannot satisfy R19/R23 or the reviewed amendment.

R15 also says missing dedupe context follows the no-candidate mapping in R22,
but R22 defines receipt shapes; the disposition mapping is R21. These are
normative references, so they cannot be left for BUILD interpretation.

Required repair: change R8 to bind the two fingerprints to R19 and R23, change
R15 to bind missing-context disposition to R21, and add a cross-reference test
or review check that every normative R-number resolves to the intended schema.

### F2 — `StageReceiptV1.reason_codes` is not a closed executable vocabulary

R17 requires stable enum codes only and mandates `PRIOR_STAGE_FAILED`, while
R1 closes no stage-reason enum and R3 closes only quarantine and fallback
reason types. Other required stage-level meanings are also not typed—for
example the parent DESIGN requires `AMBIGUOUS_LOCAL_TIME`, while R13 maps the
top-level quarantine reason to `AMBIGUOUS_VALUE`. Consequently an
implementation may emit arbitrary stage reason strings while still claiming
R17 conformance, and unknown-field/unknown-enum tests in AC-02 have no complete
expected vocabulary.

Required repair: define one closed `StageReason` enum containing every PASS,
FAIL and `NOT_RUN` code required by R9–R17, including
`PRIOR_STAGE_FAILED` and the typed ambiguous-local-time detail; specify which
stage/outcome combinations permit each code; reject every unknown value.
Top-level quarantine/fallback reasons must remain the distinct R3 types.

### F3 — The fail-stop receipt state machine permits orphan `NOT_RUN`

R17 states only that receipts after the first `FAIL` are `NOT_RUN`. It does not
state the converse: a `NOT_RUN` receipt is legal if and only if an earlier
receipt is `FAIL`. Thus a sequence such as `PASS, NOT_RUN, ...` with no prior
failure is not expressly rejected. No R21 disposition branch covers that
sequence, so the claimed disposition mapping is not total and R24's generic
contradictory-combination rejection cannot supply the missing normative rule.
AC-04 likewise asks only for first-failure behavior, not orphan-`NOT_RUN`
rejection.

Required repair: define the only legal receipt language as either nine PASS
receipts, or zero or more PASS receipts followed by exactly one FAIL and only
`NOT_RUN` receipts thereafter. Require `NOT_RUN` if and only if an earlier
stage failed, prohibit execution/output data on `NOT_RUN`, bind every legal
failure sequence to R21, and add AC-04 coverage for orphan/premature
`NOT_RUN` rejection.

### F4 — The collision predicate is ambiguous for equal dual digests with unequal length

R16 describes “SHA-256-only or SHA-512-only equality” with another
digest/length mismatch. Read literally, this covers exactly one matching
digest but not the corrupted/collision-suspect case where both digests are
equal and `byte_length` differs. The reviewed Amendment 1 requires a collision
signal when a digest match coexists with another digest **or length** mismatch.
Full-triple match and collision must form a complete, non-overlapping
predicate, not depend on the interpretation of “only.”

Required repair: define collision mechanically as fingerprints being unequal
while `(sha256 equal OR sha512 equal)`, which includes one or both equal
digests with any remaining-field mismatch; define full triple equality as the
only normal match; add AC-03/AC-06 vectors for both-digests-equal/length-diff,
each-single-digest-equal, and no-digest-equal cases.

## Requirements and acceptance assessment

- R1–R7, R9–R14, R18–R30 otherwise preserve the reviewed local, deterministic,
  no-paraphrase, sensitivity/topic, redaction, quarantine non-ownership,
  100/100 control-coverage, candidate-null and claim boundaries at the SPEC
  level. This observation does not waive F1–F4.
- R8, R15–R17 and their interactions with R21/R24 are not executable without
  repair for F1–F4.
- AC-01 fails because this independent review has findings. AC-02, AC-03,
  AC-04 and AC-06 are underspecified by those findings and cannot yet prove the
  intended closed contract. AC-05 and AC-07 through AC-12 are appropriately
  bounded but cannot authorize progression while earlier acceptance gates
  fail.
- Disclosure and I/O boundaries remain strict: no raw/matched-sensitive data
  in public models, receipts, exceptions, logs or snapshots; no provider,
  network, database, filesystem/environment discovery, secret read, clock or
  randomness in the pipeline.
- P3-B/P3-C, `data_scope` runtime wiring, provider behavior, external ingest,
  persistence, retrieval/RAG, learning, confirmed truth and production remain
  outside this SPEC.

## Disposition

`REVIEW_FAIL` with no waiver. The SPEC must return to `SPEC_AUTHOR` for the
four repairs above and independent re-review. It **may not transfer to
`WORK_ORDER_AUTHOR`**.

This receipt grants no WORK_ORDER, BUILD, provider/network call, remote ingest,
persistence, retrieval/RAG, staging, commit, push or later-lane authority. No
provider or network call was performed during this review.
