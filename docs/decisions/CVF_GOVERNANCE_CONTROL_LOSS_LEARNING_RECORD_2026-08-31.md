# CVF Governance Control-Loss Learning Record

- Record id: `CVF-GOVERNANCE-CONTROL-LOSS-LEARNING-2026-08-31`
- Date: `2026-08-31`
- Phase: `INTAKE`
- Status: `READY_FOR_INDEPENDENT_INTAKE_REVIEW`
- Risk: `R2`
- Author role: `INTAKE_AUTHOR` held by the primary orchestrator after two
  delegated authors were interrupted for producing no observable artifact
- Findings/waivers: for independent reviewer determination
- BUILD/external-effect authority: `NOT_GRANTED`

## 1. Executive disposition

The operator has parked the complete project delivery roadmap. Carrier SPEC,
the parent `0281e93` target rebase, P4-E, fixture repair, XR1, product work and
all other delivery movement remain parked. No Work Order, BUILD, Core update,
provider/network action, deployment, release, commit or push is authorized.

This record treats the recent sequence as **governance control loss even though
the seven-step phase chain continued to operate and unsafe BUILD effects were
prevented**. Formal compliance prevented external damage, but predictable
defects were discovered too late, repeated review became the primary defect-
discovery mechanism, repairs introduced adjacent defects, and orchestration
consumed avoidable quota and latency. A control system that is safe only after
many expensive loops is not yet operating according to CVF's intended values.

This is the single canonical incident and learning record. It records facts,
accountability and proposed controls for both this downstream project and CVF
Core. Proposed Core changes are not implemented; the sibling Core is read-only.

## 2. Claim boundary

This is a repository-maintenance and process incident record. It does not
claim that CVF controlled AI/agent behavior, that any provider followed these
instructions, or that proposed learning has been institutionalized. No live
provider call is required or used. Dates, hashes and dispositions below come
from exact local repository artifacts. Git author identity is not treated as
proof of who composed content; role records are used for responsibility.

No product/runtime/production defect or external mutation occurred in this
incident chain. The failure is governance effectiveness, authoring quality,
review economics and framework capability—not a production-impact claim.

## 3. Evidence-bound chronology

### 3.1 Latent invariant-framework boundary — 2026-08-23

Commit `140218d5f06df991ef256276f69dc970104a4aa0` introduced the invariant-
family schema, contract and ownership guard under tranche
`CROSS-AGENT-INVARIANT-LEARNING-2026-08-22`. Git records author/committer
`Blackbird081`; governance records assign work through provider-neutral
`IMPLEMENTATION_WORKER`, `REPAIR_WORKER` and independent reviewer roles.

That tranche itself required ten completion-review rounds before
`REVIEW_PASS_ROUND_10`. This was early evidence that phase compliance and
large repair loops could coexist. The installed framework was valid for its
then-tested examples, but it encoded two assumptions not declared as capability
limits:

1. field domains omit JSON `null`; and
2. every ownership `consumerPath` must already be an existing regular file
   before any binding strategy is evaluated.

Evidence:

- `docs/cvf/invariants/invariant-family.schema.json`
- `scripts/invariant_family_contract.py`
- `scripts/invariant_family_ownership.py` lines 194–227
- `docs/decisions/CROSS_AGENT_INVARIANT_LEARNING_COMPLETION_REVIEW_2026-08-23.md`
- `docs/decisions/CROSS_AGENT_INVARIANT_LEARNING_WORKER_RETURN_2026-08-23.md`
- `docs/cvf/INVARIANT_FAMILY_STANDARD.md`

These were latent limitations, not necessarily defects against the original
synthetic family. They became blockers when a later tranche required null and
future BUILD consumers. CVF had no mandatory capability audit to expose the
mismatch before the later SPEC was authored.

### 3.2 Attempt 3 inline-wrapper failure — 2026-08-30/31

