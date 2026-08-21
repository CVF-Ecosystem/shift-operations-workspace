#!/usr/bin/env python3
"""P4-A3 post-review live evidence runner.

Runs memory refusals at zero mutation/zero provider attempts, admits and
re-reads one synthetic memory entry, runs the inherited P4-A2 refusal chain,
then uses the revalidated memory text as the query for exactly one full
P4-A2/AIGateway provider dispatch. This consuming path requires the separate
post-review operator authority recorded for P4-A3.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

REPO_ROOT = Path(__file__).resolve().parents[1]
_SIBLING_PATHS = (
    "apps/workspace-api/src", "packages/application-memory/src",
    "packages/cvf-runtime/src", "packages/operations-ledger/src",
    "packages/operations-domain/src", "packages/refinery-bridge/src",
    "packages/retrieval-contracts/src", "packages/governed-retrieval/src",
    "packages/ai-gateway/src", "packages/governed-rag/src", "packages/ai-providers",
)
for _path in (str(REPO_ROOT / item) for item in _SIBLING_PATHS):
    if _path not in sys.path:
        sys.path.insert(0, _path)
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from _p4a2_governed_rag_live_evidence_support import (  # noqa: E402
    CallBudget, build_synthetic_knowledge_root, endpoint, execution_metadata,
    key_presence, p4a1_request_body, rag_request,
    run_refusals as run_rag_refusals, safe_origin, scan_for_secrets,
    seeded_workspace, sha256_hex,
)
from _p4a3_application_memory_live_evidence_support import (  # noqa: E402
    REFUSAL_CASES, _GuardProvider, admission_request, fake_revalidator,
    fresh_service, run_refusals as run_memory_refusals, source_ref,
)
from ai_gateway.models import Placement  # noqa: E402
from ai_gateway.registry import ProviderRegistry  # noqa: E402
from ai_gateway.service import AIGateway  # noqa: E402
from ai_gateway.usage import UsageLedger  # noqa: E402
from application_memory.models import MemoryFinalOutcome, SourceRevalidationOutcome  # noqa: E402
from run_p4a2_governed_rag_live_evidence import (  # noqa: E402
    _LiveDashScopeProvider, _RefusalGuardProvider,
)
from workspace_api.application.governed_rag import execute_governed_rag  # noqa: E402

TRANCHE = "P4A3-APPLICATION-MEMORY-2026-08-21"
RECEIPT_PATH = REPO_ROOT / "docs" / "decisions" / "P4A3_APPLICATION_MEMORY_LIVE_EVIDENCE_RECEIPT.md"
ADMITTED_MEMORY_TEXT = "handover procedure"
OWNER_ID = "operator-1"
SHIFT_ID = UUID("00000000-0000-0000-0000-000000000001")
SCOPE_DIGEST = "a" * 64


def _clock() -> datetime:
    return datetime.now(timezone.utc)


def _memory_admission() -> tuple[object, object]:
    declared = source_ref(text="synthetic source text")
    service, store = fresh_service(
        clock=_clock,
        revalidator=fake_revalidator(outcome=SourceRevalidationOutcome.VALID),
    )
    admitted = service.admit(
        request=admission_request(content=ADMITTED_MEMORY_TEXT, source=declared),
        owner_id=OWNER_ID, shift_id=SHIFT_ID,
        authorization_scope_digest=SCOPE_DIGEST,
    )
    if admitted.receipt.final_outcome is not MemoryFinalOutcome.ADMITTED:
        raise RuntimeError("synthetic memory admission was not admitted")
    reread = service.read(
        owner_id=OWNER_ID, shift_id=SHIFT_ID,
        authorization_scope_digest=SCOPE_DIGEST, limit=1,
    )
    if (
        reread.receipt.final_outcome is not MemoryFinalOutcome.READ_COMPLETE
        or len(reread.entries) != 1
        or reread.entries[0].entry_id != admitted.entries[0].entry_id
        or reread.entries[0].entry_digest_sha256 != admitted.entries[0].entry_digest_sha256
        or len(store.snapshot()[0]) != 1
    ):
        raise RuntimeError("synthetic memory read binding failed")
    return admitted, reread


def _write_receipt(payload: dict) -> tuple[str, list[str]]:
    body = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    hits = scan_for_secrets(body)
    document = f"""# P4-A3 Application Memory - Live Evidence Receipt

- Tranche: `{TRANCHE}`
- Generated: `{payload['generated_at']}`
- Disposition: `{payload['disposition']}`
- Physical provider calls this run: `{payload['physical_calls']}`

Sanitized machine-readable record. It contains safe ids, digests, counts,
outcomes and reason codes only; no memory text, query, evidence body, provider
output body, endpoint path, authorization header or credential.

```json
{body}
```

## Claim boundary

