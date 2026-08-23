# WORK ORDER — Cross-Agent Invariant Learning

- Tranche: `CROSS-AGENT-INVARIANT-LEARNING-2026-08-22`
- Date: `2026-08-23`
- Phase: `WORK_ORDER`
- Risk: `R2`
- Status: `READY_FOR_INDEPENDENT_AUTHORIZATION_REREVIEW`
- Parent SPEC: `docs/specs/CROSS_AGENT_INVARIANT_LEARNING_SPEC.md` v1.0
- Parent SPEC canonical SHA-256:
  `082cb5c1667b4d4685b3613d6654bda67552b6709416caafe8cd64ecf653b1b5`
- Execution base HEAD/origin:
  `319c6a809ef29134a0de8c4a9923bb18669c349c`
- Provider/network/install/database/commit/push/deployment budget: `0`

## 1. Objective

Implement SPEC R1-R22 and AC-01..AC-18 as a provider-neutral,
repository-native invariant-family standard, closed machine declarations,
deterministic repository guard, synthetic mechanics proof and shared
Work Order/reviewer routing. Do not retrofit or modify P4-B or any application
runtime.

This document authorizes nothing by itself. BUILD requires both an independent
authorization review PASS and a fresh explicit human BUILD approval for this
exact Work Order.

## 2. Exact 27-path worker ceiling

The `IMPLEMENTATION_WORKER` may create or modify exactly these paths and no
others. Every path must differ from its pre-BUILD preimage at return; an
unnecessary path requires a reviewed SPEC/Work Order reduction before BUILD.

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

Path 9 is the reviewed minimal synthetic emitter required by DESIGN §8/§10 and
SPEC R8/R14; it is not an application or provider runtime surface.

## 3. Reviewer and governance-owned paths

Only the independent completion reviewer may create path 28:

28. `docs/decisions/CROSS_AGENT_INVARIANT_LEARNING_COMPLETION_REVIEW_2026-08-23.md`

It is read-only to the worker. No path 29 exists or is reserved.

These pre-BUILD governance paths are also read-only to the worker:

- `docs/decisions/INTAKE_2026-08-22_CROSS_AGENT_INVARIANT_LEARNING.md`
- `docs/decisions/CROSS_AGENT_INVARIANT_LEARNING_INTAKE_REVIEW_2026-08-22.md`
- `docs/decisions/DESIGN_2026-08-22_CROSS_AGENT_INVARIANT_LEARNING.md`
- `docs/decisions/CROSS_AGENT_INVARIANT_LEARNING_DESIGN_REVIEW_2026-08-22.md`
- `docs/specs/CROSS_AGENT_INVARIANT_LEARNING_SPEC.md`
- `docs/decisions/CROSS_AGENT_INVARIANT_LEARNING_SPEC_REVIEW_2026-08-23.md`
- `docs/work_orders/CROSS_AGENT_INVARIANT_LEARNING_WORK_ORDER.md`
- `docs/decisions/CROSS_AGENT_INVARIANT_LEARNING_WORK_ORDER_AUTHORIZATION_REVIEW_2026-08-23.md`

The independent authorization reviewer may create or amend only the final path
above, retaining prior review lineage on rereview.
It must recompute the Work Order/SPEC hashes and exact baseline before returning
`AUTHORIZATION_REVIEW_PASS`, `AUTHORIZATION_REVIEW_CHANGES_REQUIRED` or a
precise blocker.

After that review, the ORCHESTRATOR performs read-only verification and asks
for human BUILD authority without editing any §6 preimage or protected path.
The authorization-review artifact is the additive transition receipt. The
worker records BUILD authority/role acknowledgment as its first exact-27 edit
only after G6 passes. If any pre-BUILD continuity sync is required sooner, stop,
rebaseline this Work Order and repeat authorization review.

## 4. Dirty-worktree isolation contract

This repository intentionally contains settled, unstaged P4-B and current
governance work. BUILD must preserve unrelated user/project changes rather than
requiring a clean worktree.

The authorization baseline before this Work Order contained 59 status paths,
staged 0, at the execution base above. At final authoring sync, the protected
dirty set is every status path outside the exact 27 plus the two Work Order
review paths. Its canonical algorithm is:

