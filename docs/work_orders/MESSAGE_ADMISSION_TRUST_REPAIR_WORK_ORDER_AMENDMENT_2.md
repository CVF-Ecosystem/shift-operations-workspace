# Work Order Amendment 2 — Independent BUILD Review Repair

- Tranche: `MESSAGE-ADMISSION-TRUST-REPAIR-2026-07-30`
- Risk: R2
- Status: `REVIEW_PASS — REPAIR PROHIBITED UNTIL PUSHED CONTINUITY ACK`
- Implementation/repair worker: Claude Code `2.1.215`
- Independent reviewer/commit steward: Codex

## 1. Final C3 ceiling

The original 29 paths remain authorized. Add exactly:

30. `tests/unit/test_shift_create_openapi_contract.py`

The final C3 ceiling is exactly 30 paths. No 31st path is conditional.

## 2. Repair scope

`MAR-BUILD-REV-F1` may modify path 30 only to reverse the complete later
SPEC R13 delta before the predecessor proof hashes its unchanged baseline.
No historical digest refresh is authorized.

`MAR-BUILD-REV-F2` through `MAR-BUILD-REV-F5` may modify only these
already-authorized paths as needed:

- `scripts/_message_admission_live_evidence_support.py`
- `scripts/run_message_admission_live_governance_evidence.py`
- `tests/integration/test_message_admission_live_evidence_runner.py`
- `tests/cvf/test_message_admission.py`
- `tests/integration/test_message_sqlite.py`
- `tests/integration/test_message_postgres_live.py`
- `docs/decisions/MESSAGE_ADMISSION_TRUST_REPAIR_BUILD_EVIDENCE_RECEIPT.md`
- `docs/decisions/MESSAGE_ADMISSION_TRUST_REPAIR_LIVE_EVIDENCE_RECEIPT.md`
- `docs/catalog/MODULE_REGISTRY.json`
- `docs/catalog/MODULE_CATALOG.md`

Other original C3 paths may remain dirty from the implementation but receive
no unrelated repair. Authorization documents and continuity are read-only
to the repair worker.

## 3. Required repair order

1. Repair the historical OpenAPI reduction and run all OpenAPI-chain tests.
2. Put endpoint parsing/cleaning inside the sanitized failure boundary; add
   invalid-port and malformed-endpoint negative tests.
3. Measure refusal message/audit/provider deltas; add an injected-audit
   negative test.
4. Strengthen InMemory/SQLite/PostgreSQL rollback and no-partial assertions.
5. Correct receipt contradictions and registry/catalog truth.
6. Run focused and full non-live suites. Any failure blocks live execution.
7. Rerun disposable PostgreSQL 16 evidence with exact cleanup.
8. Only then run one fresh real-provider proof and replace the sanitized
   live receipt.
9. Run all repository gates and return for independent re-review.

## 4. Mandatory evidence

At minimum:

```powershell
python -m pytest -q tests/unit/test_shift_create_openapi_contract.py tests/unit/test_message_openapi_contract.py tests/unit/test_p2b_openapi_contract.py tests/unit/test_p2c_read_openapi_contract.py
python -m pytest -q tests/integration/test_message_admission_live_evidence_runner.py tests/cvf/test_message_admission.py tests/integration/test_message_sqlite.py tests/integration/test_postgres_live_runner.py
python -m pytest -q
python scripts/testing/validate_repository.py
python scripts/generate_catalog.py --check
python scripts/check_session_state.py
python scripts/check_file_size.py
git diff --check
python scripts/run_postgres_live_roundtrip.py --json
python scripts/run_message_admission_live_governance_evidence.py
```

Also return:

- adversarial invalid-port/malformed-endpoint results with no secret;
- adversarial injected-refusal-audit detection;
- exact 30-path inventory and protected-boundary zero diff;
- JSON parse, secret scan and zero Docker residue;
- doctor `PASS WITH NOTE (24/1)` with only the bounded legacy warning.

## 5. Stop and ownership

Stop on any required 31st path, raw secret, false-positive refusal, partial
state, full-suite failure, provider/PostgreSQL failure, cleanup uncertainty
or new warning.

Claude must not stage, commit, push, review or FREEZE. Codex owns independent
re-review and any later selective commit/push.

Return only after every requirement passes:

`READY_FOR_INDEPENDENT_MESSAGE_ADMISSION_BUILD_RE_REVIEW`

