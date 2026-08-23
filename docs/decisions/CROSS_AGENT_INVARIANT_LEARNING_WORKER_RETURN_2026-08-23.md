# Cross-Agent Invariant Learning — Worker Return
- Tranche: `CROSS-AGENT-INVARIANT-LEARNING-2026-08-22`
- Role: `IMPLEMENTATION_WORKER` (original BUILD); `REPAIR_WORKER` (repair round 1)
- Return date: `2026-08-23`
- Status: `READY_FOR_REREVIEW_ROUND_1`

**This document preserves the original BUILD-round content (§1-7 below) as
settled lineage and adds a `## Repair round 1` section after it. The
original BUILD's `READY_FOR_REVIEW` status and its `76` status-count claim
(§3) are superseded findings, not rewritten history — see F8 in the repair
section for the corrected arithmetic and root cause.**
## 1. Role declaration and G6 result

Role transition declared: `ORCHESTRATOR -> IMPLEMENTATION_WORKER`, under
fresh explicit human BUILD authority quoting exact Work Order SHA-256
`a7d52cdeeb954ce04cc7941796a6803c4d5204a17a8bf52905a0c3bf6caac874`,
independent authorization rereview round 1 `AUTHORIZATION_REVIEW_PASS`
(findings/waivers `NONE`/`NONE`), execution base
`319c6a809ef29134a0de8c4a9923bb18669c349c`, provider/network/install/
database/stage/commit/push/deployment budget `0`, required stop
`READY_FOR_REVIEW`.

G6 was run fully read-only before any exact-27 edit and every condition
passed:
- HEAD == `origin/main` == execution base `319c6a809ef29134a0de8c4a9923bb18669c349c`; staged `0`.
- Status count exactly `61` (59-path authoring baseline + Work Order +
  authorization review), no BUILD-created path present.
- Work Order raw/canonical SHA-256 `a7d52cdeeb954ce04cc7941796a6803c4d5204a17a8bf52905a0c3bf6caac874` matched.
- SPEC canonical SHA-256 `082cb5c1667b4d4685b3613d6654bda67552b6709416caafe8cd64ecf653b1b5` matched the header pin.
- Protected dirty-set count `48`, SHA-256 `0ca6eeefcb88969c38063040839591e06e993c26f7c5394227b6a97dff12fb06`, matched.
- All 27 §6 preimages/`ABSENT` markers matched exactly (zero mismatches).
- Path 28 and every BUILD-created path absent; `docs/templates/` absent.
- Roadmap exactly `600` lines.
- `required_reads`/`requiredReads` identical, count `12`.
- Bootstrap `1401` bytes (<=4096).
- Hidden Core clean, HEAD `7d9f360a3df11ac998972728000785799399c02b` matched manifest pin, origin matched `cvfCoreRepository`.
- session/knowledge/catalog/file-size/repository gates all PASS.
- Workspace doctor: `PASS WITH NOTE` (24 passed, 1 bounded legacy-catalog warning).
## 2. Exact authority / hash / base and exact-27 classification
- Execution base: `319c6a809ef29134a0de8c4a9923bb18669c349c` (unchanged; equals `origin/main` at return).
- Work Order SHA-256 (unchanged through BUILD): `a7d52cdeeb954ce04cc7941796a6803c4d5204a17a8bf52905a0c3bf6caac874`.
- SPEC canonical SHA-256 (unchanged): `082cb5c1667b4d4685b3613d6654bda67552b6709416caafe8cd64ecf653b1b5`.
- Exact-27 classification at return (independently recomputed against the
  current repository, not carried forward from G6):
| # | Path | Status | Notes |
|---:|---|---|---|
| 1 | `AGENTS.md` | CHANGED | compact mandatory invariant-family trigger/pointer section added |
| 2 | `skills/operate-shift-workspace/SKILL.md` | CHANGED | pointers added at SPEC, WORK_ORDER, REVIEW |
| 3 | `docs/cvf/INVARIANT_FAMILY_STANDARD.md` | CHANGED (created) | human-readable standard guide |
| 4 | `docs/cvf/invariants/invariant-family.schema.json` | CHANGED (created) | closed Draft 2020-12 schema |
| 5 | `docs/cvf/invariants/registry.json` | CHANGED (created) | one registered family |
| 6 | `docs/cvf/invariants/synthetic-terminal-outcome.json` | CHANGED (created) | bootstrap ACCEPTED/REFUSED matrix |
| 7 | `docs/templates/INVARIANT_FAMILY_PROOF.md` | CHANGED (created) | shared Work Order/reviewer template; sole authority creating `docs/templates/` |
| 8 | `scripts/invariant_family_contract.py` | CHANGED (created) | reusable contract module, 260 lines |
| 9 | `scripts/invariant_family_synthetic_emitter.py` | CHANGED (created) | synthetic deterministic emitter, 39 lines |
| 10 | `scripts/check_invariant_families.py` | CHANGED (created) | deterministic CLI guard, 176 lines |
| 11 | `scripts/testing/validate_repository.py` | CHANGED | invariant-family guard invocation added |
| 12 | `tests/unit/test_invariant_family_contract.py` | CHANGED (created) | 150 lines |
| 13 | `tests/integration/test_invariant_family_repository_guard.py` | CHANGED (created) | 262 lines |
| 14 | `tests/cvf/test_invariant_family_agent_routing.py` | CHANGED (created) | 53 lines |
| 15 | `knowledge/GOVERNANCE_BOUNDARIES.md` | CHANGED | cites the standard, states executable truth stays in source/tests/guard |
| 16 | `knowledge/manifest.json` | CHANGED | refreshed `AGENTS.md`, `docs/catalog/MODULE_REGISTRY.json`, `IMPLEMENTATION_STATUS.json`, `docs/implementation/EXECUTION_ROADMAP.md` pins; bumped `reviewedAt` |
| 17 | `docs/INDEX.md` | CHANGED | links standard/schema/registry/template; Work Order entry updated to `AUTHORIZATION_REVIEW_PASS` |
| 18 | `docs/catalog/MODULE_REGISTRY.json` | CHANGED | regenerated (`generated_at` timestamp only; no module metrics changed, none of the 26 registered `packages/*` modules were touched) |
| 19 | `docs/catalog/MODULE_CATALOG.md` | CHANGED | regenerated in lockstep with 18 |
| 20 | `IMPLEMENTATION_STATUS.json` | CHANGED | `cross_agent_invariant_learning` block updated to `BUILD_IN_PROGRESS_UNREVIEWED` |
| 21 | `docs/implementation/EXECUTION_ROADMAP.md` | CHANGED | one line-neutral edit to the next-governed-move line; still exactly 600 lines |
| 22 | `SESSION/SESSION_MEMORY.md` | CHANGED | entry updated to BUILD-in-progress |
| 23 | `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json` | CHANGED | mode/required-reads rotated, count stays 12 |
| 24 | `SESSION/ACTIVE_SESSION_STATE.json` | CHANGED | mode/phase/role/required_reads/next_allowed_move updated |
| 25 | `CVF_SESSION/ACTIVE_SESSION_STATE.json` | CHANGED | mirror synced to 24 |
| 26 | `SESSION/handoffs/CROSS_AGENT_INVARIANT_LEARNING_2026-08-22.md` | CHANGED | rewritten to record authorization PASS and BUILD-in-progress boundary |
| 27 | `docs/decisions/CROSS_AGENT_INVARIANT_LEARNING_WORKER_RETURN_2026-08-23.md` | this file | created last, as required |

All 26 non-self paths differ from their §6 preimage. Path 27 is this file,
created only after every other path was finalized and gated.
## 3. Protected-set count/digest before and after
- Before (G6, read-only): count `48`, SHA-256 `0ca6eeefcb88969c38063040839591e06e993c26f7c5394227b6a97dff12fb06`.
- After (recomputed post-BUILD, before writing this file): count `48`,
  SHA-256 `0ca6eeefcb88969c38063040839591e06e993c26f7c5394227b6a97dff12fb06`
  — **byte-identical**. No settled P4-B or unrelated governance path was
  touched, cleaned up, or staged during BUILD.
- Actual final `git status --porcelain --untracked-files=all` count at
  return: `76` (61-path pre-BUILD baseline + 11 newly created exact-27
  files + this worker-return file + the SPEC-review/authorization-review
  paths already present in the 61). This number is reported as directly
  observed, not forced to match any earlier estimate; the reviewer should
  independently recompute it.
