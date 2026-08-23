# DESIGN — Cross-Agent Invariant Learning

- Tranche: `CROSS-AGENT-INVARIANT-LEARNING-2026-08-22`
- Date: `2026-08-22`
- Phase: `DESIGN`
- Risk: `R2`
- Status: `DESIGN_REVIEW_PASS`
- Authority: operator-granted DESIGN only after independent INTAKE PASS
- SPEC/WORK_ORDER/BUILD/provider/network/install/database/commit/push/deployment: `NONE`

## 1. Decision summary

Adopt a contract-first invariant-family system whose canonical semantic owner is
a machine-readable matrix written independently from the implementation under
test. A repository validator checks matrix/registry/ownership structure; a
reusable conformance helper derives positive and one-field mutation cases from
that matrix and applies them to real emitter and validator adapters supplied by
each applicable tranche.

`AGENTS.md`, the existing `operate-shift-workspace` skill, Work Orders and
review checklists will point to this same versioned standard. They will not copy
the invariant rules. Project Knowledge will route the standard as advisory
context, while the repository guard and tests remain the executable proof.

This DESIGN does not reopen P4-B and does not claim that prose can guarantee
identical behavior by every future agent.

## 2. Applicability boundary

The mechanism is mandatory for a new or materially changed R2/R3 tranche when
at least one trigger applies:

1. two or more terminal outcomes share a receipt/model contract;
2. an outcome changes required, forbidden or conditional fields;
3. counters or facts have outcome-dependent exact relations;
4. the same contract is represented by two or more validation surfaces, such
   as Pydantic plus JSON Schema;
5. prompt/schema, contract/fixture or emitter/receipt artifacts must remain
   coupled; or
6. a prior independent finding exposed an adjacent member of an invariant
   family.

The SPEC author must declare either a registered invariant-family id or a
reviewable `NOT_APPLICABLE` rationale. R0/R1 work and R2/R3 work without a
trigger are not forced to create empty matrices. Existing legacy tranches are
not retrofitted merely by installing the mechanism; registration becomes
mandatory only when their triggered contract surface is materially changed.

## 3. Canonical ownership and serialization

### 3.1 Normative layers

The architecture has four layers with non-overlapping authority:

- `docs/cvf/INVARIANT_FAMILY_STANDARD.md`: human-readable semantics,
  applicability and role procedure;
- `docs/cvf/invariants/invariant-family.schema.json`: closed JSON Schema for
  the matrix format;
- `docs/cvf/invariants/registry.json`: exact registered family ids, matrix
  paths, owners, applicability status and lifecycle;
- one JSON matrix per registered family: the sole semantic source for that
  family's outcomes, fields, relations, mutations and ownership bindings.

The guide and skill must not restate per-outcome field rules. A Work Order or
review artifact references the family id and canonical matrix digest rather
than copying its content.

### 3.2 Matrix shape

Every active matrix must declare at least:

- schema version, family id, contract owner role and risk;
- independently authored contract-source paths and canonical digest inputs;
- applicability triggers and declared representation surfaces;
- every terminal outcome and at least one named valid shape per outcome;
- required, forbidden and conditional fields;
- closed-field policy and value domains;
- exact cross-field relations, including counter equations;
- real-emitter adapter identity and validator adapter identities;
- minimum mutation operators and explicit justified exclusions;
- ownership bindings for coupled artifacts;
- evidence test paths and bounded claim text.

Unknown matrix/schema fields fail closed. Paths are normalized,
repository-relative, non-symlink regular files. Family ids and paths are
unique. Registry and matrix ids must agree exactly.

## 4. Independence from implementation

The matrix is authored from the approved DESIGN/SPEC contract, not exported
from Pydantic models, JSON Schema, service code, fixtures or provider output.
The conformance helper may consume real emitted shapes, but it must compare
them to matrix facts that were already stated independently.

The later SPEC must require digest ordering that proves this separation:

1. approved matrix digest is pinned before BUILD adapter code;
2. adapters expose real emitter/model/schema behavior without rewriting matrix
   expectations;
