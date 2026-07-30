# Independent Authorization Review — Message Admission Work Order

- Review id: `MESSAGE-ADMISSION-TRUST-REPAIR-WO-AUTH-REVIEW-001`
- Tranche: `MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30`
- Date: 2026-07-30
- Risk: R2
- Reviewer: Codex, `ORCHESTRATOR / REVIEWER`
- Future implementation worker: unassigned and must be independent
- Disposition: `REVIEW_PASS — C1/C2 AND G6 REQUIRED; BUILD PROHIBITED`

## Boundary

The reviewer is independent from the future implementation/repair worker.
This review changed authorization/continuity documents only. It made no
source, test, API, permission, migration, provider or database change.

## Feasibility and ceiling audit

The 29-path ceiling contains:

- 10 production paths;
- 8 non-live/contract test paths;
- 3 PostgreSQL paths;
- 3 provider-evidence paths;
- 5 receipt/control/catalog paths.

Every filename is exact; there is no wildcard or conditional path.

The SQL helper is necessary because `sql_ledger.py` is already 280 lines.
InMemory changes fit within its 285-line host only if bounded and guard-checked.
The 300-line PostgreSQL runner receives a line-neutral target edit. The
customer-request service, schema parity and customer-request repair test are
authorized because they contain explicit stale `NotImplemented` assumptions
that BUILD would otherwise leave false.

No migration/domain/external-ingestion path is needed or authorized.

## Findings repaired

### `MAR-WO-AUTH-F1 STALE_REFERENCE_PATHS_OMITTED`

The initial inventory omitted
`customer_request_service.py`, whose source comment would become false.
It is now exact production path 5. No behavior change there is authorized.

### `MAR-WO-AUTH-F2 EVIDENCE_FIELD_PARITY_NOT_ASSIGNED`

The initial edit boundary did not assign the SPEC's non-empty-evidence refusal
to both backends. Section 3.2 now assigns it to InMemory and the SQL message
store and forbids silent loss.

### `MAR-WO-AUTH-F3 PREMATURE_PROVIDER_ORDER`

The initial order allowed provider work before PostgreSQL proof. Section 6 now
requires all non-live and PostgreSQL admission proof before provider execution.

All findings closed without waiver.

## SPEC coverage

| SPEC | Work Order |
|---|---|
| R1-R7 | production 1-5; API/service tests |
| R8-R11 | production 4, 6-10; parity/schema/reference tests |
| R12 | PostgreSQL paths 19-21 and owned runner |
| R13-R15 | OpenAPI paths 13-15, protected boundary, file guard |
| R16-R18 | provider paths 22-26 and secret/resource discipline |
| R19 | receipts/control mapping and C4 boundary |
| AC-01..AC-23 | evidence commands, stop conditions, review/rollback |

The provider and PostgreSQL gates are independently mandatory. External
zero-diff and nonclaims are explicit.

## Authorization probes

- focused current contract/freeze baseline: 15 passed;
- session state, repository validator, catalog and file-size: PASS;
- JSON and `git diff --check`: PASS;
- doctor: `PASS WITH NOTE (24 passed, 1 warning)`; only bounded legacy
  catalog-kit warning;
- `HEAD == origin/main` before authoring; core pin clean/equal;
- zero staged paths and zero implementation diff at review start.

These are planning feasibility facts, not BUILD evidence.

## Disposition

`REVIEW_PASS` after `MAR-WO-AUTH-F1..F3` closed without waiver.

Only these actions are next:

1. commit/push the zero-BUILD C1 authorization set;
2. record and separately commit/push C2 pre-BUILD continuity;
3. run G6;
4. assign an implementation worker independent from this reviewer.

BUILD and live calls remain unauthorized until all four pass.
