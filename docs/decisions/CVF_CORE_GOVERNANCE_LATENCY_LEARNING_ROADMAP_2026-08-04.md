# CVF Core Governance-Latency Learning Roadmap

- Date: `2026-08-04`
- Source project: `shift-operations-workspace`
- Upstream target: `Controlled-Vibe-Framework-CVF`
- Artifact class: `PUBLIC-SAFE LEARNING / ROADMAP ONLY`
- Status: `FINAL_DOWNSTREAM_EVIDENCE_ROADMAP_FOR_CORE_L0_INTAKE`
- Risk: `R2` when promoted into a core behavior change
- Downstream disposition: `PARKED_REVIEW_CHANGES_REQUIRED_LOCAL_EVIDENCE_ONLY`
- Commitment ceiling: `L0 evidence work only; L1+ requires an explicit go/no-go`

## 1. Purpose

Convert the repeated P3-A Refinery control-friction incidents and the failed
downstream governed-plan-runner prototype into a bounded, testable CVF core
learning program. The objective is not to weaken CVF. It is to preserve
security, data, provider and protected-action controls while preventing
pre-admission mechanical defects from unnecessarily consuming human approvals,
agent context, latency, commits and review attention.

This file does not authorize a CVF core edit and does not pre-approve L1-L8.
The core remains read-only from this downstream workspace. Promotion requires
a fresh core-native L0 tranche, core continuity rehydration, independent
review and the core's own evidence rules. L0 must falsify or qualify the
amplification hypothesis before any implementation program is funded.

## 2. Trigger evidence

P3-A produced useful product and governance findings, but the execution chain
also recorded fifteen documented candidate defect classes across twenty-eight
numbered amendment artifacts. The directory contains twenty-nine matching
filenames because `P3A_REFINERY_WORK_ORDER_AMENDMENT_18_EXECUTION_SHEET.md` is
supporting material, not a twenty-ninth numbered amendment. Artifact count is
not approval-consumption count: L0 must reconstruct accepted acknowledgments,
admission events and consumed approvals instead of assuming one per file.

The documented classes include:

1. Windows-invalid literal wildcard passed to `rg`;
2. missing package path for a stdin Python probe;
3. mistyped checkpoint SHA;
4. guessed pytest selector that did not exist;
5. wrong file-size script name;
6. compressed PowerShell `foreach` parse failures;
7. unavailable JavaScript decoding primitive in the selected executor;
8. UTF-8 stdin transport mismatch;
9. outer tool timeout shorter than the reviewed test budget;
10. Windows text-mode LF/CRLF translation;
11. fixture restoration that changed newline bytes;
12. mixed-line-ending patch output;
13. two-space JSON indentation/post-hash mismatch;
14. self-referential future commit-hash assumptions;
15. reviewer use of `uv` that created `.venv`/`uv.lock`, downloaded a package
    and installed dependencies despite an explicit zero-network boundary.

The parked governed-plan-runner prototype added seven independently reviewed
findings (`GPR-BUILD-F1..F7`): missing authority/R2/HEAD/topology verification,
an invalid 64-hex Git-HEAD contract, declarative-only zero-network controls,
weak resume binding, incomplete receipt truth, absent caller outer-timeout and
incomplete rollback. Focused tests passed `52/1 skipped`; adversarial probes
still reproduced the failures. This is a positive-control example of review
cost producing material value by preventing a defective control tool from
being committed or generalized upstream.

Raw repository density is directionally anomalous but not yet causal proof:
P3-A has `28 amendments / 1 base Work Order`; P2-C has `13 / 7`; P2-D has
`0 / 1`. Scope and complexity differ, so L0 must normalize by admitted
mutations, gates, elapsed time and tranche size before drawing a learning-curve
or systemic-amplification conclusion.

Some controls found meaningful issues, including stale implementation truth,
file-size debt, catalog LOC drift, missing public invariants and environment
contract mismatch. The lesson is therefore not "remove gates". It is
"separate semantic risk findings from execution-transport defects and apply a
proportionate admission/approval model."

## 3. Root-cause model

### 3.1 Governance amplification

A low-value mechanical defect becomes expensive when all of the following are
coupled:

- prose Work Orders must be manually translated into shell commands;
- in the observed P3-A chain, non-zero mechanical results repeatedly triggered
  the same amendment/R2 machinery as admitted mutations;