The attempt-3 implementation worker constructed an ephemeral inline PowerShell
preflight wrapper from Work Order requirements. The fragment
`Need (if(...){...}else{...})` used statement-form `if` where PowerShell did
not accept it as a value expression. Execution stopped before P0; network,
reconciler, pin, root, binding and evidence effects were all zero.

The immediate defect belonged to the worker-created temporary wrapper, not to
retained Work Order bytes or product code. The enabling design defect was that
effect-controlling wrapper bytes were composed only at worker execution time,
so they were not parse-tested and independently reviewed as a retained
artifact before BUILD.

Evidence:

- `docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-30_0281E93_ATTEMPT_3.md`, especially sections 2–4
- `SESSION/handoffs/CVF_CORE_REFRESH_TARGET_REBASE_0281E93_2026-08-30.md`
- completion-review SHA-256
  `004ce65b653abe23270d8da01528584eef52aeccd06a5e706ba6925ab0b59239`

### 3.3 Parent attempt-4 DESIGN — 2026-08-31

A fresh attempt-4 DESIGN tried to retain and review carrier bytes. Its first
independent review found `DR4-F1..F4`: phase ownership violation, cyclic/
incomplete authority hash binding, unrealizable PowerShell binder contract,
and contradictory child/network closure. A bounded repair closed all four.

Evidence:

- accepted DESIGN SHA-256
  `8c1f2a67dcd9f3e67b4b04f4cb950f990889bf3f811417b3ca087d4799ef9e13`
- final DESIGN-review SHA-256
  `8b259c3823589d17937f5b25b85fa0c7ac8559003f68a360d96c8a04d3d85ede`
- `docs/decisions/DESIGN_2026-08-31_CVF_CORE_REFRESH_TARGET_REBASE_0281E93_ATTEMPT_4.md`
- `docs/decisions/DESIGN_REVIEW_2026-08-31_CVF_CORE_REFRESH_TARGET_REBASE_0281E93_ATTEMPT_4.md`

The learning was only partially left-shifted: the parent DESIGN required a
separate carrier tranche, but no executable feasibility/capability audit was
performed before that carrier DESIGN began.

### 3.4 Carrier DESIGN review churn — 2026-08-31

The initial carrier DESIGN was authored by delegated task
`carrier_design_author`; independent task `carrier_design_review` found
`CDR4-F1..F6`:

- continuity timing contradicted mandatory phase acknowledgments;
- the external-authority tuple retained a self-hash cycle;
- carrier logic claimed it could enforce unobservable host invocation form;
- Git local config/fsmonitor/include behavior escaped the child/network model;
- Execute both inherited and excluded DryRun Git children; and
- non-recursive root snapshots could not prove whole-root no-write equality.

Repair round 1 closed four findings but left future-hash and Git-url residuals.
Repair round 2 closed the future-hash residual but exposed an impossible
post-G1 counter model and real Project Git-config mismatch. Round 3 closed
those roots but introduced `--ProjectRemote`, violating the parent-frozen raw
interface. Round 4 removed that new token and finally reached
`DESIGN_REVIEW_PASS`, findings/waivers `NONE/NONE`.

Final evidence:

- carrier DESIGN SHA-256
  `8f5ab09aac72a99ea706444e2f57d47a20a5bd928544cbccf799129333be3a95`
- carrier DESIGN-review SHA-256
  `91d43cfa5e596312e3473bfbe8cbb1b170f13a81137dbeb352d52850c2ca07e7`
- `docs/decisions/DESIGN_2026-08-31_CVF_CORE_REFRESH_ATTEMPT_4_CARRIER.md`
- `docs/decisions/DESIGN_REVIEW_2026-08-31_CVF_CORE_REFRESH_ATTEMPT_4_CARRIER.md`

The primary orchestrator authorized and routed every round. Sub-agent defects
remain orchestrator accountability because delegation did not transfer scope,
acceptance or review-economics responsibility.

### 3.5 Carrier SPEC semantic failure — 2026-08-31

The first SPEC set passed duplicate-key, invariant-family, pin, session and
diff guards, yet independent semantic review found `CSR4-F1..F5`:

