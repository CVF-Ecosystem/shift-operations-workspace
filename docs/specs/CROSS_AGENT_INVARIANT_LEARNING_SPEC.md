# SPEC — Cross-Agent Invariant Learning

- Tranche: `CROSS-AGENT-INVARIANT-LEARNING-2026-08-22`
- Date: `2026-08-23`
- Phase: `SPEC`
- Version: `1.0`
- Risk: `R2`
- Status: `SPEC_REVIEW_PASS`
- Parent DESIGN:
  `docs/decisions/DESIGN_2026-08-22_CROSS_AGENT_INVARIANT_LEARNING.md`
- Authority: operator-granted SPEC only after independent DESIGN PASS
- WORK_ORDER/BUILD/provider/network/install/database/commit/push/deployment:
  `NONE`

## 1. Intended result

Install one provider-neutral, repository-native contract for invariant-family
reasoning. Applicable future tranches must state terminal-outcome facts once,
exercise every valid emitted shape, compare every declared validator over one
shared corpus, mutate one semantic fact at a time, and prove coupled-artifact
ownership. Repository validation must fail closed on incomplete or drifted
declarations.

This SPEC defines intended behavior only. It does not claim the files below
exist or that P4-B has been retrofitted.

## 2. Requirements

### R1 — Applicability decision

The standard must require a registered invariant family for new or materially
changed R2/R3 work when any of these triggers is true:

1. multiple terminal outcomes share a receipt/model contract;
2. outcome controls required, forbidden or conditional fields;
3. exact counters or cross-field relations depend on outcome;
4. two or more validator/serialization surfaces represent the same contract;
5. prompt/schema, contract/fixture or emitter/receipt artifacts are coupled;
6. an independent finding exposed an adjacent member of the same family.

Otherwise the SPEC records `NOT_APPLICABLE` plus a reason. R0/R1 work and
untriggered R2/R3 work need no empty matrix. A legacy family becomes mandatory
only when its triggered surface is materially changed.

### R2 — Single canonical owner

For each active family, one JSON matrix is the sole semantic owner of outcomes,
valid shapes, field presence, value domains, relations, mutations and coupled
ownership. The standard, `AGENTS.md`, skill, templates, Work Orders, reviews
and Project Knowledge may point to a matrix id/digest but must not copy its
per-outcome rules.

### R3 — Closed matrix schema

`docs/cvf/invariants/invariant-family.schema.json` must be valid JSON Schema
Draft 2020-12. Every object level must set `additionalProperties: false` or the
equivalent closed rule. It must reject unknown fields, wrong types, empty ids,
exact duplicate list entries, missing required sections and malformed
repository-relative paths. Schema validation and the Python contract validator
must agree for the committed matrix plus every schema-expressible mutation in
R15. Semantic uniqueness such as two different objects carrying the same id is
enforced by the Python validator and tested separately; the SPEC does not claim
standard JSON Schema can express that cross-item identity rule.

### R4 — Closed registry

`docs/cvf/invariants/registry.json` must contain only the supported schema
version and an ordered family list. Every entry declares family id, matrix
path, owner role, risk, lifecycle, applicability mode and any waiver. The
registry and on-disk matrix set must agree exactly in both directions; ids and
paths are unique and registry/matrix ids match.

Only `ACTIVE` and `WAIVED_LEGACY` lifecycles are allowed initially. An active
entry cannot contain waiver fields. A waiver must name exact missing
obligations, reason, owner, independent approval artifact, expiry date or
removal trigger. Waivers cannot suppress JSON/schema/path/digest/duplicate-
ownership failures.

### R5 — Path and JSON safety

All JSON loads must reject duplicate keys. Declared paths must use `/`, be
repository-relative, normalized, contained in the repository and resolve to
non-symlink regular files. Absolute, drive-prefixed, traversal, empty-segment
and backslash paths fail closed. The guard does not infer BUILD authority from
Git tracking state; the exact Work Order/diff gate separately governs whether a
new or untracked path is authorized.