- stop-first/no-retry applies before and after the risk boundary identically;
- every repair requires a new Work Order, independent review, checkpoint and
  exact R2;
- byte hashes are applied to whitespace-insensitive artifacts;
- mutable continuity files pin or describe other mutable continuity files;
- network prohibition is a prompt instruction rather than a tool capability.

### 3.2 Agent-intelligence suppression

Over-specifying commands and formatting displaces agent judgment from the
problem domain into ceremonial transport work. The agent becomes less able to
choose a safe equivalent command, recover inside a bounded envelope or spend
context on product reasoning. Strong governance should constrain outcomes and
capabilities; it should not unnecessarily dictate fragile command syntax.

### 3.3 Missing closed-loop use of existing CVF concepts

CVF core already documents governance tax, mechanical/evidence-light work,
latency discipline and finding-to-governance learning. The gap is operational:
these concepts are not yet wired into one admission state machine, capability
profile, executable-plan contract and regression budget for downstream use.

## 4. Target operating model

```text
Intent and risk classification
        |
        v
Reviewed semantic scope + capability profile
        |
        v
Machine plan compile / validate / zero-write simulation
        | mechanical failure: repair before approval, R2 not consumed
        v
Human approval
        |
        v
ADMISSION EVENT
first successful protected mutation or external dispatch
        | approval becomes consumed here
        v
Fail-closed execution + structured receipt
        |
        v
Independent semantic review + proportional closure
        |
        v
Governance-tax and learning feedback
```

## 5. Core principles to adopt

1. **Approval consumption follows admission, not command start.** A proposed
   approval remains unconsumed until the first successful authorized durable
   mutation, protected dispatch or external call.
2. **Pre-admission mechanical failures are zero-impact.** Parse, executable,
   selector, path, timeout-budget, occurrence, post-hash simulation and
   environment failures must be caught before approval or recorded as
   `PRE_ADMISSION_MECHANICAL_FAILURE` with zero mutation/call.
3. **Semantic controls and byte-fidelity controls are distinct.** Byte-exact
   rules require an explicit fidelity reason.
4. **Capability enforcement beats prompt prohibition.** Zero-network roles
   must be technically unable to invoke package managers, fetch or remote
   transports.
5. **Work Orders compile to executable plans.** Agents design the plan;
   deterministic tooling validates transport details.
6. **Bounded autonomy is preferred to ceremonial rigidity.** Agents may choose
   equivalent local implementations inside reviewed invariants and repair
   envelopes.
7. **Governance must measure its own marginal value and cost.** A control that
   repeatedly produces low-value stops must be redesigned, not celebrated.
8. **Detection is not savings.** Report `defect caught`, `approval unconsumed`
   and `governance cycle avoided` separately; never convert one into another.
9. **Green suites do not prove a control claim.** Each security/governance
   claim requires an adversarial negative control that attempts the bypass.
10. **The improvement program governs its own cost.** Every expansion beyond
    L0 requires a measured benefit, a cheaper-alternative check and a stop rule.

## 6. Upstream workstreams

### WS-0 — Evidence packet and incident taxonomy

Deliverables:

- sanitized P3-A incident ledger;
- classification schema: `SEMANTIC_RISK_FINDING`,
  `PRE_ADMISSION_MECHANICAL_FAILURE`, `ENVIRONMENT_MISMATCH`,
  `CAPABILITY_VIOLATION`, `CONTINUITY_FEEDBACK_LOOP`, `CONTROL_FALSE_POSITIVE`;
- per-incident mutation/call state, approval state, latency, tokens, commits,
  retries, value disposition and counterfactual prevention control;
- replay fixtures with no project secrets or private payloads.
- a numbered-amendment inventory that excludes supporting sheets;
- an acknowledgment/admission/consumption ledger rather than an artifact-count
  proxy;
- independent blind classification of all fifteen candidate classes before the
  Claude paper-replay table is consulted;
- three separate replay outcomes: `defectCaughtPreAdmission`,
  `approvalUnconsumed`, and `cycleAvoided`;
- normalized amendment-density comparison across P2-C, P2-D and P3-A;
- an explicit positive-control entry for the independent runner review that
  prevented F1-F7 from entering Git history.

Exit criteria:

- every P3-A stop has exactly one primary class and optional contributing
  classes;
