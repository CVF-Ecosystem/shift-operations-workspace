# Independent INTAKE Review — P4-C Integration Edge

- Tranche: `P4C-INTEGRATION-EDGE-2026-08-23`
- Reviewed phase: `INTAKE` only
- Reviewer role: `REVIEWER` (independent from `INTAKE_AUTHOR`)
- Risk ceiling: `R2`
- Review date: `2026-08-23`
- Disposition: `INTAKE_REVIEW_CHANGES_REQUIRED`

## Review boundary and evidence

The review compared
`docs/decisions/INTAKE_2026-08-23_P4C_INTEGRATION_EDGE.md` with the canonical
continuity and predecessor handoff, roadmap P4-C/P4-D/P4-E boundaries, channel
and trust-boundary documents, module registry/catalog, the actual
`apps/integration-edge` and `packages/channel-sdk` source, the R2/live-evidence
rules in `AGENTS.md`, and the Git dirty set.

Source inspection confirms the INTAKE's central implementation truth:

- the generic webhook reads original bytes, resolves a shared secret, verifies
  an unversioned SHA-256 HMAC, and records `X-Message-Id` in a process-local
  locked set before JSON parsing;
- accepted JSON is returned as `raw_payload`, but no raw envelope is durably
  preserved and no canonical-message or authenticated downstream ingress exists;
- `raw_payload`, `quarantine`, `rate_limit`, `routing`, `outbound`, and `health`
  remain README-only or empty scaffolds;
- the roadmap assigns the provider-neutral Integration Edge foundation to
  P4-C, concrete channel adapters to P4-D, and identity mapping/conversation
  routing to P4-E. The INTAKE preserves those ownership boundaries, including
  limiting P4-C routing to an ingress seam rather than claiming P4-E routing.

Read-only verification returned: focused HMAC test `1 passed`; session-state
guard `PASS`; catalog check `PASS`; invariant-family guard `PASS`; workspace
doctor `24 passed, 1` bounded legacy-catalog warning. No provider call was
required or authorized for this document/source review, and this review makes
no claim that CVF governed AI/agent behavior.

At review start, `HEAD == origin/main ==
0b89016df8483a4904d2c64b1a6560ccbc6b27ae`, staged paths were empty, and the
dirty set consisted of the five P4-C continuity/index modifications, the new
P4-C INTAKE and handoff, plus the pre-existing untracked operator assessment.
The assessment was not opened, edited, staged, committed, or otherwise used as
review evidence.

## Numbered findings

1. **P4C-INTAKE-REV-F1 — The live-governance evidence boundary is too
   narrow.** INTAKE decision 7 requires a real provider API call only for a
   claim that CVF governs "AI/agent behavior." The mandatory project rule is
   broader: any test, roadmap closure, release gate, demo proof, or public
   claim asserting the enumerated CVF governance behaviors (including risk,
   approval, DLP, bypass detection, output validation, routing, or audit) must
   use a real provider API call and record its request/response. P4-C is
   expected to make governance-significant assertions about untrusted ingress,
   refusal/quarantine, protected routing, and outbound prerequisites, so the
   current wording could incorrectly permit deterministic or mocked evidence
   to support a governed closure claim. Repair decision 7 to quote or faithfully
   cover the full Mandatory Governance Proof rule, while keeping any consuming
   call separately authorized and outside INTAKE. This is a phase-gate finding:
   DESIGN must not open until it is repaired and independently accepted.

## Waivers

1. `NONE`. No finding is waived or deferred.

## Disposition

`INTAKE_REVIEW_CHANGES_REQUIRED`.

All other reviewed INTAKE boundaries are accepted: current source truth, R2
classification, raw-envelope/dedupe/quarantine/rate-limit/attachment concerns,
provider-neutral outbound mechanics, non-authoritative canonical candidates,
P4-D/P4-E separation, invariant-family applicability checkpoint, and the
explicit prohibition on DESIGN/SPEC/WORK_ORDER/BUILD at this checkpoint.

## Bounded rereview — P4C-INTAKE-REV-F1

- Rereview role: `REVIEWER` (independent from `REPAIR_WORKER`)
- Rereview scope: repaired INTAKE decision 7 and governing live-evidence rules
- Rereview result: `P4C-INTAKE-REV-F1 CLOSED`
- Findings: `NONE`
- Waivers: `NONE`

The repaired decision 7 now applies to any test, roadmap closure, release gate,
demo proof, or public claim asserting CVF governance behavior and explicitly
includes risk classification, approval flow, phase gates, DLP filtering,
bypass detection, output validation, provider routing, and audit-trail updates.
It requires a separately authorized real provider API call with the sanitized
request/response recorded in the evidence artifact, rejects mock or static
evidence, and states that INTAKE authorizes no such call. This faithfully
closes the broader Mandatory Governance Proof boundary identified by F1 while
preserving the current no-call authority.

Fresh rehydration found canonical state, bootstrap projection, active handoff,
session memory, and docs index consistent at
`p4c_integration_edge_intake_repair_ready_for_rereview`. The session-state and
invariant-family guards passed; the workspace doctor returned 24 passes and
the retained bounded legacy-catalog warning. No provider call was needed for
this document-only rereview, which makes no governance-behavior proof claim.

## Final disposition

`INTAKE_REVIEW_PASS`.

The initial `INTAKE_REVIEW_CHANGES_REQUIRED` disposition above is retained as
review history and is superseded by this bounded rereview. F1 is closed without
waiver. DESIGN may proceed only through the next recorded governed role/phase
transition and within the operator's existing no-commit/no-push/no-provider/
no-credential/no-deployment boundary.