The validator must never dynamically import or execute a path/symbol declared
by a matrix. Adapter identities are metadata checked by separately authorized
tests, not executable configuration.

### R6 — Matrix metadata and source independence

Every matrix must declare:

- `schemaVersion`, `familyId`, `title`, `ownerRole`, `risk` and lifecycle;
- applicability triggers;
- independently authored contract-source paths and their canonical SHA-256;
- representation surfaces and parity mode;
- terminal outcomes and valid shapes;
- mutation policy and justified exclusions;
- coupled-artifact ownership bindings;
- emitter adapter identity, evidence test paths and bounded claim.

Contract-source pins use UTF-8 universal-newline canonicalization so LF/CRLF
checkouts hash identically while any semantic text change changes the digest.
The matrix must not name implementation output as its only contract source.

For this bootstrap tranche, the approved SPEC supplies the independent
synthetic semantics in R14; the later worker materializes them into the first
matrix. Every future family must have its matrix digest pinned by its reviewed
Work Order before adapter implementation changes begin.

### R7 — Terminal outcome completeness

Every active matrix contains at least two terminal outcomes and at least one
named valid shape per outcome. Outcome ids and shape ids are unique. Each
outcome declares:

- exact required and forbidden field sets;
- conditional field rules;
- allowed value/type domains;
- closed-object boundaries;
- exact equality, digest, identity and counter relations; and
- the expected valid/invalid disposition of generated cases.

Required and forbidden fields cannot overlap. Every conditional field must be
owned by exactly one condition. Every referenced field/relation target must
exist in the declared shape vocabulary.

### R8 — Real-emitter positive contract

An applicable runtime family must invoke its real deterministic service
emitter or receipt builder through a fixed test adapter. Every emitted terminal
shape must match exactly one matrix shape, pass every declared validator,
retain all governed fields on round-trip and satisfy all matrix relations.

Handwritten positive fixtures alone are insufficient when a deterministic real
emitter exists. Provider output is not an acceptable contract source. The
bootstrap synthetic emitter is evidence only for the generic mechanics and
does not stand in for P4-B or another runtime family.

### R9 — Validator parity

The conformance helper submits the identical canonical positive and mutation
corpus to every declared validator. Every surface must agree on accept/reject
for every case. Both false acceptance and false rejection are failures.

A family with one validation surface declares parity `NOT_APPLICABLE` and a
non-empty reason. A family declaring two or more surfaces cannot waive parity.
The bootstrap synthetic family may use one surface because it proves mechanics,
not runtime model/schema parity; test doubles must still prove that the helper
detects both directions of disagreement.

### R10 — Minimum one-fact mutation basis

For every valid shape, the helper must deterministically generate all
applicable mutations below, each changing exactly one semantic fact:

1. delete each required field;
2. add each forbidden field;
3. add one unknown field at every closed object boundary;
4. replace the outcome discriminator with every sibling and one unknown value;
5. replace each bounded enum/type/value with at least one illegal value;
6. flip present/absent and null/value for conditional fields;
7. apply `-1`, `+1`, zero/nonzero and wrong-type variants to exact numeric or
   counter relations where meaningful;
8. change one side only of every equality/digest/identity relation;
9. recurse into governed nested objects.

An operator may be excluded only when structurally inapplicable; the matrix
records the operator, shape, reason and independent-review requirement.
Multi-field adversaries may supplement but never replace the minimum basis.

### R11 — Coupled-artifact ownership

Every ownership binding declares one canonical owner path plus optional JSON
Pointer/symbol, and one or more consumers using exactly one strategy:
`DIRECT_IDENTITY`, `JSON_REFERENCE`, `CANONICAL_DIGEST` or
`ADAPTER_ASSERTION`.

