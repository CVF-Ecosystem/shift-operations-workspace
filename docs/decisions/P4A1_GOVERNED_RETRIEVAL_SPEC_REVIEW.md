# P4-A1 Governed Retrieval - Independent SPEC Review

- Tranche: `P4-A1-GOVERNED-RETRIEVAL-2026-08-10`
- Review role: `INDEPENDENT_SPEC_REVIEWER`
- Risk: `R2`
- Disposition: `SPEC_REVIEW_PASS`
- Main SPEC: `docs/specs/P4A1_GOVERNED_RETRIEVAL_SPEC.md`
- Main SPEC SHA-256: `f2385689b4ccca2bf669500bc984383f223e62b46fbf5a87f54587ad9530bb09`
- Normative appendix: `docs/specs/P4A1_GOVERNED_RETRIEVAL_RECEIPT_CONTRACT.md`
- Normative appendix SHA-256: `11af01c38a45e1891b752eb65c49c86827a6504c95d35d9ab2e8206a148df619`
- Parent ADR: `docs/decisions/ADR_2026-08-10_P4A1_GOVERNED_RETRIEVAL.md`
- Parent ADR SHA-256: `8dbdfbaded8ed523eb465bc3c657620a323fafae465f5d0d0d66fe8cac6aa4fc`
- Prior findings: `F1-F4 CLOSED`
- New findings: `NONE`
- Waivers: `NONE`
- Review date: `2026-08-10`

## Reviewed boundary

The main SPEC and receipt appendix form one inseparable normative packet. The
review compared that exact pair with the accepted twelve-decision ADR, current
P3-C and project source, authorization ordering, corpus and source boundaries,
P3-B status, result union, proof requirements, and the LPCI1-REF entry gate.

The review found no ADR or current-source drift. The package, service,
`retrieval.query` action, and six canonical digest owners remain intended
future behavior rather than current implementation truth. Canonical records
remain fail-closed, Project Knowledge remains INTERNAL and local-only, and
provider, RAG, vector/index, persistence, deployment, and durable audit remain
outside P4-A1.

## Prior finding closure

### F1 - CLOSED

The receipt contract now defines nullable pre-validation fields and exact
population stages for corpus, authorization scope, limits, source cutoff, and
evidence hash. Invalid-request and access-denied receipts can therefore be
constructed without fabricating a corpus, principal, or admitted scope.

### F2 - CLOSED

The appendix defines `citation_id` as a canonical SHA-256 value, fixes rank
order, forbids duplicates, and binds every projection to its same-position
citation id. The main SPEC also rejects any mismatch between duplicated
projection and nested-citation truth class, field selector, snippet digest, or
offsets.

### F3 - CLOSED

The appendix closes the field sets for counts, limits, termination facts,
stage receipts, stage outcomes, and reason codes. Hash construction is bound
to `retrieval_contracts.canonical.canonical_json_bytes`, including UUID,
datetime, enum, NFC, tuple-order, sorted-key, and no-float behavior.

### F4 - CLOSED

Candidate normalization now emits an exact normalized-to-source offset map for
CRLF, CR, casefold expansion, whitespace collapse, and trimmed edges. Match
spans use source offsets, and a match that cannot fit the client snippet
ceilings causes whole-projection omission rather than clipped evidence. If no
projection fits, the result is `CONTEXT_BUDGET_EXCEEDED`.

## Mechanical evidence

- Exact main SPEC hash reproduced: `PASS`.
- Exact normative appendix hash reproduced: `PASS`.
- Exact parent ADR hash reproduced: `PASS`.
- Main SPEC structure: 564 lines, ASCII-only, 12 requirements, and 12 matching
  acceptance criteria.
- Normative appendix structure: 114 lines and ASCII-only.
- `python scripts/check_session_state.py`: `PASS`.
- `python scripts/check_project_knowledge.py`: `PASS`.
- `python scripts/check_file_size.py`: `PASS`.
- `python scripts/testing/validate_repository.py`: `PASS`.
- Workspace doctor with offline pinned-core allowance: `PASS WITH NOTE`, 24
  passes and one existing core-pin warning.
- `git diff --check`: no error; existing line-ending warnings only.

No provider, network, product API, database, browser, helper, or live-proof
call was made. The reviewer created only this receipt and did not modify the
SPEC pair, ADR, source, tests, roadmap, continuity, catalog, or project
knowledge. Nothing was staged, committed, or pushed.

## Disposition and transfer boundary

`SPEC_REVIEW_PASS`, new findings `NONE`, waivers `NONE`.

The exact main SPEC and appendix hashes above may transfer together to
`WORK_ORDER_AUTHOR`. A Work Order must pin both hashes and preserve the
provider-free P4-A1 boundary. This receipt grants Work Order authoring only; it
does not grant BUILD, digest-owner implementation, provider or network calls,
database changes, LPCI1-REF implementation, staging, commit, push, deployment,
or production authority.

## Claim boundary

This receipt proves only that the exact normative SPEC pair passed independent
documentation review. It does not prove governed retrieval is implemented,
canonical records are retrievable, P3-B is load-bearing, evidence reaches an
LLM, answers are grounded, citations are output-validated, receipts are
durable, or RAG, vector/index, provider, deployment, or production behavior
exists.