This receipt proves the recorded synthetic run: every P4-A3 memory refusal
changed zero state and reached the provider zero times; one admitted memory
entry was independently re-read and its text was used explicitly as the P4-A2
query; the inherited P4-A2 refusal chain stayed zero-call; and the admitted
path made at most one HTTPS POST through the real P4-A2/AIGateway composition.
It does not prove implicit recall, operational data, durable memory, a public
route, production provider integration, deployment or production readiness.
"""
    RECEIPT_PATH.write_text(document, encoding="utf-8")
    return sha256_hex(document), hits


def main() -> int:
    parser = argparse.ArgumentParser(description="P4-A3 post-review live evidence")
    parser.add_argument("--refusals-only", action="store_true")
    args = parser.parse_args()
    generated_at = datetime.now(timezone.utc).isoformat()

    memory_guard = _GuardProvider()
    memory_refusals = run_memory_refusals(memory_guard)
    memory_zero = all(
        row["mutations"] == row["provider_attempts"] == 0
        and row["appended_entries"] == row["appended_tombstones"] == 0
        for row in memory_refusals
    )
    print(f"memory refusals: {len(memory_refusals)}/{len(REFUSAL_CASES)} zero-call={memory_zero}")
    if not memory_zero or memory_guard.calls:
        print("LIVE_EVIDENCE_BLOCKED: memory refusal reached mutation/provider", file=sys.stderr)
        return 1

    try:
        admitted, reread = _memory_admission()
    except Exception as exc:
        print(f"LIVE_EVIDENCE_BLOCKED: memory admission/read {type(exc).__name__}", file=sys.stderr)
        return 1
    entry = reread.entries[0]
    print("memory admission/read: PASS")

    if args.refusals_only:
        print("refusals-only mode: stopping before provider preflight/dispatch")
        return 0

    present, key_env_name = key_presence()
    print(f"credential present: {present}; env var: {key_env_name or 'NONE'}")
    if not present or key_env_name is None:
        print("LIVE_EVIDENCE_BLOCKED: no credential", file=sys.stderr)
        return 1
    try:
        from alibaba.select_model import select_model  # noqa: PLC0415

        model_id = select_model()
    except Exception as exc:
        print(f"LIVE_EVIDENCE_BLOCKED: model selection {type(exc).__name__}", file=sys.stderr)
        return 1

    budget = CallBudget(limit=1)
    with tempfile.TemporaryDirectory(prefix="p4a3_live_evidence_") as tmp_name:
        tmp_dir = Path(tmp_name)
        rag_refusals = run_rag_refusals(model_id, budget, _RefusalGuardProvider, tmp_dir)
        rag_zero = all(
            not row["accepted"]
            and row["provider_attempts"] == row["adapter_calls"] == row["gateway_attempts"] == 0
            for row in rag_refusals
        )
        print(f"P4-A2 refusals: {len(rag_refusals)} zero-call={rag_zero}")
        if not rag_zero or budget.physical:
            print("LIVE_EVIDENCE_BLOCKED: inherited refusal reached provider", file=sys.stderr)
            return 1

        knowledge_root = build_synthetic_knowledge_root(tmp_dir / "kb")
        ledger, shift, scope, token = seeded_workspace()
        query = entry.content
        body = p4a1_request_body(query=query, shift_ids=(str(shift.shift_id),))
        provider = _LiveDashScopeProvider(budget, key_env_name)
        registry = ProviderRegistry()
        registry.register(provider, (model_id,), placement=Placement.EXTERNAL)
        origin = safe_origin(endpoint())
        gateway = AIGateway(registry, UsageLedger(), endpoint_origin=origin)
        budget.reserve()
        error_note = ""
        outcome = None
        try:
            outcome = asyncio.run(
                execute_governed_rag(
                    raw_body=body,
                    rag_request=rag_request(query=query, model_id=model_id),
                    bearer_token=token, assignment_scope=scope, ledger=ledger,
                    metadata=execution_metadata(repository_root=knowledge_root),
                    gateway=gateway, placement=Placement.EXTERNAL,
                )
            )
        except Exception as exc:
            error_note = type(exc).__name__

        accepted = bool(
            outcome is not None
            and outcome.receipt.final_outcome.value in ("ANSWERED", "ABSTAINED")
        )
        payload = {
            "generated_at": generated_at, "tranche": TRANCHE,
            "disposition": "LIVE_EVIDENCE_PASS" if accepted and budget.physical == 1 else "LIVE_EVIDENCE_BLOCKED",
            "memory_refusal_cases": memory_refusals,
            "memory_admission_outcome": admitted.receipt.final_outcome.value,
            "memory_read_outcome": reread.receipt.final_outcome.value,
            "memory_entry_id": str(entry.entry_id),
            "memory_entry_digest_sha256": entry.entry_digest_sha256,
            "memory_source_content_digest_sha256": entry.source.source_content_digest_sha256,
            "memory_provenance_digest_sha256": entry.source.provenance_digest_sha256,
            "memory_authorization_scope_digest_sha256": entry.authorization_scope_digest_sha256,
            "rag_refusal_cases": rag_refusals,
            "provider_id": provider.provider_id, "model_id": model_id,
            "endpoint_origin": origin, "credential_env_var": key_env_name,
            "physical_calls": budget.physical, "adapter_calls": provider.calls,
            "gateway_attempts": gateway.physical_attempts,
            "http_status": provider.http_status, "reached_server": provider.reached_server,
            "error_note": error_note or provider.error_note,
            "rag_receipt": json.loads(outcome.receipt.model_dump_json()) if outcome else None,
        }
        receipt_hash, hits = _write_receipt(payload)
        final_outcome = outcome.receipt.final_outcome.value if outcome else "NONE"
        print(
            f"http_status={provider.http_status} physical_calls={budget.physical} "
            f"adapter_calls={provider.calls} gateway_attempts={gateway.physical_attempts} "
            f"final_outcome={final_outcome} receipt_sha256={receipt_hash} "
            f"secret_scan={hits or 'NONE'}"
        )
        if hits or not accepted or budget.physical != provider.calls or budget.physical != 1:
            print("LIVE_EVIDENCE_BLOCKED", file=sys.stderr)
            return 1
        print("LIVE_EVIDENCE_PASS")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
