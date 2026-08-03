# INTAKE — Project Knowledge Pack

- Tranche: `PROJECT-KNOWLEDGE-PACK-2026-08-03`
- Parent: PROJECT-OPERATIONS-SKILL C4 `c4795559409ba6984b57a2e3f9fac559feeb167d`
- Risk: `R2`
- Status: `INTAKE_COMPLETE`
- Active role: `INTAKE_AUTHOR`

## Intent

Create a repository-owned, provider-neutral project knowledge pack that gives
future governed work concise project context with explicit source authority,
owner, provenance, classification, freshness, retention and correction rules.
The pack must point back to canonical repository truth and may never become a
second continuity, policy, implementation-status or domain-truth source.

## Current truth

- `knowledge/` contains only a bootstrap `README.md`.
- The portable manifest declares `knowledgePath: knowledge/`.
- The public CVF core contains read-only helper
  `scripts/ingest_cvf_downstream_knowledge.ps1`; the downstream repository has
  no same-named wrapper. The core helper creates a local `_index.json`, requires
  no external service, includes a wall-clock timestamp and absolute source
  folder, and instructs the operator to POST the result separately.
- This downstream application has no implemented retrieval/RAG runtime.
  `refinery-bridge` remains `contract-only`; retrieval-ready, governed
  retrieval, RAG and learning are later parked tranches.
- Current `knowledge/README.md` can be read as promising automatic retrieval
  and injection without distinguishing public-core capability from this
  project's implementation truth. That wording must be narrowed.

## Intake findings to resolve

1. `KPK-INTAKE-F1 AUTHORITY`: define an allowlisted canonical-source map and
   precedence rule; copied summaries must never outrank their cited sources.
2. `KPK-INTAKE-F2 PROVENANCE`: every curated document/chunk needs stable owner,
   source paths, classification and reviewed-at metadata.
3. `KPK-INTAKE-F3 FRESHNESS`: define refresh triggers, stale/expired behavior,
   correction/deletion path and retention without inventing unsupported TTLs.
4. `KPK-INTAKE-F4 PORTABILITY`: the upstream index helper emits host-specific
   path/time fields; generated `_index.json` must not become committed canonical
   truth or a reproducible-build claim.
5. `KPK-INTAKE-F5 SECURITY`: exclude secrets, credentials, raw provider
   payloads, production/customer data and RESTRICTED material; enforce
   classification-aware fail-closed validation before any ingest handoff.
6. `KPK-INTAKE-F6 CLAIM`: structural validation and local index generation do
   not prove retrieval, prompt injection, model behavior, Refinery enforcement
   or production governance. Any such future claim requires its own authorized
   runtime/live-provider evidence.

## In scope for DESIGN

- concise curated Markdown over already-reviewed project sources;
- one machine manifest for ownership/provenance/freshness/classification;
- deterministic repository validation and tests;
- zero-network rehearsal of the public-core index helper into a disposable
  output, followed by exact cleanup;
- bounded status/catalog/continuity closure only after reviewed BUILD.

## Excluded

- POSTing an index, creating a remote collection or external write;
- provider calls, retrieval/vector search, embeddings, RAG or context injection;
- Refinery implementation, data-scope runtime wiring or learning memory;
- copying secrets, customer/production data, raw messages or provider bodies;
- editing the read-only CVF core, installing a skill or claiming enforcement.

## Next governed move

DESIGN the minimal source/manifest/validator shape, index-artifact policy,
acceptance evidence and exact changed-set candidates. No BUILD or ingest POST is
authorized by this INTAKE.