1. all corpus ids violated the SPEC's mode derivation and most violated the
   expected-code derivation;
2. required `execution_id` had no machine-enforced domain;
3. later-parent Execute shapes were partial fragments accepted as complete
   closed receipts;
4. denied-candidate counters were independent ranges that admitted impossible
   combinations; and
5. ownership bindings covered the pin but not the future carrier/test.

Repair closed F1/F3/F4: 77 ids now use the exact grammar; later-parent shapes
were removed from the carrier family; denied candidates became exact G0–G8
prefix shapes. Canonical repaired matrix/pin digest is
`21aad333256b76f857b2cf985f91744118fb780c9c501783c8de82b7515d3c60`.

F2/F5 remain open because the shared schema cannot express JSON null and the
ownership guard rejects absent future consumer paths before evaluating a
strategy. The SPEC correctly reports
`SPEC_REPAIR_BLOCKED_PREREQUISITE_AMENDMENT`; it does not claim readiness.

Evidence:

- `docs/decisions/SPEC_REVIEW_2026-08-31_CVF_CORE_REFRESH_ATTEMPT_4_CARRIER.md`
  initial review SHA-256
  `9f13cb0a20530447b17d30860988187c220346d1821a7463b2e8631afe6bf818`
- `docs/specs/CVF_CORE_REFRESH_ATTEMPT_4_CARRIER_2026-08-31_SPEC.md`
- `docs/cvf/invariants/cvf-core-refresh-attempt-4-carrier-modes-2026-08-31.json`
- `docs/specs/cvf_core_refresh_attempt_4_carrier_2026_08_31_invariant_pin.py`

### 3.6 Orchestration and infrastructure latency — 2026-08-31

The primary orchestrator used long waits before interrupting some agents,
allowed formal reviewers to become the first semantic adversarial testers,
and treated newly named root causes as justification for continued repair
rounds. One repair agent failed with model-capacity error after partially
writing a DESIGN; a replacement recovered it. One SPEC author was interrupted
after producing no artifact. During creation of this record, two delegated
authors were also interrupted after producing no observable artifact, and the
primary orchestrator took the author role directly.

No exact provider-token or wall-clock total is available and none is invented.
The demonstrated cost mechanisms are repeated large-context transfer, repeated
hash/continuity reads, four DESIGN review cycles, SPEC repair, idle wait windows,
capacity recovery and re-review of increasingly large artifacts.

## 4. Accountability taxonomy

| Class | Accountable role/system | Finding |
|---|---|---|
| Immediate implementation defect | attempt-3 `IMPLEMENTATION_WORKER` | invalid ephemeral PowerShell wrapper |
| Authoring defects | current DESIGN/SPEC author tasks | contradictory interfaces, hash graph, child model, corpus and counter semantics |
| Repair regression | current repair tasks | new `--ProjectRemote` interface drift and partial-edit recovery need |
| Orchestration failure | primary `ORCHESTRATOR` | capability audit omitted; formal review used for predictable discovery; waits and repair budget poorly controlled |
| Review-system weakness | project/CVF process | structural PASS was not semantic completeness; no mandatory pre-review adversarial evidence |
| Latent framework limitation | CVF invariant-family schema/guard from `140218d5` | no JSON-null domain; no phase-valid deferred future consumer |
| Infrastructure | agent/model service | capacity failure and non-observable long-running author turns |

Git author/committer identity is provenance, not sole personal blame. Reviewers
that detected and bounded defects are not the cause merely because findings
were recorded in their artifacts.

## 5. Why seven-step compliance still lost control

The phase chain controlled **permission to proceed**, but it did not ensure the
quality or economics of reaching each gate:

- INTAKE did not require a capability audit of the exact schema/guard on which
  SPEC would depend.
- DESIGN accepted prose architecture without executable feasibility probes for
  PowerShell binding, Git transitive behavior, hash staging and filesystem
  observation.
- SPEC guards proved structural consistency but not semantic reachability or
  completeness.