The guard must reject duplicate owners for the same binding id, duplicate
consumer paths, owner-as-consumer, missing paths, unsupported strategy and
stale canonical digest. Runtime tests prove the declared identity/reference/
digest behavior. The mechanism does not claim to discover an undeclared
semantic duplicate anywhere in arbitrary source.

### R12 — Conformance result

The reusable helper returns a deterministic, JSON-serializable summary with:

- family/matrix id and canonical digest;
- every outcome and positive shape id;
- counts and ids for generated mutations by operator;
- each validator's accept/reject result;
- parity result;
- ownership-binding result; and
- overall `PASS` only when the whole declared family passes.

Ordering is stable. The summary contains no raw secret, provider payload or
arbitrary source content. Tests write it only to a disposable directory and
remove it on success and failure; no repository runtime receipt is retained.

### R13 — Deterministic repository guard

`scripts/check_invariant_families.py` is a read-only CLI over a reusable
contract module. With no arguments it validates the repository registry and
matrices. `--json` emits sanitized deterministic JSON. Unknown arguments fail.
The guard performs no provider/network call, credential read, install,
database action or dynamic import.

`scripts/testing/validate_repository.py` must invoke it with the current Python
executable and fail when it returns nonzero. Therefore `make validate`, CI and
the existing pre-commit pytest/repository sequence share the same guard without
duplicating its rules.

### R14 — Bootstrap synthetic family

The committed synthetic matrix must define one closed top-level receipt with
these independently specified outcomes:

- `ACCEPTED`: required `outcome`, non-empty string `payload`, integer
  `provider_attempts=1`, and `output_digest=sha256(payload)`; `reason` is
  forbidden.
- `REFUSED`: required `outcome`, `reason` in `POLICY_BLOCKED|INPUT_INVALID`,
  and integer `provider_attempts=0`; `payload` and `output_digest` are
  forbidden.

Unknown fields are forbidden. It declares one synthetic deterministic emitter,
one Python validation surface with parity `NOT_APPLICABLE`, the complete R10
mutation basis and at least one ownership binding whose consumer is proven by
canonical digest. It cites this SPEC as its independent contract source.

The synthetic family proves generic mechanics only. It makes zero provider
calls and must not be named P4-B, provider governance, production receipt or
real model/schema parity.

### R15 — Negative test matrix

Focused tests must independently prove failure for at least:

- duplicate JSON keys at registry and nested matrix levels;
- every unknown top-level and nested schema keyword/field;
- missing/wrong/duplicate family id or matrix path;
- registry extra/missing matrix and unregistered on-disk matrix;
- absolute, drive, traversal, backslash, symlink and missing paths;
- stale LF/CRLF-stable contract-source or ownership digest;
- zero/one outcome, missing valid shape and duplicate shape id;
- required/forbidden overlap, orphan conditional and unknown relation field;
- missing mutation operator or unjustified exclusion;
- duplicate owner/consumer and unsupported ownership strategy;
- emitter positive not matching, matching two shapes or failing relation;
- each R10 mutation class around both R14 outcomes;
- validator false-accept and false-reject disagreement;
- nondeterministic ordering, raw-value diagnostic leakage and retained summary;
- unknown CLI argument and repository-validator propagation.

Each negative probe must demonstrate the guard/helper actually fails, not only
assert that a diagnostic string exists in source.

### R16 — Stable diagnostics

Failures use stable codes prefixed `IFC_`, sorted by code then normalized path
and family id. Diagnostics may include safe ids/paths/field names but never raw
field values, file contents, environment values or credential material.
Positive output is `INVARIANT FAMILY CHECK: PASS` or its deterministic JSON
equivalent.

### R17 — Agent and workflow routing

`AGENTS.md` gains a compact mandatory invariant-family trigger and a pointer to
the canonical standard. The existing `operate-shift-workspace` skill gains
pointers at SPEC, WORK_ORDER and REVIEW. Neither file may copy R14 outcome
rules or the R10 operator list.

