"""P4-A2 governed RAG - application orchestration (SPEC R3).

The sole application composition owner: invokes P4-A1's
``execute_governed_retrieval`` with the caller's original, unmodified
request, then passes ONLY its result into ``governed_rag.GovernedRAG.execute``
alongside an injected, already-configured concrete ``ai_gateway.service.
AIGateway`` instance. Never opens an HTTP route (no FastAPI router/dependency
is declared here) and never persists output or index state - the pipeline's
sanitized receipt is response data only, exactly mirroring
``governed_retrieval``'s own no-audit-write convention.

Query/result continuity is owned here, not inside the pure `governed_rag`
package: the same ``raw_body["query"]`` value that reaches P4-A1 is the value
threaded into the P4-A2 request, so an unrelated positive retrieval result
can never be substituted for a different query (DESIGN 'Composition and
dependency direction').
"""

from __future__ import annotations

from typing import Any

from ai_gateway.models import Placement
from ai_gateway.service import AIGateway
from governed_rag.models import GovernedRagRequestV1
from governed_rag.service import GovernedRAG, GovernedRagOutcome
from governed_retrieval.hashing import authorization_scope_digest

from workspace_api.application import _governed_retrieval_admission as admission
from workspace_api.application.assignment_scope import AssignmentScope
from workspace_api.application.governed_retrieval import execute_governed_retrieval

GovernedRetrievalExecutionMetadataV1 = admission.GovernedRetrievalExecutionMetadataV1


async def execute_governed_rag(
    *,
    raw_body: dict[str, Any],
    rag_request: GovernedRagRequestV1,
    bearer_token: str,
    assignment_scope: AssignmentScope,
    ledger: Any,
    metadata: GovernedRetrievalExecutionMetadataV1,
    gateway: AIGateway,
    placement: Placement,
) -> GovernedRagOutcome:
    """SPEC R3 - execute P4-A1 governed retrieval with ``raw_body`` (the
    original, unmodified caller request, whose ``query`` field must equal
    ``rag_request.query``), then pass only its result into P4-A2's pure
    ``GovernedRAG.execute``. Never opens an HTTP route or persists state.

    ``gateway`` is caller-injected and already configured (registry, ledger,
    endpoint origin); this function never constructs a second gateway and
    never imports a provider SDK itself (SPEC R12). ``placement``
    (P4A2-REV-F3) is REQUIRED and must be supplied by whoever actually wired
    ``gateway`` to its real dispatch target (e.g. ``Placement.EXTERNAL`` for
    the live external HTTPS adapter) - this function has no way to inspect a
    provider's real network destination and must never guess or default it,
    since a wrong default is exactly the mislabeling defect this finding
    fixes. It is passed straight through to ``GovernedRAG.__init__``, which
    binds it for the lifetime of that one engine instance.
    """
    if raw_body.get("query") != rag_request.query:
        # RR-P4A2: query/result continuity is owned here - an application
        # bug that let a caller substitute a different P4-A1 query than the
        # one P4-A2 believes it is answering would silently break SPEC R5's
        # "no scope widening" guarantee. Fail closed rather than proceed.
        raise ValueError("raw_body query must equal rag_request.query for continuity")

    retrieval_result = execute_governed_retrieval(
        raw_body=raw_body,
        bearer_token=bearer_token,
        assignment_scope=assignment_scope,
        ledger=ledger,
        metadata=metadata,
    )

    authorization_scope_digest_sha256 = (
        retrieval_result.receipt.authorization_scope_digest_sha256
        if retrieval_result.receipt.authorization_scope_digest_sha256 is not None
        else _placeholder_scope_digest()
    )

    engine = GovernedRAG(gateway, placement=placement)
    return await engine.execute(
        request=rag_request,
        retrieval_result=retrieval_result,
        authorization_scope_digest_sha256=authorization_scope_digest_sha256,
    )


def _placeholder_scope_digest() -> str:
    """A pre-authorization P4-A1 negative outcome (e.g. INVALID_REQUEST
    before the authorization stage ran) carries no
    ``authorization_scope_digest_sha256`` at all. P4-A2 short-circuits on any
    non-positive result before this digest is ever load-bearing, so a fixed,
    clearly-synthetic all-zero placeholder (never a real scope digest) is
    used only to satisfy the receipt's required field - it is never trusted
    as authorization evidence."""
    return authorization_scope_digest("", "", ())


__all__ = ["execute_governed_rag", "GovernedRetrievalExecutionMetadataV1"]
