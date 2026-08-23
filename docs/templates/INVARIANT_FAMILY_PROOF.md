# Invariant-Family Proof (shared Work Order / Reviewer template)

Both `WORK_ORDER_AUTHOR` and `REVIEWER` complete this section for any tranche
that triggers `docs/cvf/INVARIANT_FAMILY_STANDARD.md`. This template contains
no family-specific rules — it only points to the registered matrix.

## Fields to complete

- **Applicability decision**: registered family id, or `NOT_APPLICABLE` with
  a reason (SPEC R1).
- **Matrix id / canonical digest**: exact `familyId` and the SHA-256 of the
  matrix file at the pinned commit.
- **Adapter / test paths**: real-emitter adapter path(s) and evidence test
  path(s) declared by the matrix.
- **Mutation exclusions**: any matrix-declared excluded operator, with its
  recorded reason and independent-review acknowledgment.
- **Exact commands**: the guard/test invocations used to produce evidence
  (e.g. `python scripts/check_invariant_families.py`, focused pytest paths).
- **Evidence owner**: the role responsible for the returned conformance
  summary (SPEC R12).
- **Reviewer recomputation**: confirmation that the independent reviewer
  recomputed the matrix digest, reran the same corpus, sampled at least one
  raw emitted positive per outcome, and verified no matrix expectation was
  derived during BUILD.

## Non-goals

This template does not restate outcome fields, mutation operators, or
relation rules — those live only in the registered matrix. Do not paste
matrix content into a Work Order or review artifact; reference the matrix id
and digest instead.
