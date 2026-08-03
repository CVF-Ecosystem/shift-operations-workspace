# ADR — Project Knowledge Pack

- Tranche: `PROJECT-KNOWLEDGE-PACK-2026-08-03`
- Risk: `R2`
- Status: `DESIGN_RE_REVIEW_PASS`

## Decision 1 — Curated summaries with canonical citations

Create three concise knowledge documents under `knowledge/`:

- `PROJECT_CONTEXT.md`: bounded product/architecture/roadmap orientation;
- `OPERATIONS_GLOSSARY.md`: stable domain terms and ownership boundaries;
- `GOVERNANCE_BOUNDARIES.md`: continuity, phase, evidence and claim limits.

Each document is advisory context and cites current canonical repository paths.
The pack contains no copied active handoff, active next-move text, mutable
implementation inventory or provider-local memory.

Use this exact topic-to-authority map; list order never establishes authority:

- active continuity: `SESSION/ACTIVE_SESSION_STATE.json`, with the active
  handoff/memory/mirror required to agree or stop `BLOCKED_CONTINUITY_DRIFT`;
- implementation disposition: `IMPLEMENTATION_STATUS.json`;
- module inventory/status: `docs/catalog/MODULE_REGISTRY.json` (generated
  catalog is derived);
- business sequence: `docs/implementation/EXECUTION_ROADMAP.md`;
- governance contract/policy: `AGENTS.md`, `.cvf/manifest.json` and
  `.cvf/policy.json`, which must agree on overlapping required controls;
- domain terminology: named foundation/domain contract files cited per entry.

If a summary conflicts with its topic authority, or overlapping canonical
surfaces disagree, the document is ineligible and validation stops with a
classified conflict. No fallback silently chooses another source.

## Decision 2 — One machine provenance manifest

Add `knowledge/manifest.json` with an exact schema and one entry per curated
Markdown file. Every entry carries:

- stable id and relative path;
- owner role from exactly `ORCHESTRATOR`, `SPEC_AUTHOR` or
  `SESSION_SYNC_STEWARD`;
- `INTERNAL` classification;
- purpose and allowed consumer class;
- canonical source paths plus exact SHA-256 of each source's current bytes;
- reviewed date and refresh triggers;
- retention/correction policy.

It also records `eligibleForLocalIndex`; eligibility is derived fail-closed:
all pins, metadata, classification and conflict checks must pass before a file
may enter the disposable helper input. The manifest does not authorize access and does not replace `.cvf/manifest`,
policy, continuity, catalog, roadmap or domain records.

## Decision 3 — Freshness is event-triggered, not invented TTL

The pack becomes stale on any cited-source SHA-256 change, owner withdrawal, security
reclassification, continuity/bootstrap contract change or review finding.
Stale content is excluded from ingest output until refreshed and revalidated.
There is no arbitrary age-based truth guarantee. Git history supplies durable
repository history, not an erasure guarantee. Correction is a new reviewed
commit. Reclassification, withdrawal or deletion requires `ORCHESTRATOR`
authorization plus explicit human R2 acknowledgment; `SESSION_SYNC_STEWARD`
records the disposition. Sensitive-data remediation follows a separate
incident/secret-removal authorization and may require host-level history
remediation outside this tranche.

## Decision 4 — Generated index is disposable

Use the pinned public-core helper resolved from `.cvf/manifest.json` only for a
zero-network rehearsal. Build a disposable input directory containing exactly
the manifest-eligible curated files—never the repository `knowledge/` folder
and never `README.md`. Write `_index.json` inside the disposable root, require
exact equality between eligible manifest paths and index `sourceFile` values,
validate collection/chunk coverage and secret-like absence, then remove the
whole root and its output. Do not commit the helper output because it embeds an
absolute host path and wall-clock `generatedAt` value. POST/remote collection
creation is excluded. This also contains the upstream helper's current
ingest-all-Markdown filter behavior.

## Decision 5 — Deterministic local validator

Add `scripts/check_project_knowledge.py` and
`tests/unit/test_project_knowledge_pack.py`. The validator
checks exact manifest schema/types, unique ids/paths, allowlisted classification
and owners, source existence, path containment, source coverage, reviewed date,
refresh/correction/retention fields, source SHA-256 pins, derived eligibility,
Markdown size/substance, exact forbidden claim tokens, bounded secret-like
patterns with explicit test sentinels, and absence of committed/runtime
`_index.json` residue. Tests cover path traversal, source-pin drift,
unmanifested Markdown, stale exclusion, unknown classification/owner, each
secret sentinel, safe false-positive controls, exact index-set equality and
disposable cleanup. It makes no network call and writes nothing.

Static validation is local structural evidence only. It is not data
minimization, DLP enforcement or authorization for external/provider transfer.
Although curated entries are `INTERNAL`, policy requires minimization before
external AI; this tranche neither implements nor proves that control and keeps
all rehearsal content local.

## Decision 6 — Candidate BUILD and closure separation

Candidate BUILD is exactly these eight paths:

1. `knowledge/README.md`
2. `knowledge/PROJECT_CONTEXT.md`
3. `knowledge/OPERATIONS_GLOSSARY.md`
4. `knowledge/GOVERNANCE_BOUNDARIES.md`
5. `knowledge/manifest.json`
6. `scripts/check_project_knowledge.py`
7. `tests/unit/test_project_knowledge_pack.py`
8. `tests/integration/test_project_knowledge_ingest_rehearsal.py`

The unit host covers deterministic validator contracts; the integration host
constructs the exact disposable eligible input, invokes the pinned helper and
proves index-set equality/cleanup. Governance documents,
continuity, implementation status, roadmap and catalog are protected during
BUILD. After independent BUILD review, C4 truth synchronization is a separate
exact-path commit.

## Alternatives rejected

- Copy all docs into `knowledge/`: too large, stale and creates duplicate truth.
- Commit upstream `_index.json`: nonportable and nondeterministic.
- Build retrieval/RAG now: violates the parked sequence and Refinery/data-scope
  prerequisites.
- Use a provider to summarize sources: unnecessary for deterministic curated
  BUILD and would create new provenance/call-accounting risk.
- Claim upstream CVF runtime capability as downstream implementation truth:
  false boundary expansion.

## Claim boundary

This tranche may prove only that a reviewed, source-cited, classification-aware
project knowledge pack can be validated and transformed locally into disposable
chunks by the pinned public-core helper. It cannot prove remote ingest,
retrieval, context injection, provider/model behavior, Refinery enforcement,
production governance or readiness of later queue items.

## Next move

Independent DESIGN review. Only PASS permits SPEC authoring; no BUILD,
provider call, ingest POST, external write or core modification is authorized.