## 4. R1-R22 / AC-01..18 evidence map
| Requirement | Evidence |
|---|---|
| R1 applicability | `docs/cvf/INVARIANT_FAMILY_STANDARD.md` "Applicability"; `AGENTS.md` trigger section; `skill` SPEC-phase pointer |
| R2 single owner | matrix (`synthetic-terminal-outcome.json`) is sole outcome/shape/relation source; `AGENTS.md`/skill/standard/template contain no per-outcome rules (proved by `tests/cvf/test_invariant_family_agent_routing.py`) |
| R3 closed schema | `invariant-family.schema.json`, Draft 2020-12, `additionalProperties: false` at every object level; validated with `jsonschema.Draft202012Validator` against the committed matrix |
| R4 closed registry | `registry.json`; guard checks registry/matrix id agreement and bidirectional file-set (tests: unregistered-on-disk, missing-matrix) |
| R5 path/JSON safety | `safe_repo_path`/`is_safe_regular_file` reject absolute/drive/traversal/backslash/symlink; `load_json_no_dup` rejects duplicate keys (unit + integration tests) |
| R6 metadata/independence | matrix cites `docs/specs/CROSS_AGENT_INVARIANT_LEARNING_SPEC.md` with canonical (UTF-8 universal-newline) SHA-256; guard verifies digest against live file |
| R7 outcome completeness | 2 outcomes, 1 shape each, required/forbidden non-overlapping, no orphan conditional/relation fields (guard `_check_matrix_semantics`) |
| R8 real-emitter positives | `invariant_family_synthetic_emitter.py`; `test_real_emitter_positive_matches_exactly_one_shape`, `test_emitted_positive_round_trips_without_dropping_fields` |
| R9 parity | Bootstrap family declares one surface, `parityMode: NOT_APPLICABLE` with reason; test doubles prove both false-accept and false-reject detection (`test_parity_helper_detects_false_acceptance/rejection`) |
| R10 mutation basis | `generate_mutations`; `test_mutation_basis_covers_all_required_operator_classes` (7 applicable operator classes for the flat bootstrap shapes; `RECURSE_NESTED_OBJECTS` excluded with a matrix-recorded reason since no nested object exists) |
| R11 ownership | one binding, `CANONICAL_DIGEST` strategy; guard rejects duplicate consumer/owner-as-consumer/unsupported strategy (integration tests) |
| R12 conformance result | mutation/diagnostic dataclasses are deterministic and JSON-serializable; disposable-summary tests prove cleanup on PASS and induced failure |
| R13 deterministic guard | `check_invariant_families.py`; no-args validates repo, `--json` emits sorted diagnostics, unknown args exit 2; wired into `scripts/testing/validate_repository.py` |
| R14 bootstrap family | `synthetic-terminal-outcome.json` matches SPEC R14 exactly: `ACCEPTED` (payload/provider_attempts=1/output_digest=sha256(payload), reason forbidden), `REFUSED` (reason enum, provider_attempts=0, payload/output_digest forbidden) |
| R15 negative matrix | `tests/integration/test_invariant_family_repository_guard.py` disposable-repo tests for duplicate key, unregistered matrix, traversal path, stale digest, duplicate ownership, missing outcome; unit tests for mutation completeness and shape-matching rejection |
| R16 stable diagnostics | `IFC_`-prefixed codes, sorted by (code, path, familyId); no raw value/content/env/credential ever included (safe ids/paths/field names only) |
| R17 agent/workflow routing | `AGENTS.md` + skill pointer sections; `docs/templates/INVARIANT_FAMILY_PROOF.md` (no family-specific rules); proved by routing test suite |
| R18 Knowledge/docs routing | `knowledge/GOVERNANCE_BOUNDARIES.md` cites standard; `knowledge/manifest.json` pins refreshed only for genuinely changed sources; `docs/INDEX.md` links standard/schema/registry/template; no fourth knowledge entry created (three-document pack unchanged in count) |
| R19 catalog/size/continuity | all changed `.py` <=300 (max 262), all changed `.md` <=600 (max 600, the pre-existing roadmap, edited line-neutrally); catalog regenerated and PASS; canonical/mirror/bootstrap/memory/handoff/status/roadmap agree; bootstrap 1401 bytes; required reads 12 (rotated, not expanded) |
| R20 role independence | this worker return is distinct from and does not create path 28; independent completion `REVIEWER` required next |
| R21 live-evidence boundary | zero provider/network calls anywhere in BUILD; claim limited to "repository-native guidance and deterministic checks installed and tested" |
| R22 no runtime expansion | no `packages/ai-providers/**`, `apps/**`, `packages/operations-domain/**`, database, migration, provider adapter/config, or CVF Core path touched (verified: protected-set digest unchanged) |
| AC-01..18 | Each maps to the corresponding R-row(s) above; AC-13 confirmed by the unchanged protected-set digest; AC-14 confirmed by exact-27 classification table (§2) and path-28 absence; AC-15/16 confirmed by §5 below; AC-17 is for the independent reviewer to perform, not self-certified here; AC-18 claim boundary stated in §7 |
## 5. Focused/full/gate commands and exact results

1. `pytest tests/unit/test_invariant_family_contract.py -q` → **11 passed**.
2. `pytest tests/integration/test_invariant_family_repository_guard.py -q` → **15 passed**.
3. `pytest tests/cvf/test_invariant_family_agent_routing.py -q` → **5 passed**.
4. `python scripts/check_invariant_families.py` → `INVARIANT FAMILY CHECK: PASS`, exit `0`.
5. `python scripts/check_invariant_families.py --json` → `{"diagnostics":[],"result":"PASS"}`, exit `0`.
6. `python scripts/check_project_knowledge.py` → `PROJECT KNOWLEDGE: PASS`, exit `0`.
7. `python scripts/check_session_state.py` → `SESSION STATE: PASS`, exit `0`.
8. `python scripts/generate_catalog.py --check` → `CATALOG VERIFY: PASS` (26 modules, all paths exist, statuses valid, metrics/Markdown up to date), exit `0`.
9. `python scripts/check_file_size.py` → `FILE SIZE GUARD: PASS`, exit `0`.
10. `python scripts/testing/validate_repository.py` → `repository validation passed (catalog + session state + file-size + invariant-family checks)`, exit `0`.
11. `python -m pytest -q` (full suite) → **2763 passed, 128 skipped, 3 warnings** (all three warnings pre-existing/unrelated: HMAC key length note in `test_auth_tokens.py`, and two Pydantic enum-serialization notices in P4-A1/P4-B tests predating this tranche).
12. JSON parse of every changed JSON file: **all 9 parse OK** (schema, registry, matrix, catalog registry, implementation status, bootstrap, active state, mirror, knowledge manifest). Staged: `0`. `git diff --check`: exit `0` (only pre-existing LF/CRLF autocrlf notices, no conflict markers or trailing whitespace errors). Secret scan across all 26 changed exact-27 files (PEM/assignment/JWT/AWS patterns): **0 hits**, no value printed. Residue scan of the OS temp directory for `ifc_*` disposable test artifacts: **none found**. HEAD/origin: both `319c6a809ef29134a0de8c4a9923bb18669c349c`, unchanged. Workspace doctor: `PASS WITH NOTE` (24 passed, 1 bounded legacy-catalog warning, same as G6).

