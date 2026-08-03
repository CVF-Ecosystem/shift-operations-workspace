# P3-A Refinery — Independent INTAKE Review

- Tranche: `P3-A-REFINERY-2026-08-03`
- Parent closure: `107c8fa5b8bd2db753334da84c56872266fa587b`
- Reviewed INTAKE SHA-256: `271dd0085da921ff9f9d75ec9864bb09f56d9c45df8491aa4a82e26041a239b7`
- Risk: `R2`
- Review role: `INDEPENDENT_INTAKE_REVIEWER`
- Disposition: `INTAKE_REVIEW_PASS`
- Waiver: `NONE`
- Review date: `2026-08-03`

## Review findings

- **Request boundary:** PASS. The request is limited to designing a local,
  deterministic, fail-closed, non-truth-owning transformation boundary for
  `packages/refinery-bridge`. It may produce context candidates, stage
  receipts and typed refusal/fallback outcomes, but cannot confirm operational
  truth, mutate domain/ledger state, ingest remote data, persist raw envelopes,
  invoke providers, retrieve/vectorize, or implement RAG/learning/production
  behavior. This INTAKE authorizes no implementation.
- **Risk classification:** PASS. `R2` is correct because sensitivity
  classification, redaction, quarantine and future context eligibility can
  affect what data may later reach AI. The ceiling is not reduced merely
  because the proposed implementation is deterministic and local.
- **Present implementation truth:** PASS. The module registry truthfully marks
  `refinery-bridge` `contract-only`, with zero code files and no tests. The
  current YAML has four required input names and eight required output names,
  but no typed/versioned schemas for provenance, quarantine, quality, stage
  failures or fallback. The submodules and worker job are README-only.
  `cvf_runtime.data_scope` is callable but has no runtime caller; its
  `allow_after_minimization` branch does not accept or verify minimization
  evidence. P3-A therefore cannot call it load-bearing or claim DLP or
  minimization enforcement.
- **Fixture defect:** PASS, retained as a DESIGN input rather than accepted
  truth. `fixtures/refinery/normalized_message.json` changes `11h40` to
  `23:40` without AM/PM, timezone, shift-relative or other supporting evidence.
  It also lacks current contract-required `source_type` and `received_at`.
  Its rewrite of `tech đang xuống` as `Bộ phận kỹ thuật đang xử lý` must also
  be treated as an interpretation requiring an explicit rule/evidence basis,
  not silently promoted to a fact. The fixture is not golden and must be
  replaced, corrected or used as negative/quarantine evidence in DESIGN.
- **Sensitivity versus topic classification:** PASS. Policy sensitivity is
  the closed vocabulary `PUBLIC`, `INTERNAL`, `CONFIDENTIAL`, `RESTRICTED`,
  while the fixture value `equipment_downtime` is a domain-topic label. DESIGN
  must use distinct fields/types; one ambiguous `classifications` collection
  cannot serve both purposes. A topic label cannot grant provider placement,
  and a sensitivity label cannot masquerade as domain semantics.
- **Raw-retention ownership:** PASS with a mandatory DESIGN resolution. The
  existing boundary and policy require the upstream raw message to remain
  evidence for `raw_message_retention_days: 365`; P3-A keeps only stable source
  linkage/digest and neither stores nor deletes raw data. DESIGN must name the
  upstream retention owner or explicit external dependency, define source-link
  availability/failure semantics and specify the digest representation. It
  must not create a second raw store or claim retention enforcement from a
  link alone.
- **Quarantine, quality and fallback:** PASS as explicitly open design work.
  Quarantine retention is 30 days, but P3-A does not own its persistence;
  DESIGN must assign disposition ownership, reason codes and behavior when no
  quarantine sink exists. Data-quality needs deterministic dimensions,
  thresholds and a fail-closed relationship to missing, ambiguous and
  conflicting values. “Fallback về rules” must resolve to typed behavior—an
  explicit no-candidate/refusal or a named reduced deterministic pipeline—not
  silent stage omission or a partially trusted candidate.
- **Queue separation:** PASS. Only P3-A DESIGN may follow this review. P3-B
  runtime wiring of `data_scope`/cost/termination, P3-C retrieval-ready
  contracts, Phase 4 retrieval/RAG/providers/channels, learning and production
  remain parked. P3-A context candidates are local intermediate outputs, not
  P3-C retrieval records and not automatic LLM context.
- **Provider-evidence boundary:** PASS. No provider call is needed or authorized
  to design or prove deterministic local contract/transformation behavior.
  Mock output cannot prove AI governance. Any later claim that the refinery or
  CVF actually controls provider/AI behavior requires a separate governed call
  budget, a real provider call and a sanitized receipt.

## Sufficiency of the eight DESIGN decisions

The eight decisions are sufficiently bounded and testable to transfer from
INTAKE to DESIGN, provided DESIGN resolves each one explicitly rather than
copying the current placeholder contract:

1. **Envelope/provenance:** define an exact schema version, source identity,
   source version/time/type, source-link contract, digest algorithm and whether
   bytes are raw or canonicalized; require deterministic digest/link tests.
2. **Normalization/ambiguity:** publish an allowlist of syntax, Unicode,
   whitespace, terminology and time rules plus a typed unresolved form; prove
   no unsupported value completion, including the current time fixture.
3. **Deduplication:** bind identity, scope, window and collision outcomes;
   distinguish duplicate evidence from a global exactly-once guarantee.
4. **Classification:** define separate sensitivity and topic vocabularies,
   unknown-value behavior and provenance for each classification result.
5. **Redaction:** identify policy ownership and supported deterministic
   detectors; prove sensitive originals cannot appear in candidates, public
   errors, receipts or logs while source evidence remains upstream-owned.
6. **Quarantine:** define typed dispositions/reasons, owner/handoff semantics,
   the 30-day policy relationship and fail-closed behavior without pretending
   P3-A persists quarantine records.
7. **Data quality:** define dimensions, scoring/thresholds and deterministic
   handling of missing, ambiguous and conflicting data; below-threshold input
   must not yield a candidate.
8. **Fallback:** select and type the exact refusal/no-candidate or reduced
   rules-only result; name which stages ran and failed, with no silent partial
   success or fabricated fact.

Across all eight decisions, DESIGN must type and version the context-candidate
output and make eligibility mechanically testable: a candidate exists only if
every required stage has a successful receipt, no quarantine disposition
applies and the quality threshold is satisfied. Failure produces a typed
non-candidate outcome.

## Disposition

`INTAKE_REVIEW_PASS` is recorded with no waiver. The request boundary, current
truth, risk and parked-lane constraints are adequate for transfer to
`DESIGN_AUTHOR`. The eight decisions remain unresolved obligations and must be
closed in an independently reviewable DESIGN before SPEC begins.

This review grants no SPEC, WORK_ORDER, BUILD, provider/helper/network/POST,
remote-ingest, persistence, retrieval/RAG, stage, commit, push or later-lane
authority. During this review no provider, helper, network, POST, staging,
commit or push action was performed.
