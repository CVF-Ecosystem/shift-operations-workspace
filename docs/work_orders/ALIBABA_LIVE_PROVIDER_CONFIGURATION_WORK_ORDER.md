# Work Order: Alibaba Live Provider Configuration

- Work order: `WO-PROVIDER-ALIBABA-LIVE-CONFIG-2026-07-22`
- Risk: R2
- Status: AUTHORIZED
- Authority: operator request in the active session authorizing recurring
  Alibaba live runs and environment configuration
- Design: `docs/decisions/ADR_2026-07-22_ALIBABA_LIVE_PROVIDER_CONFIGURATION.md`
- Specification: `docs/specs/ALIBABA_LIVE_PROVIDER_CONFIGURATION_SPEC.md`

## Authorized changed set

- `.gitignore` only if an additional secret-local pattern is necessary.
- `packages/ai-providers/alibaba/model-quota-catalog.json`
- `packages/ai-providers/alibaba/select_model.py`
- `packages/ai-providers/alibaba/README.md`
- `tests/unit/test_alibaba_model_selector.py`
- A redacted evidence receipt under `docs/decisions/`.
- Required catalog and continuity files if source truth changes.
- Current-user `ALIBABA_API_KEY` environment value, outside the repository.

## Explicit exclusions

- Do not copy, move, edit, or delete the source credential CSV.
- Do not put the key in `.env`, source, tests, documentation, shell output,
  Git history, or evidence.
- Do not modify the pinned CVF core.
- Do not implement the application AI gateway.
- Do not repair or close P2-B authentication findings in this tranche.
- Do not claim provider-wide or production readiness from one live call.

## Implementation role

`IMPLEMENTATION_WORKER` may:

1. Parse the named CSV in memory and extract only `apiKey`.
2. Persist it as the Windows current-user environment variable
   `ALIBABA_API_KEY` and set it in the current process for verification.
3. Create the non-secret catalog, selector, documentation, and tests.
4. Run a secret-safe readiness check.
5. Select a currently eligible model and run minimal Alibaba live validation.
6. Store only redacted evidence.

## Evidence and tests

- Key presence check reports only boolean/source metadata.
- Unit tests must cover eligibility and deterministic selection.
- `python -m pytest -q`
- `python scripts/testing/validate_repository.py`
- `python scripts/check_session_state.py`
- `python scripts/generate_catalog.py --check`
- CVF workspace doctor.
- Minimal live Alibaba call with explicit selected model.

## Stop conditions

Stop without repeated paid calls if:

- CSV structure is ambiguous or contains multiple candidate keys;
- a command would expose the credential;
- no catalog model is eligible;
- the first live call reports authentication, quota, model-not-found, or
  expiration failure;
- repository continuity drifts;
- implementation requires files outside the authorized set.

## Review and closure

An independent `REVIEWER` must inspect the changed set, secret handling,
selector behavior, tests, and redacted live receipt. `CLOSER` may freeze only
after review pass and synchronized continuity. Commit ownership remains with
`COMMIT_STEWARD`; this work order does not itself authorize rewriting history
or force-pushing.
