# ADR — Project Operations Skill Architecture

- ADR: `ADR-PROJECT-OPERATIONS-SKILL-001`
- Tranche: `PROJECT-OPERATIONS-SKILL-2026-08-02`
- Phase: `DESIGN`
- Risk: `R2`
- Status: `INDEPENDENT_DESIGN_REVIEW_PASS`
- Parent: INTAKE commit `66c93825cc872a5a1eb423e7a7796b802fd9e82a`

## Context

Agents repeatedly need the same project-specific operating sequence: resolve
the portable CVF binding, rehydrate canonical continuity, distinguish the
seven-step control chain from the five-phase roadmap, declare role/risk,
respect exact Work Orders, collect honest evidence, obtain independent review,
and separate BUILD from C4 closure. Re-copying those rules into prompts is
costly and drifts. A reusable skill can route an agent to current truth, but it
must not become a second policy or continuity source.

## Decisions

### D1 — Portable source, separate installation

The versioned source will be `skills/operate-shift-workspace/`; skill name and
folder are `operate-shift-workspace`. BUILD will initialize it with the
skill-creator's `init_skill.py`, not hand-scaffold it. Repository source is not
an installed personal skill. Any later write to a Codex/agent home, marketplace
or other external location requires separate explicit authority after FREEZE.

### D2 — Minimal artifact shape

Initial source contains only:

```text
skills/operate-shift-workspace/
├── SKILL.md
└── agents/openai.yaml
```

No `README`, changelog, quick reference, assets, copied policy, bundled
knowledge or duplicated project scripts are allowed. Add a bundled resource
only through a reviewed amendment proving it is necessary.

### D3 — Dynamic canonical-truth routing

`SKILL.md` remains concise and imperative. It directs the agent to resolve the
current working project's `AGENTS.md`, `.cvf/manifest.json`, `.cvf/policy.json`
and manifest-declared continuity/docs at runtime. It never embeds commit hashes,
absolute paths, active handoff names, test counts, next moves or policy prose
that can stale. It treats `SESSION/` as canonical only after the project
manifest/AGENTS contract says so, and treats `CVF_SESSION/` as a mirror here.

### D4 — Workflow contract

The skill routes these bounded operations:

1. resume/recover context and emit a fresh CVF declaration;
2. open a tranche at INTAKE and classify risk/authority;
3. advance DESIGN→SPEC→WORK_ORDER without skipping review;
4. hand a worker an exact changed set, evidence order and stop conditions;
5. independently review/repair without self-approval;
6. commit/push a reviewed BUILD and close with a separate C4;
7. stop on continuity drift, missing authority, mock governance proof, secret,
   out-of-workspace action, outside path, failed gate or destructive ambiguity.

The skill gives navigation/procedure, never permission. Canonical source,
tests, receipts and independent verdicts remain authoritative.

### D5 — Reuse existing deterministic tools

The skill invokes repository-owned doctor, session, catalog, file-size and
repository validators discovered from the current project. It does not wrap or
fork them initially. Shell commands are examples only after path resolution;
they cannot silently commit, push, install or call a provider.

### D6 — Validation and evidence layers

BUILD validation must include all four layers:

1. skill-creator `quick_validate.py` for name/frontmatter/layout;
2. project contract tests for required routing and forbidden stale/secret/
   provider-named/auto-side-effect content;
3. independent forward tests with fresh agents given the raw skill path and
   realistic resume/open/review scenarios, without leaking expected answers;
4. if closure claims the skill influences governance behavior, one sanitized
   real-provider API evidence run after zero-call refusal/admission gates.

Layer 4 proves only bounded instruction-following for synthetic project-safe
scenarios. It does not prove runtime enforcement, production safety or that a
prompt can replace CVF gates. Mock mode may test metadata/layout only.

### D7 — UI metadata

`agents/openai.yaml` is generated deterministically from the finalized skill
using skill-creator tooling. It contains only `display_name`,
`short_description` and `default_prompt` unless a later explicit requirement
authorizes more. It must remain semantically aligned with `SKILL.md`.

## Alternatives rejected

- **Write directly to `$CODEX_HOME/skills`:** violates the current workspace
  boundary and mixes portable source with machine-local installation.
- **Bundle copies of AGENTS/policy/continuity:** creates stale competing truth.
- **Provider-specific Claude/Codex branches:** violates provider-neutral roles.
- **One large reference pack:** defeats progressive disclosure and overlaps the
  next `PROJECT-KNOWLEDGE-PACK` tranche.
- **Structural validation only:** insufficient for any governance-behavior
  claim under the mandatory live-evidence rule.

## Acceptance approach for SPEC

SPEC must turn D1-D7 into exact trigger/frontmatter/body/metadata contracts,
forbidden-content checks, scenario expectations, live-evidence claim boundary,
changed-set ceiling, cleanup and rollback criteria. Installation stays outside
the tranche unless separately authorized.

## Unresolved tradeoffs

- Exact forward-test scenario count and whether a small dedicated live runner
  is necessary versus a reviewed reuse of existing sanitized provider support.
- Exact test/evidence/receipt paths and file-size allocation.

These are SPEC/WORK_ORDER decisions. No skill BUILD is authorized by this ADR.

## Independent design review

Verdict: `DESIGN REVIEW_PASS`, no open finding or waiver. The reviewer
confirmed D1-D7 align with skill-creator and project governance, including the
portable-source/install split, minimal shape, dynamic truth routing,
provider-neutral navigation-not-permission boundary, validator reuse and four
bounded validation layers. Exact scenarios/runner/paths remain deferred to
SPEC/WORK_ORDER. No implementation, installation or provider call was made.
