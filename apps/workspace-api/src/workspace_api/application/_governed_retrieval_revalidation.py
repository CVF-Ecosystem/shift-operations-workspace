"""P4-A1 governed retrieval - single-unit use-time revalidation and R8
projection assembly (SPEC R7/R8).

Every Ledger-backed call in one execution shares the single ``unit`` token
opened by the orchestrator's one ``Ledger.transaction()``. This module
re-runs active assignment for every selected shift immediately before
returning, drives the Project Knowledge-specific reread-and-rebuild through
``_governed_retrieval_knowledge.revalidate_entry``, compares every R7-required
fact against the originally-ranked candidate, and assembles the R8
citation/projection tuple with aggregate budget trimming. It performs no
second Ledger transaction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import UUID

from cvf_runtime.identity import Principal
from governed_retrieval.evidence_models import CitationV1, EvidenceProjectionV1
from governed_retrieval.lexical import normalize_with_offsets
from governed_retrieval.projection import build_snippet, estimate_tokens, serialized_projection_bytes
from retrieval_contracts.contract_models import RetrievalReadyV1

from workspace_api.application.assignment_scope import AssignmentScope, OperationalResourceNotFound

from . import _governed_retrieval_knowledge as knowledge


def build_citation_and_projection(
    ready: RetrievalReadyV1, normalized_query: str, query_tokens: tuple[str, ...],
    *, max_snippet_codepoints: int, max_snippet_utf8_bytes: int, sensitivity: str,
) -> tuple[CitationV1, EvidenceProjectionV1] | None:
    """R8/R9 - build the citation and evidence projection for one
    revalidated candidate using the best lexical span, applying the
    already-``min(server, client)``-resolved snippet ceilings and the real
    P3-A candidate ``sensitivity`` (never a hardcoded literal). Returns
    ``None`` if no snippet fits either ceiling (caller omits the whole
    projection)."""
    normalized = normalize_with_offsets(ready.redacted_normalized_text)
    snippet = build_snippet(
        source_text=ready.redacted_normalized_text,
        normalized=normalized,
        normalized_query=normalized_query,
        query_tokens=query_tokens,
        max_snippet_codepoints=max_snippet_codepoints,
        max_snippet_utf8_bytes=max_snippet_utf8_bytes,
    )
    if snippet is None:
        return None
    record_id = ready.source_reference.record_id
    source_id_value = ready.source_reference.source_id if record_id is None else None
    citation = CitationV1(
        chunk_id=ready.chunk_id,
        content_digest_sha256=ready.content_digest_sha256,
        source_digest_sha256=ready.source_reference.source_digest_sha256,
        version=ready.source_reference.version,
        truth_class=ready.truth_class,
        record_type=ready.source_reference.record_type,
        record_id=record_id,
        source_id=source_id_value,
        field_selector=ready.field_selector,
        revalidation_token=ready.lifecycle.revalidation_token,
        source_cutoff_utc=ready.source_reference.source_cutoff_utc,
        snippet_digest_sha256=snippet.snippet_digest_sha256,
        snippet_start_codepoint=snippet.snippet_start_codepoint,
        snippet_end_codepoint=snippet.snippet_end_codepoint,
    )
    projection = EvidenceProjectionV1(
        citation=citation,
        truth_class=ready.truth_class,
        field_selector=ready.field_selector,
        sensitivity=sensitivity,
        content_snippet=snippet.content_snippet,
        snippet_start_codepoint=snippet.snippet_start_codepoint,
        snippet_end_codepoint=snippet.snippet_end_codepoint,
        snippet_digest_sha256=snippet.snippet_digest_sha256,
        projection_complete=snippet.projection_complete,
    )
    return citation, projection


@dataclass(frozen=True)
class RevalidatedCandidate:
    """One candidate that survived R7 use-time revalidation, with the
    freshly rebuilt (never the stale ranked-time) ready contract and
    sensitivity."""

    entry: dict[str, Any]
    ready_contract: RetrievalReadyV1
    sensitivity: str


def _facts_unchanged(ranked: RetrievalReadyV1, fresh: RetrievalReadyV1) -> bool:
    """R7 - compare every use-time drift class the SPEC names: source
    digest, version union, correction lineage (via the source_reference
    dump as a whole, which the version/correction fields are part of),
    lifecycle, parent-shift observation, retention/erasure assertion,
    content digest, chunk id, and revalidation token. A candidate whose
    freshly rebuilt contract differs in ANY of these facts is stale."""
    return (
        ranked.content_digest_sha256 == fresh.content_digest_sha256
        and ranked.chunk_id == fresh.chunk_id
        and ranked.source_reference.source_digest_sha256 == fresh.source_reference.source_digest_sha256
        and ranked.source_reference.version == fresh.source_reference.version
        and ranked.lifecycle == fresh.lifecycle
        and ranked.lifecycle.revalidation_token == fresh.lifecycle.revalidation_token
        and ranked.retention == fresh.retention
        and ranked.scope == fresh.scope
        and ranked.redacted_normalized_text == fresh.redacted_normalized_text
    )


def revalidate_knowledge_candidates(
    candidates: list[tuple[dict[str, Any], RetrievalReadyV1, str]],
    repository_root: Path,
    metadata: Any,
    now: Any,
) -> tuple[list[RevalidatedCandidate], int]:
    """R7 Project Knowledge use-time revalidation: reread the manifest,
    *rebuild* the full P3-C contract from current bytes, and compare every
    required fact (source/content digest, version, chunk id, revalidation
    token, sensitivity, owner/retention, lifecycle) against the originally
    ranked candidate. Any drift, a source-read failure, an unavailable
    manifest, or a manifest overflow removes/fails - never silently
    refreshed into the ranked request and never a reuse of the stale
    ranked-time contract.

    Returns the surviving candidates (carrying the freshly rebuilt contract)
    plus the number removed for staleness. ``now`` is the execution's single
    ``started_at_utc`` (never a second clock read here).
    """
    context = knowledge.ProjectKnowledgeExecutionContext(
        repository_root=repository_root, control_bundle=metadata.control_bundle,
        now=now, dedupe_context=metadata.dedupe_context,
        quarantine_route=metadata.quarantine_route, anchor_shift=None, anchor_principal_user_id="",
    )
    survivors: list[RevalidatedCandidate] = []
    stale_count = 0
    for entry, ranked_ready, ranked_sensitivity in candidates:
        try:
            fresh = knowledge.revalidate_entry(entry["id"], repository_root, context)
        except Exception:  # noqa: BLE001 - RR2-F2: any ordinary use-time
            # failure (manifest/path/overflow/P3-A/P3-C/unexpected) removes
            # this individual item as stale; only BaseException (process
            # termination, keyboard interrupt) is ever allowed to propagate.
            stale_count += 1
            continue
        if fresh is None:
            stale_count += 1
            continue
        fresh_entry, fresh_ready, fresh_sensitivity = fresh
        if fresh_entry.get("path") != entry.get("path"):
            stale_count += 1
            continue
        if not _facts_unchanged(ranked_ready, fresh_ready) or fresh_sensitivity != ranked_sensitivity:
            stale_count += 1
            continue
        survivors.append(
            RevalidatedCandidate(entry=fresh_entry, ready_contract=fresh_ready, sensitivity=fresh_sensitivity)
        )
    return survivors, stale_count


def reverify_final_assignments(
    *,
    shift_ids: tuple[UUID, ...],
    principal: Principal,
    assignment_scope: AssignmentScope,
    unit: Any,
) -> bool:
    """R7 - re-run active assignment for every selected shift immediately
    before returning, inside the same unit. Any single failure denies the
    entire response (whole-response assignment denial, never per-item)."""
    for shift_id in shift_ids:
        try:
            assignment_scope.require_shift(shift_id, principal, unit=unit)
        except OperationalResourceNotFound:
            return False
    return True


@dataclass
class ProjectionAssembly:
    """R8 result: projections plus their canonical dumps and the count of
    whole projections omitted for source-span or aggregate-budget reasons."""

    projections: list[EvidenceProjectionV1] = field(default_factory=list)
    citation_dumps: list[dict[str, Any]] = field(default_factory=list)
    projection_dumps: list[dict[str, Any]] = field(default_factory=list)
    budget_omitted: int = 0


def assemble_projections(
    survivors: list[RevalidatedCandidate],
    *,
    normalized_query: str,
    query_tokens: tuple[str, ...],
    max_projection_records: int,
    max_snippet_codepoints: int,
    max_snippet_utf8_bytes: int,
    max_serialized_utf8_bytes: int,
    max_estimated_input_tokens: int,
) -> ProjectionAssembly:
    """R8 - build citation/projection for up to ``max_projection_records``
    revalidated candidates, applying the already-``min(server, client)``-
    resolved ``max_snippet_codepoints``/``max_snippet_utf8_bytes`` ceilings
    and the candidate's real P3-A sensitivity (never a hardcoded literal),
    then trim the aggregate serialized-byte/token-estimate budget by
    removing the lowest-ranked whole projection until both pass.

    RR1-F5: this scans the COMPLETE deterministic ``survivors`` window (rank
    order preserved by the caller's list order) - never a pre-slice. A
    survivor that cannot fit under the applied per-snippet ceilings is
    skipped (never force-fitted) and the scan continues past it in rank
    order, so a later-ranked survivor that WOULD fit is never skipped just
    because an earlier one didn't. Scanning stops once
    ``max_projection_records`` projections have been emitted or the window
    is exhausted."""
    assembly = ProjectionAssembly()
    for candidate in survivors:
        if len(assembly.projections) >= max_projection_records:
            break
        built = build_citation_and_projection(
            candidate.ready_contract, normalized_query, query_tokens,
            max_snippet_codepoints=max_snippet_codepoints, max_snippet_utf8_bytes=max_snippet_utf8_bytes,
            sensitivity=candidate.sensitivity,
        )
        if built is None:
            assembly.budget_omitted += 1
            continue
        citation, projection = built
        assembly.projections.append(projection)
        assembly.citation_dumps.append({"citation": citation.model_dump(mode="python")})
        assembly.projection_dumps.append(projection.model_dump(mode="python"))

    while assembly.projections:
        serialized_bytes = serialized_projection_bytes(assembly.projection_dumps)
        estimated_tokens = estimate_tokens(serialized_bytes)
        if serialized_bytes <= max_serialized_utf8_bytes and estimated_tokens <= max_estimated_input_tokens:
            break
        assembly.projections.pop()
        assembly.citation_dumps.pop()
        assembly.projection_dumps.pop()
        assembly.budget_omitted += 1
    return assembly