- meaningful findings remain distinguishable from transport defects;
- the packet is public-safe and independently reviewed.
- the independent classification is compared with the Claude `14/15`
  hypothesis, with disagreements retained rather than averaged away;
- no claim equates twenty-eight amendment files with twenty-eight consumed R2s
  unless the authority ledger proves it;
- L0 returns one of `PROCEED_FULL`, `PROCEED_WS2_ONLY`, `DEFER_LEARNING_CURVE`
  or `STOP_NO_MATERIAL_CASE`.

### WS-1 — Approval-consumption state machine

Define canonical states:

```text
PROPOSED -> REVIEWED -> ACKNOWLEDGED -> PREFLIGHTED -> ADMITTED -> CONSUMED
                                      \-> REJECTED_MECHANICAL_UNCONSUMED
```

Required rules:

- acknowledgment alone does not consume approval;
- read-only validation and memory-only simulation do not consume approval;
- consumption occurs atomically with the first admitted mutation/dispatch;
- a failure after `ADMITTED` remains stop-first and consumes authority;
- receipts must state admission event, mutation count and external-call count;
- ambiguous admission state fails closed and requires review.

Regression proofs:

- syntax failure before mutation leaves approval reusable;
- simulated post-hash mismatch leaves approval reusable;
- first successful write consumes approval exactly once;
- external dispatch consumes before response handling;
- crash around admission cannot produce double-use or unknown state.

Design note: filesystem admission and external dispatch are not identical.
For a provider/network action, authority must become consumed atomically before
the first outbound attempt, not after a successful response. For filesystem
mutation, consumption must bind to the first successful authorized atomic
replacement. Ambiguous crash recovery fails safe, but the unknown-state rate
must be measured; sustained ambiguity above the L0/L1 threshold is a state-
machine defect, not acceptable normal operation.

### WS-2 — Capability-enforced role profiles

Create machine profiles for at least:

- `LOCAL_READ_ONLY_REVIEWER`;
- `ZERO_NETWORK_IMPLEMENTATION_WORKER`;
- `PROVIDER_EVIDENCE_WORKER`;
- `COMMIT_STEWARD`;
- `CORE_READ_ONLY_REFERENCE`.

The zero-network profiles must deny package managers, remote Git operations,
HTTP/DNS/socket access and environment creation unless separately authorized.
Allowlist system interpreters and tracked scripts explicitly. Log denied
attempts as capability evidence without turning them into provider calls.

Regression proof must reproduce the historical `uv` attempt and demonstrate
that it is blocked before `.venv`, lockfile, download or install occurs.
It must also reject `curl`, `wget`, `git fetch/pull`, `pip`, `uv`, arbitrary
Python socket/HTTP access and inherited credential/proxy environments. This is
the earliest implementation priority after L0, because both the reviewer
incident and runner F3 independently prove prompt/declarative prohibition is
insufficient.

### WS-3 — Governed machine-plan contract and runner

Standardize:

- canonical JSON plan schema;
- argv arrays with `shell=false`;
- repository-relative explicit paths; no glob, absolute path or `..` escape;
- environment/cwd/executable/pytest-node/timeout-budget validation;
- byte replacement occurrence counts and pre/post hashes;
- newline and indentation metrics;
- all-output precomputation;
- same-directory atomic replacement and rollback;
- deterministic sanitized receipts;
- resume of `NOT_RUN` gates only with full drift rejection.

The downstream governed-plan runner is a learning prototype, not automatically
the upstream implementation. Its F1-F7 findings are mandatory negative
fixtures. Core must decide whether to replace it, salvage bounded components or
discard it; no upstream implementation may inherit its green-suite claims.

### WS-4 — Semantic versus byte-fidelity policy

Introduce explicit artifact modes:

| Mode | Appropriate use | Comparison |
|---|---|---|
| `SEMANTIC_CANONICAL` | ordinary JSON/YAML structured truth | parsed canonical form + schema |
| `TEXT_NORMALIZED` | Markdown and generated text without signature value | normalized encoding/newlines |
| `BYTE_EXACT` | signatures, receipts, canonical payloads, binary/migrations | raw bytes + SHA-256 |

Every `BYTE_EXACT` control must declare why semantic or normalized comparison
is insufficient. Whitespace-only JSON drift must not automatically receive the
same escalation cost as a semantic or security change.

