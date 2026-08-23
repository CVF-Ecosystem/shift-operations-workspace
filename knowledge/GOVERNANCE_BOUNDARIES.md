# Governance Boundaries

This document is advisory. Agents and humans must read the cited governance
sources and current canonical continuity before material work.

## Operating boundary

Governed work follows `INTAKE → DESIGN → SPEC → WORK_ORDER → BUILD → REVIEW →
FREEZE`. That control chain describes how one bounded unit moves through gates;
it is distinct from the project's five-phase business roadmap. Risk is
classified before action, R2 requires human review, role transitions are
explicit, and exact Work Orders bound changed paths, evidence, stop conditions,
and commit ownership.

Canonical continuity lives under `SESSION/`. The compatibility state under
`CVF_SESSION/` is a mirror, not an independent authority. On session, tranche,
handoff, role, or context transitions, rehydrate the canonical state, active
handoff, session memory, implementation status, documentation index, and
roadmap. Conflicting continuity stops work rather than selecting a convenient
source.

Source and evidence must stay within classification, provenance, purpose, and
data-scope boundaries. INTERNAL data is not automatically eligible for an
external model; minimization and a separately authorized runtime gate remain
necessary. Provider output and chat history are not canonical operational
truth. Static validation and local chunk creation do not prove DLP, retrieval,
prompt behavior, governance enforcement, or production readiness.

Any claim that CVF controls AI or agent behavior needs fresh real-provider
evidence under an authorized call budget. Mock output is restricted to UI-only
claims. Secrets, credentials, raw provider payloads, production/customer data,
and RESTRICTED content are excluded from this pack. Corrections preserve
history; withdrawal, reclassification, or deletion follows explicit R2
authority and does not imply Git history erasure.

A new or materially changed R2/R3 contract surface follows
`docs/cvf/INVARIANT_FAMILY_STANDARD.md` as repository-native guidance. This
pack does not restate its per-outcome rules; executable truth remains in
`docs/cvf/invariants/`, `scripts/check_invariant_families.py`, and their
tests.

Sources: `AGENTS.md`; `.cvf/manifest.json`; `.cvf/policy.json`; `docs/cvf/CONTEXT_CONTROL.md`; `docs/cvf/EVIDENCE_AND_TRUTH.md`; `docs/cvf/PROVIDER_GOVERNANCE.md`; `docs/cvf/RISK_AND_APPROVAL.md`
