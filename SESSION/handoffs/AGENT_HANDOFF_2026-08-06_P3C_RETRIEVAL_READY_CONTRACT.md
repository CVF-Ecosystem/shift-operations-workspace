# Agent Handoff - P3-C Retrieval-Ready Data Contract

- Tranche: `P3-C-RETRIEVAL-READY-DATA-CONTRACT-2026-08-06`
- Execution base: `c81bf7e9607464cc3456f343feed5796b1435987`
- Risk: `R2`
- Current phase: `INTAKE`
- Status: `INTAKE_REVIEW_PENDING`
- Active role: `INDEPENDENT_INTAKE_REVIEWER`

## Startup acknowledgment

Startup acknowledged: current mode=`p3c_intake_review_pending`; active
handoff=`AGENT_HANDOFF_2026-08-06_P3C_RETRIEVAL_READY_CONTRACT.md`; next
allowed move=one consolidated independent review of the P3-C INTAKE; parked
checkpoint=`P3C_INTAKE_REVIEW_PENDING_NO_DESIGN_OR_BUILD`.

The workspace doctor passed with 24 checks and one bounded legacy-catalog
warning. Project `main` and `origin/main` were both at `c81bf7e` before this
INTAKE tranche began. The hidden public core is clean and pinned at
`9b039ea6b`.

## Completed in this tranche

The INTAKE author created:

`docs/decisions/INTAKE_2026-08-06_P3C_RETRIEVAL_READY_DATA_CONTRACT.md`

Frozen pre-review SHA-256:

`83ba292fe751b88e3be490e6e9dec687ef187d9cbf723ba15b41c0367fe1c8c3`

The packet records current source truth, the bounded objective, hard
exclusions, cheap alternatives, ten DESIGN decisions, acceptance criteria,
governance-cost controls, stop conditions and the independent-review contract.

## Material source findings

- P3-A already emits a redacted deterministic `ContextCandidateV1`; P3-C
  should adapt it rather than duplicate Refinery behavior.
- Operational source types do not share one version or lifecycle shape.
- Current assignment scope is per-shift in one workspace and explicitly has no
  tenant model.
- Current policy owns raw-message and quarantine retention only; it does not
  own retrieval-record retention or erasure.
- `data_scope` does not accept minimization evidence and has no load-bearing AI
  caller. P3-C may carry evidence but cannot claim placement enforcement.

## Authority and parked lanes

Current authority is documentation-only INTAKE review. It permits local source
reads and read-only checks. It grants no DESIGN drafting, SPEC, WORK_ORDER,
BUILD, provider/helper/network/POST call, retrieval, persistence, vector/index,
P3-B, P4, staging, commit by the reviewer or public/deployment action.

The rejected governed-plan runner remains isolated on local evidence-only
branch `evidence/governed-plan-runner-rejected-20260804` at `99789c0`. It is
not part of P3-C and must not be merged or promoted.

## Reviewer return contract

Review the INTAKE against its cited current source and the canonical roadmap.
Return one consolidated finding set and exactly one disposition:

- `INTAKE_REVIEW_PASS`
- `INTAKE_REVIEW_CHANGES_REQUIRED`
- `INTAKE_BLOCKED_SOURCE_OR_OWNER`

Preserve disagreements. Same-scope repairs do not need a new operator
checkpoint. At repair round three without a new independent root cause, stop
with `REVIEW_COST_ESCALATION_REQUIRED`.

## Next governed move

Obtain the independent INTAKE review. Only `INTAKE_REVIEW_PASS` may transfer
the ten bounded decisions to `DESIGN_AUTHOR`. No later-phase authority carries
forward.

## INTAKE review return - 2026-08-06

The corrected independent review targeted the exact project repository,
commit `072624d0ed49db1fdd8412d7d0cda40939b391e7` and frozen INTAKE SHA-256
`83ba292fe751b88e3be490e6e9dec687ef187d9cbf723ba15b41c0367fe1c8c3`.

Disposition: `INTAKE_REVIEW_PASS`. Findings: `NONE`. Waivers: `NONE`.

The earlier wrong-repository `INTAKE_BLOCKED_SOURCE_OR_OWNER` return is invalid
surface evidence and does not block P3-C. The authoritative review record is
`docs/decisions/P3C_RETRIEVAL_READY_DATA_CONTRACT_INTAKE_REVIEW.md`.

Role transition: `INDEPENDENT_INTAKE_REVIEWER` to `DESIGN_AUTHOR`.

Next move: resolve all ten accepted decisions in one bounded ADR and stop for
independent DESIGN review. No SPEC, WORK_ORDER, BUILD, provider/helper/product-
network/POST call or retrieval authority exists.

## Claim boundary

P3-C is not designed or built. No retrieval-ready schema, tenant isolation,
retention/erasure enforcement, load-bearing data-scope control, retrieval,
RAG, provider behavior or production readiness is claimed.
