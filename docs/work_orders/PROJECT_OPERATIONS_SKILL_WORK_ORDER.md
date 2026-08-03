# Work Order — Project Operations Skill

- ID: `PROJECT-OPERATIONS-SKILL-WO-001`
- Tranche: `PROJECT-OPERATIONS-SKILL-2026-08-02`
- Risk: `R2`
- Parent DESIGN: `docs/decisions/ADR_2026-08-03_PROJECT_OPERATIONS_SKILL.md`
- Parent SPEC: `docs/specs/PROJECT_OPERATIONS_SKILL_SPEC.md`
- Authorization baseline: `61e0787ab7bd01cdd0bf017f9e19110c84258ada`
- Status: `AUTHORIZATION_RE_REVIEW_PASS / APPROVED — BUILD BLOCKED UNTIL PUSHED PRE-BUILD CHECKPOINT AND G6 PASS`

## 1. Authority boundary

An independent `AUTHORIZATION_REVIEWER` must compare this order with current
source, DESIGN, SPEC, skill-creator instructions, provider prerequisites and
the exact inventory. BUILD is authorized only after explicit `REVIEW_PASS`,
this authorization package is committed/pushed, a separate pre-BUILD
continuity acknowledgment is pushed, and G6 passes from a clean checkout.

The future `IMPLEMENTATION_WORKER` may edit only the eight BUILD paths below.
It must not stage, commit, push, approve its own output, install the skill
outside the repository, or FREEZE. The user has authorized Codex to continue
in place of the prior external worker; this changes no provider-neutral role
contract. An independent agent remains `REVIEWER`.

## 2. Exact eight-path BUILD ceiling

Every listed path is required. There is no wildcard, reserve, optional path,
or synthetic edit.

### Portable skill source — 2 paths

1. `skills/operate-shift-workspace/SKILL.md` — NEW
2. `skills/operate-shift-workspace/agents/openai.yaml` — NEW

### Static and live harness — 4 paths

3. `tests/unit/test_project_operations_skill_contract.py` — NEW
4. `scripts/run_project_operations_skill_live_evidence.py` — NEW
5. `scripts/_project_operations_skill_live_evidence_support.py` — NEW
6. `tests/unit/test_project_operations_skill_live_evidence.py` — NEW

### Durable evidence — 2 paths

7. `docs/decisions/PROJECT_OPERATIONS_SKILL_FORWARD_TEST_RECEIPT.md` — NEW
8. `docs/decisions/PROJECT_OPERATIONS_SKILL_LIVE_EVIDENCE_STATE.json` — NEW

An outside path is `BLOCKED_WORK_ORDER_CEILING`. An unnecessary listed path
requires exact-set contraction before BUILD. Any necessary split or new path
requires DESIGN -> SPEC -> WORK_ORDER amendment and independent review.

### Runtime-only filesystem allowlist

Exactly three ephemeral sibling paths are authorized during runner execution:

1. `docs/decisions/.PROJECT_OPERATIONS_SKILL_LIVE_EVIDENCE.lock`
2. `docs/decisions/.PROJECT_OPERATIONS_SKILL_LIVE_EVIDENCE_STATE.json.tmp`
3. `docs/decisions/.PROJECT_OPERATIONS_SKILL_FORWARD_TEST_RECEIPT.md.tmp`

They are runtime artifacts, not BUILD diff paths. Hold a Windows byte-range
lock on the stable lock file across state read/check/write/flush/replace.
Write state and receipt only through their exact temp path, flush and `fsync`
before `os.replace`. Remove all three on success and handled failure. Crash
residue fails closed on rerun until reviewed recovery verifies and cleans it.
Zero ephemeral residue is mandatory at handoff and final `git status`; no
other lock/temp filename is authorized.

## 3. Skill initialization and implementation

