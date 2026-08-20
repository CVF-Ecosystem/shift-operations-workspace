# Specification — P4-A AI Gateway

- Tranche: `P4A-AI-GATEWAY-2026-08-20`
- Phase: `SPEC`
- Risk: `R2`
- Parent: approved P4-A DESIGN
- Status: `AUTHORIZATION_REVIEW_PASS`
- Role transition: `DESIGN_AUTHOR → SPEC_AUTHOR`

## Requirements

- `R1` — The package is importable as `ai_gateway`, uses Python >=3.12 and
  exact Pydantic 2.10.6, and has no dependency on apps, ledgers, provider SDKs,
  network clients, or the hidden CVF Core.
- `R2` — `ProviderRequest`, `ProviderResult`, provider protocol, gateway
  request/result, policy/context facts, usage reservation, termination facts,
  and receipt models are strict, immutable where practical, and reject unknown
  fields. Mutable defaults are forbidden.
- `R3` — `AIGateway.execute` is the sole provider-dispatch point and follows
  the exact DESIGN order. Dependency tests prove it directly invokes
  `assert_placement_allowed`, `assert_within_budget`, and
  `assert_not_terminated` before dispatch.
- `R4` — `NO_AI`, `RULES_ONLY`, no evidence, malformed schema, unknown
  provider/model, failed placement, unavailable budget, and active kill switch
  all fail or fall back before dispatch with `provider_attempts=0`.
- `R5` — PUBLIC external placement is admitted only with explicit redaction and
  budget facts. INTERNAL requires positive minimization evidence. The current
  P4-A1 handoff (`NOT_PROVEN`/`NOT_EVALUATED`/`NO_LOAD_BEARING_CALLER`) is
  rejected for external dispatch without mutation or relabeling. CONFIDENTIAL
  and RESTRICTED are rejected for the public evidence endpoint.
- `R6` — The process-local usage ledger atomically reserves estimated usage,
  prevents concurrent over-reservation, commits actual usage exactly once,
  releases failed pre-dispatch reservations, and refuses double commit/release.
  Daily/monthly/per-request policy limits are enforced. No durability claim.
- `R7` — Kill switch and termination preflight run before dispatch. Timeout
  produces one recorded physical attempt, invokes best-effort
  `cancel_request`, releases/settles the reservation deterministically, emits a
  safe terminal receipt, and does not retry.
- `R8` — The physical attempt counter changes from zero to one immediately
  before provider I/O. This tranche permits at most one attempt per execution
  and exactly one total live attempt in the BUILD evidence run.
- `R9` — Provider output is accepted only when it is an object satisfying the
  exact caller-supplied JSON Schema. Invalid output never becomes an accepted
  result and retains the one-attempt failure receipt.
- `R10` — Receipts bind canonical SHA-256 digests for request metadata,
  admitted evidence/context, output schema, and accepted output; record safe
  provider/model/endpoint identifiers, all gate outcomes, reservation and
  actual usage, timeout/cancel state, and physical attempts. Raw prompt,
  context, output, secret, authorization header, or unsafe exception text is
  forbidden.
- `R11` — The provider registry is explicit and deterministic. Replacing the
  injected provider implementation does not modify gateway core. The evidence
  runner's adapter is evidence-only and does not change P4-B from open.
- `R12` — Component tests may use fakes only for non-governance mechanics.
  They must be labeled non-proof. Every governance claim in R3–R9 requires the
  fresh live run described in R13.
- `R13` — With an eligible model selected by
  `packages/ai-providers/alibaba/select_model.py`, the live runner proves in
  one run: all pre-call refusal cases have zero physical attempts; one PUBLIC
  canary passes the three gates; exactly one HTTPS request reaches the allowed
  DashScope endpoint; returned JSON passes the schema; usage is committed; and
  a sanitized receipt is written. Missing credentials/model or any live
  failure yields `LIVE_EVIDENCE_BLOCKED`; no second attempt is authorized.
- `R14` — Catalog, status, roadmap, CVF mappings, Project Knowledge pins, and
  continuity report only bounded truth: P4-A `CLOSED_BOUNDED` after REVIEW;
  P3-B may close only for the gateway/live-evidence call-site boundary; Phase 3
  may become 6/6 only if every existing Phase 3 gate remains true. P4-B,
  P4-A2, app callers, durability, deployment, and production remain open.
- `R15` — Worker status is exactly the 40 DESIGN paths, staged set is empty,
  `git diff --check` passes, and no secret-like value exists in the diff. The
  reviewer alone adds the completion review and recomputes the final 41 paths.

## Required commands

From project root, capture command, exit code, and concise output for:

```powershell
python -m pytest -q tests/unit/test_p4a_gateway_models.py tests/unit/test_p4a_gateway_registry.py tests/unit/test_p4a_gateway_usage.py tests/unit/test_p4a_gateway_context.py tests/unit/test_p4a_gateway_validation.py tests/unit/test_p4a_gateway_receipts.py tests/unit/test_p4a_gateway_dependency_boundaries.py tests/contract/test_p4a_ai_gateway_schema.py tests/integration/test_p4a_gateway_live_evidence_support.py
python -m pytest -q
python scripts/run_p4a_gateway_live_evidence.py
python scripts/generate_catalog.py --check
python scripts/check_session_state.py
python scripts/check_project_knowledge.py
python scripts/check_file_size.py
python scripts/testing/validate_repository.py
powershell -ExecutionPolicy Bypass -File "..\.Controlled-Vibe-Framework-CVF\scripts\check_cvf_workspace_agent_enforcement.ps1" -ProjectPath "."
git diff --check
git diff --cached --name-only
git status --short
```

Parse every changed JSON file with `json.loads`. The worker must compare the
sorted status paths exactly with DESIGN's 40-path set.

## Acceptance and claims

All R1–R15 pass without waiver, with a fresh sanitized live receipt and exactly
one physical call. Acceptance proves a bounded library call site where the
three CVF gates precede provider dispatch. It does not prove an application API
uses the gateway, durable accounting, a production provider adapter, RAG,
deployment, or production readiness.
