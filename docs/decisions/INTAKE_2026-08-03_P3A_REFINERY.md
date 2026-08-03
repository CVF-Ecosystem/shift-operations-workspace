# INTAKE — P3-A Refinery Boundary

- Tranche: `P3-A-REFINERY-2026-08-03`
- Parent closure: `107c8fa5b8bd2db753334da84c56872266fa587b`
- Control-chain phase: `INTAKE`
- Risk: `R2`
- Status: `OPEN_FOR_INTAKE_REVIEW`
- Active roles: `ORCHESTRATOR`, `INTAKE_AUTHOR`

## Request and roadmap position

The operator said to continue after Project Knowledge Pack reached reviewed
`FREEZE / CLOSED_BOUNDED`. The canonical roadmap permits only fresh P3-A
Refinery INTAKE. P3-B runtime gate wiring, P3-C retrieval-ready contracts,
retrieval, RAG and learning remain parked.

P3-A is the first real implementation tranche for `packages/refinery-bridge`,
currently `contract-only`. Its roadmap purpose is deterministic normalization,
deduplication, redaction, classification, quarantine, provenance and a bounded
data-quality result before input may become a context candidate, with safe
fallback when refinement fails. It is not RAG and does not confirm operational
truth.

## Current implementation truth

- `packages/refinery-bridge/contracts/refinery_contract.yaml` requires only
  four input and eight output fields. It has no quarantine disposition,
  provenance receipt, data-quality result, stage errors or fallback result.
- All refinery submodules are README-only; registry status is correctly
  `contract-only`, with no runtime bridge or tests.
- `cvf_runtime.data_scope` is callable but has no runtime caller. Its
  `allow_after_minimization` rule does not accept or verify minimization
  evidence, so P3-A must not claim `data_scope` is load-bearing.
- `fixtures/refinery/normalized_message.json` changes ambiguous `11h40` to
  `23:40`. Without explicit AM/PM or shift-relative evidence this invents a
  missing value and conflicts with `invent_missing_values: false`; the fixture
  is not eligible as golden truth in its current form.
- Existing Project Knowledge Pack content is advisory INTERNAL input. P3-A may
  use repository-owned fixtures, but it receives no authority for remote ingest
  or automatic context injection.

## Proposed bounded objective

Design a local, deterministic, fail-closed refinery boundary that:

1. accepts an explicitly versioned source envelope and keeps a stable link and
   digest to source bytes without taking ownership of upstream raw retention;
2. normalizes only evidence-supported syntax, whitespace, Unicode, terminology
   and time values—ambiguous values remain unresolved;
3. produces deterministic duplicate, sensitivity classification, redaction,
   conflict, quarantine and data-quality receipts;
4. emits context candidates only when every required stage succeeds and the
   result is not quarantined;
5. returns a typed local fallback/refusal outcome on stage failure, never a
   fabricated fact or silent partial candidate.

## Hard boundaries

This INTAKE authorizes no implementation. The eventual P3-A design must not:

- call a provider/LLM, build retrieval/vectorization/RAG or claim AI behavior;
- ingest remote/channel data, persist raw envelopes, implement Integration
  Edge, or alter retention/deletion ownership;
- confirm operational facts, mutate ledger/domain records, or bypass human
  confirmation and existing service governance;
- claim DLP, minimization or `data_scope` is load-bearing without an actual
  runtime caller and evidence contract;
- implement P3-B, P3-C, Phase 4, learning, production deployment or an
  autonomous workflow;
- treat the existing ambiguous-time fixture as correct evidence.

## Decisions required before DESIGN closes

1. Canonical envelope/version and exact provenance fields, including whether
   source digest covers raw bytes or a canonical UTF-8 representation.
2. Allowed deterministic normalization rules and explicit ambiguity format.
3. Dedupe identity/scope/window and collision behavior; no global exactly-once
   claim from a content digest alone.
4. Sensitivity classification vocabulary versus domain-topic labels; these
   must not share one ambiguous field.
5. Redaction policy ownership, supported detectors and evidence that original
   sensitive values never appear in context candidates or public errors.
6. Quarantine ownership, reason taxonomy and relationship to the existing
   30-day policy without claiming persistence that P3-A does not own.
7. Data-quality dimensions, deterministic scoring/thresholds and fail-closed
   behavior for missing/ambiguous/conflicting data.
8. Meaning of “fallback về rules”: a typed no-candidate/refusal result versus a
   reduced deterministic pipeline, with no silent degradation.

## Risk and evidence posture

`R2` applies because this boundary handles sensitive-data classification and
may later control what becomes AI context. Pure deterministic local contract
and transformation claims do not require a provider call. Any later claim that
CVF actually governs provider/AI behavior must use fresh real-provider evidence
under a separately approved call budget; mock output cannot prove it.

## Intake acceptance boundary

INTAKE is acceptable only if review confirms the objective is local,
deterministic and non-truth-owning; the fixture defect is retained; P3-B/P3-C
and later work remain parked; and no DESIGN/BUILD authority is inferred.

## Next governed move

Review this INTAKE and resolve its eight design decisions. Only accepted INTAKE
may transfer to `DESIGN_AUTHOR`; no provider, BUILD, stage, commit or later-lane
authority is granted by this document alone.