1. read `git status --porcelain=v1 --untracked-files=all`;
2. normalize each path separator to `/`;
3. exclude the exact 27 and the Work Order/authorization-review paths;
4. for every remaining path emit
   `<two-character-status>\t<path>\t<raw-file-sha256-or-MISSING>`;
5. sort rows ascending by ordinal Unicode code-point order over the complete
   row (equivalent to ascending UTF-8 byte order for the permitted ASCII row
   alphabet); culture-aware/case-insensitive shell sorting is prohibited;
6. join with LF and one trailing LF; hash UTF-8 bytes with SHA-256.

Final authoring values are recorded in §5. Any count/digest drift stops before
BUILD. The worker reruns the same protected-set computation after every repair
and before return; it must remain byte-exact. The worker may not "clean up" or
stage settled P4-B/governance paths.

## 5. G6 pre-BUILD gate

Before any worker edit, require all of the following:

- fresh human BUILD authority quotes this tranche and exact-27 Work Order;
- independent authorization review is PASS with no unresolved finding;
- HEAD and origin/main both equal the execution base; staged count is zero;
- status count is exactly 61: the 59-path authoring baseline plus this Work
  Order and its authorization review, with no BUILD-created path yet;
- protected dirty-set count/hash equal the final values below:
  - count: `48`
  - SHA-256: `0ca6eeefcb88969c38063040839591e06e993c26f7c5394227b6a97dff12fb06`
- SPEC canonical SHA-256 equals the pin in the header;
- Work Order raw/canonical hash equals the value recomputed and recorded by the
  authorization reviewer; worker never trusts a copied chat hash;
- all 27 preimages equal §6; `ABSENT` paths remain absent;
- path 28 and every BUILD-created path are absent;
- `docs/templates/` is absent and expected to be created only through path 7;
- roadmap is exactly 600 lines; later edit is line-neutral or net-negative;
- canonical/bootstrap required-read lists are identical and at most 12; any
  new pointer rotates an entry rather than adding a thirteenth;
- bootstrap is at most 4096 bytes; no file-size exception/debt change;
- hidden Core is clean and equals manifest pin/origin/main;
- session, knowledge, catalog, file-size, repository and doctor gates pass,
  allowing only the existing bounded legacy-catalog warning.

No automatic repair is allowed at G6. Any mismatch returns a precise blocker.

## 6. Exact worker-path preimages

