# INTAKE - P3-C Retrieval-Ready Data Contract

- Tranche: `P3-C-RETRIEVAL-READY-DATA-CONTRACT-2026-08-06`
- Execution base: `c81bf7e9607464cc3456f343feed5796b1435987`
- Parent closure: P3-A Refinery `FREEZE / CLOSED_BOUNDED`
- Control-chain phase: `INTAKE`
- Risk: `R2`
- Status: `OPEN_FOR_INTAKE_REVIEW`
- Active roles: `ORCHESTRATOR`, `INTAKE_AUTHOR`
- Provider/product-API/POST calls: `0/0/0`
- Governance network: public-core freshness fetch by the mandatory workspace
  doctor only; no product/runtime network

## Request and roadmap position

The operator instructed the project to continue after the CVF workspace refresh
and the rejected governed-plan runner was isolated as evidence. The canonical
roadmap permits one fresh bounded P3-C INTAKE next.

P3-C defines the deterministic contract between an admitted P3-A context
candidate, canonical operational source records and a future governed retrieval
caller. It must make chunk identity, record linkage, scope, lifecycle state,
retention/erasure posture and provenance mechanically explicit before P4-A1 may
build retrieval behavior.

This tranche is not P3-B runtime gate wiring, P4-A1 retrieval, vector indexing,
RAG, provider integration, learning, application memory or production work.

## Current implementation truth

| Current fact | Verified source | Consequence for P3-C |
|---|---|---|
| P3-C requires canonical chunks/record links, tenant/shift/time scope, source version, correction/freeze state, retention/erasure marker and deterministic provenance. | `docs/implementation/EXECUTION_ROADMAP.md:428` | DESIGN must resolve each item; INTAKE cannot reduce the roadmap boundary silently. |
| P3-A `ContextCandidateV1` already carries redacted normalized text, sensitivity, topic labels, source identity/version/owner/link/fingerprint, rule versions and quality evidence. | `packages/refinery-bridge/src/refinery_bridge/output_models.py:84` | Prefer a bounded retrieval-ready envelope or adapter over duplicating the Refinery pipeline. |
| `Shift`, `OperationalEvent`, `Task`, `CustomerRequest`, `Incident` and `Handover` have different lifecycle and version shapes; `Message` and `Correction` do not expose a universal record version. | `packages/operations-domain/src/operations_domain/models.py:58`, `:73`, `:83`, `:103`, `:123`, `:147`, `:199`, `:246` | No universal source-version field may be guessed. DESIGN needs an exact per-record eligibility/version matrix. |
| Report snapshots already bind supported records to record type/id, conditional source version and canonical SHA-256 digest. | `packages/operations-domain/src/operations_domain/report_models.py:169` | Reuse the established digest/link semantics where compatible; do not claim the report manifest covers every P3-C source type. |
| Report lifecycle has `DRAFT`, `IN_REVIEW`, `APPROVED`, `FROZEN`; operational records use other state/status vocabularies. | `packages/operations-domain/src/operations_domain/report_models.py:158`; `packages/operations-domain/src/operations_domain/models.py:30`, `:46` | Retrieval eligibility must be record-type-specific and must not flatten unlike lifecycle states into one misleading enum. |
| Shift assignment explicitly has no tenant field and is only per-shift resource scope inside one workspace. | `packages/operations-domain/src/operations_domain/assignment_models.py:5`, `:28` | P3-C must not invent tenant isolation. Any tenant-required route must fail closed until an owning model exists. |
| `data_scope` can classify provider placement and report that INTERNAL requires minimization, but its placement assertion accepts no minimization receipt. | `packages/cvf-runtime/src/cvf_runtime/data_scope.py:48`, `:52` | A P3-C contract may carry evidence; it cannot claim minimization or provider placement was enforced. P3-B/P4 owns the runtime caller. |
| Current policy owns only raw-message retention at 365 days and quarantine retention at 30 days. | `packages/cvf-application-profile/data-policy.yaml:2-3` | There is no current retrieval-record retention or erasure authority. P3-C must expose an unresolved/blocked posture rather than invent policy. |

## Problem statement

P3-A proves that a local input can become a redacted, normalized, high-quality
context candidate. It does not prove that the candidate:

