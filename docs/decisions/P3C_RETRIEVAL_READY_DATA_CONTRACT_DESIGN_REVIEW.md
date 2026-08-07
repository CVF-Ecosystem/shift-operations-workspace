# P3-C Retrieval-Ready Data Contract - Independent DESIGN Review

- Tranche: `P3-C-RETRIEVAL-READY-DATA-CONTRACT-2026-08-06`
- Review target commit: `85052cf96ad99bf465569a20bcb929e63feee11c`
- Reviewed artifact: `docs/decisions/ADR_2026-08-06_P3C_RETRIEVAL_READY_DATA_CONTRACT.md`
- Reviewed SHA-256: `288ebab12f64c036a23ef765c6230a48b2bff04d70ffd591529cad5757ff318b`
- Risk: `R2`
- Review role: `INDEPENDENT_DESIGN_REVIEWER`
- Disposition: `DESIGN_REVIEW_CHANGES_REQUIRED`
- Findings: `P3C-DESIGN-F1`
- Waivers: `NONE`
- Review date: `2026-08-06`

## Consolidated review result

### P3C-DESIGN-F1 - Proposed owner is not an existing wired Python package

Decision 1 described `packages/workspace-contracts/retrieval/` as reusing an
existing Python package and proposed adding Pydantic models and a constructor
there. Current source does not support that claim:

- `packages/workspace-contracts/` contains JSON schemas and a README;
- it has no `pyproject.toml`, Python source package or root `pythonpath` entry;
- current tests consume its files by path;
- no current package imports Python from `workspace-contracts`.

Therefore the asserted reuse and dependency-direction proof were not
source-verifiable. This is an owner/dependency source-fact defect, not a style
finding.

Required repair: either select an existing wired Python package or explicitly
propose a new sibling Python package following the repository's established
one-package-per-`pyproject.toml` pattern, then state and verify the corrected
dependency direction.

## Passed decisions

Decisions 2 through 10, their cited source facts, risk, hard boundaries,
admission algorithm, test direction and claim boundary passed as written. They
must not be reopened or expanded during the F1 repair.

## Reviewer operation statement

The reviewer reported no edit, SPEC drafting, build, provider/network call,
stage, commit or push. The result was supplied to the session-sync steward by
the operator and recorded without expanding its claims.

## Repair authority

`P3C-DESIGN-F1` authorizes one same-scope DESIGN repair to Decision 1 and any
direct owner-name/dependency consequences elsewhere in the ADR. It grants no
SPEC, WORK_ORDER, BUILD, provider/helper/product-network/POST or retrieval
authority.

## Claim boundary

This review does not reject the P3-C objective or Decisions 2-10. It proves
only that the first DESIGN candidate cannot pass until its Python owner and
dependency direction match current repository topology.

## Next governed move

Repair F1 in place, freeze the revised ADR at a new SHA-256 and obtain an
independent DESIGN re-review. Same-scope repair needs no new operator
checkpoint.