| # | Path | Raw SHA-256 preimage |
|---:|---|---|
| 1 | `AGENTS.md` | `ea41042f396d570272cf99be333b51be02f7cfb78cf26389703b2a27305892ac` |
| 2 | `skills/operate-shift-workspace/SKILL.md` | `3f59d6587536bd6569993f4228ee57cd8ce851ee3c27888d3ac2d33cbdaf829f` |
| 3 | `docs/cvf/INVARIANT_FAMILY_STANDARD.md` | `ABSENT` |
| 4 | `docs/cvf/invariants/invariant-family.schema.json` | `ABSENT` |
| 5 | `docs/cvf/invariants/registry.json` | `ABSENT` |
| 6 | `docs/cvf/invariants/synthetic-terminal-outcome.json` | `ABSENT` |
| 7 | `docs/templates/INVARIANT_FAMILY_PROOF.md` | `ABSENT` |
| 8 | `scripts/invariant_family_contract.py` | `ABSENT` |
| 9 | `scripts/invariant_family_synthetic_emitter.py` | `ABSENT` |
| 10 | `scripts/check_invariant_families.py` | `ABSENT` |
| 11 | `scripts/testing/validate_repository.py` | `2559240456dbe8d2e5d5d61537a3d7091f5d636fcf2a51944e414a54c76b3a97` |
| 12 | `tests/unit/test_invariant_family_contract.py` | `ABSENT` |
| 13 | `tests/integration/test_invariant_family_repository_guard.py` | `ABSENT` |
| 14 | `tests/cvf/test_invariant_family_agent_routing.py` | `ABSENT` |
| 15 | `knowledge/GOVERNANCE_BOUNDARIES.md` | `6c9ce47326b53320ce11d185e48338910e0ce6d0e2635fe80026f8d4575a55d4` |
| 16 | `knowledge/manifest.json` | `c88048ff8ca9f31ef503a664dc04f2ec68f6f252992f45cd8775c963ec505386` |
| 17 | `docs/INDEX.md` | `87a05670be04d097aeb3b66d4b9249f97dcdabfa8cc5a99a316575675e66362b` |
| 18 | `docs/catalog/MODULE_REGISTRY.json` | `f0045e8cfd89d2568f8ba95f69867e7aeef942c6a39a8471b88d0b3b2ed67327` |
| 19 | `docs/catalog/MODULE_CATALOG.md` | `f6dfde3aea48164fbe861b578770f179db4df96bf1a8590173b86901cc411e65` |
| 20 | `IMPLEMENTATION_STATUS.json` | `d3d4d10c5f219ee55669a4c6edb8e301a3e0212397da4993e9d5f3268793e058` |
| 21 | `docs/implementation/EXECUTION_ROADMAP.md` | `9dec952285797f242faa00fae90d5a8c8a88f74ecc8085b62566c0f6351529f6` |
| 22 | `SESSION/SESSION_MEMORY.md` | `5acca41762882f999b5d47a3a994e35105aeeef4b76f55e44d1d037e35b617fa` |
| 23 | `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json` | `eb1baaa7e64eb846ac00ee4473d6d3ae9df3db0c02b0b93ff951d0c823699813` |
| 24 | `SESSION/ACTIVE_SESSION_STATE.json` | `d63b783ac4f7fd982d5ddef5bcaa93af18ee12beb884df671ae604ead19b14ed` |
| 25 | `CVF_SESSION/ACTIVE_SESSION_STATE.json` | `243bbe152765cb2ff22c59acf17ca9102a04fdd89fc0f282214564a35bc2d08b` |
| 26 | `SESSION/handoffs/CROSS_AGENT_INVARIANT_LEARNING_2026-08-22.md` | `b16c8077dd848664598847787e07453ef505ad9bdcada9d8d5257abb167df648` |
| 27 | `docs/decisions/CROSS_AGENT_INVARIANT_LEARNING_WORKER_RETURN_2026-08-23.md` | `ABSENT` |

Preimages are raw on-disk SHA-256; `ABSENT` means the file must not exist at
G6. The authorization reviewer independently recomputes all 27.

## 7. Role and execution order

1. `INDEPENDENT_AUTHORIZATION_REVIEWER` reviews INTAKE, accepted DESIGN,
   accepted SPEC, this Work Order, exact paths, baseline and stop conditions.
2. Human operator grants fresh BUILD authority for this exact reviewed order.
3. A separate `IMPLEMENTATION_WORKER` rehydrates, declares the role, passes G6
   and implements only the exact 27.
4. Worker runs focused checks, repository gates and the full non-live suite in
   §10, updates path 27 and stops at `READY_FOR_REVIEW` or a precise blocker.
5. An independent `REVIEWER` creates only path 28, compares source/tests/output
   to SPEC and reruns permitted evidence without trusting worker PASS claims.
6. Findings return to `REPAIR_WORKER` only within the unchanged exact-27 set.
7. `CLOSER` may consider FREEZE only after independent REVIEW_PASS and any
   separately required live authority/evidence. Commit/push remain separate.

The same individual/provider instance that performs BUILD cannot perform the
independent completion review. Role labels remain provider-neutral.

## 8. BUILD contract

The worker must implement every SPEC requirement, including:

- one semantic-owner matrix and pointer-only routing;
- Draft 2020-12 closed structural schema plus Python semantic uniqueness;
- duplicate-key rejection, bidirectional registry/file-set validation and safe
  non-executable path resolution;
- bootstrap synthetic `ACCEPTED`/`REFUSED` family exactly as SPEC R14;
- real deterministic synthetic emitter positives, complete R10 one-fact
  mutations and honest one-surface parity N/A;
- test-double proof of false-accept and false-reject parity detection;
- declared ownership strategies without arbitrary duplicate-discovery claims;
- deterministic sanitized `IFC_` diagnostics and disposable summaries cleaned
  on PASS and induced failure;
- repository-validator integration, shared template, AGENTS/skill pointers and
  existing three-document Project Knowledge routing;
- exact pin/catalog/status/continuity regeneration without hand-editing derived
  catalog truth.

