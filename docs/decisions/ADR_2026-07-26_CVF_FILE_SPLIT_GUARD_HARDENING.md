# ADR — CVF File-Split Guard Hardening

Status: ACCEPTED — INDEPENDENT AUTHORIZATION REVIEW PASS  
Tranche: `CVF-FILE-SPLIT-GUARD-HARDENING-2026-07-26`  
Risk: R2  
Owner boundary: repository tooling and behavior-preserving file extraction

## 1. Context

The existing file-size guard is real but too permissive for Python:

- warning at 300 lines;
- failure only above 400 lines;
- `--warn` is informational;
- the exception registry can currently exempt any suffix;
- a missing or malformed registry is not handled as a governed policy error.

The P2B BUILD demonstrated the practical gap. Seven files changed by C3 are
above 300 lines but below 400, including a 384-line acceptance-test file and a
394-line ledger file. All gates passed because the guard treats those files as
warnings rather than split obligations.

The operator requires the split rule to be enforced by repository guards, not
remembered by agents.

## 2. Decision

### 2.1 Executable-code limits

The guard will enforce these hard limits:

| Suffix | warning | hard |
|---|---:|---:|
| `.py` | 250 | 300 |
| `.ts`, `.tsx`, `.js`, `.jsx` | 160 | 200 |

Markdown remains governed by its existing 400/600 thresholds. Historical
governance records are not rewritten by this tranche.

### 2.2 Legacy-debt ratchet

Existing executable files above the new hard limit may remain only through a
tracked debt baseline containing:

- normalized repository-relative path;
- exact SHA-256;
- exact line count;
- applicable hard limit;
- bounded reason and required split action.

An oversized debt file passes only while its bytes and line count match the
baseline exactly. If touched, it must be split to the hard limit or below in
the same changed set. Same-line-count edits do not bypass the rule because the
digest must still match.

Stale, missing, duplicate, malformed, untracked, outside-repository or
below-limit debt entries fail closed.

### 2.3 Exception boundary

Executable suffixes cannot use `FILE_SIZE_EXCEPTION_REGISTRY.json`.
Exceptions are restricted to approved non-executable/generated or frozen
documentation surfaces and must pass strict schema/path validation.

The debt baseline is not a general exception mechanism. Adding or changing a
debt entry is a governed policy change and remains visible in Git review.

### 2.4 Immediate debt repayment

The seven C3-touched Python files currently above 300 lines must be split in
this tranche:

1. `apps/workspace-api/src/workspace_api/application/approval_service.py`
2. `apps/workspace-api/src/workspace_api/infrastructure/repository.py`
3. `packages/operations-ledger/src/operations_ledger/sql_ledger.py`
4. `scripts/run_approval_governance_evidence.py`
5. `tests/cvf/test_approver_identity_reconciliation.py`
6. `tests/integration/test_schema_parity.py`
7. `tests/unit/test_operations_domain_serialization.py`

Extraction must preserve public imports, behavior, schemas, test identities,
provider-call cardinality and receipt semantics.

Other pre-existing executable files above 300 lines are recorded in the
digest-bound debt baseline. They are not refactored in this tranche, but any
future content change forces their split.

The baseline set is closed to exactly four paths:

1. `scripts/generate_catalog.py`
2. `scripts/run_identity_live_governance_evidence.py`
3. `tests/cvf/test_customer_request_vertical.py`
4. `tests/cvf/test_shift_close_governance.py`

No other executable path may be grandfathered.

### 2.5 Enforcement route

The strict default command remains:

`python scripts/check_file_size.py`

It is already invoked by:

- `scripts/testing/validate_repository.py`;
- `.githooks/pre-commit`;
- CI through repository validation.

Negative tests will prove these integrations and the fail-closed cases. The
guard must reject unknown CLI arguments rather than silently ignoring them.

## 3. Alternatives rejected

### Keep 400 and ask agents to split near 300

Rejected because it repeats the memory-dependent control the operator
explicitly rejected.

### Lower the limit and grandfather by path only

Rejected because a grandfathered file could continue changing under its old
cap. Digest binding makes the legacy allowance immutable.

### Split every historical oversized file immediately

Rejected as an unnecessarily broad refactor. The digest ratchet blocks future
growth while keeping this tranche focused on the debt introduced or touched by
the immediately preceding BUILD.

### Permit Python exceptions with a reason

Rejected because an implementation worker could route around the split rule
by adding a registry entry.

## 4. Compatibility and claim boundary

This is a structural refactor and repository-enforcement tranche:

- no API, OpenAPI, database schema or migration change;
- no CVF approval/identity/evidence behavior change;
- no provider call and no secret read are required;
- no PostgreSQL-live claim;
- no claim that CVF controls AI/agent behavior is introduced.

The existing P2B live receipt remains historical evidence for P2B only.

## 5. Roles

- Codex: `ORCHESTRATOR → SPEC_AUTHOR → WORK_ORDER_AUTHOR → REVIEWER`
- Claude: `IMPLEMENTATION_WORKER`, only after explicit authorization and
  pre-BUILD continuity
- Codex: independent `REVIEWER → COMMIT_STEWARD → CLOSER`

Claude may not self-approve, commit or push BUILD.

## 6. Consequences

Positive:

- new executable files cannot quietly grow to 400 lines;
- touched legacy debt cannot hide behind a grandfathered path;
- exception misuse and malformed policy fail closed;
- the seven immediate C3 debt files are decomposed now.

Cost:

- the C3 refactor touches several compatibility seams;
- helper modules increase file count;
- future work touching frozen debt must budget a split first.

## 7. Acceptance authority

The normative requirements and exact changed-set ceiling are in:

- `docs/specs/CVF_FILE_SPLIT_GUARD_HARDENING_SPEC.md`
- `docs/work_orders/CVF_FILE_SPLIT_GUARD_HARDENING_WORK_ORDER.md`

No BUILD is authorized by this ADR alone.

## 8. Independent authorization review

Codex reviewed the authorization package independently from the future
implementation worker and initially found:

- `FSG-AUTH-F1`: legacy debt set was not enumerated;
- `FSG-AUTH-F2`: four already-correct route surfaces were unnecessarily
  writable.

Both were repaired without waiver. The debt set is now exactly four paths,
route surfaces are read-only, and the C3 ceiling is 24 paths.

Disposition: `REVIEW_PASS` on 2026-07-26.