One shared `Invariant-family proof` template must require matrix id/digest,
applicability, adapter/test paths, exclusions, commands, evidence owner and
reviewer recomputation. WORK_ORDER_AUTHOR and REVIEWER use this same template;
it contains no family-specific rules.

### R18 — Project Knowledge and documentation routing

`knowledge/GOVERNANCE_BOUNDARIES.md` cites the standard as repository-native
guidance and states that executable truth remains in source/tests/guard.
`knowledge/manifest.json` refreshes only genuinely changed pins and current UTC
review dates. `docs/INDEX.md` links the standard, schema, registry and shared
template. No new knowledge Markdown entry is created because the existing
closed three-document pack owns governance boundaries.

### R19 — Catalog, size and continuity

All executable files stay at or below 300 lines; Markdown stays at or below 600
lines. No new exception/debt entry is allowed. Catalog artifacts are regenerated
if source metrics change. Canonical state, mirror, bootstrap, memory, active
handoff, implementation status and roadmap must agree on phase/status/next move.
Bootstrap remains <=4096 bytes, state required reads <=12, roadmap <=600 lines.

### R20 — Role and review independence

The later Work Order must assign BUILD to an `IMPLEMENTATION_WORKER` distinct
from the independent completion `REVIEWER`. Worker return and completion review
are separate paths; the worker cannot edit the reviewer path, self-close a
finding, declare FREEZE or authorize external effects.

WORK_ORDER authoring, BUILD, provider call, commit and push each require their
own current authority. Repair may continue only within the exact reviewed
objective, matrix digest, path set, risk and external-effect class.

### R21 — Live evidence boundary

BUILD and normal review require zero provider/network calls and make only the
claim that repository-native guidance and deterministic checks are installed
and tested. They must not claim that a real AI agent followed the guidance.

Any stronger agent-behavior claim requires a separate operator-authorized live
checkpoint after non-consuming review: refusal/preflight cases first at zero
call, at most one admitted call through the stable runner/runtime, sanitized
public contract input, no secret output, retained failed lineage, no retry and
a claim limited to that exact provider/run. Such a runner/receipt is outside the
normal BUILD set below.

### R22 — No runtime/product expansion

No P4-A/P4-A2/P4-A3/P4-B source, application domain, API/UI, provider adapter,
provider configuration, database, migration, deployment, CVF Core or external
reference path may change. P4-B receipts/reviews remain byte-exact settled
history.

## 3. Candidate exact later BUILD surface

A later Work Order may authorize exactly these 27 worker-owned paths, subject
to independent SPEC review and Work Order authorization review:

1. `AGENTS.md`
2. `skills/operate-shift-workspace/SKILL.md`
3. `docs/cvf/INVARIANT_FAMILY_STANDARD.md`
4. `docs/cvf/invariants/invariant-family.schema.json`
5. `docs/cvf/invariants/registry.json`
6. `docs/cvf/invariants/synthetic-terminal-outcome.json`
7. `docs/templates/INVARIANT_FAMILY_PROOF.md`
8. `scripts/invariant_family_contract.py`
9. `scripts/invariant_family_synthetic_emitter.py`
10. `scripts/check_invariant_families.py`
11. `scripts/testing/validate_repository.py`
12. `tests/unit/test_invariant_family_contract.py`
13. `tests/integration/test_invariant_family_repository_guard.py`
14. `tests/cvf/test_invariant_family_agent_routing.py`
15. `knowledge/GOVERNANCE_BOUNDARIES.md`
16. `knowledge/manifest.json`
17. `docs/INDEX.md`
18. `docs/catalog/MODULE_REGISTRY.json`
19. `docs/catalog/MODULE_CATALOG.md`
20. `IMPLEMENTATION_STATUS.json`
21. `docs/implementation/EXECUTION_ROADMAP.md`
22. `SESSION/SESSION_MEMORY.md`
23. `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json`
24. `SESSION/ACTIVE_SESSION_STATE.json`
25. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
26. `SESSION/handoffs/CROSS_AGENT_INVARIANT_LEARNING_2026-08-22.md`
27. `docs/decisions/CROSS_AGENT_INVARIANT_LEARNING_WORKER_RETURN_2026-08-23.md`