The guard must not dynamically import matrix-declared symbols, infer authority
from Git tracking state, access credentials, or execute provider/network/
database/external-write behavior.

## 9. Operational constraints from SPEC review

- `OBS-1`: path 21 must finish at <=600 lines with no exception/debt edit.
- `OBS-2`: paths 23/24 must carry identical required reads <=12; prefer pointer
  routing over adding another startup read.
- `OBS-3`: path 7 is the only authority to create `docs/templates/`.
- All new/changed `.py` files must remain <=300 lines; every `.md` <=600.
- Do not compress code/assertions merely to pass line limits; split only within
  the already-authorized exact paths or stop for amendment.
- P4-B live receipts/reviews and every P4 runtime source/test stay byte-exact.

## 10. Required evidence order

Use the stable existing runtime; install is forbidden. On this machine the
known stable executable is:
`C:\Users\DELL\AppData\Local\cvf-p4a-py313-venv\Scripts\python.exe`.

Run and record exact commands/results in this order:

1. focused unit test for invariant contract/schema/registry/mutations;
2. focused repository-guard integration test;
3. focused AGENTS/skill/Knowledge routing test;
4. `python scripts/check_invariant_families.py`;
5. `python scripts/check_invariant_families.py --json`;
6. `python scripts/check_project_knowledge.py`;
7. `python scripts/check_session_state.py`;
8. `python scripts/generate_catalog.py --check`;
9. `python scripts/check_file_size.py`;
10. `python scripts/testing/validate_repository.py`;
11. full non-live `python -m pytest -q`;
12. parse every changed JSON, exact worker delta/preimage/protected-set checks,
    staged-zero, residue scan, changed-set secret scan without printing values,
    `git diff --check`, HEAD/origin check and workspace doctor.

Tests must execute the R15 failures, including false-accept/false-reject,
duplicate ids with differing fields, induced cleanup failure and repository
entry-point propagation. Source-string assertions alone are insufficient.

## 11. Exact external-effect budget

- provider/API/network calls: `0`
- retries: `0`
- credential reads/prints/writes: `0`
- installs or environment substitutions: `0`
- database/migration operations: `0`
- commits/pushes/deployments/staging: `0`
- CVF Core/workspace-root writes: `0`

Mocks/test doubles are permitted only for generic parity-helper mechanics, not
as evidence that AI governance or a real runtime family is controlled.

## 12. Worker return

Path 27 must record:

- role declaration and G6 result;
- execution base, SPEC/Work Order hashes and exact-27 classification;
- protected-set count/digest before and after;
- R1-R22/AC-01..18 evidence map;
- focused/full/gate commands and exact results, skips and warnings;
- each JSON/mutation/parity/ownership/cleanup/secret/residue result;
- line counts for every changed executable/Markdown near its limit;
- staged/provider/network/install/database/commit/push/deployment counts;
- honest claim boundary and open findings.

Return `READY_FOR_REVIEW` only when every requirement passes. Do not create or
edit path 28, self-review, declare FREEZE, request/execute a live call, stage,
commit or push.

## 13. Review and repair contract

The independent reviewer must recompute all pins, preimages, protected-set
digest, emitted positives, full mutation corpus, parity disagreement probes,
ownership binding, diagnostics, cleanup and repository integration. It must
inspect actual source and outputs rather than accept path 27's assertions.

All findings are returned together in one consolidated pass where possible.
A repair worker may continue within this order only when objective, matrix
contract/digest, exact paths, risk and external-effect class are unchanged. Any
new/substituted path, SPEC change, provider call, install, database, commit,
push or deployment requires a reviewed amendment and fresh authority. At round
three without an independent new root cause, record
`REVIEW_COST_ESCALATION_REQUIRED`.

## 14. Stop conditions

Stop immediately on missing authority/review, G6 mismatch, protected-set drift,
path 28/work-order/review mutation, path 29, unnecessary exact path, path
overflow, matrix/SPEC conflict, dynamic import, external effect, secret
exposure, P4/Core diff, file-size overflow, required-read/roadmap overflow,
staged residue, cleanup failure, test/gate failure, self-review or broadened
claim. Do not silently reduce acceptance or create a waiver.

