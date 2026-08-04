# Project Context

This document is advisory orientation. `IMPLEMENTATION_STATUS.json`, the
machine module registry, and the execution roadmap remain authoritative.

## Current bounded context

Shift Operations Workspace is a modular operations application organized
around shift records, messages, events, tasks, customer requests, incidents,
handovers, reports, approvals, corrections, and audit evidence. The module
registry distinguishes real runtime behavior from partial, contract-only, and
stub surfaces; those labels must not be rounded up into production readiness.

Phase 1 is complete under its reviewed local/disposable infrastructure
boundary. Phase 2 is closed bounded for the reviewed start-to-freeze lineage.
The Project Operations Skill and Project Knowledge Pack are closed bounded.
P3-A currently has a deterministic local Refinery
`BUILD_CANDIDATE_PENDING_INDEPENDENT_REVIEW`; this is not P3-A closure and
does not complete Phase 3. The candidate has no runtime application caller and
does not prove provider behavior, remote ingest, persistence, `data_scope`
enforcement, retrieval, RAG, learning, production readiness, or confirmed
truth. Those capabilities remain later governed work in the recorded business
sequence.

Plans state intent. Implementation status, source, tests, and independent
review evidence determine implemented truth. A future reader must re-open the
canonical files instead of treating this summary as fresh continuity.

Sources: `IMPLEMENTATION_STATUS.json`; `docs/catalog/MODULE_REGISTRY.json`; `docs/implementation/EXECUTION_ROADMAP.md`
