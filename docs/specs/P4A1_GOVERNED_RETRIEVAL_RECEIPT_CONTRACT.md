# P4-A1 Governed Retrieval Receipt Contract V1

- Status: `NORMATIVE_APPENDIX_CANDIDATE_PENDING_INDEPENDENT_REVIEW`
- Parent SPEC: `docs/specs/P4A1_GOVERNED_RETRIEVAL_SPEC.md`
- Parent ADR: `docs/decisions/ADR_2026-08-10_P4A1_GOVERNED_RETRIEVAL.md`
- Scope: R9 citation, receipt, stage, nested-model, and hash semantics only

This appendix is a required part of the parent SPEC. It adds no runtime scope,
provider call, durable audit, persistence, corpus eligibility, or authority.

## Citation and projection binding

`CitationV1` rejects unknown fields and contains exactly `chunk_id`,
`content_digest_sha256`, `source_digest_sha256`, the exact P3-C version union,
`truth_class`, `record_type`, exactly one safe `record_id` or `source_id`,
`field_selector`, `revalidation_token`, `source_cutoff_utc`,
`snippet_digest_sha256`, `snippet_start_codepoint`, and
`snippet_end_codepoint`. A path alone or missing digest/version is invalid.

`citation_id` is SHA-256 of P3-C canonical JSON bytes for
`{"citation": <CitationV1 model_dump(mode="python")>}`. Receipt, handoff, and
projection tuples use these ids in projection rank order; duplicates are
forbidden. `EvidenceProjectionV1.citation` hashes to its same-position id.

## Closed nested models

`RetrievalCountsV1` contains exactly these non-negative integers:

- `source_records_read`;
- `candidates_admitted`;
- `matches_ranked`;
- `selected_for_revalidation`;
- `stale_omitted`;
- `projections_emitted`;
- `projections_budget_omitted`.

`RetrievalLimitsV1` contains exactly `result_limit` plus the five R2
context-budget fields. `TerminationFactsV1` contains exactly positive
`configured_timeout_ms`, `timed_out`, and `cancelled`; its booleans cannot both
be true.

`RetrievalStageReceiptV1` contains exactly `stage`, `outcome`, nullable
`reason_code`, and `safe_counts: RetrievalCountsV1`. Stage order is exactly:

1. `REQUEST_VALIDATED`;
2. `AUTHENTICATED`;
3. `PERMISSION_AUTHORIZED`;
4. `ASSIGNMENT_AUTHORIZED`;
5. `CORPUS_RESOLVED`;
6. `SOURCES_READ`;
7. `P3C_ADMITTED`;
8. `MATCHED_AND_RANKED`;
9. `REVALIDATED`;
10. `PROJECTED`;
11. `RECEIPT_EMITTED`.

Stage outcome is exactly `PASS`, `DENY`, `FAIL`, or `NOT_RUN`. The first
terminal operational stage is `DENY` for access or `FAIL` otherwise; later
operational stages are `NOT_RUN`. `RECEIPT_EMITTED` is `PASS` for every safe
returned receipt. Denial/unavailable receipts have zero protected-source
counts. Each stage count is the safe cumulative snapshot after that stage.

`reason_code` is null for `PASS`/`NOT_RUN`; for `DENY`/`FAIL` it is exactly one
of the eight R2 codes, `AUTHENTICATION_FAILED`, `ACCESS_DENIED`, or one of the
nine negative R11 outcome literals other than `INVALID_REQUEST`. Free text is
forbidden.

## RetrievalReceiptV1

`RetrievalReceiptV1` contains exactly:

- `contract_version="1.0"`;
- UUIDv4 `receipt_id` and `retrieval_correlation_id`;
- UTC `started_at_utc`, `finished_at_utc`, nullable `source_cutoff_utc`, and
  non-negative `elapsed_ms`;
- nullable `corpus_id` and `authorization_scope_digest_sha256`;
- the exact eleven stage receipts and `final_outcome`;
- nullable `requested_limits: RetrievalLimitsV1` and
  `applied_limits: RetrievalLimitsV1`;
- `counts: RetrievalCountsV1` and `termination: TerminationFactsV1`;
- ordered `citation_ids`, nullable `evidence_set_hash_sha256`, and
  `receipt_hash_sha256`.

The service allocates correlation/receipt ids and start time before R2.
`corpus_id` is populated only after `CORPUS_RESOLVED=PASS`; the authorization
digest only after authentication plus every assignment passes; requested
limits only after structural validation; applied limits only after corpus
resolution; source cutoff only after a source snapshot; and evidence hash only
for `EVIDENCE_AVAILABLE`. Earlier values are null, never fabricated.

## Canonical preimages

The authorization preimage is exactly `{"workspace_id": workspace scope,
"principal_user_id": principal id, "admitted_shift_ids": sorted ids}`.

All hashes use `retrieval_contracts.canonical.canonical_json_bytes` on
`model_dump(mode="python")` dictionaries: enums become values, UUIDs lowercase,
UTC datetimes use `Z`, NFC strings and tuple order are preserved, map keys sort,
and floats are forbidden. Evidence hash covers exactly
`{"citations": ordered citation dumps, "projections": ordered projection dumps}`.
Receipt hash covers the entire receipt dump with only `receipt_hash_sha256`
omitted. Fixed clock/id values are injected for byte-determinism tests.

## Ephemeral boundary

The receipt is response data only. It is not an `operations_domain` record,
`AuditRecord`, approval, correction, or durable Ledger entry. P4-A1 calls
neither `audit_log.record` nor `Ledger.append_audit`.

## Acceptance binding

The parent SPEC AC-09 applies to every field and invariant in this appendix.
Any missing appendix pin, nested-field drift, fabricated negative value,
citation mismatch, free-text reason, hash mismatch, or audit write fails R9.