## 15. Rollback

Before commit, restore only the exact 27 to their §6 preimages and delete only
those marked `ABSENT`; never touch the protected dirty set or governance review
history. Verify the protected 48-path digest plus the Work Order and
authorization-review paths (61 total status paths), then rerun all non-consuming
gates. After any separately authorized future commit, rollback is a new
corrective commit; no amend/reset/force-push.

## 16. Claim boundary

Later PASS may claim only that repository-native invariant-family guidance,
closed declarations, deterministic guard and synthetic conformance mechanics
were installed and independently tested. It cannot claim universal agent
compliance, automatic undeclared-duplicate discovery, P4-B retrofit, provider
or runtime AI governance, production readiness, or absence of future findings.

A claim that a real agent consumed/followed the rule requires separately
authorized post-review live evidence and is not part of this Work Order.

## 17. Current stop condition

Stop at `READY_FOR_INDEPENDENT_AUTHORIZATION_REREVIEW`. BUILD remains
unauthorized until both independent authorization PASS and fresh explicit human
BUILD approval. Provider call, install, database, staging, commit, push and
deployment remain unauthorized.

## 18. Authorization repair round 1 — WO-F1

The first independent authorization review returned
`AUTHORIZATION_REVIEW_CHANGES_REQUIRED` with blocking `WO-F1`: count 48 was
correct, but the protected-set digest did not reproduce under §4's literal
ordinal ordering. Root cause was author-side use of PowerShell `Sort-Object`,
whose default comparison is culture-aware/case-insensitive rather than ordinal.

Repair is limited to this Work Order path. Section 4 now defines ordering
unambiguously and forbids culture-aware sorting; §5 records the independently
reproduced digest
`0ca6eeefcb88969c38063040839591e06e993c26f7c5394227b6a97dff12fb06`.
All 27 preimages, count 48, SPEC pin, objective, paths, roles, risk and
external-effect budget are unchanged. No continuity/preimage path was synced.
Return to the same independent authorization-review path for rereview; BUILD
remains unauthorized.

---

## 19. Amendment 1 — dependency boundary and repair round 2

### 19.1 Authority and accepted upstream amendment

The operator granted bounded Amendment authority on 2026-08-23 after
completion rereview round 1. DESIGN Amendment 1 was authored and independently
returned `DESIGN_AMENDMENT_REVIEW_PASS`, findings/waivers `NONE/NONE`.

- amended DESIGN SHA-256:
  `ead2ac34f7d7ef16f2e2a942ad47ab2d69cde8a5dae1c9fd38d7b93f89bfe83c`;
- SPEC v1.0 remains byte-exact at
  `082cb5c1667b4d4685b3613d6654bda67552b6709416caafe8cd64ecf653b1b5`;
- prior Work Order SHA-256 `a7d52cde...` remains retained lineage and is
  superseded only by the post-Amendment hash recomputed by authorization
  review;
- objective, R2 ceiling, exact-27 implementation union, path-28 ownership,
  no-path-29 rule, claim boundary and external-effect budget remain unchanged.

The guard may use the repository-declared `jsonschema` dependency already
present in the stable runtime for Draft 2020-12 validation. Missing or
incompatible availability fails closed. Install, upgrade, substitution,
download or fallback to reduced validation is forbidden.

### 19.2 Exact Amendment governance surface and isolation

Amendment author/review may edit exactly four existing governance paths:

1. `docs/decisions/DESIGN_2026-08-22_CROSS_AGENT_INVARIANT_LEARNING.md`
2. `docs/decisions/CROSS_AGENT_INVARIANT_LEARNING_DESIGN_REVIEW_2026-08-22.md`
3. `docs/work_orders/CROSS_AGENT_INVARIANT_LEARNING_WORK_ORDER.md`
4. `docs/decisions/CROSS_AGENT_INVARIANT_LEARNING_WORK_ORDER_AUTHORIZATION_REVIEW_2026-08-23.md`

Their raw pre-Amendment SHA-256 values were respectively:

1. `acf04a72358b4d9b5cd668a2776edafe3c8d4fc54783a04e8b380c7d522a6452`
2. `def1741487591e1916a7d6bc5d5303e910474d9a20709dd55059b777a4ae6613`
3. `a7d52cdeeb954ce04cc7941796a6803c4d5204a17a8bf52905a0c3bf6caac874`
4. `fb8bf7076297f74672566ec8c7252b1889e048f2ace60b66b9aaac5a3a32e1c0`

For Amendment and repair-round-2 isolation, exclude the exact-27, these
exact-4 governance paths and reviewer-owned path 28 from the status set, then
apply section 4's ordinal row algorithm. The protected set must remain:

- count `46`;
- SHA-256
  `1ddda7de1e54064ee7839b670291d27d39ddca3577137ea5ee3e9c7d0fcfc140`.

Status must remain `78`, staged `0`, until a separately authorized new path or
Git action changes that boundary. SPEC/SPEC review and completion review path
28 remain byte-exact throughout Amendment authoring/review.

### 19.3 Exact repair-round-2 acceptance contract

After independent Amendment authorization review PASS, the existing
exact-27 `REPAIR_WORKER` authority requires one consolidated repair of
`F1-R1` through `F7-R1`:

1. **Structural closure:** orphan conditionals, unknown nested-shape targets
   and duplicate contract-source entries must fail schema/Python validation.
   Apply the same uniqueness/reference reasoning to every R3-R7 list and
   cross-reference edge.
2. **Ownership strategies:** each schema-allowed strategy must carry its
   required proof metadata and fail when that proof is absent, unsafe, stale
   or mismatched. A label alone cannot pass. Positive and paired negative
   tests must exercise production ownership checking.
3. **Conformance truth:** supplied validators must accept every positive and
   reject every mutation. Two validators agreeing on the wrong disposition
   fails. Zero/incomplete mutation corpus fails. Every emitted positive is
   bound to its intended shape, including multiple shapes under one outcome.
   Summary includes per-validator results, mutation ids/counts by operator,
   parity, ownership result and overall result.
4. **Conditional/nested semantics:** add a closed, evaluable conditional-rule
   representation and validated nested-shape references. Generate the full
   present/absent and null/value basis, recursive closed-boundary mutations,
   and prove exactly one semantic fact changes. Structurally inapplicable
   operators require explicit matrix exclusions for each shape.
5. **Sanitization:** duplicate-key canaries at registry and nested matrix
   levels appear in neither text nor JSON diagnostics. Audit every diagnostic
   constructor for raw arbitrary content, not only JSON Schema exceptions.
6. **Dependency preflight:** prove the stable runtime can import a compatible
   `jsonschema` and execute `Draft202012Validator`; do not install or mutate
   the environment. Missing/incompatible dependency fails closed.
7. **Evidence arithmetic:** path 27 retains both superseded counts, then records
   the reproducible transition `61 + 12 formerly-ABSENT + 4 formerly-clean
   tracked = 77; + reviewer path 28 = 78`.

Required adversarial probes include the exact three false-PASS probes from
completion rereview round 1: all validators false-accept mutations, all
validators false-reject positives, and a zero-mutation corpus. All must return
FAIL through production conformance code. Source-string assertions and
test-local reimplementations are insufficient.

### 19.4 Size, evidence and stop condition

The source/test files currently near 300 lines must be redistributed only
among already authorized exact-27 paths; do not compress away assertions or
create another path. Run the complete section 10 evidence order plus the new
family-level probes, exact-4/protected-set recomputation, dependency preflight,
secret/residue scan and doctor.

The repair worker may edit only exact-27 and must leave this amended Work
Order, exact-4 review artifacts and path 28 byte-exact. No provider/network/
credential/install/database/stage/commit/push/deployment. Stop at
`READY_FOR_REREVIEW_ROUND_2`; do not self-review or FREEZE.

---

## 20. Amendment 2 — exact-30 and repair round 3

### 20.1 Accepted upstream contract

Operator authority ratifies exactly three repair-round-2 split paths. DESIGN
Amendment 2 and SPEC Amendment 2 independently passed with no finding/waiver.
Accepted current hashes are:

- DESIGN `6aea401805641a8f128946fd78c1f4ab60a3afcebd8525bb57420edc059da0cf`;
- DESIGN review `53c19e31c9fd02371921a1c1707860ee61645a36a6624fb1e0b4bccab16f9a50`;
- SPEC `2b90376b450cc08db577c34d34d3ba93325834ad01e5a6676821a8182e3e2f0c`;
- SPEC review `b70a8b21714b12ea013bfe88beed4228f6e00845c720e480895ab6e6ddb3e739`.