Repository newline hygiene is a prerequisite, not a complete solution. This
downstream repo currently has no `.gitattributes`, local/global
`core.autocrlf` are unset, and the effective inherited value is `true`; L0 must
evaluate a cheap repository baseline. Git settings do not prevent Python
`read_text()`/`write_text()` from translating bytes on Windows, however;
snapshot/restore fixtures still need an explicit byte-preserving helper and
targeted tests. Do not add a broad ban on `read_text()` or a noisy static rule
without evidence that the narrower fix is insufficient.

### WS-5 — Mechanical repair envelope

Define a reviewed envelope that can cover:

- command transport and executable selection;
- timeout-budget correction;
- encoding/newline preservation;
- canonical formatting;
- receipt serialization;
- equivalent selector/path expression correction.

The envelope must bind allowed paths, defect classes, maximum attempts,
zero-call boundary and semantic invariants. It must never cover product logic,
security policy, data scope, provider behavior, migrations or claim changes.

### WS-6 — Continuity and finality redesign

Prevent self-referential control loops:

- immutable receipts carry build/review/closure identifiers;
- mutable status summaries reference receipts rather than pinning their own
  future bytes;
- future commit hashes are never guessed or embedded pre-commit;
- closure post-images are compiled before staging;
- one logical closure should not require repeated commits solely to record the
  hash of the previous continuity commit;
- canonical and mirror surfaces must be generated or validated from one model.

Do not create a separate WS-11 authority-state system by default. First extend
the existing `SESSION/ACTIVE_SESSION_STATE.json` model and its validated
`CVF_SESSION/ACTIVE_SESSION_STATE.json` mirror with normalized authority,
admission and consumption fields. A new store is justified only if L1 proves
the current state model cannot provide atomicity or crash recovery.

### WS-7 — Governance-tax fitness function

Add mandatory metrics:

- approval count and consumption count;
- mechanical-stop count and rate;
- meaningful-finding count and rate;
- p50/p95 governance latency;
- token and agent-turn cost;
- checkpoint/commit count;
- false-positive and repeated-failure rate;
- controls triggered per prevented impact class;
- downstream adoption friction.

Candidate SLOs for pilot:

- no fixed reduction target before L0 establishes a reproducible baseline;
- report defect-catch, approval-survival and cycle-avoidance rates separately;
- after L0, set a cycle-avoidance target with confidence bounds and a declared
  denominator, rather than inheriting the unverified `14/15 (93%)` estimate;
- zero R2 consumption for proven pre-admission mechanical failures;
- zero unauthorized external calls in capability-restricted roles;
- no reduction in security/data/provider/protected-action refusal coverage;
- no stale continuity or unreviewed semantic mutation at closure.
- record unknown-admission-state rate; a proposed initial ceiling is `5%`,
  subject to L0 evidence and core review.

### WS-8 — Finding-to-learning integration

Route this program through `GOVERNANCE_CONTROL_PLANE` with:

- candidate defect class for L0 validation: `GOVERNANCE_AMPLIFICATION`;
- initial disposition: `MACHINE_CHECK_CANDIDATE`;
- supporting dispositions: `PHASE_GATE_PLACEMENT_GAP`,
  `DESIGN_REVIEW_REQUIRED`, `STANDARD_UPDATED`, `TEMPLATE_UPDATED`;
- learning state progression:
  `OBSERVED -> REPRODUCED -> SIMULATED -> PILOTED -> ADOPTED`;
- rollback state: `REJECTED_OR_REVERTED` with retained evidence.

No single project incident may silently rewrite global policy. Promotion must
require cross-project replay and human approval.

### WS-9 — Cross-project pilot and migration

Pilot on at least:

1. `shift-operations-workspace` using the P3-A replay corpus;
2. one low-risk documentation/tooling tranche;
3. one security/provider/data-governed tranche.

Compare legacy and candidate modes using identical intents and acceptance
criteria. The candidate wins only if governance cost falls without loss of
control coverage or evidence fidelity.

The pilot must include an untreated or historical baseline so ordinary agent
and Windows-environment learning is not misattributed to the core change. If
amendment density falls similarly without the candidate controls, report the
learning-curve null hypothesis rather than claiming causal improvement.

### WS-10 — Public release and downstream adoption

Core release deliverables:

- updated standards/templates;
- executable admission and capability checks;
- plan schema/runner or reference implementation;
- migration guide and compatibility mode;
- governance-tax benchmark report;
- public-safe learning receipt;
- versioned core commit and release note.

Downstream adoption sequence:

1. update the hidden core through the sanctioned workspace reconciler;
2. update `.cvf/manifest.json` pin in a separate downstream tranche;
3. run doctor and compatibility checks;
4. supersede or reduce the downstream runner Work Order;
5. replay P3-A incidents under old and new behavior;
6. independently review results;
7. FREEZE only the bounded adoption claim.

## 7. Staged tranche plan inside CVF core

This is a conditional sequence, not authorization to execute nine tranches.
Commit only to L0 at intake. Each funding gate may shrink or stop the program.

### Stage A — evidence commitment

1. `CVF-GOVERNANCE-LATENCY-L0`: public-safe evidence ledger, blind incident
   classification, authority-consumption reconstruction, normalized benchmark,
   cheap-alternative inventory and independent review.

**Gate A:**

- `PROCEED_FULL` when systemic amplification remains material after
  normalization and multiple workstreams have incremental value;
- `PROCEED_WS2_ONLY` when capability enforcement is supported but the broader
  causal case is weak;
- `DEFER_LEARNING_CURVE` when untreated comparable work is improving at a
  similar rate;
- `STOP_NO_MATERIAL_CASE` when expected benefit does not exceed program cost.

### Stage B — design and contracts, only after Gate A

Scope Stage B from the Gate A disposition:

- for `PROCEED_WS2_ONLY`, L1 DESIGN and L2 SPEC cover only capability profiles,
  zero-network enforcement, portability, compatibility, adversarial denials
  and evidence. Then run a bounded L3 capability BUILD, independent REVIEW and
  release/closure; do not design or imply admission, fidelity, repair-envelope,
  runner or continuity work;
- for `PROCEED_FULL`, use the complete sequence below.

2. `CVF-GOVERNANCE-LATENCY-L1`: full DESIGN for admission state, capability
   profiles, fidelity modes, repair envelope, continuity and compatibility.
3. `CVF-GOVERNANCE-LATENCY-L2`: full SPEC, schemas, adversarial controls and
   rollback/receipt contracts. F1-F7 become mandatory negative fixtures.

**Gate B:** unresolved admission, crash recovery, capability mechanism,
compatibility or cost-ceiling decisions block BUILD. A cheaper configuration or
template solution must be preferred when it satisfies the same acceptance
criteria.

### Stage C — smallest high-confidence implementation

4. `CVF-GOVERNANCE-LATENCY-L3`: capability profiles and zero-network proof
   first, because this is the strongest independently evidenced failure class.
5. `CVF-GOVERNANCE-LATENCY-L4`: approval/admission state machine and durable
   receipts, only if Gate A selected `PROCEED_FULL`.

**Gate C:** run a bounded replay after L3. Stop or ship WS-2 alone if the
capability slice captures most measured benefit or if broader implementation
cost exceeds the revised budget.

### Stage D — broader automation, only after Gate C

6. `CVF-GOVERNANCE-LATENCY-L5`: machine plan compiler/runner, built from the
   core SPEC rather than copied from the failed downstream prototype.
7. `CVF-GOVERNANCE-LATENCY-L6`: continuity/finality and template migration by
   extending the existing machine-readable state model where feasible.
8. `CVF-GOVERNANCE-LATENCY-L7`: replay benchmark and cross-project pilot with
   untreated/historical baselines.
9. `CVF-GOVERNANCE-LATENCY-L8`: independent final review, public release and
   FREEZE of only the evidence-supported claim.

Each tranche must use the core's current control chain and cannot claim new
behavior before source, tests and evidence exist. Governance-behavior claims
require whatever real-provider evidence the core policy mandates; mock
evidence cannot substitute. Governance cost for this program must be included
in its own WS-7 metrics.

## 8. Decision gates

Before DESIGN closes, core maintainers must decide:

1. exact admission event for filesystem, database, Git and provider actions;
2. whether bounded pre-admission correction reuses the same acknowledgment or
   requires an automatically derived execution token;