3. generated cases combine the pinned matrix with runtime outputs;
4. a matrix change invalidates the Work Order pin and requires review.

A test generator derived solely from the implementation is prohibited. A
handwritten positive fixture alone is insufficient when a real deterministic
emitter exists.

## 5. Positive shapes, parity and mutation closure

### 5.1 Positive coverage

For each terminal outcome, tests invoke the real deterministic service emitter
or receipt builder through a thin adapter. Every emitted positive shape must:

- match one and only one named matrix shape;
- be accepted by every declared representation validator;
- contain the exact required/forbidden/conditional facts and relations; and
- round-trip without silently dropping or inventing fields.

Synthetic shapes validate the reusable mechanics only; they cannot replace an
applicable tranche's real-emitter positives.

### 5.2 Paired parity

The same canonical corpus is submitted to every declared validator surface.
For each case, all validators must agree on accept/reject. A matrix with two or
more declared surfaces cannot waive parity. A single-surface family records
parity as not applicable and names the reason.

### 5.3 Minimum mutation basis

Around every valid shape, the helper produces at least:

- deletion of each required field;
- insertion of each forbidden field and one unknown field;
- discriminator replacement with each sibling outcome and one unknown value;
- legal-to-illegal value change for each bounded enum/type/value domain;
- null/value and present/absent flips for conditional fields;
- `-1`, `+1`, zero/nonzero and type mutations around exact numeric/counter
  relations where meaningful;
- one-side changes for each equality/digest/identity relation;
- recursive one-field mutations for governed nested objects; and
- one independent extra-field mutation at every closed object boundary.

Each mutation must alter exactly one semantic fact relative to its valid
parent. Pairwise or multi-field adversaries may be added but never substitute
for this basis. Any inapplicable operator needs a reason recorded in the
matrix and accepted by independent review.

## 6. Coupled-artifact ownership

Each semantic contract has exactly one canonical owner binding. Consumers must
use one of these declared strategies:

- direct import/object identity for code-owned constants;
- JSON Pointer/reference for schema-owned fragments;
- canonical digest reference for cross-language or documentation consumers;
- an adapter test that proves the consumer obtains the owner value unchanged.

Independent literal copies of a coupled prompt/schema or contract/fixture are
prohibited. The deterministic guard validates declared owner uniqueness,
consumer path uniqueness, path existence and allowed strategy. Conformance
tests prove identity/digest/reference behavior. The design intentionally does
not promise semantic duplicate detection across arbitrary source code; an
unregistered duplicate remains reviewable as a finding.

## 7. Shared Work Order and review protocol

A single template section, `Invariant-family proof`, is referenced by both
WORK_ORDER_AUTHOR and REVIEWER. It contains matrix id/digest, applicability
decision, adapter/test paths, mutation exclusions, exact commands and evidence
owner. The template does not copy matrix rules.

The worker must return a machine-readable conformance summary containing every
registered outcome, positive-shape id, mutation operator and validator parity
result. The reviewer independently recomputes the matrix digest, reruns the
same corpus, samples at least one raw emitted positive per outcome and verifies
that no matrix expectation was derived during BUILD.

Closure is family-based: all declared outcomes and the complete minimum
mutation basis must pass. Closing only reviewer-supplied probes is forbidden.
Repair authority continues under the existing Work Order only when objective,
matrix digest, paths, risk and external-effect class remain unchanged.

## 8. Deterministic guard and integration

The proposed validator is read-only, dependency-free and split into a reusable
contract module plus a small CLI. It validates:

- closed registry and matrix schemas, duplicate JSON keys and normalized paths;
- registry/matrix identity, lifecycle and exact file-set agreement;
- complete outcomes, shapes, field policies, relations and mutation basis;
- canonical-owner uniqueness and consumer binding structure;
- existence of declared adapters/evidence tests and matrix-digest pins; and
- stable, non-secret diagnostic codes and deterministic ordering.