- independent review became the first place adversarial examples were tried.
- repair authority was repeatedly continued when findings had new labels, even
  though aggregate review cost already showed loss of control.
- no immutable machine-checkable constraint ledger prevented a repair from
  changing the parent-frozen interface.
- no orchestration contract required observable progress or early agent
  interruption.

Therefore “all seven phases were followed” is necessary but not sufficient.
CVF must also bound discovery latency, repair churn, artifact complexity and
review cost. Otherwise compliance can become procedural containment after
poor preparation instead of prevention by construction.

## 6. Root-cause tree

```text
Governance control loss
├── Left-shift failure
│   ├── no dependency capability audit
│   ├── no executable DESIGN feasibility probes
│   └── no semantic author preflight before formal review
├── Contract-complexity failure
│   ├── large prose artifact with duplicated rules
│   ├── no single immutable constraint ledger
│   └── matrix/schema capabilities discovered after authoring
├── Repair-control failure
│   ├── repair added adjacent interface drift
│   ├── aggregate review cost was not a hard stop
│   └── “new root cause” classification prolonged the loop
├── Orchestration failure
│   ├── delegated output accepted too early for review
│   ├── primary precheck was incomplete
│   └── idle/capacity turns interrupted too late
└── CVF Core/framework gap
    ├── phase gates measure authorization, not review efficiency
    ├── schema lacks required value/lifecycle capabilities
    └── guards do not require semantic adversarial coverage
```

## 7. Complete current finding disposition

| Finding family | State | Notes |
|---|---|---|
| attempt-3 wrapper defect | `CLOSED_BOUNDED_ZERO_EFFECT_REFUSAL` | target not adopted; no retry |
| parent `DR4-F1..F4` | `CLOSED` | parent parked at DESIGN PASS |
| carrier `CDR4-F1..F6` | `CLOSED` | repaired |
| carrier `RR1-F1/F2` | `CLOSED` | repaired |
| carrier `RR2-F1/F2` | `CLOSED` | repaired |
| carrier `RR3-F1` | `CLOSED` | raw interface restored |
| SPEC `CSR4-F1/F3/F4` | `CLOSED_IN_REPAIR_PENDING_REREVIEW` | structural/targeted guards pass; no final SPEC PASS |
| SPEC `CSR4-F2/F5` | `OPEN_BLOCKED_PREREQUISITE` | requires separately governed shared framework change |
| review-cost/orchestration incident | `OPEN_AT_INTAKE` | this record requires independent review |
| upstream CVF learning adoption | `PROPOSED_NOT_IMPLEMENTED` | sibling Core read-only |

## 8. Immediate containment — implemented now

1. `IMPLEMENTED`: canonical active state parks all roadmap/delivery movement.
2. `IMPLEMENTED`: carrier remains blocked at SPEC; no Work Order or BUILD.
3. `IMPLEMENTED`: parent rebase, P4-E, fixture repair and XR1 stay parked.
4. `IMPLEMENTED`: this single record prevents incident facts from being
   scattered across new learning documents.
5. `IMPLEMENTED`: delegated author turns with no observable artifact were
   interrupted rather than allowed to wait indefinitely.
6. `OPEN`: independent review of this record is still required.

## 9. Project learning controls

The following controls are requirements for any restart; they are not yet
implemented merely by appearing here:

1. **Capability audit before DESIGN/SPEC** — executable probes must demonstrate
   every required schema type, ownership lifecycle and guard strategy.
2. **Immutable constraint ledger** — exact interface, artifact paths, phase
   owners, hash DAG, child sequence, counters and framework capabilities must
   have one machine-checkable owner; repair diff must fail on undeclared drift.
3. **Author semantic preflight** — author must run wrong-type, impossible-
   counter, partial-envelope, missing-future-consumer and interface-regression
   probes before requesting independent review.
4. **Orchestrator acceptance precheck** — formal review may start only after
   the primary orchestrator reproduces lineage hashes and semantic negatives.