3. maximum repair-envelope attempts and escalation rules;
4. capability enforcement mechanism on Windows, Linux and CI;
5. canonicalization rules by artifact type;
6. receipt durability and crash-recovery model;
7. compatibility behavior for existing downstream AGENTS contracts;
8. who owns governance-tax SLO exceptions and expiration;
9. maximum total program latency/turn/approval budget and tranche stop rules;
10. whether L0 supports `PROCEED_FULL`, `PROCEED_WS2_ONLY`,
    `DEFER_LEARNING_CURVE` or `STOP_NO_MATERIAL_CASE`;
11. how Git-object identity (current SHA-1-sized HEAD and possible future hash
    formats) is represented separately from SHA-256 artifact digests;
12. which existing active-state fields can be extended instead of creating a
    second authority-state system.

Unresolved decisions block SPEC; they must not be hidden in implementation.

## 9. Non-goals and safety boundary

This roadmap does not authorize:

- weakening identity, approval quorum, data-scope, DLP, provider or protected
  action controls;
- retrying an admitted/consumed R2 operation;
- automatic policy mutation from agent feedback;
- committing downstream source into the CVF core;
- treating provider/chat memory as canonical truth;
- claiming production readiness from local replay;
- bypassing independent review.

## 10. Shift-operations final park disposition

The wait/review lane has ended:

1. Claude completed the exact-eight runner candidate and reported green gates;
2. Codex independently returned `REVIEW_CHANGES_REQUIRED`, F1-F7, no waiver;
3. Claude accepted all findings and retracted the overbroad BUILD conclusion;
4. the operator chose evidence retention, not repair or deletion;
5. the exact-eight candidate, BUILD review, this roadmap, Claude handoff, paper
   replay and self-critique remain local, unstaged and uncommitted;
6. project continuity is `PARKED_REVIEW_CHANGES_REQUIRED_LOCAL_EVIDENCE_ONLY`;
7. no runner R2 may be reused or retroactively recognized;
8. no downstream commit or push is authorized for this evidence set.

The original machine/workspace is intentionally retained. Before any future
downstream action, verify the frozen checksums in
`SESSION/handoffs/AGENT_HANDOFF_2026-08-04_GOVERNED_PLAN_RUNNER.md`, staged
paths zero and the parked continuity state. Any mismatch triggers evidence-
integrity review before fresh INTAKE.

## 11. Resume packet for the future CVF core session

The core session must begin by reading:

- core `AGENTS.md` and active handoff;
- the governance-tax fitness function;
- error-to-governance learning philosophy;
- commit-steward latency standard;
- Work Order finding-to-governance lanes;
- this downstream roadmap;
- `GOVERNED_PLAN_RUNNER_BUILD_INDEPENDENT_REVIEW.md`;
- `CLAUDE_HANDOFF_TO_CODEX_2026-08-04.md`;
- `CVF_GOVERNANCE_LATENCY_L0_5_PAPER_REPLAY_2026-08-04.md` and its companion
  `CVF_GOVERNANCE_LATENCY_L0_5_SELF_CRITIQUE_2026-08-04.md` as hypotheses and
  counterarguments, not accepted metrics;
- P3-A Work Orders/reviews only as evidence, not as core authority.

First core action: author a public-safe L0 evidence packet and independently
verify incident classification, authority consumption, cycle avoidance and
normalized density. Do not read Claude's replay table before completing the
blind classification. Do not begin core BUILD from this downstream roadmap.

## 12. Definition of done

L0 is complete when it has an independent disposition and reproducible evidence
for Gate A. It may validly stop or defer the broader program.

If Gate A selects `PROCEED_WS2_ONLY`, the bounded capability problem is closed
only when zero-network profiles and their adversarial proofs are released; the
broader latency hypothesis remains explicitly deferred, not silently solved.

If Gate A selects `PROCEED_FULL`, the broader problem is treated as resolved
only when:

- core policy has an executable approval-consumption boundary;
- zero-network capability is technically enforced;
- pre-R2 plan validation catches the recorded mechanical defect classes;
- semantic and byte-exact fidelity modes are tested;
- continuity self-reference loops are eliminated;
- mechanical repair envelope boundaries are machine-checked;
- governance-tax regression metrics pass the cross-project pilot;
- core release is independently reviewed and pushed;
- shift-operations adopts the release through a reviewed core-pin update;
- P3-A and cross-project replay show the evidence-derived cycle-avoidance target
  with no control regression and with total program cost included.