- represents a currently eligible canonical operational record;
- is scoped to an authorized workspace, shift or time window;
- still matches the current source version and digest;
- reflects a later correction or freeze transition;
- remains usable under retention or erasure obligations;
- has been admitted by a load-bearing `data_scope` caller;
- can be indexed or retrieved safely.

Without a typed boundary, future retrieval could return stale, cross-scope,
corrected, erased or non-canonical material while preserving a superficially
valid P3-A receipt.

## Proposed bounded objective

Design a versioned, deterministic, local retrieval-ready contract that:

1. binds each chunk to one admitted P3-A candidate and one explicit canonical
   record reference or a typed non-record source class;
2. defines deterministic chunk identity, ordering, canonical byte encoding and
   digest without semantic summarization or provider output;
3. carries explicit workspace/shift/time scope and fails closed when required
   tenant scope is not modeled;
4. binds source type, record identity, the source's real version semantics and
   canonical digest without fabricating a universal version;
5. records correction, source-state, parent-shift and freeze observations with
   a clear staleness/revalidation contract;
6. carries retention and erasure disposition from an owning policy/source and
   rejects admission when that disposition is missing, expired or erased;
7. preserves deterministic provenance back to P3-A receipts, source linkage and
   all contract/rule versions;
8. produces only a retrieval-ready value or a typed non-admission result.

## Hard boundaries

This INTAKE authorizes no implementation. P3-C must not:

- query, rank, search, embed, vectorize, index or persist retrieval material;
- invoke a provider, LLM, network, API, POST, browser or external service;
- implement P3-B, P4-A1, P4-A2, learning or application memory;
- create a tenant model, infer tenant identity or claim tenant isolation;
- treat per-shift assignment as tenant authorization or provider `data_scope`;
- claim minimization, DLP, placement or outbound-provider governance is
  load-bearing;
- own raw-source, quarantine, retrieval retention or erasure policy without an
  existing canonical owner;
- mutate source records, correct operational truth, freeze a shift or consume
  an approval;
- use chat/provider-local memory as canonical source truth;
- reopen, merge or promote the rejected governed-plan runner evidence branch.

## Cheap-alternative inventory

DESIGN must evaluate these options before opening a broader package or runtime
program:

| Alternative | Default disposition | Reason |
|---|---|---|
| Add a narrow retrieval-ready envelope/adapter around `ContextCandidateV1`. | `PREFER` | Reuses P3-A redaction, provenance and quality evidence without duplicating its pipeline. |
| Reuse compatible `ReportSourceRef` digest/version semantics and existing canonical record-digest helpers. | `PREFER_WITH_SOURCE_MATRIX` | Existing evidence is strong but does not cover every source type or lifecycle shape. |
| Represent current scope as explicit single-workspace plus shift/time bounds; mark tenant scope `NOT_MODELED`. | `PREFER` | Truthful to current source and fail-closed for future tenant-required use. |
| Carry retention/erasure status supplied by an upstream owner and reject unknown status. | `PREFER` | Avoids building a second policy or deletion engine in P3-C. |
| Define deterministic whole-record or field-bound chunks before arbitrary text splitting. | `EVALUATE_FIRST` | Smaller surface and easier digest/revalidation proof. |
| Add a vector database, retrieval service, index store or background sync job. | `REJECT_IN_P3C` | This is P4-A1/runtime work and creates cost before the contract is stable. |
| Create a new tenant/authorization subsystem. | `REJECT_IN_P3C` | No current source owner or roadmap authority. |
| Expand P3-C into P3-B runtime placement enforcement. | `REJECT_IN_P3C` | Different owner, caller and evidence class. |

## Decisions required before DESIGN closes

1. **Contract owner and dependency direction:** choose the smallest owning
   package/surface and prove it does not make `operations-domain` import an app,
   ledger, runtime or provider layer.
2. **Source eligibility matrix:** enumerate admitted source types and the exact
   lifecycle states eligible for chunk creation; explicitly disposition
   `Message`, `Correction`, `CustomerRequest`, `Report` and non-record P3-A
   sources rather than assuming uniform behavior.
3. **Record link and source version:** define record type/id, real version or a
   typed unversioned form, canonical digest, source cutoff and stale-source
   behavior for each eligible type.
4. **Chunk canonicalization:** define input fields, deterministic boundaries,
   stable chunk id, order, UTF-8/canonical JSON preimage, digest algorithm and
   collision behavior. No semantic rewrite or summarization is allowed.
