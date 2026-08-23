# Cross-Agent Invariant Learning — Independent DESIGN Review

- Tranche: `CROSS-AGENT-INVARIANT-LEARNING-2026-08-22`
- Role: `INDEPENDENT_DESIGN_REVIEWER` (independent from `DESIGN_AUTHOR`/`ORCHESTRATOR`)
- Reviewed document: `docs/decisions/DESIGN_2026-08-22_CROSS_AGENT_INVARIANT_LEARNING.md`
- Execution base / HEAD: `319c6a809ef29134a0de8c4a9923bb18669c349c` (unchanged)
- Disposition: `DESIGN_REVIEW_PASS`
- Findings / waivers: `NONE` / `NONE`

## Continuity verification before review

`git rev-parse HEAD` returned `319c6a809ef29134a0de8c4a9923bb18669c349c`,
matching the execution base named by the active handoff and
`SESSION/ACTIVE_SESSION_STATE.json`. `git status --porcelain
--untracked-files=all` shows exactly 57 paths, staged `0`: 16 modified paths
and 41 untracked paths, all of which are either (a) the settled P4-B
`AI-PROVIDERS-2026-08-21` tranche's own artifacts (its INTAKE/DESIGN/SPEC/
Work Order/reviews/worker return/live-evidence receipt docs, the
`packages/ai-providers/` library, its tests, and the two live-evidence
runner scripts), already independently reviewed and `FREEZE / CLOSED_BOUNDED`
per `docs/decisions/P4B_AI_PROVIDERS_COMPLETION_REVIEW_2026-08-21.md`, or (b)
this tranche's own INTAKE-phase and DESIGN-phase documents (`INTAKE_2026-08-22
_CROSS_AGENT_INVARIANT_LEARNING.md`, its independent INTAKE review, the
DESIGN under review, and the active handoff). No `docs/cvf/
INVARIANT_FAMILY_STANDARD.md`, no `docs/cvf/invariants/` schema/registry/
matrix, no invariant contract module, no CLI guard, no change to `AGENTS.md`
or `skills/operate-shift-workspace/SKILL.md`, and no `scripts/testing/
validate_repository.py` edit exist anywhere in the changed set. This
confirms DESIGN did not slip into SPEC/WORK_ORDER/BUILD.

`SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json`,
`SESSION/ACTIVE_SESSION_STATE.json`, `SESSION/SESSION_MEMORY.md`, and the
active handoff `SESSION/handoffs/CROSS_AGENT_INVARIANT_LEARNING_2026-08-22.md`
agree exactly on mode (`cross_agent_invariant_learning_design_ready_for_
review`), phase (`DESIGN`), active role (`ORCHESTRATOR`), and next allowed
move (independent DESIGN review of this document). The role route recorded —
`CLOSER -> ORCHESTRATOR -> INTAKE_AUTHOR -> ORCHESTRATOR ->
INDEPENDENT_REVIEWER -> ORCHESTRATOR -> DESIGN_AUTHOR -> ORCHESTRATOR` — is
internally consistent and shows `DESIGN_AUTHOR` and the prior
`INDEPENDENT_REVIEWER` (INTAKE) as distinct occupants from this review's
role. No continuity drift found; `BLOCKED_CONTINUITY_DRIFT` does not apply.

The independent INTAKE review
(`docs/decisions/CROSS_AGENT_INVARIANT_LEARNING_INTAKE_REVIEW_2026-08-22.md`)
returned `INTAKE_REVIEW_PASS`, findings/waivers `NONE/NONE`, and named seven
acceptance questions DESIGN must resolve. This review checks the DESIGN
against those seven plus the twelve points named in the current review
instruction, since the two lists overlap but are not identical (the review
instruction adds explicit points on legacy-waiver bounding, matrix/registry
id agreement, and early-phase-execution verification).

## Review against the twelve required points

**1. Matrix is the sole canonical semantic owner.** DESIGN §3.1 states the
four layers have "non-overlapping authority" and explicitly: "The guide and
skill must not restate per-outcome field rules." §9 confirms `AGENTS.md` and
the skill "gain only a pointer" and the skill "does not become canonical
semantic storage." §3.2 requires family ids and paths to be unique and
registry/matrix ids to "agree exactly," which forecloses a second
registration silently shadowing the same family. Held.

**2. Contract matrix is independent of emitter/model/schema
implementation.** §4 states the matrix "is authored from the approved
DESIGN/SPEC contract, not exported from Pydantic models, JSON Schema,
service code, fixtures or provider output," and requires digest-pin
ordering (matrix digest pinned *before* BUILD adapter code) so the
independence is structurally checkable, not just asserted in prose. §5.1
adds that "synthetic shapes validate the reusable mechanics only; they
cannot replace an applicable tranche's real-emitter positives" — closing
the loophole where a hand-rolled fixture could stand in for a real service
emission. §12's rejected-alternative 3 ("Generate contract and tests from
implementation") names the exact failure mode this design is built to avoid
and is consistent with the P4-B history, where every repair round closed
the reviewer's exact probe while an adjacent shape stayed open precisely
because tests were derived from what the implementation already did. Held.

**3. Mutation basis closes the adjacent-invariant-family class, not just
named probes.** §5.3 lists nine mutation classes (required-field deletion,
forbidden/unknown-field insertion, discriminator replacement including one
unknown value, enum/type/value-domain legal-to-illegal changes,
conditional-field null/absent flips, numeric/counter relation mutations,
equality/digest/identity one-side changes, recursive nested-object
mutations, and closed-object extra-field mutations) plus the rule that
"each mutation must alter exactly one semantic fact relative to its valid
parent" and that any inapplicable operator needs a recorded, independently
accepted reason. Cross-checked against the actual P4-B finding lineage in
`P4B_AI_PROVIDERS_COMPLETION_REVIEW_2026-08-21.md`: F5/F5-R1/F5-R2/F5-R3 were
all "adjacent shape in the same outcome family survives a fix that closed
only the named example" failures (ghost `rule_id`, `rules_evaluated=0`,
missing provider/model ids, wrong counter on the *sibling* outcome,
`provider_attempts=0` on the sibling of the one already-fixed case). Every
one of those historical gaps is a direct instance of one of §5.3's
enumerated classes (conditional-field flip, numeric/counter mutation,
one-side equality mutation). The basis is not merely plausible in the
abstract — it demonstrably would have caught the actual repeat-finding
pattern this tranche exists to prevent. Held.

**4. Model/schema parity covers accept and reject.** §5.2: "The same
canonical corpus is submitted to every declared validator surface. For
each case, all validators must agree on accept/reject." This is explicitly
bidirectional (not "reject" alone, which would miss the P4B-REV-F5 pattern
where the model over-accepted relative to schema, and not "accept" alone,
which would miss under-acceptance). The "single-surface family records
parity as not applicable and names the reason" clause is a legitimate
scope-narrowing (parity is undefined with one surface), not a weakening of
the bidirectional requirement when two or more surfaces exist — and §3.2
requires "declared representation surfaces" to be stated up front, so a
family cannot silently claim single-surface status to dodge parity after
the fact; that claim itself is matrix content subject to the same
independent-authorship and review discipline as everything else. Held.

**5. Applicability/rollout does not over-apply to unrelated tranches.**
§2 ties mandatory registration to six concrete triggers (shared receipt/
model contract, required/forbidden/conditional field changes, exact
counter relations, multi-surface representation, coupled-artifact
requirements, or a prior finding exposing an adjacent family member) and
explicitly exempts "R0/R1 work and R2/R3 work without a trigger." §10 pins
initial rollout to `NEW_OR_MATERIALLY_CHANGED_TRIGGERED_FAMILIES` and states
plainly that "P4-B is historical motivation only; its settled receipts and
review remain untouched" and that legacy tranches are "not retrofitted
merely by installing the mechanism; registration becomes mandatory only
when their triggered contract surface is materially changed." This matches
the INTAKE's own constraint boundary and does not reach into P4-A/P4-A2/
P4-A3 or any other closed tranche. Held.

**6. Ownership binding does not overclaim arbitrary-duplicate detection.**
§6 states plainly: "The design intentionally does not promise semantic
duplicate detection across arbitrary source code; an unregistered duplicate
remains reviewable as a finding." The guard's actual claim is narrower and
structural: "declared owner uniqueness, consumer path uniqueness, path
existence and allowed strategy" (§8) for *registered* coupled artifacts
only. This is an honest claim boundary, not a silent gap — it correctly
distinguishes "we detect drift among things we already know are coupled"
from "we detect any two files in the repo that happen to encode the same
fact," which is the P4B-LIVE-F1 root cause (an independently duplicated
schema) but not a general static-analysis promise. Held.

**7. AGENTS/skill/Knowledge routing uses pointers, not copied rules.** §9:
the skill "gains only a pointer... It does not become canonical semantic
storage," `AGENTS.md` "gains a compact mandatory trigger/pointer rule," and
Project Knowledge's `GOVERNANCE_BOUNDARIES.md` "cites the standard." §3.1
reinforces this from the matrix side: "The guide and skill must not restate
per-outcome field rules." No excerpted rule text, per-outcome table, or
mutation list is proposed for duplication into any of these three surfaces.
Held.

**8. Work Order and reviewer share matrix id/digest.** §7: the shared
`Invariant-family proof` template section "contains matrix id/digest,
applicability decision, adapter/test paths, mutation exclusions, exact
commands and evidence owner. The template does not copy matrix rules," and
"the reviewer independently recomputes the matrix digest, reruns the same
corpus... and verifies that no matrix expectation was derived during
BUILD." This is a real independence check (recomputed, not trusted from the
worker return), consistent with this project's general reviewer-independence
discipline in `AGENTS.md` and the skill. Held.

**9. Legacy waiver is bounded, expiring, and independently approved.** §10:
"A legacy waiver is registry-scoped, temporary and fail-closed. It must name
the family, owner, exact missing obligation, reason, expiry or removal
trigger and independent approval artifact. A waiver cannot suppress
malformed JSON, unknown fields, path safety, duplicate ownership or stale
digest failures. Waivers cannot be created by IMPLEMENTATION_WORKER or
accepted silently." All four review-instruction sub-requirements are present
verbatim: bounded (registry-scoped + named missing obligation), expiry
(explicit expiry/removal trigger field), independent approval (named
artifact requirement, explicit worker-cannot-self-issue clause), and a
floor of non-waivable structural failures. Held.

**10. Claim/live-provider boundary follows `AGENTS.md`.** §11 requires BUILD
mechanics to be "deterministic and require zero provider/network calls,"
limits their proof scope to "matrix parsing, repository guarding, test
generation, adapter parity and canonical binding," and routes any stronger
claim ("a real AI agent consumed the repository learning and followed it")
through "a separately authorized bounded live checkpoint" with the same
shape this project already uses for P4-B (zero-call refusal/preflight
first, at most one admitted call, retained failed lineage, no secrets, and
a claim limited to "that exact provider/run"). It also offers the narrower
non-live closure path explicitly. This mirrors `AGENTS.md`'s Live
Governance Evidence Rule and the project's Mandatory Governance Proof
section without carving any exemption for this tranche. Held.

**11. No SPEC, WORK_ORDER or BUILD executed early.** Verified directly
against the actual changed set (see Continuity verification above): zero
new/modified paths outside the P4-B settled set and this tranche's own
INTAKE/DESIGN documents. §1, §13, and §15 all state SPEC/WORK_ORDER/BUILD/
provider/network/install/database/commit/push/deployment are `NONE` and
that the DESIGN stops at `READY_FOR_INDEPENDENT_DESIGN_REVIEW`. Matches the
verified repository state exactly. Held.

**12. Proposed artifact classes are sufficient for a later SPEC to set an
exact-path ceiling.** §13 enumerates nine bounded classes (this tranche's
own phase documents; `AGENTS.md` + the named skill; "one" guide/schema/
registry/synthetic-matrix; "one" contract module + "one" CLI guard;
repository-validator integration plus focused tests; "one" shared template;
Project Knowledge boundary text/manifest pin; the standard continuity
surfaces; an optional gated live-runner class) and explicitly excludes
application domain, P4-A/A2/A3/P4-B runtime, database, API/UI, provider
adapter/configuration, and CVF Core paths. The repeated singular counts
("one CVF standard guide, one schema, one registry and one synthetic
matrix," "one reusable invariant contract module and one CLI guard," "one
shared Work Order/reviewer checklist template") give a later SPEC concrete,
countable path slots rather than an open-ended class description, which is
what an exact-path Work Order ceiling needs. Held.

## Additional cross-check: matrix shape vs. schema-agreement requirement

DESIGN §3.2 requires "Registry and matrix ids must agree exactly" as a
structural matrix/registry-shape rule. This directly answers acceptance-
question-8-adjacent review point 8 (Work Order/reviewer using the same
matrix id/digest) at the schema level, not only the template-usage level:
even before any Work Order references a matrix, the registry itself cannot
carry a drifted id relative to the matrix file it points to. This is a
genuine structural closure, not merely a procedural convention.

## Points not decided by this DESIGN (correctly deferred)

Consistent with control-chain discipline, this DESIGN does not fix exact
file paths (left to SPEC per §13), does not write the schema/registry/guard
code (BUILD), and does not pre-approve a live checkpoint (§11, gated on
separate authority). None of these deferrals weaken the twelve review
points above; each is explicitly named as SPEC/WORK_ORDER/BUILD-phase work
in §13 and §15.

## Review boundary and effect

This review confirms the DESIGN is internally consistent, independently
authored relative to any implementation, closes the actual P4-B
adjacent-family repeat-finding pattern by construction (not merely by
assertion), does not overclaim guard capability, does not over-apply to
unrelated or legacy tranches, keeps the live-evidence claim boundary intact,
and gives a later SPEC enough artifact-class structure to set an exact-path
ceiling. It does not evaluate or author any SPEC, WORK_ORDER, or BUILD
content, and it grants no such authority.

No source, `AGENTS.md`, skill, validator, schema, registry, matrix, or test
file was created, modified, or deleted during this review. No provider or
network call, credential use, install, database mutation, commit, push, or
deployment occurred.

## Disposition

`DESIGN_REVIEW_PASS`, findings/waivers `NONE`/`NONE`.

Only the `ORCHESTRATOR` may request fresh `SPEC` authority next. This review
does not open `SPEC` itself and grants no `WORK_ORDER` or `BUILD` authority
at any point in the future chain.

---

## Amendment 1 independent DESIGN review — 2026-08-23

- Reviewed DESIGN SHA-256:
  `ead2ac34f7d7ef16f2e2a942ad47ab2d69cde8a5dae1c9fd38d7b93f89bfe83c`
- Trigger: completion rereview round 1 `F6-R1`
- Role: `INDEPENDENT_DESIGN_AMENDMENT_REVIEWER`
- Disposition: `DESIGN_AMENDMENT_REVIEW_PASS`
- Findings / waivers: `NONE` / `NONE`

The amendment is the minimum correction to the accepted dependency boundary.
It authorizes only the repository-declared `jsonschema` dependency already
available in the stable runtime for Draft 2020-12 validation. It prohibits
install, upgrade, substitution, download and silent validation reduction, and
makes missing/incompatible availability fail closed.

The objective, R2 ceiling, schema/Python ownership split, deterministic and
sanitized diagnostics, matrix-adapter non-execution rule, zero-external-effect
class, exact-27 implementation union and claim boundary are unchanged. SPEC
v1.0 remains byte-exact because it already requires Draft 2020-12 validation
without claiming dependency-free execution. No matrix/source pin changes.

Review recomputed the pre-amendment exact-4 governance preimages and the
amendment isolation baseline. At review time: HEAD/origin remained
`319c6a809ef29134a0de8c4a9923bb18669c349c`, status `78`, staged `0`; the
protected set excluding exact-27, exact-4 amendment paths and reviewer-owned
path 28 remained count `46`, SHA-256
`1ddda7de1e54064ee7839b670291d27d39ddca3577137ea5ee3e9c7d0fcfc140`.

This PASS authorizes no implementation by itself. Proceed only to the bounded
Work Order amendment and its independent authorization review under the
operator's explicit Amendment authority.

---

## Amendment 2 independent DESIGN review — 2026-08-23

- Role: `INDEPENDENT_DESIGN_AMENDMENT_REVIEWER`
- Disposition: `DESIGN_AMENDMENT_2_REVIEW_PASS`
- Findings / waivers: `NONE` / `NONE`

The reviewed amendment ratifies exactly the three operator-named paths and
their supplied hashes as an artifact redistribution: one ownership helper and
two split test files. Each hash was independently recomputed byte-exact. The
three files remain within the existing contract, ownership and repository-
guard artifact classes and introduce no runtime/product/provider route.

The exact implementation union is now 30; reviewer path 28 remains reviewer-
owned/read-only despite its historical ordinal label, and “path 31” means any
additional implementation or governance path and is prohibited. Objective,
R2 ceiling, external-effect class, dependency boundary, matrix authority and
claim boundary remain unchanged. This PASS grants only progression to the
bounded SPEC/Work Order amendment and their independent reviews; it grants no
BUILD, provider, Git or deployment authority.