It is added to `scripts/testing/validate_repository.py`, so local validation,
pre-commit and CI use the same fail-closed check. Unit tests use disposable
repositories and cover malformed/unknown fields, missing outcomes, missing
operators, duplicate ownership, traversal/symlink paths, stale digests,
unregistered matrices and stable diagnostics. Integration tests prove the
repository entry point fails on each representative mutation and passes the
committed synthetic conformance family.

The guard validates declarations and structure; pytest conformance tests prove
runtime emitter/validator behavior. Neither layer is presented as proof of the
other.

## 9. Repository routing

The existing `operate-shift-workspace` skill remains the procedural navigation
front door because it already covers phase, role, evidence and review. It gains
only a pointer to the invariant-family standard at SPEC/WORK_ORDER/REVIEW. It
does not become canonical semantic storage and no new provider-specific skill
is created.

`AGENTS.md` gains a compact mandatory trigger/pointer rule. Project Knowledge's
`GOVERNANCE_BOUNDARIES.md` cites the standard and is repinned through the
existing manifest. `docs/INDEX.md` routes humans to the guide, schema and
registry. Catalog/status/roadmap/continuity are synchronized only as required
by their existing contracts.

## 10. Rollout and legacy waivers

Initial rollout mode is `NEW_OR_MATERIALLY_CHANGED_TRIGGERED_FAMILIES`. The
committed synthetic family proves the mechanism without changing historical
P4-B runtime truth. P4-B is historical motivation only; its settled receipts
and review remain untouched.

A legacy waiver is registry-scoped, temporary and fail-closed. It must name the
family, owner, exact missing obligation, reason, expiry or removal trigger and
independent approval artifact. A waiver cannot suppress malformed JSON,
unknown fields, path safety, duplicate ownership or stale digest failures.
Waivers cannot be created by IMPLEMENTATION_WORKER or accepted silently.

## 11. Evidence and live-provider boundary

BUILD mechanics are deterministic and require zero provider/network calls.
They may prove only matrix parsing, repository guarding, test generation,
adapter parity and canonical binding.

If REVIEW/FREEZE claims that a real AI agent consumed the repository learning
and followed it, a separately authorized bounded live checkpoint is required.
That checkpoint must use the stable runner/runtime, send only sanitized public
contract material, run zero-call refusal/preflight cases first, make at most
one admitted provider call, retain failed lineage and avoid secrets. Its claim
is limited to that exact provider/run; it cannot prove universal future-agent
behavior. The tranche may instead close without a live call using the narrower
claim that repository-native guidance and deterministic checks were installed
and tested, not that agent behavior was governed.

## 12. Alternatives considered

1. **AGENTS prose only — rejected.** Easy to distribute but cannot detect
   missing outcomes, parity drift or incomplete mutation coverage.
2. **New provider-specific skill or prompt memory — rejected.** Violates
   provider neutrality and makes availability/session state the learning
   carrier.
3. **Generate contract and tests from implementation — rejected.** Produces a
   self-confirming system that preserves the same defect in every surface.
4. **Retrofit every historical tranche immediately — rejected.** Large,
   irrelevant scope and a high waiver burden; rollout is trigger-based.
5. **Chosen: independent matrix + registry + guard + conformance helper.** It
   separates intended truth, structural enforcement and runtime evidence while
   keeping all agents on one repository-native version.

## 13. Proposed artifact classes for later SPEC/Work Order

The later SPEC may allocate exact paths only within these classes:

- this tranche's DESIGN/SPEC/Work Order/review/return artifacts;
- `AGENTS.md` and the existing `skills/operate-shift-workspace/SKILL.md`;
- one CVF standard guide, one schema, one registry and one synthetic matrix;
- one reusable invariant contract module and one CLI guard;
- repository-validator integration plus focused unit/integration tests;
- one shared Work Order/reviewer checklist template;
- Project Knowledge boundary text/manifest pin;
- required docs index, catalog, status, roadmap and continuity surfaces;
- optional bounded live runner/support/tests/receipt only after separate
  provider authority.

No application domain, P4-A/P4-A2/P4-A3/P4-B runtime, database, API/UI,
provider adapter/configuration or CVF Core path belongs in this tranche. The
SPEC must enumerate every path and respect executable/Markdown size limits;
the Work Order must set the exact ceiling with no wildcard or reserve path.