The Work Order may reduce this set if a path is unnecessary, but cannot add or
substitute a path without a reviewed SPEC amendment. The independent completion
review is reviewer-owned path 28 and read-only to the worker:
`docs/decisions/CROSS_AGENT_INVARIANT_LEARNING_COMPLETION_REVIEW_2026-08-23.md`.
No path 29 is reserved. Governance authorization artifacts are pre-BUILD paths,
not part of the worker ceiling.

## 4. Acceptance criteria

- `AC-01`: R1 applicability triggers and honest `NOT_APPLICABLE` behavior are
  pointer-routed through standard/AGENTS/skill/template without copied family
  rules.
- `AC-02`: Draft 2020-12 schema, Python validator and registry jointly fail
  closed on R3-R7 adversaries, with Python-owned semantic uniqueness,
  duplicate-key rejection and exact file-set parity tested explicitly.
- `AC-03`: The R14 matrix is byte-independent from implementation, pins this
  SPEC canonically and validates under both schema and Python contract paths.
- `AC-04`: Synthetic real-emitter positives cover both outcomes and match one
  matrix shape each.
- `AC-05`: Every applicable R10 one-fact mutation is generated for every R14
  valid shape; no known-example-only closure is accepted.
- `AC-06`: Test doubles prove the parity helper catches both false acceptance
  and false rejection; the one-surface bootstrap records honest N/A.
- `AC-07`: Ownership tests catch duplicate/stale/unsupported bindings and prove
  the synthetic digest consumer.
- `AC-08`: Conformance summary is deterministic, complete, sanitized and
  cleaned after PASS and deliberate failure.
- `AC-09`: CLI text/JSON output and all `IFC_` diagnostics are deterministic;
  unknown arguments fail.
- `AC-10`: Repository validation propagates guard failure from a disposable
  mutation and passes the committed repository.
- `AC-11`: All R15 negative probes execute and fail for the intended reason.
- `AC-12`: No dynamic import, provider/network/credential/install/database or
  external-write route exists in the guard/helper/emitter.
- `AC-13`: P4-A/P4-A2/P4-A3/P4-B runtime/history and CVF Core have zero diff.
- `AC-14`: Exact later worker set is at most the 27 listed paths; path 28 is
  reviewer-owned; no path 29.
- `AC-15`: Focused, full non-live, JSON, catalog, session, knowledge, file-size,
  repository, secret, diff and doctor gates pass with only the bounded legacy
  doctor warning.
- `AC-16`: Every executable/Markdown budget in R19 passes without exception or
  debt changes; required-read and roadmap budgets remain bounded.
- `AC-17`: Independent completion review recomputes matrix/source/ownership
  digests, reruns emitted positives and the full mutation corpus, and reports
  findings/waivers exactly.
- `AC-18`: Closure claim remains repository-guidance/guard mechanics only unless
  a separately authorized live checkpoint is later performed.

## 5. Verification sequence for a later Work Order

The Work Order must pin exact commands or equivalent repository-native
invocations in this order:

1. pre-BUILD continuity, exact-path and source-pin checks;
2. invariant schema/contract unit tests;
3. repository-guard integration and agent-routing tests;
4. `python scripts/check_invariant_families.py` and `--json`;
5. `python scripts/check_project_knowledge.py`;
6. `python scripts/check_session_state.py`;
7. `python scripts/generate_catalog.py --check`;
8. `python scripts/check_file_size.py`;
9. `python scripts/testing/validate_repository.py`;
10. full non-live Python suite;
11. JSON parse, exact-path, staged, secret, residue and `git diff --check`;
12. workspace doctor resolved from the pinned read-only Core.