The original §3/§6 exact-27 is extended, in this order, by:

28. `scripts/invariant_family_ownership.py` — pre-repair SHA-256
    `9b0e0c1d667f41267ffdf654909aa9416bf8d05a5d18efb7253e6ad8f096ffaf`;
29. `tests/unit/test_invariant_family_contract_repair_round2.py` —
    `5415b52d9b864fb0435f02ee957d203551302035eeeb69971d263d5d4a3741a0`;
30. `tests/integration/test_invariant_family_repository_guard_repair_round2.py`
    — `fad94162154e85bff222fd6ef3cddf24b906a7563080378ed90366be44db97ce`.

The existing completion-review artifact retains the historical label “path
28” but is outside and read-only to the worker union. In this amendment,
“path 31” means any further implementation or governance path; none is
authorized. Objective, R2 ceiling, effects and claim boundary do not change.

### 20.2 Amendment isolation and G6-R3

Amendment author/reviewer may edit only the existing DESIGN, DESIGN review,
SPEC, SPEC review, this Work Order and authorization review. Excluding those
six paths, exact-30 and the completion-review artifact from §4's canonical
status rows must yield:

- status `81`, staged `0`;
- protected count `44`;
- protected SHA-256
  `8a7a92f7d99a87f876e4b0b8c2c1693ccf7cda6661ff60cc3b0bc30daf728446`.

Before repair, the authorization reviewer must independently reproduce those
values, all six governance hashes, the exact-three preimages, unchanged HEAD/
origin, and completion-review SHA-256
`aec45fca8e17e197c7b2082b03e2a4599bcb5886fc64e6761da7129b41eb1faf`.
Any mismatch blocks repair.

### 20.3 Consolidated repair-round-3 order

After `AMENDMENT_2_AUTHORIZATION_REVIEW_PASS`, `REPAIR_WORKER` shall resolve
`F1-R2` through `F5-R2` together inside exact-30:

1. derive required mutation/operator coverage from the closed production
   contract; deleting counter or one-side-relation coverage must fail;
2. reject duplicate, inactive and inapplicable conditional ownership rules;
3. bind every ownership strategy to real production proof, remove permissive
   defaults, and prove invalid/missing adapter assertions fail;
4. reject symlinks before resolution, with paired safe/symlink tests;
5. run the exact §10 sequence in the stable runtime and record reproducible
   commands/counts/hashes, including full non-live suite and doctor.

Use production-code probes, paired negatives and cleanup-safe disposable
fixtures. Do not satisfy findings with source-string assertions or test-local
reimplementations. Recompute exact-30 preimages and the protected set before
return. The six amendment paths and completion review stay byte-exact.

No provider/network/credential/install/database/stage/commit/push/deployment.
Stop at `READY_FOR_REREVIEW_ROUND_3`; do not self-review, sync closure or
FREEZE. This conditional repair authority becomes effective only after the
independent Amendment 2 authorization review records PASS.

## 21. Amendment 3 — closure knowledge dependency

On 2026-08-23, after independent `REVIEW_PASS_ROUND_10`, the operator
authorized the ORCHESTRATOR to finish this tranche, hold required roles, use an
independent subagent and push the closed result. CLOSER synchronization changed
the three authoritative sources pinned by the active Project Knowledge entry;
`check_project_knowledge.py` therefore correctly failed closed.

This amendment adds exactly one existing closure-only path to the union:
`knowledge/PROJECT_CONTEXT.md`, preimage SHA-256
`2248d996386549fd6485c4930722ae9ce7c25d4dfb2e78f25df36260a3008f1c`.
It may only replace stale BUILD wording with the accepted round-10 FREEZE truth.
Existing exact-30 path `knowledge/manifest.json` may refresh only the affected
Project Context source pins. No source/test/objective/risk/claim or external-
effect change is authorized; no new file, provider/credential/install/database/
deployment action is allowed. Independent authorization review must PASS before
path 31 is edited, followed by independent closure rereview before commit/push.
