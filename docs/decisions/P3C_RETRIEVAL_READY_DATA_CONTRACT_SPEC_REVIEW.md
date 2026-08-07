# P3-C Retrieval-Ready Data Contract - Independent SPEC Review

- Tranche: `P3-C-RETRIEVAL-READY-DATA-CONTRACT-2026-08-06`
- Review target commit: `9317cfa116eea2e04b154d5d0520c92bc144fbd8`
- Reviewed artifact: `docs/specs/P3C_RETRIEVAL_READY_DATA_CONTRACT_SPEC.md`
- Reviewed SHA-256: `cdb00667cf8f8fd16fa5e0dfd3cd07eb149ddac6938ed5e1db71d70abad53558`
- Parent ADR SHA-256: `f7c78d3e2e3a6e1de462b64e2b906a0cbb7e35e9f2d521b3e528aba6b2ea05f2`
- Risk: `R2`
- Review role: `INDEPENDENT_SPEC_REVIEWER`
- Disposition: `SPEC_REVIEW_CHANGES_REQUIRED`
- Findings: `P3C-SPEC-F1`
- Waivers: `NONE`
- Review date: `2026-08-07`

## Consolidated review result

Repository identity, target commit, SPEC hash, parent ADR hash and the parent
`DESIGN_REVIEW_PASS` were independently verified. The reviewer source-verified
the P3-A bindings, operations-domain models, package topology, data-scope claim
and R1-R23 enum/field counts. One gap remains.

### P3C-SPEC-F1 - Private Report digest helpers need an explicit bypass guard

R8 correctly rejected current `workspace_api` digest helpers, generic Pydantic
dump hashing and misuse of `ReportSourceRef` or `HandoverItem` digests. It did
not name two module-level helpers in the otherwise allowed dependency package:

- `operations_domain.report_models._canonical_bytes`;
- `operations_domain.report_models._recompute_record_digest`.

They are private implementation helpers scoped to validation of canonical dict
records already embedded in `ReportContent`. Python can still import them
directly, so a future BUILD could incorrectly use them as a generic digest
owner unless the SPEC and static import tests prohibit that shortcut.

Required repair: name both helpers in the R8 forbidden-bypass list and add an
explicit R20 static-import test and/or R23 fixture requirement that prevents
`retrieval_contracts` from importing them outside their existing internal
Report-snapshot validation role.

## Passed scope

All other reviewed source facts and R1-R23 requirements passed as written and
must not be reopened or expanded during F1 repair.

## Repair authority

One same-scope SPEC repair may modify only the digest-helper source row, R8,
R20, the R23 fixture matrix and their direct acceptance/continuity
consequences. No waiver is authorized.

This review grants no Work Order, BUILD, provider/helper/product-network/POST,
retrieval, persistence, vector/index, staging by the reviewer, deployment or
production authority.

## Next governed move

Repair F1, freeze a new SPEC SHA-256 and obtain independent SPEC R1 re-review.
Only `SPEC_REVIEW_PASS` may transfer to `WORK_ORDER_AUTHOR`.