5. **Scope model:** define workspace, optional shift and time-window fields;
   define `TENANT_NOT_MODELED` behavior and prove tenant-required admission is
   impossible rather than silently broad.
6. **Correction/freeze/revalidation:** define how corrected records, correction
   links, record state, parent-shift version/status and report freeze affect
   admission, invalidation and revalidation.
7. **Retention/erasure:** name the owning source for every marker, vocabulary,
   effective/expiry timestamps and fail-closed rules. If no owner exists, keep
   admission blocked and return the missing-owner reason.
8. **Provenance chain:** bind the retrieval-ready value to P3-A candidate and
   source fingerprints, stage/rule versions, source record digest and contract
   version without copying raw sensitive input.
9. **Data-scope boundary:** define what evidence P3-C carries versus what only a
   later load-bearing caller may decide. A refinery receipt is not automatically
   minimization-complete or provider-placement approval.
10. **Non-admission outcomes and evolution:** define typed reasons for stale,
    unsupported, erased, expired, scope-missing and policy-owner-missing input;
    define additive/breaking schema evolution without silent fallback.

## Acceptance criteria for this INTAKE

INTAKE is acceptable only if independent review confirms all of the following:

- the objective is contract-only, deterministic, local and non-truth-owning;
- the current source inventory and the absence of tenant/retention owners are
  represented accurately;
- the ten DESIGN decisions cover the complete roadmap boundary;
- cheap alternatives are evaluated before new runtime/package surfaces;
- P3-B, P4-A1, P4-A2, providers, retrieval and persistence remain parked;
- no DESIGN, SPEC, WORK_ORDER or BUILD authority is inferred;
- the runner evidence branch remains outside this tranche;
- no live-provider evidence is claimed or needed for this INTAKE.

## Governance cost and latency controls

- One consolidated INTAKE review must report all foreseeable boundary/source
  findings in a single pass.
- Findings must identify a new root cause or dependency, not restate an already
  accepted concern with different wording.
- Same-scope repairs remain under the same INTAKE-review authority.
- At repair round three without an independent new root cause, stop with
  `REVIEW_COST_ESCALATION_REQUIRED` and park low-value branches.
- DESIGN should prefer one ADR and one independent review; amendments require a
  real changed boundary, source fact or unresolved correctness defect.
- No provider quota, live-test budget or implementation test matrix is opened
  before DESIGN is accepted.

## Risk and evidence posture

`R2` is retained because the future contract controls the eligibility and scope
of sensitive operational material before retrieval. This local INTAKE changes
no runtime behavior and needs no provider call. Any later claim that CVF gates
retrieval or outbound AI context requires a separate approved live-proof plan
and real provider evidence.

## Stop conditions

Stop and return to the orchestrator if review finds any of these conditions:

- an eligible source type has no canonical identity/digest/version semantics;
- tenant isolation is required but still not modeled by an owning source;
- retrieval admission requires retention/erasure authority that has no owner;
- P3-C cannot avoid duplicating P3-A source-of-truth or redaction behavior;
- the proposal requires runtime retrieval, persistence, provider or network
  behavior to make the contract meaningful;
- continuity or evidence-branch isolation drifts.

These are bounded DESIGN blockers, not permission to widen the tranche.

## Independent review contract

The next role is `INDEPENDENT_INTAKE_REVIEWER`. Review this artifact against the
cited current source and canonical roadmap. Preserve disagreements and return
exactly one disposition:

- `INTAKE_REVIEW_PASS`
- `INTAKE_REVIEW_CHANGES_REQUIRED`
- `INTAKE_BLOCKED_SOURCE_OR_OWNER`

The reviewer may read local source and run read-only checks. The reviewer may
not design, implement, call providers/network, stage, commit, push, merge the
evidence branch or infer later-phase authority.

## Claim boundary

This artifact only bounds P3-C INTAKE. It does not prove that any retrieval-ready
contract exists, that source records are eligible, that retention/erasure is
enforced, that tenant isolation exists, that `data_scope` is load-bearing or
that retrieval/RAG/provider behavior is implemented.

## Next governed move

Obtain one consolidated independent INTAKE review. Only
`INTAKE_REVIEW_PASS` may transfer the bounded ten-decision packet to
`DESIGN_AUTHOR`. No DESIGN drafting, source change, provider/helper/network/
POST call, staging, commit of later-phase artifacts or BUILD is authorized by
this INTAKE alone.