## 14. DESIGN acceptance questions

Independent DESIGN review must confirm:

1. canonical ownership is singular and matrix semantics are not duplicated;
2. emitter positives remain independent from the contract matrix;
3. the mutation basis closes adjacent invariant-family members;
4. parity semantics cover both acceptance and rejection;
5. applicability and rollout do not over-apply to irrelevant/legacy work;
6. guard claims stop at structural proof and do not overstate duplicate
   detection or universal agent behavior;
7. skill/AGENTS/Knowledge routing uses pointers rather than copied rules;
8. later path/evidence/independence/live boundaries are sufficient for R2.

## 15. Stop condition

Independent DESIGN review passed with findings/waivers `NONE/NONE`. Stop at
`DESIGN_REVIEW_PASS_AWAITING_SPEC_AUTHORITY`. SPEC, WORK_ORDER and BUILD remain
unauthorized without fresh authority.

---

## Amendment 1 — validation dependency boundary (2026-08-23)

- Amendment authority: explicit operator approval after completion rereview
  round 1 finding `F6-R1`.
- Risk/objective/external-effect class: unchanged (`R2`, deterministic
  repository mechanics, zero provider/network/install/database/commit/push/
  deployment).
- Implementation union: unchanged exact-27; reviewer path 28 remains
  reviewer-owned; no path 29.
- Amendment author role: `AMENDMENT_AUTHOR`.

DESIGN section 8's phrase "dependency-free" is superseded only for the JSON
Schema validation dependency boundary. The deterministic guard may depend on
the repository-declared `jsonschema` package already present in the stable
runtime to execute Draft 2020-12 validation. It must not install, upgrade,
substitute, download or dynamically acquire that dependency during governed
work. All guard code outside that declared validator dependency remains Python
standard-library code.

This correction preserves the original architectural intent: one closed Draft
2020-12 schema, Python-owned semantic checks, deterministic sanitized
diagnostics, no dynamic import of matrix-declared adapters, and zero external
effects. Availability of `jsonschema` is now an explicit preflight condition;
missing/incompatible availability fails closed rather than triggering install
or silently reducing validation.

SPEC v1.0 is unchanged: it already requires Draft 2020-12 schema validation
and does not claim the validator is dependency-free. The exact-27 path set,
matrix semantics, acceptance criteria and claim boundary are unchanged.
Independent Amendment 1 DESIGN review is required before the Work Order
amendment or repair round 2 proceeds.

---

## Amendment 2 — bounded artifact redistribution (2026-08-23)

The operator ratifies the repair-round-2 source/test split as the minimum
redistribution needed to keep executable files within repository size limits.
The implementation surface changes from exact-27 to exact-30 by adding only:

1. `scripts/invariant_family_ownership.py` — ownership semantics extracted
   from the contract module;
2. `tests/unit/test_invariant_family_contract_repair_round2.py` — paired
   contract/ownership adversarial coverage;
3. `tests/integration/test_invariant_family_repository_guard_repair_round2.py`
   — repository-guard adversarial coverage.

Their ratified raw SHA-256 values are, in order,
`9b0e0c1d667f41267ffdf654909aa9416bf8d05a5d18efb7253e6ad8f096ffaf`,
`5415b52d9b864fb0435f02ee957d203551302035eeeb69971d263d5d4a3741a0`,
and `fad94162154e85bff222fd6ef3cddf24b906a7563080378ed90366be44db97ce`.

This supersedes only the DESIGN's artifact-count assumption: the reusable
contract artifact class may be realized by a contract module plus an ownership
helper, and the previously approved unit/integration test classes may span the
two added test files. There is no new subsystem, runtime route or governance
surface. Objective, architecture, R2 ceiling, `jsonschema` boundary, matrix
authority, path-28 reviewer ownership, external effects and claim boundary are
unchanged. Path 31 is forbidden. Independent Amendment 2 DESIGN review and the
corresponding SPEC/Work Order amendments are required before repair resumes.