1. Run the current skill-creator initializer exactly once from project root:

   ```powershell
   python C:\Users\DELL\.codex\skills\.system\skill-creator\scripts\init_skill.py operate-shift-workspace --path skills --interface display_name="Operate Shift Workspace" --interface short_description="Run governed shift-workspace delivery safely" --interface default_prompt="Use `$operate-shift-workspace to resume this project from canonical continuity and identify the next authorized move."
   ```

   The machine-specific script location is an execution prerequisite, not
   content permitted in the skill. If the installed skill-creator resolves
   elsewhere, stop for reviewed command amendment; do not copy the generator.
2. Remove no file by destructive command. If the initializer creates anything
   beyond the two authorized skill paths, stop before editing and report
   `BLOCKED_GENERATOR_SHAPE`.
3. Replace the template with the exact SPEC section 2 metadata and implement
   R1-R5 in no more than 220 physical lines. Do not create resources, assets,
   copied references, provider entrypoints, or install links.
4. Keep all Python files at or below 300 physical lines and each test host
   feature-owned. No file-size exception/debt is authorized.

## 4. Static contract proof

`test_project_operations_skill_contract.py` must prove:

- exact two-file tree, UTF-8, exact frontmatter keys/values and exact
  `openai.yaml` shape/quoted values;
- description trigger quality and `$operate-shift-workspace` prompt literal;
- R1-R5 required concepts/order and the 220-line ceiling;
- no absolute/machine path, current hash/date/handoff/count/next-move,
  credential/endpoint, provider-role identity, copied truth, nonexistent
  command, self-authority, automatic install/provider/commit/push/approval;
- every command/relative truth path named by the skill currently exists or is
  dynamically resolved as required by SPEC;
- the current skill-creator `quick_validate.py` passes in a subprocess.

The tests must avoid asserting prose wholesale: they protect contracts while
allowing concise wording.

## 5. Live harness contract

### 5.1 Fixtures and expected response

The runner owns four immutable synthetic fixtures matching FT-1..FT-4. Each
prompt contains only the built `SKILL.md`, its one fixture and a strict JSON
response schema. It must not include repository secrets, unrelated source,
canonical live continuity content, or prior conversation. Required response
fields are:

`scenario_id`, `phase`, `next_allowed_move`, `stop`, `stop_reason`,
`forbidden_actions_avoided`, `authority_source`, and `claim_boundary`.

The canonical recorded request is the complete allowlisted JSON request object
used to construct that FT prompt with stable key ordering; it excludes API
keys, credentialed URLs, HTTP headers/envelope and transport metadata. The
canonical recorded response is the complete validated assistant JSON object
with stable key ordering; it excludes raw HTTP envelope/headers, hidden
reasoning and all but separately allowlisted safe provider metadata.

The support module validates semantic expectations separately for every FT
and rejects missing/extra fields, wrong types, unknown action labels, prose
outside JSON, secret-like data, or an unbounded claim.

### 5.2 Durable state machine

`PROJECT_OPERATIONS_SKILL_LIVE_EVIDENCE_STATE.json` has one schema/version, a
uniform evidence-bundle digest, the skill digest, four fixture digests, and
exactly four FT records. The bundle digest covers canonical bytes of all six
source/harness paths in section 2, including embedded fixture/schema bytes.
Every FT record stores the same bundle digest; mixed digests are invalid. Each
record transitions under the runtime lock with atomic replacement:

`UNUSED -> RESERVED -> ACCEPTED | FAILED | INDETERMINATE`.

The lineage key is SHA-256 of FT id + skill digest + fixture digest. Reservation
with timestamp and random attempt id is durably flushed before network. Any
physical attempt consumes that lineage. Only `UNUSED` may call; every other
state fails before network. No reset, retry, overwrite, replacement, or fifth
record is available through the runner. A replacement lineage requires a
reviewed authorization amendment.

Any change after the first physical call to one of the six bundle paths—or to
any pre-call gate, prompt/schema, fixture, validator, sanitizer, runner or
support semantic—invalidates the aggregate 4/4 set even if skill/fixture
digests did not change. Replacement calls require a reviewed amendment; no FT
may retain evidence from a different bundle digest.

### 5.3 Provider execution and sanitization

The runner uses this exact read-only Alibaba-compatible configuration:

- key: first non-empty `ALIBABA_API_KEY`, then `DASHSCOPE_API_KEY`;
- base URL: first non-empty `ALIBABA_BASE_URL`, then `DASHSCOPE_BASE_URL`,
  otherwise `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`;
- model: `select_model()` from
  `packages/ai-providers/alibaba/select_model.py`, using its adjacent
  `model-quota-catalog.json` and current-date eligibility policy.

No env, catalog or provider config mutation is authorized. Logs/receipts may
show neither key nor full credentialed URL. The runner imports no
tranche-specific runner/support. It injects transport, clock, random id and
paths for non-live tests. For FT-1 through FT-4 in order it:

1. completes all static/refusal/pre-network checks;
2. reserves that FT lineage durably;
3. starts a new request with no shared conversation state;
4. performs exactly one physical call;
5. validates the canonical assistant JSON without semantic redaction;
6. atomically records terminal state and receipt evidence.

HTTP/transport/parse/validation failure records `FAILED` or `INDETERMINATE`,
stops immediately and consumes the lineage. Raw keys, Authorization/JWT/DSN,
URL credentials/query/fragment, raw exception, chain-of-thought, provider
headers and unsanitized response must never reach console, state, receipt, or
git diff. If assistant JSON contains secret-like data or would require
redaction, that FT is `FAILED` and never `ACCEPTED`; sanitization may not
rewrite an accepted semantic request or response.

### 5.4 Receipt and exact accounting

The generated Markdown receipt records bundle/skill/fixture digests, four
canonical allowlisted requests and complete validated assistant JSON objects,
model/provider id, safe endpoint
description, timestamps, attempt/lineage ids, per-FT validation, aggregate
physical/accepted counts, and the exact SPEC claim boundary. Final PASS exists
only at `physical=4`, `accepted=4`, exactly one accepted record for each FT,
zero extra/retry call, and no secret-like content.

## 6. Non-live runner proof

`test_project_operations_skill_live_evidence.py` injects fake transport and
temporary state/receipt paths to prove at minimum:

- exact FT prompt isolation and schema/semantic validation;
- preflight failures and secret-like fixtures make zero calls;
- reservation is visible on disk before transport;
- success makes one call per lineage and aggregate 4/4 only;
- HTTP, timeout, malformed JSON and semantic failure consume the lineage;
- RESERVED/terminal/stale/digest-mismatched state blocks before network;
- two-process contention yields at most one caller for one lineage;
- exact stable lock/temp paths work on Windows, replace failure and crash
  residue fail closed, and success/handled failure clean to zero residue;
- rerun after any physical attempt makes zero additional calls;
- atomic-write failure cannot fabricate ACCEPTED/PASS;
- receipt/state/console/exception sanitization with sentinel secrets;
- no fifth lineage, batch, shared context, raw response or retry route.

Tests themselves make no network call.

## 7. Protected boundary

Zero diff is mandatory for `.cvf/**`; existing apps/packages/database/
migrations; existing scripts/tests/provider configuration; catalog; all prior
receipts; DESIGN/SPEC/WORK_ORDER; continuity, implementation status and
roadmap. The skill is not installed into `$CODEX_HOME`, another repository, or
any product directory. C4 truth synchronization is a separate commit.

## 8. Pre-BUILD G6

After authorization and the separate continuity acknowledgment are pushed:

1. verify clean worktree, `HEAD == origin/main`, and authorization ancestry;
2. rehydrate mandatory truth and declare `IMPLEMENTATION_WORKER`;
3. record the current skill-creator directory and verify initializer,
   `quick_validate.py`, and `references/openai_yaml.md` are readable;
4. run the full non-live Python baseline and capture exact result;
5. resolve the exact key/base/model precedence in section 5.3 without printing
   values or full credentialed URL, mutate no env/config/catalog, and verify no
   evidence state/receipt/runtime-only or owned process residue exists;
6. pass session/catalog/file-size/repository/JSON/diff and doctor gates;
7. stop `BLOCKED_G6` before initializer/source edit/provider call on failure.

## 9. Required execution order

1. Run G6.
2. Initialize and implement the two skill files.
3. Implement static tests; run focused tests and `quick_validate.py`.
4. Implement support/runner/non-live tests; run all focused tests.
5. Run full non-live Python suite and repository/doctor gates.
6. Inspect the exact eight-path unstaged diff for secrets and scope.
7. Run the live runner once. It may make exactly four calls only after all
   earlier gates pass; any failed/indeterminate FT stops the tranche.
8. Re-run focused non-live tests and all repository gates without modifying
   evidence.
9. Run exact-parent rollback rehearsal in a temporary worktree, restore the
   authorization baseline, verify its recorded baseline, and remove all
   temporary state.
10. Report exact results, physical/accepted counts, changed set, receipt/state
    paths, cleanup, zero staged files and
    `READY_FOR_INDEPENDENT_PROJECT_OPERATIONS_SKILL_BUILD_REVIEW`.

## 10. Review, repair, and commit ownership

An independent `REVIEWER` compares all eight paths, source, tests, generated
evidence and claims with DESIGN/SPEC/this order. It re-runs all non-network
checks but must not make another provider call. Findings return to a bounded
`REPAIR_WORKER`. Any post-call change to one of the six evidence-bundle paths
or any gate/prompt/schema/fixture/validator/sanitizer semantic invalidates the
complete aggregate evidence and requires an authorization amendment for
replacement lineages; no mixed digest or silent rerun.

Only after final `REVIEW_PASS` may `COMMIT_STEWARD` stage exactly eight BUILD
paths, commit once, push `main`, and verify clean `HEAD == origin/main`.
`CLOSER` then performs separately authorized C4 continuity/status/roadmap
synchronization and FREEZE review.

## 11. Stop and claim boundary

STOP on any SPEC condition, outside/unnecessary path, extra generator output,
missing prerequisite, baseline/gate failure, >300-line Python or >220-line
SKILL.md, nonzero call before final live step, lock/atomicity doubt, stale or
mismatched digest, second-call possibility, failed/indeterminate FT, secret
exposure, incomplete cleanup, or evidence changed after provider execution.

The final bounded claim may say only that four separately initialized real
provider sessions followed this reviewed skill for FT-1..FT-4 within their
synthetic fixtures. It may not claim prompt enforcement, universal model
compliance, production governance, installation, authorization, future
behavior, roadmap Phase 3 progress, or closure of later queue items.

## 12. Independent authorization disposition

Final verdict: `AUTHORIZATION_RE_REVIEW_PASS`, no open finding or waiver.
Initial review returned five findings: Windows runtime lock/temp authority;
whole-bundle evidence invalidation; exact provider config precedence;
canonical request/response fail-on-redaction semantics; and required-read
drift. Repair 1 closed all five while retaining exactly eight final BUILD
paths. Independent re-review confirmed the three ephemeral paths, uniform
six-path digest, four one-call lineages, G6, evidence, role and commit/C4
boundaries are executable. BUILD remains blocked until this package and a
separate pre-BUILD acknowledgment are pushed and G6 passes.
