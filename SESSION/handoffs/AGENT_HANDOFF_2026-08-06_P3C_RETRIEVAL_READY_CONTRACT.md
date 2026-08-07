# Agent Handoff - P3-C Retrieval-Ready Data Contract

- Tranche: `P3-C-RETRIEVAL-READY-DATA-CONTRACT-2026-08-06`
- Execution base: `c81bf7e9607464cc3456f343feed5796b1435987`
- Risk: `R2`
- Current phase: `SPEC`
- Status: `SPEC_REVIEW_PENDING`
- Active role: `INDEPENDENT_SPEC_REVIEWER`

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

## DESIGN author return - 2026-08-06

The DESIGN author created:

`docs/decisions/ADR_2026-08-06_P3C_RETRIEVAL_READY_DATA_CONTRACT.md`

Frozen pre-review SHA-256:

`288ebab12f64c036a23ef765c6230a48b2bff04d70ffd591529cad5757ff318b`

The ADR resolves all ten accepted decisions in one pass. It selects
`workspace-contracts/retrieval` as the existing owner surface; defines exact
canonical/advisory source eligibility and version forms; uses one deterministic
field-bound chunk per P3-A candidate; records no-tenant scope explicitly;
requires use-time lifecycle/correction/freeze revalidation; admits only active
owner-asserted retention; binds a closed provenance chain; leaves minimization
and placement not evaluated; and returns a strict ready/non-admission union.

No source, schema, runtime, test, provider/product-network/POST or retrieval
action was performed. The rejected runner branch remains isolated.

Role transition: `DESIGN_AUTHOR` to `INDEPENDENT_DESIGN_REVIEWER`.

Next move: one consolidated independent DESIGN review. Return exactly one of
`DESIGN_REVIEW_PASS`, `DESIGN_REVIEW_CHANGES_REQUIRED`, or
`DESIGN_BLOCKED_SOURCE_OR_OWNER`. Only PASS may transfer to `SPEC_AUTHOR`.
No SPEC drafting or BUILD authority exists.

## DESIGN review and R1 repair - 2026-08-07

Independent review of commit `85052cf` and ADR SHA-256 `288ebab1...318b`
returned `DESIGN_REVIEW_CHANGES_REQUIRED`, finding `P3C-DESIGN-F1`, waiver
`NONE`. The review record is:

`docs/decisions/P3C_RETRIEVAL_READY_DATA_CONTRACT_DESIGN_REVIEW.md`

F1 correctly found that schema-only `packages/workspace-contracts/` is not an
existing wired Python package. Same-scope R1 repairs Decision 1 and its direct
consequence text only:

- owner is now an explicit new sibling `packages/retrieval-contracts/`;
- it follows the existing package-local `pyproject.toml` and `src/` pattern;
- it receives an explicit root test `pythonpath` entry during future authorized
  BUILD;
- dependency direction is `retrieval-contracts` importing
  `refinery-bridge` and `operations-domain`;
- reverse imports and app/ledger/runtime/provider imports remain forbidden;
- schema-only `workspace-contracts` is not widened or reclassified.

Decisions 2-10 remain unchanged and passed review as written. Revised ADR
SHA-256:

`f7c78d3e2e3a6e1de462b64e2b906a0cbb7e35e9f2d521b3e528aba6b2ea05f2`

Next role: `INDEPENDENT_DESIGN_REREVIEWER`. Re-review F1 and regression-check
Decisions 2-10. Only `DESIGN_REVIEW_PASS` may open SPEC. No BUILD or call
authority exists.

## Claim boundary

P3-C is not designed or built. No retrieval-ready schema, tenant isolation,
retention/erasure enforcement, load-bearing data-scope control, retrieval,
RAG, provider behavior or production readiness is claimed.

## DESIGN R1 re-review return - 2026-08-07

Independent re-review targeted commit `6641d9419c38829b57fd5949b627287b526578f5`
and revised ADR SHA-256
`f7c78d3e2e3a6e1de462b64e2b906a0cbb7e35e9f2d521b3e528aba6b2ea05f2`.

Disposition: `DESIGN_REVIEW_PASS`. Findings: `NONE`. Waivers: `NONE`.

The authoritative re-review record is
`docs/decisions/P3C_RETRIEVAL_READY_DATA_CONTRACT_DESIGN_REREVIEW.md`.
`P3C-DESIGN-F1` is closed: the owner is an explicit new sibling
`packages/retrieval-contracts/` with one-way dependencies into
`refinery-bridge` and `operations-domain`; Decisions 2-10 remain unchanged.

Role transition: `INDEPENDENT_DESIGN_REREVIEWER` to `SPEC_AUTHOR`.

Next move: author one bounded testable SPEC, freeze it at a SHA-256 and stop
for independent SPEC review. No WORK_ORDER, BUILD, provider/helper/product-
network/POST call, retrieval, persistence or vector/index authority exists.

## SPEC author return - 2026-08-07

The SPEC author created:

`docs/specs/P3C_RETRIEVAL_READY_DATA_CONTRACT_SPEC.md`

Frozen pre-review SHA-256:

`cdb00667cf8f8fd16fa5e0dfd3cd07eb149ddac6938ed5e1db71d70abad53558`

The SPEC defines 23 normative requirements and 12 acceptance criteria. It
reuses the exact P3-A envelope/result/candidate classes, closes source/version/
projection/scope/lifecycle/retention/provenance schemas, defines independent
digest/chunk/revalidation hashing and uses a strict ready/non-admission union.

Source verification found current application digest helpers, but they live
under forbidden `workspace_api`. No public generic digest owner exists in the
two allowed dependency packages. The SPEC therefore requires canonical types
to return `SOURCE_DIGEST_OWNER_MISSING` unless a separately reviewed source
change adds an allowed owner; it does not invent a generic Pydantic digest.

Role transition: `SPEC_AUTHOR` to `INDEPENDENT_SPEC_REVIEWER`.

Next move: one consolidated independent SPEC review against exact commit and
hash. Return `SPEC_REVIEW_PASS`, `SPEC_REVIEW_CHANGES_REQUIRED`, or
`SPEC_BLOCKED_SOURCE_OR_OWNER`. Only PASS transfers to `WORK_ORDER_AUTHOR`.
No WORK_ORDER drafting, BUILD, provider/helper/product-network/POST call,
retrieval, persistence or vector/index authority exists.