No live call belongs in this sequence. A later separately authorized live
checkpoint follows R21 and cannot be silently added to the Work Order.

## 6. Failure and repair semantics

Any schema/registry/matrix/path/digest/ownership/mutation/parity failure returns
nonzero and no PASS summary. Test or summary residue is removed in `finally`.
No automatic matrix rewrite, waiver creation, retry or acceptance downgrade is
allowed.

Stop on path overflow, DESIGN/SPEC conflict, matrix contract change, risk or
external-effect change, dynamic import, secret exposure, P4 runtime/history
diff, Core mutation, file-size debt/exception request, staged residue or failed
gate. A scope-changing repair requires a reviewed amendment. At repair round
three without an independent new root cause, record
`REVIEW_COST_ESCALATION_REQUIRED` per `AGENTS.md`.

## 7. Rollback

Before commit, rollback means reverting only the later exact worker-owned set to
its recorded pre-BUILD state; authorization/review history remains retained.
After a separately authorized commit, rollback is a new corrective commit, not
amend/reset/force-push. Rollback must restore repository validation, catalog,
continuity and Project Knowledge pins and leave no matrix or summary residue.

## 8. Claim boundary

Passing this SPEC may establish only that a provider-neutral invariant-family
standard, closed declarations, deterministic guard and conformance mechanics
were implemented and independently tested in this repository. It does not
establish universal agent compliance, automatic discovery of undeclared
duplicates, retrofit P4-B, runtime AI governance, provider parity, production
readiness or absence of all future findings.

## 9. Stop condition

Independent SPEC review passed with findings/waivers `NONE/NONE` and
non-blocking observations `OBS-1` through `OBS-3`. Stop at
`SPEC_REVIEW_PASS_AWAITING_WORK_ORDER_AUTHORITY`. WORK_ORDER and BUILD remain
unauthorized without fresh authority.

---

## 10. Amendment 2 — exact-30 repair contract (2026-08-23)

The exact implementation ceiling is amended from 27 to 30 by adding only the
ownership helper and paired unit/integration split-test paths named and hashed
in DESIGN Amendment 2. The original 27 paths retain their ordering; these are
paths 28–30 of the worker union. The independently created completion review
remains reviewer-owned/read-only and is not part of that union. No additional
path (“path 31”) is allowed.

Repair-round-3 acceptance adds the following testable requirements without
changing R1–R22 or the claim boundary:

- mutation completeness is derived from the closed operator/shape contract,
  not a hand-maintained subset; removing `COUNTER_MUTATION` or
  `ONE_SIDE_RELATION_CHANGE` coverage must make the production summary FAIL;
- conditional ownership is singular: duplicate conditionals and inactive or
  semantically inapplicable conditional rules fail closed;
- every ownership strategy, including `ADAPTER_ASSERTION`, validates real
  binding/proof semantics through production code; no function-name existence
  check, caller default, test-local literal, or omitted ownership result may
  produce PASS;
- repository traversal rejects a symlink before path resolution can erase its
  identity, with paired safe-path and symlink-negative tests;
- evidence uses the stable runtime and the complete non-live verification
  sequence; reported commands, counts, skips, warnings, hashes and dirty-set
  arithmetic must be independently reproducible. Doctor remains required but
  may retain only its already bounded legacy warning.

The three ratified pre-repair SHA-256 values are
`9b0e0c1d667f41267ffdf654909aa9416bf8d05a5d18efb7253e6ad8f096ffaf`,
`5415b52d9b864fb0435f02ee957d203551302035eeeb69971d263d5d4a3741a0`,
and `fad94162154e85bff222fd6ef3cddf24b906a7563080378ed90366be44db97ce`.
No provider/network/credential/install/database/stage/commit/push/deployment
is permitted.