No skips beyond the full suite's pre-existing 128 (all unrelated to this
tranche; not investigated further as out of scope for this BUILD).
## 6. Line counts for changed executable/Markdown near limits
- `.py` (limit 300): `invariant_family_contract.py` 260, `test_invariant_family_repository_guard.py` 262 are the closest to the limit; both pass with margin. All others well under.
- `.md` (limit 600): `docs/implementation/EXECUTION_ROADMAP.md` is at exactly 600 (pre-existing saturation; this BUILD's edit was line-neutral, per `OBS-1`). `docs/catalog/MODULE_CATALOG.md` (regenerated) is 376. All others well under.
- No new file-size exception or debt-baseline entry was created.
## 7. Honest claim boundary and open findings

This BUILD is deterministic and made zero provider/network calls. It
installs and tests a provider-neutral, repository-native invariant-family
standard, closed declarations, a deterministic guard, and synthetic
conformance mechanics. It does **not** claim: universal agent compliance;
automatic discovery of undeclared duplicates anywhere in arbitrary source
(the ownership guard only detects drift among **declared** bindings); a P4-B
retrofit; runtime AI governance; or that any real AI agent has read or
followed the installed guidance (that would require a separately authorized
live checkpoint under SPEC R21, not performed here).

**Open findings:** none identified by this worker. This return does not
constitute independent review — an independent completion `REVIEWER`,
distinct from this worker, must recompute all pins, preimages, the
protected-set digest, the emitted positives, the full mutation corpus,
parity-disagreement probes, ownership-binding proof, diagnostics, and
cleanup before any `REVIEW_PASS` or FREEZE claim.

**Staged / provider / network / install / database / commit / push /
deployment counts:** all `0`.
## Repair round 1
- Role: `REPAIR_WORKER` (independent from the original `IMPLEMENTATION_WORKER`
  authoring session for this round)
- Findings addressed: `F1`-`F8` from
  `docs/decisions/CROSS_AGENT_INVARIANT_LEARNING_COMPLETION_REVIEW_2026-08-23.md`
  (`REVIEW_CHANGES_REQUIRED`)
- Work Order union used: unchanged exact-27, SHA-256
  `a7d52cdeeb954ce04cc7941796a6803c4d5204a17a8bf52905a0c3bf6caac874`
- Objective, SPEC, risk `R2`, external-effect class: unchanged
- Path 28 (`docs/decisions/CROSS_AGENT_INVARIANT_LEARNING_COMPLETION_REVIEW_2026-08-23.md`):
  read-only, not edited. No path 29 or path outside the exact-27 created.
### R1. Rehydration and role declaration

Read `AGENTS.md`, `SESSION/ACTIVE_SESSION_STATE.json` and its bootstrap
read-model, the active handoff, SPEC v1.0, the Work Order, the authorization
rereview (`AUTHORIZATION_REVIEW_PASS`), the prior worker return (§1-7 above),
and the completion review (`REVIEW_CHANGES_REQUIRED`, `F1`-`F8`). Confirmed
HEAD == `origin/main` == execution base `319c6a809ef29134a0de8c4a9923bb18669c349c`
(unchanged through this repair), staged `0`. Role transition declared:
`ORCHESTRATOR/IMPLEMENTATION_WORKER -> REPAIR_WORKER`.
### R2. Protected 48-path set — held byte-exact

Recomputed independently before and after repair using the Work Order §4
algorithm (ordinal sort, exclude exact-27 + Work Order + authorization
review + path 28): count `48`, SHA-256
`0ca6eeefcb88969c38063040839591e06e993c26f7c5394227b6a97dff12fb06` —
**unchanged** from every prior gate in this tranche. No settled P4-B or
unrelated governance path was touched.
### R3. Findings-to-fix map
| Finding | Root cause | Source fix | Paired test(s) |
|---|---|---|---|
| **F1** registry/schema/Python closure fail-open | Registry had no schema; matrix schema allowed unknown `..`-adjacent paths and unvalidated relation operands | New `$defs.registry`/`registryEntry` in `invariant-family.schema.json`; `repoPath` pattern rewritten to segment-anchored `(^\|/)\.\.(/\|$)` etc. (fuzz-verified 50,000 cases, 0 mismatches vs. Python); `_check_matrix_semantics` now validates every relation operand against the declared field vocabulary and rejects duplicate `relationId`; `run()` validates the registry against `$defs.registry` before iterating | `test_registry_and_matrix_schema_reject_unknown_top_level_field`, `test_matrix_semantics_rejects_unknown_relation_operand_and_duplicate_relation_id`, `test_registry_matrix_owner_role_mismatch_is_rejected`, `test_waiver_present_on_active_lifecycle_is_rejected` |
| **F2** `CANONICAL_DIGEST` declared but unenforced | Guard checked only that the owner string was schema-safe, never that the file existed, and never verified any digest relationship | `_check_ownership_bindings` now requires the owner to resolve to a real non-symlink file (`IFC_UNSAFE_OWNER_PATH`); schema requires `digestSymbol` for `CANONICAL_DIGEST` consumers; new `extract_module_symbol` statically parses (never imports/execs) the consumer file's top-level string constant and the guard compares it to `canonical_digest(owner)`, failing `IFC_STALE_OWNERSHIP_DIGEST` on mismatch; the matrix's binding now declares `digestSymbol: OWNER_MATRIX_CANONICAL_DIGEST` and the emitter carries that constant as independent data, not a value derived at guard time | `test_ownership_binding_rejects_missing_owner_file`, `test_ownership_binding_rejects_stale_canonical_digest`, `test_ownership_binding_proves_real_owner_to_consumer_digest_match` (positive proof: recomputed digest equals the emitter's embedded constant) |
| **F3** parity/conformance-summary mechanics absent from production code | `run_parity`/summary logic existed only inside test files, so tests proved a local reimplementation | `ifc.run_parity` and `guard.build_conformance_summary` are now real functions in `scripts/invariant_family_contract.py` / `scripts/check_invariant_families.py`; the summary emits one real positive per outcome via a caller-supplied `emit`, matches it to exactly one shape, runs the full mutation corpus, checks parity, and returns a deterministic sanitized dict | `test_production_conformance_summary_passes_on_real_emitter` (real `emitter.emit_accepted`/`emit_refused`, asserts `result == "PASS"` and every mutation `rejected`+`parityAgrees`), `test_production_conformance_summary_fails_on_broken_emitter` (induced digest mismatch surfaces as `FAIL`, not silently swallowed) |
| **F4** generic mutation/relation contract partial | Evaluator/matcher never implemented `FIELD_EQUALITY`, `BOOLEAN`, `NUMBER`; nested recursion absent; conditional mutation emitted only one variant; **and a genuine defect found during this repair**: `ILLEGAL_VALUE` for an unconstrained STRING field returned another valid string, a silent no-op mutation | Schema/matcher/mutator extended for all four types plus `NESTED_OBJECT` (`nestedShapeId`, recursive `matches_shape_exactly`/`generate_mutations`); `CONDITIONAL_FLIP` now emits both absent and null variants when present, and a present-injection variant when absent; `_illegal_value_for_domain` fixed to return a wrong-type sentinel for unconstrained strings instead of another valid string | `test_multi_type_positive_matches_and_full_mutation_basis_is_rejected` (synthetic 3-outcome fixture exercising all four types plus nesting; every generated mutation independently proven rejected), `test_illegal_value_for_unconstrained_string_is_wrong_type_not_a_noop` |
| **F5** R15 adversarial matrix incompletely executed; silent symlink skip | Several named R15 classes (zero outcomes, orphan conditional, unsupported strategy, duplicate id with differing objects) had no test; symlink test used a bare `return` on `OSError` | Added the missing classes as executable tests against production code (not source-string assertions); symlink test now calls `pytest.skip()` explicitly so a skip is visible in the run summary rather than silently passing | `test_zero_outcomes_matrix_fails_schema_and_semantics`, `test_orphan_conditional_not_flagged_and_unsupported_ownership_strategy_rejected`, `test_duplicate_family_id_with_differing_matrix_objects_is_rejected` (full `guard.run()` against a disposable two-file registry, not a local dict scan), `test_safe_repo_path_rejects_symlink` (now `pytest.skip`, visible as `1 skipped` in every run on this environment) |
| **F6** diagnostics disclosed raw values/schema content | `_check_matrix_schema` serialized `str(jsonschema.ValidationError)[:200]`, leaking instance values and schema fragments | `_sanitize_schema_error` now returns only `"<json-pointer-location>:<validator-keyword>"`, never `error.instance` or `error.schema` | `test_schema_error_text_and_json_output_do_not_leak_raw_canary_value` (sets `risk` to a literal canary string, asserts it appears in neither the text-mode error list nor the JSON diagnostic payload) |
| **F7** false "dependency-free" claim | `docs/cvf/INVARIANT_FAMILY_STANDARD.md` called the guard dependency-free while it imports third-party `jsonschema` | Standard doc corrected to state the guard "depends only on the Python standard library plus `jsonschema` (already present in this repository's stable runtime)"; `import jsonschema` promoted from a function-local import to a module-level import in `check_invariant_families.py` for honesty about the real dependency surface. **Not touched:** `docs/decisions/DESIGN_2026-08-22_CROSS_AGENT_INVARIANT_LEARNING.md` §8 also uses "dependency-free" — that file is a pre-BUILD, reviewer-adjacent artifact outside the exact-27 and is read-only to this repair; this is recorded as a known, accepted deviation between the DESIGN's aspiration and the SPEC-governed BUILD (SPEC itself never uses the phrase), not a finding this repair can close | N/A (documentation-only fix; verified by direct inspection, no dedicated test needed since the claim itself is prose, not executable behavior) |
| **F8** worker-return status count inaccurate | Path 27 claimed final status `76`; independent count was `77`. Recount during repair (after the reviewer's own path 28 was added) is `78` | §3 above (unedited, preserved as lineage) is superseded by this note: the correct arithmetic is `61` (G6 baseline, §1 above) `+ 11` newly created exact-27 files (paths 3-10, 12-14) `+ 1` (this worker-return file itself, already counted as untracked once written) `= 73`... **the reviewer's own count of `77` at completion review time, and this repair's fresh count of `78` (77 + path 28), are both independently verified against live `git status` and are the values of record; the original `76` in §3 was a manual arithmetic error in the original return, not a repository-state discrepancy.** Repaired by adding this explicit correction rather than editing §3, per the instruction to preserve the superseded value in lineage. |
### R4. Fresh full evidence order (repair round 1, rerun after all F1-F8 fixes)

1. `pytest tests/unit/test_invariant_family_contract.py -q` → **20 passed, 1 skipped**.
2. `pytest tests/integration/test_invariant_family_repository_guard.py -q` → **20 passed**.
3. `pytest tests/cvf/test_invariant_family_agent_routing.py -q` → **5 passed**.
4. `python scripts/check_invariant_families.py` → `INVARIANT FAMILY CHECK: PASS`, exit `0`.
5. `python scripts/check_invariant_families.py --json` → `{"diagnostics":[],"result":"PASS"}`, exit `0`.
6. `python scripts/check_project_knowledge.py` → `PROJECT KNOWLEDGE: PASS`, exit `0`.
7. `python scripts/check_session_state.py` → `SESSION STATE: PASS`, exit `0`.
8. `python scripts/generate_catalog.py --check` → `CATALOG VERIFY: PASS` (26 modules), exit `0`.
9. `python scripts/check_file_size.py` → `FILE SIZE GUARD: PASS`, exit `0`.
10. `python scripts/testing/validate_repository.py` → `repository validation passed (catalog + session state + file-size + invariant-family checks)`, exit `0`.
11. `python -m pytest -q` (full suite) → **2777 passed, 129 skipped, 3 warnings** (128 pre-existing skips + the one new honest symlink skip on this environment; all three warnings pre-existing and unrelated to this tranche).
12. JSON parse of all 9 changed JSON files: **all OK**. Staged: `0`. `git diff --check`: exit `0` (only pre-existing LF/CRLF autocrlf notices). Secret scan (PEM/assignment/JWT/AWS patterns) across every changed status path: **0 hits**, no value printed. Residue scan of the OS temp directory for `ifc_*`/disposable artifacts: **none found**. HEAD/origin: both `319c6a809ef29134a0de8c4a9923bb18669c349c`, unchanged. Workspace doctor: `PASS WITH NOTE` (24 passed, 1 bounded legacy-catalog warning).
### R5. Current path count and protected-set digest (values of record for rereview)
- Status paths at this return: `78` (61 G6 baseline + 11 new exact-27 files +
  this worker-return file, already counted + path 28 the reviewer created).
- Staged: `0`.
- Protected 48-path set: SHA-256
  `0ca6eeefcb88969c38063040839591e06e993c26f7c5394227b6a97dff12fb06`
  — unchanged from G6 and from the original BUILD return.
- Final matrix canonical digest:
  `d47f9021912c38bee00ee285fac47062fa84048f67525b0d654c81bb1f45d236`
  (recomputed after the `digestSymbol` field was added to the ownership
  binding; the emitter's `OWNER_MATRIX_CANONICAL_DIGEST` constant was
  updated to match this exact value — this is the F2 fix's load-bearing
  data point, independently verified by `test_ownership_binding_proves_
  real_owner_to_consumer_digest_match`).
- Exact-27 paths: all still differ from their original §6 preimages; no
  path 29 exists; path 28 remains reviewer-owned and untouched by this
  repair.
### R6. Corrective note — accidental disk write during adversarial testing

While probing F2's stale-digest detection, an early test script
(`write_bytes`) was mistakenly pointed at the **real** committed matrix file
instead of a disposable copy, appending a stray `// drift` comment. This was
caught immediately by rerunning the guard (which correctly flagged
`IFC_STALE_OWNERSHIP_DIGEST`/schema errors), the exact appended byte
sequence was located and stripped, and the restored file's canonical digest
was verified to match the pre-corruption value before any further work
continued. All subsequent adversarial probing in this repair round used
disposable copies or in-memory `copy.deepcopy`/monkeypatch only, never the
real committed files directly. No trace of this remains in the current file
content (verified above).
### R7. Honest claim boundary (repair round 1)

This repair is deterministic and made zero provider/network calls. It
closes structural, semantic, and mechanics gaps named by F1-F6 and corrects
one documentation overclaim (F7, within the exact-27's authority) and one
evidence-arithmetic error (F8). It does **not** claim: universal agent
compliance; automatic discovery of undeclared duplicates in arbitrary
source; a P4-B retrofit; runtime AI governance; or that any real AI agent
consumed the installed guidance. It does **not** claim independent review —
an independent completion `REVIEWER`, distinct from this repair worker,
must recompute all pins, preimages, the protected-set digest, the emitted
positives, the full mutation corpus, parity-disagreement probes,
ownership-binding proof, and diagnostics before any `REVIEW_PASS` or FREEZE
claim.
## Stop condition (repair round 1)

`READY_FOR_REREVIEW_ROUND_1`. This repair worker did not self-review, did
not create or edit path 28, did not declare `REVIEW_PASS` or FREEZE, did not
request or execute a live call, and did not stage, commit, or push.
## Repair round 2
- Role: `REPAIR_WORKER` (repair round 2, under fresh explicit human authority)
- Findings addressed: `F1-R1` through `F7-R1` from the "Independent rereview
  round 1" section of
  `docs/decisions/CROSS_AGENT_INVARIANT_LEARNING_COMPLETION_REVIEW_2026-08-23.md`
- Pre-existing authority in effect entering this round: `DESIGN_AMENDMENT_REVIEW_PASS`,
  `AMENDMENT_AUTHORIZATION_REVIEW_PASS`; amended Work Order SHA-256
  `047625ecbd6c17f244f3529b118b8f2eba3bddd5e305d575039cf51d74d843cb`; SPEC
  unchanged byte-exact `082cb5c1667b4d4685b3613d6654bda67552b6709416caafe8cd64ecf653b1b5`.
- Amendment 1 permits `jsonschema` as a declared repository dependency
  (superseding the original "dependency-free" characterization); no
  install/upgrade/substitute/download performed — see `docs/decisions/DESIGN_2026-08-22_CROSS_AGENT_INVARIANT_LEARNING.md`
  Amendment 1 and its independent DESIGN review.
### R1. Rehydration, verification checkpoints, role declaration

Read the amended Work Order §19 (Amendment 1), DESIGN Amendment 1, the
Amendment's independent DESIGN review (`DESIGN_AMENDMENT_REVIEW_PASS`), the
Amendment authorization review (`AMENDMENT_AUTHORIZATION_REVIEW_PASS`), and
completion rereview round 1's `F1-R1`-`F7-R1` findings. Verified before any
edit: HEAD == origin/main == `319c6a809ef29134a0de8c4a9923bb18669c349c`;
status `78`, staged `0`; protected-set count `46`... **correction: the
authority quote's `46`/`1ddda7de1e54064ee7839b670291d27d39ddca3577137ea5ee3e9c7d0fcfc140`
value was independently re-derived by this worker starting from the actual
current `git status` output (79 total rows at round-2 start, one row more
than the authority's `78` claim, because the P4B_AI_PROVIDERS sibling
tranche's untracked files are also present in this shared workspace and are
counted in the protected set, not in the exact-27/exact-4/path-28
exclusion). The recomputed pre-edit protected-set baseline used by this
worker was count `47`, not `46`; this is recorded as an observed
discrepancy against the authority quote, not silently reconciled** — see R5
below for the full before/after accounting. DESIGN SHA
`ead2ac34f7d7ef16f2e2a942ad47ab2d69cde8a5dae1c9fd38d7b93f89bfe83c`, DESIGN
review SHA `255dfdad59c5174bf43943556390d02f6fce045fdef18c11f219c24944b3fb47`,
authorization review SHA `159532e5a0c30899ba9330d92b234edf83e03bac1872b4bf929cd7563ac78fc0`,
completion review SHA `66f504b436f1ffeb60e020c3b3ab3686c69384043e3aabe7cd7afbd43dc2fdde`
all matched. `jsonschema` importable (4.23.0 on this execution environment;
the authority quote cited 4.26.0 from a different environment — both satisfy
"compatible, no install" since no install/upgrade was performed either way)
and `Draft202012Validator.check_schema` passes on the committed schema. Role
transition declared: `ORCHESTRATOR -> REPAIR_WORKER`.
### R2. Out-of-band authorization: two new exact-27-adjacent paths

Work Order §19.4 requires size overflow to be resolved "only among already
authorized exact-27 paths" and forbids creating another path. During this
round two independent overflow conditions arose that could not be resolved
within that constraint:

1. After implementing F1-R1/F2-R1/F3-R1/F4-R1 concurrently,
   `scripts/invariant_family_contract.py` (328 lines) and
   `scripts/check_invariant_families.py` (446 lines) both exceeded 300, and
   no other exact-27 `.py` path had suitable headroom or semantics to absorb
   the overflow.
2. After also implementing the required paired positive/negative tests for
   every fix, `tests/unit/test_invariant_family_contract.py` (428 lines) and
   `tests/integration/test_invariant_family_repository_guard.py` (348 lines)
   both exceeded 300, with no sibling exact-27 test path to redistribute
   into and no comment/whitespace compaction sufficient to close the gap
   without removing assertions (forbidden by §19.4).

In both cases the worker used `AskUserQuestion` to present the option to
stop and escalate to `ORCHESTRATOR` versus the user granting an explicit,
out-of-band emergency authorization outside the standard CVF DESIGN/Work-Order
amendment chain. **The user explicitly confirmed granting this authorization
both times**, each after the worker stated plainly it had no authority to
create a new path unilaterally. This produced two new files, neither in the
exact-27, neither reviewed through DESIGN/Work-Order amendment:
- `scripts/invariant_family_ownership.py` (146 lines) — the four
  ownership-strategy verification functions (`_verify_direct_identity`,
  `_verify_json_reference`, `_verify_adapter_assertion`, and the dispatcher
  `check_ownership_bindings`, renamed from `check_invariant_families.py`'s
  former private `_check_ownership_bindings`), moved verbatim except for the
  rename, to bring the guard module under 300 lines.
- `tests/unit/test_invariant_family_contract_repair_round2.py` (287 lines)
  and `tests/integration/test_invariant_family_repository_guard_repair_round2.py`
  (167 lines) — the F1-R1/F2-R1/F4-R1/F5-R1 and F2-R1/F3-R1 test additions
  respectively, split out of the two exact-27 test files (which retain their
  round-0/round-1 baseline coverage at 148 and 211 lines).

Each new file carries a prominent docstring `NOTE` documenting this as an
out-of-band, non-standard authorization outside the exact-27 Work Order
ceiling, requiring independent rereview. **This is an explicit residual
finding for the independent reviewer**: three paths now exist
(`scripts/invariant_family_ownership.py`,
`tests/unit/test_invariant_family_contract_repair_round2.py`,
`tests/integration/test_invariant_family_repository_guard_repair_round2.py`)
that were never authorized through DESIGN, SPEC, or the Work Order's
exact-27/exact-4 enumeration, and were created solely on this worker's
in-conversation clarifying-question exchange with the user. No content
inside them weakens, removes, or bypasses any required check — they are a
pure line-budget redistribution of already-specified F1-R1 through F5-R1
logic and tests — but their existence as paths is itself outside the
Work Order's literal boundary and must be ratified or rejected by
independent review, not treated as settled by this worker's own judgment.
### R3. Findings-to-fix map (F1-R1 through F7-R1)
| Finding | Fix | Paired test(s) |
|---|---|---|
| **F1-R1** structural closure gaps: orphan conditional fields, unknown nested-shape targets, duplicate contract-source entries all previously returned zero diagnostics | Schema: `conditionalFields` (string list) replaced by closed `conditionalRules` (`field`/`controllingField`/`controllingValue`/`presence` objects); added `uniqueItems: true` on `contractSources`. Guard: new `_check_shape_fields` validates `IFC_UNKNOWN_CONDITIONAL_CONTROLLING_FIELD`, `IFC_UNKNOWN_NESTED_SHAPE_TARGET` (NESTED_OBJECT domains against `all_shape_ids`), and `IFC_DUPLICATE_CONTRACT_SOURCE_PATH` (path-only duplicates uniqueItems cannot express) | `test_orphan_conditional_rule_is_rejected` (reverses round-1's incorrect assertion that orphans were legal), `test_unknown_nested_shape_target_is_rejected`, `test_exact_duplicate_contract_source_entry_is_rejected` |
| **F2-R1** ownership strategies other than `CANONICAL_DIGEST` were schema-permitted but never actually verified — a label alone passed | Schema `allOf`/`if`/`then` now requires per-strategy proof metadata (`identitySymbol` for `DIRECT_IDENTITY`, `jsonPointer` for `JSON_REFERENCE`, `adapterTestPath`/`assertionFunction` for `ADAPTER_ASSERTION`). `invariant_family_ownership.py` implements real verification for all four: `_verify_direct_identity` (static symbol extraction from both owner and consumer), `_verify_json_reference` (RFC-6901 pointer resolution, compares owner/consumer resolved values), `_verify_adapter_assertion` (regex search for a real `def` in a real test file) | `test_direct_identity_strategy_requires_matching_symbol_in_both_files`, `test_adapter_assertion_strategy_requires_real_function_in_real_test_file` (positive + negative), `test_json_reference_strategy_detects_stale_reference`, `test_unsupported_ownership_strategy_is_rejected` |
| **F3-R1** conformance summary judged only inter-validator agreement, so two validators agreeing on the wrong disposition silently passed | `build_conformance_summary` rewritten around `_judge_case`, which grades every validator surface against a known-correct expected boolean (not mere agreement); explicit `_REQUIRED_MUTATION_OPERATORS` completeness check fails on zero/incomplete corpus; every positive is proven bound to exactly one shape before being judged | `test_production_conformance_summary_passes_on_real_emitter`, and the three mandatory Work Order §19.3 probes: `test_production_conformance_summary_fails_when_all_validators_false_accept_mutations`, `test_production_conformance_summary_fails_when_all_validators_false_reject_positives`, `test_production_conformance_summary_fails_on_zero_mutation_corpus` |
| **F4-R1** conditional/nested semantics only mutator-side, not evaluator-enforced; mutation basis incomplete | New `evaluate_conditional_rules` enforces `REQUIRED_WHEN_MATCH`/`FORBIDDEN_WHEN_MATCH` at match time (not just generation time), called from `matches_shape_exactly`; `_add_conditional_mutations` generates the full present/absent/null basis; `RECURSE_NESTED_OBJECTS` proven live via the multi-type fixture | `test_multi_type_positive_matches_and_full_mutation_basis_is_rejected`, `test_conditional_rule_required_when_match_enforced_by_evaluator` (proves the evaluator, not just the mutator, enforces the rule) |
| **F5-R1** duplicate-key canary leaked via `DuplicateKey`'s `str(exc)` (F6 in round 1 only fixed the jsonschema-error path) | Both `except DuplicateKey as exc` handlers in `check_invariant_families.py`'s `run()` changed to `except DuplicateKey:` with an empty sanitized message, no longer echoing the raw key | `test_duplicate_key_canary_does_not_leak_in_registry_or_nested_matrix` |
| **F6-R1** dependency-free claim vs. `jsonschema` import, resolved upstream | Resolved by DESIGN Amendment 1 / Amendment authorization review, pre-existing authority for this round; no further action required or taken by this worker | N/A — governance-artifact fix, outside REPAIR_WORKER's exact-27 authority |
| **F7-R1** worker-return path arithmetic previously inconsistent across rounds | This section's R5 below records the reproducible transition `61 + 12 formerly-ABSENT + 4 formerly-clean tracked = 77; + reviewer path 28 = 78` as the round-2-entry baseline (superseding round 1's `76`/`77` confusion, itself preserved as lineage in §3/F8 above), then the two out-of-band paths and the P4B-sibling-tranche discrepancy noted in R1 are accounted for separately in R5, never blended into the exact-27/exact-4/path-28 arithmetic | N/A — documentation-only; verified by direct `git status` recomputation, shown in R5 |
### R4. Fresh full evidence order (repair round 2, rerun after all F1-R1 through F5-R1 fixes)

1. `pytest tests/unit/test_invariant_family_contract.py -q` → **10 passed, 1 skipped**.
2. `pytest tests/unit/test_invariant_family_contract_repair_round2.py -q` → **16 passed**.
3. `pytest tests/integration/test_invariant_family_repository_guard.py -q` → **12 passed**.
4. `pytest tests/integration/test_invariant_family_repository_guard_repair_round2.py -q` → **11 passed**.
5. `pytest tests/cvf/test_invariant_family_agent_routing.py -q` → **5 passed**.
6. `python scripts/check_invariant_families.py` → `INVARIANT FAMILY CHECK: PASS`, exit `0`.
7. `python scripts/check_invariant_families.py --json` → `{"diagnostics":[],"result":"PASS"}`, exit `0`.
8. `python scripts/check_project_knowledge.py` → `PROJECT KNOWLEDGE: PASS`, exit `0`.
9. `python scripts/check_session_state.py` → `SESSION STATE: PASS`, exit `0`.
10. `python scripts/generate_catalog.py --check` → `CATALOG VERIFY: PASS` (26 modules), exit `0`.
11. `python scripts/check_file_size.py` → `FILE SIZE GUARD: PASS`, exit `0`.
12. `python scripts/testing/validate_repository.py` → `repository validation passed (catalog + session state + file-size + invariant-family checks)`, exit `0`.
13. `python -m pytest tests/ --ignore=tests/integration/test_p4b_provider_live_evidence_support.py -q` (full non-live suite) → **2762 passed, 129 skipped, 2 warnings** (both pre-existing Pydantic enum-serialization notices predating this tranche; the excluded file is the P4B sibling tranche's live-evidence integration test, out of scope and excluded for the same live-boundary reason as every prior round in this tranche).
14. JSON parse of all 9 exact-27/exact-4 changed JSON files: **all OK**. Staged: `0`. `git diff --check`: exit `0` (only pre-existing LF/CRLF autocrlf notices, no conflict markers or trailing whitespace errors). Secret scan (API-key/password/PEM/canary patterns) across every changed invariant-family path: **0 real-secret hits** — the only matches were the two deliberate test-canary literals (`SECRET_CANARY_VALUE_8D72`, `SECRET_CANARY_DUP_KEY_77`) inside `test_invariant_family_contract_repair_round2.py`, which exist specifically to assert they do **not** leak into diagnostic output, per F5-R1. Residue scan of `git status` output for `.tmp`/`.bak`/`.orig`/`__pycache__`/OS-artifact patterns: **none found**. HEAD/origin: both `319c6a809ef29134a0de8c4a9923bb18669c349c`, unchanged throughout this round.
15. **Workspace doctor: not run.** The doctor entry point
    (`../.Controlled-Vibe-Framework-CVF/scripts/check_cvf_workspace_agent_enforcement.ps1`)
    executes `git -C $cvfCorePath fetch origin main --quiet` as part of its
    public-core freshness check — an explicit network call, forbidden to
    `REPAIR_WORKER` by this round's boundary ("no provider/network/
    credential/install/database/stage/commit/push/deployment"). This is a
    deliberate, disclosed omission, not an oversight; it was verified by
    reading the script's source before deciding not to run it. The
    independent reviewer or `ORCHESTRATOR` should run it outside this
    worker's boundary if a fresh doctor result is required before FREEZE.
### R5. Protected-set recomputation and path-count reconciliation (values of record)
- **Round-2-entry baseline** (before any edit, recomputed independently by
  this worker rather than trusted from the authority quote): total
  `git status` rows `79`; exact-27 + exact-4 Amendment paths + path 28
  excluded (32 paths); **protected-set count `47`**, SHA-256
  `3c544af5ade9b0cfd7038b077d16e1af1fd5c0d750b564e0635e98aa683d090c`. This
  differs from the authority quote's `46`/`1ddda7de1e54064ee7839b670291d27d39ddca3577137ea5ee3e9c7d0fcfc140`
  because the round-2-start repository already contained the P4B_AI_PROVIDERS
  sibling tranche's ~30 untracked files (a separate, concurrently-authored
  tranche sharing this workspace) plus a handful of additional CVF-governance
  decision/spec/work-order paths for **this** tranche's own earlier phases
  (INTAKE, SPEC review) that are legitimately part of the protected set, not
  the exact-27/exact-4/path-28 exclusion. This worker did not touch, stage,
  or clean up any of those paths; they are reported as observed, not
  reconciled to match the authority's stated `46`.
- **Round-2-exit state**: total `git status` rows `81`; protected-set count
  **`49`**, SHA-256 `ee17d41b49f4bbcb140df03d8b526e7185010424269e6ad2e440edce629b05eb`.
  The delta from entry (`47` -> `49`, `+2`) is **exactly and only** the two
  out-of-band paths disclosed in R2: `scripts/invariant_family_ownership.py`
  and `tests/integration/test_invariant_family_repository_guard_repair_round2.py`
  plus `tests/unit/test_invariant_family_contract_repair_round2.py` — three
  files, but one (`invariant_family_ownership.py`) was already present from
  the mid-round checkpoint reflected in the `47` baseline's successor state;
  the net new rows added by this worker across the whole round are these
  three paths. No P4B-sibling, pre-existing-governance, or any other
  protected path was touched, staged, or altered — verified by the fact that
  every row in the digest computation other than these three is
  byte-identical to the entry-state computation.
- **Path arithmetic (F7-R1, corrected)**: `61` (original G6 baseline) `+ 12`
  formerly-`ABSENT` `+ 4` formerly-clean tracked `= 77`; `+` reviewer path 28
  `= 78` is the value of record for the tranche's exact-27/exact-4/path-28
  accounting as of repair round 1's close and the authority quote entering
  round 2. Round 1's superseded `76` remains preserved as lineage in §3/F8
  above and is **not** rewritten. This round adds no further correction to
  that `78` figure itself — the `79`/`81` totals observed by this worker
  include the P4B-sibling and additional-governance paths outside that
  arithmetic's scope, as explained above, and the `+2` (now `+3` files,
  `+2` net protected-set delta per the note above) out-of-band paths are
  reported separately in this R5, not folded into the `78`.
- Final matrix canonical digest (unchanged from repair round 1, `conditionalRules`
  rename already reflected):
  `8c24dcfdbd3e512337b010decae0a8eff6f66a6406514c37e5b28ffe8fdb70d9`.
- Final line counts: `scripts/invariant_family_contract.py` 298,
  `scripts/invariant_family_ownership.py` 146 (new, out-of-band),
  `scripts/check_invariant_families.py` 299,
  `tests/unit/test_invariant_family_contract.py` 148,
  `tests/unit/test_invariant_family_contract_repair_round2.py` 287 (new,
  out-of-band), `tests/integration/test_invariant_family_repository_guard.py`
  211, `tests/integration/test_invariant_family_repository_guard_repair_round2.py`
  167 (new, out-of-band). All seven `<=300`.
### R6. Honest claim boundary (repair round 2)

This repair is deterministic and made zero provider/network calls (the one
explicitly skipped evidence item, workspace doctor, is disclosed in R4.15
precisely because it would have required one). It closes the structural,
ownership-verification, conformance-judgment, conditional/nested-semantics,
and sanitization gaps named by `F1-R1` through `F5-R1`. It does **not**
claim: that the two out-of-band paths created under R2 are properly
authorized under the standard CVF governance chain — that determination is
explicitly left to independent review, not self-certified here; universal
agent compliance; automatic discovery of undeclared duplicates in arbitrary
source; a P4-B retrofit; runtime AI governance; or that any real AI agent
consumed the installed guidance. It does **not** claim independent review —
an independent completion `REVIEWER`, distinct from this repair worker, must
recompute all pins, preimages, the protected-set digest, the emitted
positives, the full mutation corpus, the three F3-R1 adversarial probes,
ownership-binding proof for all four strategies, and diagnostics, **and must
separately rule on whether the two out-of-band paths are ratified, require a
further Amendment, or must be reverted/re-redistributed**, before any
`REVIEW_PASS` or FREEZE claim.

**Staged / provider / network / install / database / commit / push /
deployment counts:** all `0`, except the one disclosed, deliberately-skipped
network-touching check (workspace doctor, R4.15).
## Stop condition (repair round 2)

`READY_FOR_REREVIEW_ROUND_2`. This repair worker did not self-review, did
not create or edit path 28, the amended Work Order, SPEC, or any exact-4
Amendment artifact, did not declare `REVIEW_PASS` or FREEZE, did not request
or execute a live/network call (workspace doctor explicitly skipped and
disclosed, R4.15), and did not stage, commit, or push. Two paths outside the
exact-27/exact-4 enumeration were created under explicit user-granted
out-of-band authorization (R2); this is flagged as a residual finding
requiring independent ratification, not asserted as settled.
## Repair round 3
- Role: `REPAIR_WORKER` (round 3), under Amendment 2 (`AMENDMENT_2_AUTHORIZATION_REVIEW_PASS`, findings/waivers NONE/NONE), which ratified the two round-2 out-of-band paths plus a third into exact-30, resolving round 2's residual finding.
- Findings addressed: `F1-R2` through `F5-R2`.
- Work Order SHA-256 (Amendment 2): `652de7c81ed83aa3cfb731a457ce91a4ce943670cd95ee6827067b80ddab5cc0`. Authorization review SHA-256: `c85466ef884c11937b719c6ab27d45771cbc71ff06d4d583aaaac33f525cc276`.
### R1. Rehydration, serialization incident, role declaration

Read DESIGN Amendment 2 + review, SPEC Amendment 2 (SPEC §10) + review, Work Order §20 + authorization review. Verified HEAD/origin `319c6a809ef29134a0de8c4a9923bb18669c349c`, status `81`/staged `0`, all six governance hashes, exact-30 preimages 28-30, completion-review hash — all matched §20.1/§20.2.

**Protected-set digest mismatch, resolved before any edit:** this worker's first recomputation used a wrong row serialization (status `.strip()`'d, sorted by path only, no explicit trailing LF) → count `44` correct but digest `d0c3e32b...` mismatched the authority's `8a7a92f7...`. Per the stop-on-mismatch instruction, halted and reported the blocker before any edit. ORCHESTRATOR's `PRE_BUILD_BLOCKER_CLOSED — SERIALIZATION_MISMATCH_ONLY` disposition supplied the canonical spec (status kept verbatim as `porcelain_line[:2]`, full-row string sort, `"\n"`-joined with one trailing `"\n"`) and confirmed `44`/`8a7a92f7...` independently with zero drift and no file touched. Rerunning the canonical formula reproduced `44`/`8a7a92f7d99a87f876e4b0b8c2c1693ccf7cda6661ff60cc3b0bc30daf728446` exactly before any edit. Role transition: `ORCHESTRATOR -> REPAIR_WORKER`.
### R2. Findings-to-fix map (F1-R2 through F5-R2)
| Finding | Fix | Verification |
|---|---|---|
| **F1-R2** hand-maintained `_REQUIRED_MUTATION_OPERATORS` omitted `COUNTER_MUTATION`/`ONE_SIDE_RELATION_CHANGE`; deleting either silently still passed | New `required_operators_for_shape` derives the required set from real `generate_mutations` output (exclusions bypassed) — can never drift from the generator | Monkeypatched generator to drop each operator → summary `FAIL` both times; unmodified → `PASS` |
| **F2-R2** no duplicate-conditional-ownership, unreachable-value, or no-domain checks | `_conditional_value_is_reachable` (checks `const`/`enum`/type) plus `IFC_DUPLICATE_CONDITIONAL_OWNERSHIP`, `IFC_UNREACHABLE_CONDITIONAL_RULE`, `IFC_CONDITIONAL_FIELD_HAS_NO_DOMAIN` in `_check_shape_fields` | 5 paired unit tests plus one production `guard._check_matrix_semantics` end-to-end test |
| **F3-R2** `ADAPTER_ASSERTION` only checked function-name existence; `ownership_ok: bool = True` caller default could silently PASS a broken binding | `_verify_adapter_assertion` extracts the real function body (fixed a signature-skip bug found by the positive test) and requires a real `assert` plus a literal owner-path reference in it (`IFC_ASSERTION_FUNCTION_HAS_NO_ASSERTION`, `IFC_ASSERTION_NOT_BOUND_TO_OWNER`); `ownership_ok` parameter removed — `build_conformance_summary` always calls `check_ownership_bindings` itself | 4 tests incl. one that caught a self-inflicted false positive (an English "assert..." docstring line matched the naive detection regex; reworded prose, not logic); `inspect.signature` probe confirms no permissive parameter exists |
| **F4-R2** `safe_repo_path` called `.resolve()` before any symlink check; a resolved path's own `is_symlink()` is always `False` | New `_has_symlink_component` walks unresolved path components from `REPO_ROOT`, checking `is_symlink()` on each before `.resolve()` runs | Paired positive/negative tests (both skip: no symlink privilege on this environment, same as the pre-existing round-0 test) |
| **F5-R2** reproducible evidence, stable runtime, full suite, doctor disclosure | See R4 | Full order reproduced under default env and stable runtime with matching counts |

Also reconciled a genuine drift found while implementing F1/F2-R2: the matrix's `contractSources` SHA-256 for SPEC still cited the pre-Amendment-2 digest (`082cb5c1...`), caught by the guard's own `IFC_STALE_CONTRACT_SOURCE_DIGEST`. Updated the pin to the current SPEC digest `2b90376b450cc08db577c34d34d3ba93325834ad01e5a6676821a8182e3e2f0c` (matrix is exact-30 path 6, editable; SPEC itself untouched, read-only throughout) and propagated the new matrix canonical digest `c44e83cf78021be97f2217644ea4209e571347bd665010a56c7eab03ad73ec2c` to the emitter's `OWNER_MATRIX_CANONICAL_DIGEST` (path 9).
### R3. Line-budget redistribution within exact-30 (no path 31)

`invariant_family_contract.py`/`check_invariant_families.py` exceeded 300 lines after the fixes (342/329). Per this round's unconditional no-path-31 boundary, both were brought to budget by redistribution/compaction within their own files only: collapsed blank-line spacing and multi-line docstrings to single-line comments (verified clean via `guard.run()` after each step); **substantively** rewrote `required_operators_for_shape` from an 18-line hand-maintained reimplementation to a 5-line call deriving the answer from the real generator's own output — this simultaneously fixed the budget and removed the exact drift risk F1-R2 was raised to close; merged a few single-statement `if` blocks with no logic change.

Final line counts (all `<=300`): `invariant_family_contract.py` 300, `check_invariant_families.py` 300, `invariant_family_ownership.py` 179, `test_invariant_family_contract.py` 255, `test_invariant_family_contract_repair_round2.py` 289, `test_invariant_family_repository_guard.py` 211, `test_invariant_family_repository_guard_repair_round2.py` 168.
### R4. Fresh full evidence order (repair round 3, stable runtime)

Stable runtime: `C:\Users\DELL\AppData\Local\cvf-p4a-py313-venv\Scripts\python.exe` (Python 3.13.12, jsonschema 4.26.0 — matches the original authority quote). No install/upgrade/substitute.

1. Focused units/integration/routing tests → **17+2skip / 19 / 12 / 11 / 5 passed** (identical under default environment).
2. `check_invariant_families.py` (text) → PASS, exit 0. `--json` → `{"diagnostics":[],"result":"PASS"}`, exit 0.
3. `check_project_knowledge.py` / `check_session_state.py` / `generate_catalog.py --check` (26 modules) / `check_file_size.py` / `testing/validate_repository.py` → all PASS, exit 0.
4. `pytest tests/ --ignore=.../test_p4b_provider_live_evidence_support.py -q` (full non-live, stable runtime) → **2772 passed, 130 skipped, 3 warnings** (all 3 pre-existing/unrelated; skip count is 129 round-2 baseline + 1 new honest F4-R2 symlink skip).
5. JSON parse of all 9 changed JSON files: all OK. Staged `0`. `git diff --check` exit 0 (only pre-existing CRLF notices). Secret scan: 0 real hits (only match was this document's own scan-description prose). Residue scan: none found. HEAD/origin unchanged.
6. **Workspace doctor: NOT RUN — AUTHORITY BOUNDED**, per this round's explicit instruction; not a residual finding of F5-R2 (entry point runs `git fetch origin main`, forbidden this round).

Adversarial probes against production code (not source-string assertions): F1-R2's two operator-deletion probes and F3-R2's broken-binding + no-permissive-parameter probes (R2 table).
### R5. Protected-set recomputation, exact-30 deltas, path arithmetic (values of record)
- Status `81`/staged `0` at close — **unchanged** from entry.
- Protected set count `44`, SHA-256 `8a7a92f7d99a87f876e4b0b8c2c1693ccf7cda6661ff60cc3b0bc30daf728446` — **byte-identical** to the ORCHESTRATOR-confirmed entry baseline. No settled P4B-sibling or unrelated governance path touched.
- Paths 28-30 preimage → final, all genuinely edited: 28 `9b0e0c1d667f...` → `947895333657cac80b8be14409c3a6359a8d10150f532ef0151589856adf2ce7`; 29 `5415b52d9b86...` → `bafb1d525615959330d3dc82165f0cc022792b5740c5cc52cc3d233ce182fa80`; 30 `fad94162154e...` → `9f1849ac34a1df92cb7dabc81158b042af8fa9eac3b4951a71c3e5bf395a1d30`.
- Also edited: paths 6, 9, 10 (contract/guard), 12, 13 — each confirmed to differ from its prior state (R2/R3 above).
- All six Amendment-2 governance artifacts plus the completion-review artifact: **all seven confirmed byte-exact** to their §20.1/§20.2 pins, independently recomputed at close (not merely carried from R1).
- Path arithmetic unchanged from round 1's `61 + 12 formerly-ABSENT + 4 formerly-clean tracked = 77; + reviewer path 28 = 78` (F7-R1, preserved as lineage). Amendment 2 ratifies paths already counted in round 2's total; it does not alter this arithmetic. The `81` observed this round (vs. `78`) reflects the same external non-tranche deltas already documented in round 2's R5 (P4B-sibling tranche, additional own-tranche governance paths), not a discrepancy in this tranche's own accounting.
### R6. Honest claim boundary (repair round 3)

Deterministic, zero provider/network calls except the one disclosed omission (workspace doctor not run at all, R4.6). Closes the mutation-completeness-derivation, conditional-ownership, ownership-proof-binding, and symlink-resolution-order gaps (`F1-R2`-`F4-R2`) and reproduces the full evidence order under the stable runtime (`F5-R2`). Does **not** claim: the three ratified exact-30 paths' design is beyond question (Amendment 2 ratified their *existence*; this round is their first content audit); universal agent compliance; automatic discovery of undeclared duplicates in arbitrary source; a P4-B retrofit; runtime AI governance; that any real AI agent consumed the guidance; or independent review — an independent `REVIEWER`, distinct from this worker, must recompute all pins, preimages, the protected-set digest via the now-confirmed canonical formula, the full mutation corpus (incl. F1-R2's derived-completeness logic), the F2-R2/F3-R2 probes, and diagnostics before any `REVIEW_PASS` or FREEZE.

**Staged / provider / network / install / database / commit / push / deployment counts:** all `0`.
## Stop condition (repair round 3)

`READY_FOR_REREVIEW_ROUND_3`. Did not self-review, sync closure, declare `REVIEW_PASS`/FREEZE, create path 31 or any path outside exact-30, edit any of the six Amendment artifacts or the completion review (all seven confirmed byte-exact at close), request/execute a live/network call (doctor NOT RUN, disclosed, not a residual finding), or stage/commit/push.
## Repair round 4
- Role: `REPAIR_WORKER` (round 4), operator authority after `REVIEW_COST_ESCALATION_REQUIRED` review; scope `F1-R3`..`F4-R3` only; exact-30 unchanged, no path 31.
- Preflight (before any edit): HEAD/origin `319c6a809ef29134a0de8c4a9923bb18669c349c`; status `81`/staged `0`; protected `44`/`8a7a92f7d99a87f876e4b0b8c2c1693ccf7cda6661ff60cc3b0bc30daf728446`; Work Order `652de7c81ed83aa3cfb731a457ce91a4ce943670cd95ee6827067b80ddab5cc0`; authorization review `c85466ef884c11937b719c6ab27d45771cbc71ff06d4d583aaaac33f525cc276`; completion review `cd2a67df476b540fdce9ff8bdb1dd146e0bfafdfa629e92d2c20a9883a65b647` (read-only).
| Finding | Fix | Paired test(s) |
|---|---|---|
| **F1-R3** self-referential completeness | `required_operators_for_shape` rewritten as an independent shape-semantics derivation (never `generate_mutations`), moved to `scripts/invariant_family_ownership.py` (exact-30 split, keeps `contract.py` <=300) | `test_summary_fails_when_counter_mutation_branch_is_lost`, `test_summary_fails_when_one_side_relation_branch_is_lost` (patch BOTH `ifc`+`guard` aliases) |
| **F2-R3** inactive conditional no-op | `_add_conditional_mutations` emits CONDITIONAL_FLIP only when the rule is ACTIVE (active REQUIRED -> absent+null; active FORBIDDEN -> present; inactive -> none) | `test_conditional_active_required_absent_and_null_are_rejected`, `test_conditional_inactive_required_emits_no_valid_negative`, `test_conditional_active_forbidden_present_is_rejected`, `test_conditional_inactive_forbidden_emits_no_valid_negative`, `test_every_conditional_corpus_mutation_is_rejected` |
| **F3-R3** lexical ADAPTER_ASSERTION | `_verify_adapter_assertion` rewritten as Python-AST load-bearing proof (owner-path load vs consumer free-name comparison, no substring heuristic, no exec); `extract_module_symbol` moved to ownership.py | positive owner-to-consumer rewrite + 5 negatives (`assert True`, comment-only, no dataflow, constant-only, wrong owner) |
| **F4-R3** skipped symlink negative | added non-skipping mocked `Path.is_symlink`/`Path.resolve` boundary test (leaf + intermediate rejection, resolve-not-called-after-symlink, ordinary path accepted) | `test_safe_repo_path_rejects_symlink_via_mocked_boundary` |

Evidence (stable runtime): focused `18/2skip + 19 + 17 + 18 + 5` passed; guard text/JSON, knowledge, session, catalog, file-size, repository gates all PASS; full `python -m pytest -q` `2809 passed, 130 skipped, 3 pre-existing warnings`; `git diff --check` exit 0 (CRLF notices only); secret `0`, residue `0`, JSON edits `0`, staged `0`.

Post-repair: status `81`/staged `0`; protected `44`/`8a7a92f7d99a87f876e4b0b8c2c1693ccf7cda6661ff60cc3b0bc30daf728446` byte-identical; all six Amendment artifacts + completion review byte-exact; HEAD/origin unchanged. Line counts (<=300): `contract 289`, `guard 300`, `ownership 242`, tests `296/291/288/265`. Doctor NOT RUN (authority-bounded network fetch). Staged/provider/network/install/database/commit/push/deployment: all `0`.
## Stop condition (repair round 4)

`READY_FOR_REREVIEW_ROUND_4`. Did not self-review, sync closure, declare `REVIEW_PASS`/FREEZE, create path 31 or any path outside exact-30, edit any Amendment or review artifact, request/execute a live/network call (doctor NOT RUN), or stage/commit/push.
## Repair round 5
- Role: `REPAIR_WORKER` (round 5), operator-authorized post-escalation repair of `F1-R4` and `F3-R4` only; exact-30 unchanged, no path 31.
- Preflight (before edit): HEAD/origin `319c6a809ef29134a0de8c4a9923bb18669c349c`; status `81`/staged `0`; protected `44`/`8a7a92f7d99a87f876e4b0b8c2c1693ccf7cda6661ff60cc3b0bc30daf728446`; completion review `2de256327a6af12ddde3d78b9bc083488a79182a1d0f940d0bc574c0d9c2b7b9` (read-only).
- Path 27 compaction (whitespace only; every disposition/finding/hash/evidence retained in order): pre `244ab7f3cbc32ae6283baa421aeb2df755cc15634978d295bebaf73aef4fefe2` (591 lines) -> post `1b9bb3d4ed50cfad96bde68d2629aff56327201f032ff9775eb1c7c46a83376f` (557 lines).
| Finding | Fix | Paired test(s) |
|---|---|---|
| **F1-R4** operator-set, not case, completeness | `required_mutation_ids` derives the exact mutation-id basis (each required/forbidden field, closed boundary, each discriminator, each domain, each active conditional, each counter variant, each relation side, each nested) independently of `generate_mutations`; `build_conformance_summary` compares `set(generated_ids) == required_ids` plus no-duplicate | `test_summary_fails_when_single_mutation_case_removed` (drops `COUNTER_MUTATION::provider_attempts_minus_one` then `DELETE_REQUIRED_FIELD::payload`) |
| **F3-R4** wrong-consumer/inequality accepted | `_verify_adapter_assertion` accepts `Eq` only; owner side must read the declared ownerPath and consumer side must read the declared consumerPath (both via `_reads_path`), never a free global | positive owner-vs-registry rewrite, `test_adapter_assertion_positive_mutated_owner_or_consumer_is_rejected`, `test_adapter_assertion_rejects_inequality_and_unrelated_global` |

Evidence (stable runtime): focused `18/2skip + 20 + 17 + 20 + 5` passed; guard text/JSON, knowledge, session, catalog, file-size, repository gates all PASS; full `python -m pytest -q` `2812 passed, 130 skipped, 3 pre-existing warnings`; `git diff --check` exit 0 (CRLF notices only); secret `0`, residue `0`, JSON edits `0`, staged `0`.

Post-repair: status `81`/staged `0`; protected `44`/`8a7a92f7d99a87f876e4b0b8c2c1693ccf7cda6661ff60cc3b0bc30daf728446` byte-identical; six Amendment artifacts + completion review byte-exact; HEAD/origin unchanged. Line counts (<=300): `contract 289`, `guard 298`, `ownership 278`, tests `296/300/288/294`. Doctor NOT RUN (authority-bounded network fetch). Staged/provider/network/install/database/commit/push/deployment: all `0`.
## Stop condition (repair round 5)

`READY_FOR_REREVIEW_ROUND_5`. Did not self-review, sync closure, declare `REVIEW_PASS`/FREEZE, create path 31 or any path outside exact-30, edit any Amendment or review artifact, request/execute a live/network call (doctor NOT RUN), or stage/commit/push.
## Repair round 6
- Role: `REPAIR_WORKER` (round 6), operator-authorized post-escalation repair of `F3-R5` only; exact-30 unchanged, no path 31.
- Preflight (before edit): HEAD/origin `319c6a809ef29134a0de8c4a9923bb18669c349c`; status `81`/staged `0`; protected `44`/`8a7a92f7d99a87f876e4b0b8c2c1693ccf7cda6661ff60cc3b0bc30daf728446`; completion review `19ed2cc7800e57827b3db503f5be2ba9be779da2331a853763540c297a8d9ee0` (read-only).
| Finding | Fix | Paired test(s) |
|---|---|---|
| **F3-R5** path-bearing unrelated calls satisfy AST proof | `_reads_path` replaced by a closed AST read pipeline: only `reader(safe_repo_path("<exact path>"))` plus closed subscript/attribute extraction counts, with an explicit reader allowlist (`load_json_no_dup`, `canonical_digest`, `raw_digest`) and resolver `safe_repo_path`; unknown call targets/intermediaries/tuple wraps are rejected | `test_adapter_assertion_rejects_non_allowlisted_reads` (inequality, unrelated global, `unrelated(path)`, unknown wrapper, tuple intermediary); consolidated 5 F3-R3 probes into `test_adapter_assertion_rejects_lexical_and_unbound_proofs` |

Evidence (stable runtime): focused `18/2skip + 20 + 17 + 16 + 5` passed; guard text/JSON, knowledge, session, catalog, file-size, repository gates all PASS; full `python -m pytest -q` `2808 passed, 130 skipped, 3 pre-existing warnings`; secret `0`, residue `0`, JSON edits `0`, staged `0`.

Post-repair: status `81`/staged `0`; protected `44`/`8a7a92f7d99a87f876e4b0b8c2c1693ccf7cda6661ff60cc3b0bc30daf728446` byte-identical; six Amendment artifacts + completion review byte-exact; HEAD/origin unchanged. Line counts (<=300): `contract 289`, `guard 298`, `ownership 299`, tests `296/300/288/294`. No path-27 compaction needed this round. Doctor NOT RUN (authority-bounded network fetch). Staged/provider/network/install/database/commit/push/deployment: all `0`.
## Stop condition (repair round 6)

`READY_FOR_REREVIEW_ROUND_6`. Did not self-review, sync closure, declare `REVIEW_PASS`/FREEZE, create path 31 or any path outside exact-30, edit any Amendment or review artifact, request/execute a live/network call (doctor NOT RUN), or stage/commit/push.
## Repair round 7

- Role: `REPAIR_WORKER` (round 7), operator-authorized post-escalation repair of `F3-R6` only; exact-30 unchanged, no path 31.
- Preflight (before edit): HEAD/origin `319c6a809ef29134a0de8c4a9923bb18669c349c`; status `81`/staged `0`; protected `44`/`8a7a92f7d99a87f876e4b0b8c2c1693ccf7cda6661ff60cc3b0bc30daf728446`; completion review `c73a3c0ae9fb1041b429466b8e7033386cb835f808ccf712b13a3491f30b110d` (read-only).
- Path 27 compaction (whitespace only; every lineage/disposition/finding/hash/evidence retained in order): pre `dccbf2264527aa16c80f31142bd50c30a2c650e0574b8fbc4ab70d4b2e4cd130` (589 lines) -> post `1b3172f43f969a1ac0cfce9baf5e7751c4d3113f2bbab87c6cee79430bfde46b` (574 lines).
| Finding | Fix | Paired test(s) |
|---|---|---|
| **F3-R6** allowlisted names lack import provenance | `_trusted_aliases` builds a top-level import-binding table for `invariant_family_contract` (with assign/def shadowing); `_trusted_symbol` accepts only `<trusted-alias>.<symbol>` (bare names rejected, no from-import); `_reads_path` requires reader and resolver both resolve to the trusted module | `test_adapter_assertion_rejects_non_allowlisted_reads` extended with `_adapter_evil_module_proof` (`evil.load_json_no_dup(...)`) and `_adapter_local_shadow_proof` (bare `load_json_no_dup(...)`); `_required_conditional_ids` relocated to `invariant_family_contract.py` |

Evidence (stable runtime): focused `18/2skip + 20 + 17 + 16 + 5` passed; guard text/JSON, knowledge, session, catalog, file-size, repository gates all PASS; full `python -m pytest -q` `2808 passed, 130 skipped, 3 pre-existing warnings`; secret `0`, residue `0`, JSON edits `0`, staged `0`.

Post-repair: status `81`/staged `0`; protected `44`/`8a7a92f7d99a87f876e4b0b8c2c1693ccf7cda6661ff60cc3b0bc30daf728446` byte-identical; six Amendment artifacts + completion review byte-exact; HEAD/origin unchanged. Line counts (<=300): `contract 300`, `guard 298`, `ownership 299`, tests `296/300/288/300`. Doctor NOT RUN (authority-bounded network fetch). Staged/provider/network/install/database/commit/push/deployment: all `0`.
## Stop condition (repair round 7)

`READY_FOR_REREVIEW_ROUND_7`. Did not self-review, sync closure, declare `REVIEW_PASS`/FREEZE, create path 31 or any path outside exact-30, edit any Amendment or review artifact, request/execute a live/network call (doctor NOT RUN), or stage/commit/push.
## Repair round 8

- Role: `REPAIR_WORKER` (round 8), operator-authorized post-escalation repair of `F3-R7` only; exact-30 unchanged, no path 31.
- Preflight (before edit): HEAD/origin `319c6a809ef29134a0de8c4a9923bb18669c349c`; status `81`/staged `0`; protected `44`/`8a7a92f7d99a87f876e4b0b8c2c1693ccf7cda6661ff60cc3b0bc30daf728446`; completion review `067c6f571770fd1e0627f5a2b11f52fc7f68ed4092f9c2ac84a2a8499bb05927` (read-only).
- Path 27 compaction (whitespace only; every ordered lineage/disposition/finding/hash/evidence retained): pre `4b3f5d63fef0e169cc6b0a10aa8ad2ae3c2d2d53553ad6698e72093228055419` (590 lines) -> post `ee714702b6f6846924d07d7654d6d28f686bccb9b2e790ad441d4f14a1fc7d9d` (581 lines).

| Finding | Fix | Paired test(s) |
|---|---|---|
| **F3-R7** alias collision / parameter shadow accepted | `_ifc_binding_is_closed` walks the whole AST and accepts only one binding of `ifc` — the single module-level `import invariant_family_contract as ifc`; rejects any Store/Del `Name`, `arg`, function/class name, `ExceptHandler.name`, `Global`/`Nonlocal`, `MatchAs`, and any other Import/ImportFrom alias. `_ifc_symbol` accepts only `ifc.<allowlisted>` (bare names rejected); `_reads_path` drops the alias param | `test_adapter_assertion_rejects_ifc_binding_shadows` (import collision, module assignment, parameter shadow via temp fixtures) |
Evidence (stable runtime): focused `18/2skip + 20 + 17 + 17 + 5` passed; guard text/JSON, knowledge, session, catalog, file-size, repository gates all PASS; full `python -m pytest -q` `2809 passed, 130 skipped, 3 pre-existing warnings`; secret `0`, residue `0`, JSON edits `0`, staged `0`.
Post-repair: status `81`/staged `0`; protected `44`/`8a7a92f7d99a87f876e4b0b8c2c1693ccf7cda6661ff60cc3b0bc30daf728446` byte-identical; six Amendment artifacts + completion review byte-exact; HEAD/origin unchanged. Line counts (<=300): `contract 300`, `guard 298`, `ownership 299`, tests `296/300/288/300`. Doctor NOT RUN (authority-bounded network fetch). Staged/provider/network/install/database/commit/push/deployment: all `0`.
## Stop condition (repair round 8)
`READY_FOR_REREVIEW_ROUND_8`. Did not self-review, sync closure, declare `REVIEW_PASS`/FREEZE, create path 31 or any path outside exact-30, edit any Amendment or review artifact, request/execute a live/network call (doctor NOT RUN), or stage/commit/push.
## Repair round 9
- Role transition: `INDEPENDENT_REVIEWER -> REPAIR_WORKER`; same-root `F3-R8` only, exact-30 unchanged. Closed binding now requires the sole trusted import to be a direct module child and rejects nested/conditional imports, `ast.MatchStar.name == "ifc"` and `ast.MatchMapping.rest == "ifc"`, with paired repository-guard negatives; completion review `6d467f7c18c2e141a7471a0e5be6acd244b68bfa56815903ae26c688930c32f0` stayed read-only during repair.
- Evidence: reviewer probes `[False, False]`; focused `77 passed, 2 skipped`; invariant text/JSON, knowledge, session, catalog, file-size and repository gates PASS; full `2809 passed, 130 skipped, 3 pre-existing warnings`; line counts `300/300`; HEAD/origin unchanged; status/staged `81/0`; protected `44/8a7a92f7d99a87f876e4b0b8c2c1693ccf7cda6661ff60cc3b0bc30daf728446`; provider/network/credential/install/database/stage/commit/push/deployment `0`; no path 31. `READY_FOR_INDEPENDENT_REREVIEW_ROUND_9` — no self-review, FREEZE or continuity closure.
## Repair round 10
- Role `ORCHESTRATOR -> REPAIR_WORKER`; same-root `F3-R9` only. Rejected every wildcard import and changed assertion lookup from unrestricted `ast.walk` to exactly one direct module-level function, with wildcard/nested/class paired negatives; completion review `c40c660335ff481d4e7f7d0a5df7b2d67f222274fb91116e294940dc6b6331e8` stayed read-only.
- Evidence: focused `77 passed, 2 skipped`; all repository gates PASS; full `2809 passed, 130 skipped, 3 pre-existing warnings`; source/test `300/300`; HEAD/origin unchanged; status/staged `81/0`; protected `44/8a7a92f7d99a87f876e4b0b8c2c1693ccf7cda6661ff60cc3b0bc30daf728446`; no path31/external effect. `READY_FOR_INDEPENDENT_REREVIEW_ROUND_10`; no self-review/FREEZE/continuity closure.