5. **Two-round root-cause audit** — after two repair rounds, stop phase work and
   perform aggregate root-cause/cost review regardless of finding labels.
6. **Repair regression gate** — compare option/path/role/artifact-class sets
   byte-for-byte with accepted parent constraints.
7. **Artifact decomposition** — no growing monolithic DESIGN; reusable semantic
   tables belong in a single canonical machine-readable artifact.
8. **Observable agent progress** — an author must create a bounded skeleton or
   return a blocker within the configured interval; otherwise interrupt and
   reassign. Partial writes require explicit recovery review.
9. **Review-efficiency receipt** — record author passes, formal review rounds,
   reopened findings, repair-introduced findings, idle waits and escalation
   decision without inventing provider-token totals.

## 10. Proposed CVF Core learning requirements

These are upstream proposals, not downstream implementation authority:

| Id | Requirement | Status | Proposed owner/gate |
|---|---|---|---|
| `CVF-L1` | Add a mandatory dependency capability audit between INTAKE and DESIGN/SPEC for R2/R3 work | `PROPOSED` | CVF Core DESIGN/SPEC review |
| `CVF-L2` | Require semantic adversarial evidence before formal phase review; structural guard PASS cannot be sole readiness evidence | `PROPOSED` | Core policy + templates + guard tests |
| `CVF-L3` | Add a canonical constraint-ledger contract and parent-to-repair interface regression check | `PROPOSED` | Core schema/guard tranche |
| `CVF-L4` | Make aggregate repair cost a stop condition after two rounds; a “new root cause” must not automatically reset economics | `PROPOSED` | Core governance-latency policy |
| `CVF-L5` | Add JSON `NULL` field-domain semantics with mutation and parity tests | `OPEN_PREREQUISITE` | invariant schema/contract/guard full chain |
| `CVF-L6` | Add phase-valid deferred ownership for reviewed consumers that are intentionally absent until BUILD, with post-BUILD closure evidence | `OPEN_PREREQUISITE` | invariant schema/ownership guard full chain |
| `CVF-L7` | Require artifact-size/decomposition review before large governance prose can pass a phase | `PROPOSED` | Core file-size/policy guard |
| `CVF-L8` | Add observable agent-progress, timeout, partial-write recovery and capacity-failure handling to orchestration guidance | `PROPOSED` | Core downstream template/skill |
| `CVF-L9` | Add review-effectiveness metrics: defect discovery phase, repair-introduced defects, review rounds and avoidable operator wait | `PROPOSED` | Core evidence template/catalog |
| `CVF-L10` | Treat repeated formal-review discovery as a control-loss incident even when BUILD remained blocked | `PROPOSED` | Core incident/escalation policy |

No proposal may be copied directly into the sibling Core from this project.
Each requires its own public-Core authority, phase chain, independent review,
tests and release disposition.

## 11. Restart criteria

The delivery roadmap remains parked until all applicable criteria are met:

1. this record receives independent INTAKE review with findings/waivers stated;
2. operator chooses whether to advance the learning tranche beyond INTAKE;
3. CVF-L5/L6 receive separately reviewed prerequisite authority or the carrier
   contract is independently redesigned without weakening accepted behavior;
4. a machine-checkable project constraint ledger and semantic preflight exist;
5. the carrier SPEC is independently rereviewed to `SPEC_REVIEW_PASS`;
6. exact Work Order and authorization review pass before any source/test BUILD;
7. restart acknowledgment identifies which learning controls are actually
   implemented and which remain explicitly accepted debt.

Absence of a new chat objection, a structural guard PASS, or continued operator
instruction alone does not satisfy these criteria.

## 12. Next governed move

A distinct `INDEPENDENT_INTAKE_REVIEWER` must compare this exact record with
the named evidence, verify attribution and completeness, challenge whether the
proposed controls prevent recurrence rather than only add documentation, and
state findings/waivers. The reviewer must not repair this file, resume the
roadmap, open CVF Core changes or authorize BUILD.
