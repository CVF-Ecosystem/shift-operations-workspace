# P3-C Retrieval-Ready Data Contract - Independent DESIGN R1 Re-review

- Tranche: `P3-C-RETRIEVAL-READY-DATA-CONTRACT-2026-08-06`
- Review target commit: `6641d9419c38829b57fd5949b627287b526578f5`
- Re-reviewed artifact: `docs/decisions/ADR_2026-08-06_P3C_RETRIEVAL_READY_DATA_CONTRACT.md`
- Re-reviewed SHA-256: `f7c78d3e2e3a6e1de462b64e2b906a0cbb7e35e9f2d521b3e528aba6b2ea05f2`
- Original review: `docs/decisions/P3C_RETRIEVAL_READY_DATA_CONTRACT_DESIGN_REVIEW.md`
- Risk: `R2`
- Review role: `INDEPENDENT_DESIGN_REREVIEWER`
- Disposition: `DESIGN_REVIEW_PASS`
- Findings: `NONE`
- Waivers: `NONE`
- Review date: `2026-08-07`

## Reviewed boundary

The independent return supplied by the operator is recorded against the exact
commit and frozen ADR hash above. The re-review scope was limited to closure of
`P3C-DESIGN-F1` and a regression check that Decisions 2-10 remained unchanged.

No edit, SPEC drafting, BUILD, provider, product-network, POST, retrieval,
stage, commit or push action is attributed to the independent reviewer.

## Finding closure

### P3C-DESIGN-F1 - CLOSED

Decision 1 now proposes `packages/retrieval-contracts/` explicitly as a new
sibling Python package. It no longer describes schema-only
`packages/workspace-contracts/` as an existing wired Python owner.

The proposed package follows the current one-package-per-`pyproject.toml`
pattern, owns `src/retrieval_contracts/`, receives an explicit root test
`pythonpath` entry only in a later authorized BUILD, and has the one-way
dependency direction:

- `retrieval-contracts` -> `refinery-bridge`;
- `retrieval-contracts` -> `operations-domain`.

Reverse imports remain forbidden. The new package also remains forbidden from
importing `workspace-api`, `operations-ledger`, `cvf-runtime`, provider or
retrieval runtime modules. Schema-only `workspace-contracts` is not widened.

## Regression disposition

Decisions 2-10 retain the previously passed source facts, eligibility/version
matrix, deterministic field-bound chunking, no-tenant boundary, lifecycle
revalidation, owner-asserted retention/erasure, closed provenance, non-load-
bearing data-scope status and typed ready/non-admission union. The R1 repair
does not reopen or expand them.

## Transfer boundary

`DESIGN_REVIEW_PASS`, findings `NONE`, waivers `NONE`. The exact ADR at SHA-256
`f7c78d3e2e3a6e1de462b64e2b906a0cbb7e35e9f2d521b3e528aba6b2ea05f2`
may transfer to `SPEC_AUTHOR`.

This receipt grants bounded SPEC authoring only. It grants no WORK_ORDER,
BUILD, provider/helper/product-network/POST call, retrieval, persistence,
vector/index, staging, commit by a worker, deployment or production authority.

## Next governed move

Author one testable P3-C SPEC that resolves the accepted ADR into exact schemas,
algorithms, negative cases, fixtures, acceptance criteria and claim boundaries.
Then freeze its SHA-256 and obtain independent SPEC review. Only
`SPEC_REVIEW_PASS` may transfer to `WORK_ORDER_AUTHOR`.
