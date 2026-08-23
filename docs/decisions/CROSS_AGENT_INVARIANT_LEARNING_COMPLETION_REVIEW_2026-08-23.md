# Cross-Agent Invariant Learning — Independent Completion Review
- Tranche: `CROSS-AGENT-INVARIANT-LEARNING-2026-08-22`
- Review date: `2026-08-23`
- Role: `INDEPENDENT_REVIEWER` (distinct from `IMPLEMENTATION_WORKER`)
- Execution base / HEAD / `origin/main`:
  `319c6a809ef29134a0de8c4a9923bb18669c349c`
- Reviewed Work Order SHA-256:
  `a7d52cdeeb954ce04cc7941796a6803c4d5204a17a8bf52905a0c3bf6caac874`
- Reviewed SPEC SHA-256:
  `082cb5c1667b4d4685b3613d6654bda67552b6709416caafe8cd64ecf653b1b5`
- Disposition: `REVIEW_CHANGES_REQUIRED`
- Open findings / waivers: `F1-F8` / `NONE`
- FREEZE: `NOT_AUTHORIZED`
## 1. Independent scope and baseline verification
The reviewer rehydrated canonical continuity, inspected source rather than
accepting the worker return, and ran the workspace doctor before review.
Doctor result was `PASS WITH NOTE`: 24 passed plus the same bounded legacy-
catalog warning.
Independent recomputation produced:
- staged paths: `0`;
- status paths: `77`;
- protected dirty-set count: `48`;
- protected dirty-set SHA-256:
  `0ca6eeefcb88969c38063040839591e06e993c26f7c5394227b6a97dff12fb06`;
- all exact-27 paths present and path 28 absent before this review;
- roadmap: `600` lines; bootstrap: `1401` bytes;
- hidden Core clean at the manifest pin.
The protected set, execution base, SPEC pin and Work Order pin are intact. No
path outside reviewer-owned path 28 was edited by this review. No provider,
network, credential, install, database, stage, commit, push or deployment
action occurred.
## 2. Passing evidence (insufficient for acceptance)
The reviewer independently reran the worker's existing evidence:
- focused tests: `11 + 15 + 5 = 31 passed`;
- invariant guard text/JSON: PASS;
- knowledge, session, catalog, file-size and repository gates: PASS;
- full suite: `2763 passed, 128 skipped, 3 pre-existing warnings`.
These results establish that the committed happy path and the worker-selected
probes pass. They do not satisfy R1-R22/AC-01..18 because the independent
mutations below pass through the guard or expose missing production mechanics.
## 3. Consolidated findings
### F1 — HIGH — Registry/schema/Python closure is fail-open
R3-R7, R13, R15 and AC-02/AC-11 require a closed registry, schema/Python
agreement and semantic validation of all referenced fields. The implementation
loads `registry.get("families", [])` without validating registry keys or entry
shape. An added top-level `unknownRegistryField` returned exit `0` and
`INVARIANT FAMILY CHECK: PASS`.
The JSON Schema accepts `docs//specs/...` while `safe_repo_path` rejects it,
violating required schema/Python parity. Changing a digest relation's
`sourceField` to an undeclared field also returned guard PASS. The semantic
checker does not fully validate conditional ownership, relation operands,
relation-specific required members, mutation exclusions, lifecycle/waiver
placement, registry/matrix metadata agreement, or all uniqueness rules.
Repair must close the registry and every schema/Python semantic edge named by
R3-R7, with paired mutations that fail for the intended diagnostic.
### F2 — HIGH — `CANONICAL_DIGEST` ownership is declared but not enforced
R11/AC-07 require owner existence, canonical digest/reference proof and stale
consumer detection. The current checker rejects only an unsafe owner string;
it does not require the owner to be a regular non-symlink file. Replacing the
owner with a normalized missing path returned guard PASS.
The matrix declares `CANONICAL_DIGEST`, but neither its consumer record nor the
synthetic emitter carries/verifies a digest binding. Appending drift to the
declared consumer also returned guard PASS. There is no test proving a real
owner-to-consumer digest relationship.
Repair must define an implementable non-self-confirming binding representation,
verify owner and consumer paths, enforce the selected strategy, reject stale
bindings, and add positive plus paired negative tests.
### F3 — HIGH — Reusable parity and conformance-summary mechanics are absent
R9/R12 and AC-06/AC-08 require the reusable helper to run one canonical corpus
across declared validators and return a deterministic complete sanitized
summary. `scripts/invariant_family_contract.py` exposes neither a parity
helper nor a conformance-summary function/type.
The parity function exists only inside the integration test, so the test proves
its own local set-comparison helper rather than production behavior. Summary
tests likewise write the arbitrary literal `{"result":"PASS"}` and delete its
directory; they never call production conformance code, prove completeness, or
induce a production failure. Repair must implement and test the real reusable
mechanics, including PASS and deliberate-failure cleanup.
### F4 — HIGH — The advertised generic mutation/relation contract is partial
R7/R10/R14/R15 and AC-05/AC-11 require the complete applicable one-fact basis.
The schema advertises `FIELD_EQUALITY`, `BOOLEAN` and `NUMBER`, while the
runtime evaluator/matcher does not implement those declared variants.
Nested-object recursion is not implemented at all. Conditional mutation emits
only one payload per field rather than the required present/absent and
null/value variants, and the bootstrap matrix records no explicit
`CONDITIONAL_FLIP` exclusions for its structurally inapplicable shapes.
The test for “exactly one semantic fact” asserts only that at least one key
changed. Repair must either implement every schema-advertised generic feature
and full R10 basis or narrow the reviewed declaration without changing SPEC;
every applicable operator must be enumerated and tested around every positive
shape, with explicit reviewed exclusions for inapplicable operators.
### F5 — HIGH — Required R15 adversarial matrix was not executed
The focused suite omits many explicit R15 classes, including closed registry
fields/entries, every unknown nested field, all path variants, missing owner
and stale ownership digest, duplicate ids with differing objects, zero
outcomes, orphan conditionals, unknown relation operands, missing mutation
operators, unsupported or stale ownership strategies, ambiguous/no positive
shape match, production summary completeness/sanitization/cleanup, and
repository-validator propagation from a disposable mutation.
The symlink test silently returns when symlink creation fails instead of using
an explicit skip or alternate probe. Repair must add the full enumerated R15
table as executable paired negatives; source-string assertions do not count.
### F6 — HIGH — Diagnostics disclose raw invalid values and schema content
R12/R16 require sanitized diagnostics with no raw value or file content.
`_check_matrix_schema` emits `str(jsonschema.ValidationError)[:200]`.
Setting `risk` to `SECRET_CANARY_VALUE_8D72` caused that exact canary to appear
in JSON output, together with schema excerpts. Repair must map validation
failures to stable sanitized codes/locations without serializing instances,
schema fragments, environment values or content. Add canary tests over text
and JSON modes.
### F7 — MEDIUM — The `dependency-free` claim is false
`docs/cvf/INVARIANT_FAMILY_STANDARD.md` calls the guard dependency-free, but
`scripts/check_invariant_families.py` imports third-party `jsonschema` at
runtime. The dependency happens to exist in the stable environment; that does
not make the CLI dependency-free. Repair the implementation or narrow the
claim consistently with DESIGN/SPEC without weakening Draft 2020-12
validation.
### F8 — LOW — Worker-return final status evidence is inaccurate
Path 27 records final status count `76`; independent `git status
--porcelain=v1 --untracked-files=all` returns `77`. The protected-set count and
digest remain correct, so this is evidence drift rather than scope drift.
Repair path 27 with the reproducible arithmetic and retain the superseded value
in lineage.
## 4. Repair boundary
All findings are within the unchanged objective, R2 ceiling, zero-external-
effect class and existing exact-27 worker union. A `REPAIR_WORKER` may repair
F1-F8 under Work Order section 13 without a new path or provider authority.
Path 28 remains reviewer-owned and read-only to the repair worker; no path 29
may be created. SPEC, Work Order, authorization review, settled P4/runtime
history and protected dirty set remain read-only.
Before return, the repair worker must run one consolidated adversarial pass,
the complete required evidence order, independently recompute the protected
set, and stop at `READY_FOR_REREVIEW_ROUND_1`. It must not declare REVIEW PASS
or FREEZE.
## 5. Claim and live-evidence boundary
No live provider call is required to repair or review deterministic repository
guidance/guard mechanics. This review makes no claim that a real agent consumed
or followed the rule. Such a claim remains a separately authorized checkpoint.
## Disposition
`REVIEW_CHANGES_REQUIRED` — findings `F1-F8`, waivers `NONE`. No FREEZE.
---
## Independent rereview round 1
- Reviewed return: path 27 `READY_FOR_REREVIEW_ROUND_1`
- Role: `INDEPENDENT_REVIEWER`, distinct from the repair worker
- Disposition: `REVIEW_CHANGES_REQUIRED_ROUND_1`
- Round-0 lineage: retained unchanged above
- Closed from round 0: partial source repairs only; no finding family is yet
  accepted as fully closed
- Open residual findings / waivers: `F1-R1` through `F7-R1` / `NONE`
- FREEZE: `NOT_AUTHORIZED`
### R1.1 Independent state and passing checks
The reviewer recomputed, rather than copied, the repair state:
- HEAD / `origin/main`: execution base `319c6a809ef29134a0de8c4a9923bb18669c349c`;
- status paths `78`, staged `0`;
- protected set `48`, SHA-256
  `0ca6eeefcb88969c38063040839591e06e993c26f7c5394227b6a97dff12fb06`;
- matrix canonical SHA-256
  `d47f9021912c38bee00ee285fac47062fa84048f67525b0d654c81bb1f45d236`;
- exact-27 ceiling retained; path 28 remained reviewer-owned; no path 29;
- focused suite `45 passed, 1 skipped`;
- invariant text/JSON guard and repository validator: PASS;
- full suite `2777 passed, 129 skipped, 3 pre-existing warnings`;
- doctor `PASS WITH NOTE` (24 plus the bounded legacy warning).
These green results do not close the findings because the family-level probes
below exercise contract combinations not covered by the repair tests.
### F1-R1 — HIGH — Structural closure still accepts invalid family declarations
F1 is not closed. Independent in-memory probes against the production schema
and semantic checker returned zero diagnostics for each of:
1. a conditional field with no condition/ownership rule;
2. a `NESTED_OBJECT` whose `nestedShapeId` does not exist; and
3. an exact duplicate `contractSources` entry.
The repair test explicitly asserts that an orphan conditional is legal, which
contradicts SPEC R7: every conditional field must be owned by exactly one
condition. Other list/file-set uniqueness and nested-reference edges remain
unenforced. Repair must turn the complete R3-R7 obligations into closed schema
or Python checks, not mark a required semantic edge as permissible.
### F2-R1 — HIGH — Ownership enforcement covers only one strategy
F2 is only partially closed for the committed `CANONICAL_DIGEST` example.
Changing the consumer to `DIRECT_IDENTITY`, removing `digestSymbol`, and
supplying no identity/reference proof passes both schema and
`_check_ownership_bindings` with zero diagnostics. `ADAPTER_ASSERTION` is
likewise accepted without an adapter proof. R11 requires every declared
strategy to be enforceable and runtime-tested, not merely recognized as an
allowed label.
Repair must define required per-strategy fields and verification for
`DIRECT_IDENTITY`, `JSON_REFERENCE`, `CANONICAL_DIGEST`, and
`ADAPTER_ASSERTION`, or narrow the allowed strategy enum consistently through
the accepted contract. Unsupported/unproven strategies must fail closed.
### F3-R1 — HIGH — Conformance summary returns false PASS
F3 is not closed. Three independent probes against the production
`build_conformance_summary` returned:
- two validators that accept every invalid mutation: `PASS`;
- two validators that reject every valid positive: `PASS`;
- every mutation operator excluded, producing a zero-case corpus: `PASS`.
The helper checks only whether validators agree with one another; it never
checks their result against the expected positive/negative disposition.
Positive shapes are not submitted to supplied surfaces at all. The summary
also omits each validator's accept/reject result and the ownership-binding
result required by R12, and it does not fail on an empty/incomplete operator
basis. With multiple shapes under one outcome, the same emitted value may be
credited to every shape because `match_count == 1` is not bound to the current
shape.
Repair must make the matrix's expected disposition load-bearing for each named
surface and case, bind positives to the intended shape, require the complete
operator corpus/exclusions, include per-validator and ownership results, and
return FAIL for each probe above.
### F4-R1 — HIGH — Conditional and nested mutation semantics remain incomplete
F4 remains open independently of F1/F3. The schema represents a conditional
field only as a string name; it has no condition, controlling field/value, or
present/absent/null rule to evaluate. The helper therefore cannot generate or
judge the required conditional fact flips. The committed bootstrap matrix
still records no explicit `CONDITIONAL_FLIP` exclusion for either flat shape.
Nested mutation tests use an artificial terminal outcome as a nested-shape
container, while semantic validation does not verify `nestedShapeId` targets.
Repair must provide a closed conditional-rule representation and valid nested
shape/reference semantics, then prove each generated mutation changes one
semantic fact and is rejected for that fact.
### F5-R1 — HIGH — Sanitization still leaks duplicate-key values
F6 is only fixed for `jsonschema.ValidationError`. Duplicate-key handling still
uses `str(DuplicateKey)` in diagnostics. A disposable matrix containing the
duplicate key `SECRET_CANARY_DUP_KEY_77` returned exit 1 but printed that exact
canary in JSON output. R16 prohibits raw arbitrary content; sanitized failure
must not echo a hostile key/value merely because the parser detected it.
Repair every diagnostic constructor, not only schema errors, and run the same
canary corpus through registry and nested matrix duplicate keys in text and
JSON modes.
### F6-R1 — MEDIUM — Accepted DESIGN and implemented dependency boundary disagree
F7 is not closed by changing only the standard. Accepted DESIGN section 8
requires a dependency-free validator; the implementation imports third-party
`jsonschema`, while the standard now documents that dependency. The worker
correctly left the DESIGN read-only, but cannot classify the resulting
normative mismatch as an accepted deviation without reviewer/operator
authority.
Either satisfy the accepted dependency-free design within exact-27 without
weakening Draft 2020-12 behavior, or obtain a reviewed DESIGN/SPEC/Work Order
amendment authorizing `jsonschema` as the validation dependency. The latter is
outside the current repair authority.
### F7-R1 — LOW — Corrected path arithmetic is still arithmetically false
F8 remains open. The repair note says `61 + 11 + 1 = 73`, which is false and
still omits four previously clean tracked exact paths that entered status.
The reproducible transition is:
- baseline status: `61`;
- newly present formerly-ABSENT paths: `12` (including path 27);
- previously clean tracked exact paths that became modified: `4`;
- pre-review total: `77`;
- reviewer-owned path 28: `+1`, current total `78`.
Repair path 27 with this exact classification while retaining both superseded
statements as lineage.
### R1.2 Repair and authority boundary
`F1-R1` through `F5-R1` and `F7-R1` remain inside the existing exact-27,
R2, zero-external-effect repair boundary. The repair worker must add paired
family-level probes for the exact failures above and rerun the complete
evidence sequence. Path 28 remains read-only; no path 29.
`F6-R1` cannot be waived by the worker. If the implementation retains
`jsonschema`, an operator-authorized reviewed amendment is required because
the accepted DESIGN dependency boundary changes. No provider/live call is
needed for either route.
## Round-1 disposition
`REVIEW_CHANGES_REQUIRED_ROUND_1` — residual findings `F1-R1` through
`F7-R1`, waivers `NONE`. Stop before FREEZE.
---
## Independent rereview round 2 and out-of-band scope audit
- Reviewed return: path 27 `READY_FOR_REREVIEW_ROUND_2`
- Role: `INDEPENDENT_REVIEWER`, distinct from repair worker
- Disposition: `SCOPE_AMENDMENT_REQUIRED_AND_REVIEW_CHANGES_REQUIRED_ROUND_2`
- Open findings / waivers: `SCOPE-F1`, `F1-R2` through `F5-R2` / `NONE`
- FREEZE: `NOT_AUTHORIZED`
### R2.1 Independent state and passing evidence
Reviewer recomputation produced HEAD/origin at execution base, status `81`,
staged `0`, exact-4 Amendment artifacts byte-exact, and path 28 unchanged
before this append. Doctor passed 24 checks with the same bounded warning.
Using the mandated stable runtime (`jsonschema 4.26.0`): focused suites passed
`54 passed, 1 skipped`; invariant text/JSON, knowledge, session, catalog,
file-size and repository gates passed; the exact full command
`python -m pytest -q` passed `2786 passed, 129 skipped, 3 pre-existing
warnings`. This supersedes the worker's reduced full-suite command and supplies
the doctor it correctly omitted under its no-network boundary.
### SCOPE-F1 — HIGH — Two approvals created three non-Work-Order paths
The operator confirms that Claude requested and received permission for two
out-of-Work-Order actions: one source split and one test split. Those actions
created three paths:
1. `scripts/invariant_family_ownership.py` — SHA-256
   `9b0e0c1d667f41267ffdf654909aa9416bf8d05a5d18efb7253e6ad8f096ffaf`;
2. `tests/unit/test_invariant_family_contract_repair_round2.py` — SHA-256
   `5415b52d9b864fb0435f02ee957d203551302035eeeb69971d263d5d4a3741a0`;
3. `tests/integration/test_invariant_family_repository_guard_repair_round2.py`
   — SHA-256
   `fad94162154e85bff222fd6ef3cddf24b906a7563080378ed90366be44db97ce`.
Independent source/test review finds the split materially useful, within the
same objective/R2/external-effect class, and free of P4/runtime expansion.
Content disposition is `RATIFIABLE`. It is not yet `RATIFIED`: SPEC section 3
and Work Order sections 2/19 still mandate exact-27 and no path 29. Direct
operator permission proves intent but cannot waive the mandatory phase and
independent authorization-review chain. A bounded DESIGN/SPEC/Work Order
Amendment 2 must convert exact-27 to exact-30 and independently review these
three exact hashes before further worker edits or FREEZE.
### R2.2 Correct scope arithmetic
The worker's `79/47` entry explanation and `81/49 ee17...` exit receipt do not
reproduce. Immediately before round 2, independent review recorded status
`78`, protected `46 / 1ddda7de...`. The P4-B paths cited by the worker already
existed in that baseline and do not explain an extra row.
Current exact arithmetic is:
- pre-round-2 governed state: status `78`, protected `46`, digest
  `1ddda7de1e54064ee7839b670291d27d39ddca3577137ea5ee3e9c7d0fcfc140`;
- three new unratified paths: status `+3` = `81`;
- treating them as unratified protected drift: count `49`, digest
  `3a908dc4655eb15adcb860b987cd2961f375737f22af32e2e636e8f00cb07531`;
- excluding the exact-three candidate Amendment 2 paths restores protected
  `46 / 1ddda7de...` byte-exact.
Path 27 must retain the worker's incorrect receipts as superseded lineage and
record this independently reproducible classification.
### F1-R2 — HIGH — Mutation completeness is hard-coded to a partial basis
`_REQUIRED_MUTATION_OPERATORS` contains only five base operators. Independent
monkeypatch removed every `COUNTER_MUTATION` and
`ONE_SIDE_RELATION_CHANGE`; both shapes still reported
`mutationCorpusComplete=true` and the overall summary returned `PASS`.
Conditional and nested requirements are likewise not derived from each
shape's actual relations/domains/rules.
Repair must derive the required operator/id basis from the matrix shape and
its independently reviewed exclusions. Every counter, equality/digest,
conditional and nested obligation must be load-bearing; missing any applicable
case returns FAIL.
### F2-R2 — HIGH — Conditional ownership and mutation semantics remain open
Schema and Python accept two conditional rules owning the same field, contrary
to R7's exactly-one-condition rule. For a valid positive where a
`REQUIRED_WHEN_MATCH` condition is inactive and the field is absent,
`generate_mutations` inserts the field and labels it `CONDITIONAL_FLIP`, but
the resulting payload remains valid. Thus the helper emits a supposed negative
that changes no invalid semantic fact.
Repair must reject duplicate conditional ownership and generate conditional
mutations relative to active/inactive rule semantics, proving every emitted
negative is actually rejected for exactly one fact.
### F3-R2 — HIGH — Ownership proof and summary ownership result are tautological
`ADAPTER_ASSERTION` verifies only that a named function exists. Pointing it to
the unrelated `test_zero_outcomes_matrix_fails_schema_and_semantics` function
returned no ownership diagnostic; it never proves the consumer obtains the
owner value unchanged.
`build_conformance_summary` accepts caller argument `ownership_ok=True` by
default. A matrix with a missing owner path therefore returned summary
`ownershipResult=PASS` and overall `PASS`. Production summary must compute or
consume an independently structured ownership result bound to the matrix, not
accept an unproven boolean. Cleanup tests also still serialize a test-local
literal summary rather than the production summary on PASS/failure.
### F4-R2 — HIGH — Declared symlink rejection remains unproven and fail-open
`safe_repo_path` calls `.resolve()` before `is_safe_regular_file`, so a
declared symlink pointing to another file inside the repository becomes the
target path and no longer appears as a symlink. The only test is skipped on
this environment. R5 requires declared symlink paths to fail closed, not only
external-target traversal. Preserve the lexical candidate, inspect every path
component without following it, and provide a deterministic platform-capable
probe or an equivalent mocked filesystem boundary test.
### F5-R2 — MEDIUM — Worker evidence did not follow the amended execution order
The worker used an environment with `jsonschema 4.23.0` instead of the
mandated stable runtime preflight at `4.26.0`, replaced the required full suite
with a command that excluded one test, and published non-reproducible
protected-set receipts. The doctor omission alone is accepted because its Core
freshness check can touch network and the independent reviewer supplied it.
Path 27 must report the reviewer's exact stable-runtime/full-suite results and
must not relabel the reduced command as the full Work Order gate.
### R2.3 Next governed move
Do not delete or further edit the three candidate paths: their content is
useful evidence and the operator intended both splits. First obtain bounded
Amendment 2 authority for exact-30 and independent authorization review.
Then one consolidated repair round 3 may address `F1-R2` through `F5-R2`.
These include independent new root causes, so the round-three cost-escalation
condition is not triggered. No provider/live call is required.
## Round-2 disposition
`SCOPE_AMENDMENT_REQUIRED_AND_REVIEW_CHANGES_REQUIRED_ROUND_2` — candidate
paths `RATIFIABLE_NOT_RATIFIED`; findings `SCOPE-F1`, `F1-R2` through
`F5-R2`; waivers `NONE`; no FREEZE.
---
## Independent rereview round 3 — 2026-08-23
- Reviewed return: `READY_FOR_REREVIEW_ROUND_3`
- Role: `INDEPENDENT_REVIEWER`, distinct from repair worker
- Disposition: `REVIEW_COST_ESCALATION_REQUIRED`
- Open findings / waivers: `F1-R3` through `F4-R3` / `NONE`
- Closed this round: `SCOPE-F1`, `F5-R2`
- FREEZE: `NOT_AUTHORIZED`
### R3.1 Independent state and passing evidence
HEAD/origin remained `319c6a809ef29134a0de8c4a9923bb18669c349c`,
status/staged `81/0`, and protected set remained byte-exact at count `44`,
SHA-256
`8a7a92f7d99a87f876e4b0b8c2c1693ccf7cda6661ff60cc3b0bc30daf728446`.
All six Amendment 2 artifacts matched their pins before review; completion
review matched its pre-append pin `aec45fca...`. Exact-three scope is ratified,
so `SCOPE-F1` is closed. No path 31 exists.
Stable-runtime focused suites passed `64 passed, 2 skipped`. Invariant text/
JSON, Project Knowledge, session, catalog, file-size and repository gates all
passed. The reviewer ran the required exact full command
`python -m pytest -q`: `2796 passed, 130 skipped, 3 warnings`. This supersedes
the worker's reduced `2772` command and closes the executable-evidence portion
of `F5-R2`. Doctor remained unrun because current authority forbids its network
fetch; that omission was already accepted and is not a finding.
Green regression gates do not close the following independently reproduced
acceptance failures.
### F1-R3 — HIGH — Mutation completeness remains self-referential
`required_operators_for_shape` derives its required set by calling the same
`generate_mutations` implementation whose completeness it is meant to audit.
The reviewer removed each operator from both production call sites, matching
an implementation branch being lost. Removing all `COUNTER_MUTATION` cases
still returned summary `PASS`, corpus flags `[true,true]`; removing all
`ONE_SIDE_RELATION_CHANGE` did the same. The worker probe patched only one
alias, leaving the other alias as an accidental oracle, and therefore did not
model source coverage loss. Required obligations need an independent closed
shape/operator contract, not the output under test.
### F2-R3 — HIGH — Inactive conditional mutation is still a valid positive
For `REQUIRED_WHEN_MATCH(mode == STRICT)`, positive `{mode: LOOSE}` is valid.
Production `generate_mutations` emits
`CONDITIONAL_FLIP::note_present` with `{mode: LOOSE, note: ...}`; production
`matches_shape_exactly` accepts it. Thus a labelled negative still changes no
invalid semantic fact. Duplicate/unreachable declaration checks are useful,
but they do not close the original inactive-rule mutation finding.
### F3-R3 — HIGH — ADAPTER_ASSERTION remains lexical, not binding proof
Production `_verify_adapter_assertion` accepts a function containing only an
unrelated `assert True` plus the owner-path string assigned to an unused local;
the reviewer probe returned no diagnostic. The worker's own positive has the
same structure: an unrelated family-id assertion and owner path in a comment.
Requiring the two tokens to coexist does not prove the consumer obtains or
compares the owner value unchanged. A structured, evaluated static contract
or another load-bearing binding mechanism is still required.
### F4-R3 — MEDIUM — Symlink negative evidence remains skipped
Source order now checks unresolved components before `resolve()`, which is the
correct repair direction. However both negative symlink tests skipped on this
environment (`64 passed, 2 skipped`) and no mocked filesystem-boundary or
other deterministic platform-capable negative was added. The exact acceptance
request in `F4-R2` therefore remains unproven; the ordinary-path positive alone
cannot establish fail-closed symlink behavior.
### R3.2 Cost escalation and stop
These are residual forms of `F1-R2` through `F4-R2`, not independent new root
causes. This is repair round 3. Per `AGENTS.md`, further repair must stop and
record `REVIEW_COST_ESCALATION_REQUIRED` before continuing. No waiver is
created, no FREEZE/closure/continuity sync is authorized, and the reviewer made
no source/test/schema/guard edit. A fresh operator decision must authorize a
consolidated next repair boundary; repeating narrow token-level fixes is not
acceptable.
---
## Independent rereview round 4 — 2026-08-23
- Reviewed return: `READY_FOR_REREVIEW_ROUND_4`
- Role: `INDEPENDENT_REVIEWER`
- Disposition: `REVIEW_CHANGES_REQUIRED_ROUND_4`
- Open findings / waivers: `F1-R4`, `F3-R4` / `NONE`
- Closed: `F2-R3`, `F4-R3`
- FREEZE: `NOT_AUTHORIZED`
Before appending this review, the reviewer mechanically removed blank lines
only to keep this artifact below its 600-line hard limit. Pre-compaction hash
was `cd2a67df476b540fdce9ff8bdb1dd146e0bfafdfa629e92d2c20a9883a65b647`;
compacted pre-append hash was
`f7c76a51ba2da8b7c308c53055c133dc518eef2d78f2eaab9daa410b2448ec3d`.
All prior text, headings, dispositions, findings and hashes were retained in
order.
### R4.1 Passing evidence
HEAD/origin, status/staged, exact-30 and protected `44 / 8a7a92f7...`
remained unchanged. Six Amendment artifacts were byte-exact and no path 31
exists. Focused suites passed `77 passed, 2 skipped`; invariant, knowledge,
session, catalog, file-size and repository gates passed. The new deterministic
mocked symlink test ran rather than skipped and proves leaf/intermediate
rejection before resolution; `F4-R3` is closed. Active/inactive REQUIRED and
FORBIDDEN conditional probes all use production matcher/generator behavior
and no valid conditional negative remains; `F2-R3` is closed.
### F1-R4 — HIGH — Completeness detects missing operator classes, not cases
The independent derivation correctly detects loss of an entire operator, but
the summary compares only a set of operator names. Reviewer production probes
removed one `COUNTER_MUTATION::minus_one` case and, separately, one
`DELETE_REQUIRED_FIELD::payload` case while leaving another case of each
operator. Both summaries remained `PASS` with corpus flags `[true,true]`.
The accepted contract requires every applicable counter/field/relation/
conditional/nested obligation to be load-bearing. Completeness must compare a
closed obligation-id/count basis, not operator presence alone.
### F3-R4 — HIGH — AST proof accepts wrong consumer and inequality
The AST checker now rejects lexical-only assertions, but accepts `owner_value`
compared to an unrelated free global (`OTHER`) because any free name is treated
as a consumer binding. It also accepts `assert owner_value != consumer_value`.
Both reviewer probes returned no diagnostic. A valid proof must bind the
consumer expression to the declared consumer contract and require equality of
owner-derived and consumer-derived values; unrelated globals, inequality and
unproven dataflow must fail.
### R4.2 Next repair boundary
These two residuals remain within the operator-approved post-escalation
exact-30 objective, R2 ceiling and zero-external-effect class. Per governance
latency rules, no new operator wait is required. One consolidated repair may
address only `F1-R4` and `F3-R4`, keep governance/review artifacts read-only,
create no path 31, and return `READY_FOR_REREVIEW_ROUND_5`. No FREEZE or
continuity closure is authorized.
---
## Independent rereview round 5 — 2026-08-23
- Reviewed return: `READY_FOR_REREVIEW_ROUND_5`
- Role: `INDEPENDENT_REVIEWER`
- Disposition: `REVIEW_CHANGES_REQUIRED_ROUND_5`
- Open findings / waivers: `F3-R5` / `NONE`
- Closed: `F1-R4`
- FREEZE: `NOT_AUTHORIZED`
### R5.1 Passing evidence and F1 closure
HEAD/origin remained at the execution base; status/staged remained `81/0`;
protected `44 / 8a7a92f7...`, governance pins and exact-30 boundary were
unchanged. Focused suites passed `80 passed, 2 skipped`; invariant, knowledge,
session, catalog, file-size and repository gates passed.
Independent production probes removed exactly one counter-minus-one mutation,
removed exactly one required-field mutation, and injected a duplicate mutation
id. All three summaries returned FAIL with the affected corpus flag false.
`required_mutation_ids` is independent of the generator and exact-id equality
is load-bearing. `F1-R4` is closed.
### F3-R5 — HIGH — Path-bearing unrelated calls still satisfy AST proof
`_reads_path` currently means only “the expression contains the exact path
literal and contains some Call/Subscript node.” The reviewer supplied:
`owner_value = unrelated(<exact owner path>)`,
`consumer_value = unrelated(<exact consumer path>)`, followed by equality.
Production `_verify_adapter_assertion` returned no diagnostic. Thus arbitrary
functions can still turn path strings into an accepted proof without reading
either declared artifact. This is the same residual dataflow issue, not a new
scope. The checker must recognize a closed, explicitly allowed read pipeline
(function/argument/subscript shape), reject unknown call targets and prove the
declared paths are the actual sources of the compared values.
### R5.2 Next repair boundary
The post-escalation exact-30 authority remains applicable without operator
wait: objective, R2, paths, effects and ownership are unchanged. One repair
may address only `F3-R5`, add paired allowlisted-reader and unknown-call
probes within existing paths, keep all governance/review artifacts read-only,
and stop at `READY_FOR_REREVIEW_ROUND_6`. No path 31, FREEZE or continuity
closure is authorized.
---
## Independent rereview round 6 — 2026-08-23
- Reviewed return: `READY_FOR_REREVIEW_ROUND_6`
- Role: `INDEPENDENT_REVIEWER`
- Disposition: `REVIEW_CHANGES_REQUIRED_ROUND_6`
- Open findings / waivers: `F3-R6` / `NONE`
- FREEZE: `NOT_AUTHORIZED`
### R6.1 Passing evidence
HEAD/status/staged/protected set, exact-30 and all governance pins remained
unchanged. Focused suites passed `76 passed, 2 skipped`; invariant, knowledge,
session, catalog, file-size and repository gates passed. The closed call-shape
pipeline now rejects unrelated readers, unknown wrappers, tuple intermediaries,
wrong paths and inequality.
### F3-R6 — HIGH — Allowlisted names lack import provenance
`_callee_name` discards the module qualifier, and unqualified names are not
resolved against imports. Two reviewer probes therefore returned no diagnostic:
1. `evil.load_json_no_dup(evil.safe_repo_path(<declared path>))` on both sides;
2. locally defined shadow functions named `load_json_no_dup` and
   `safe_repo_path` on both sides.
Neither expression reads through the trusted contract module, but both satisfy
the current name-only allowlist. The proof grammar must bind exact qualified
symbols to an independently verified import from
`invariant_family_contract`, reject local shadowing and reject every unknown
module alias. This is the same `F3` provenance boundary, not a new objective.
### R6.2 Next repair boundary
Existing post-escalation exact-30 authority continues. One repair may address
only `F3-R6`: implement exact import-provenance resolution plus paired evil-
module/local-shadow negatives and a trusted-import positive. Governance/review
artifacts stay read-only; no path 31 or external effect. Stop at
`READY_FOR_REREVIEW_ROUND_7`; no FREEZE or continuity closure.
---
## Independent rereview round 7 — 2026-08-23
- Disposition: `REVIEW_CHANGES_REQUIRED_ROUND_7`
- Open findings / waivers: `F3-R7` / `NONE`
- FREEZE: `NOT_AUTHORIZED`
Whitespace-only compaction retained all prior ordered content: preimage
`c73a3c0ae9fb1041b429466b8e7033386cb835f808ccf712b13a3491f30b110d`
at 565 lines became
`7ba4b62c451b3f2ad1c3648c9a4f676fbce6309eacc6ca2fc35da4f97e210bef`
at 549 lines before this append.
### F3-R7 — HIGH — Alias collision and parameter shadow remain accepted
Focused suites passed `76 passed, 2 skipped` and repository gates passed, but
two independent AST probes returned no diagnostic: a trusted import followed
by `import evil as ifc`, and a proof function parameter named `ifc`. The alias
table ignores non-trusted import collisions and function-scope bindings, so
trusted terminal names can still resolve through an untrusted object.
The next repair must stop general alias inference and use one closed grammar:
exactly one module-level `import invariant_family_contract as ifc`, calls only
through `ifc`, and no other binding of `ifc` anywhere in the module or proof
scope. Reject all import collisions, Store-context names, parameters,
function/class names, annotated/augmented/walrus assignments, exception/with/
comprehension targets and alternate imports. This is the same F3 boundary.
Existing exact-30 post-escalation authority continues for `F3-R7` only. Keep
governance/review artifacts read-only, create no path 31 or external effect,
and stop at `READY_FOR_REREVIEW_ROUND_8`. No FREEZE/continuity closure.
---
## Independent rereview round 8 — 2026-08-23
- Disposition: `REVIEW_CHANGES_REQUIRED_ROUND_8`
- Open findings / waivers: `F3-R8` / `NONE`
- FREEZE: `NOT_AUTHORIZED`
### F3-R8 — HIGH — Structural-pattern bindings remain accepted
Independent AST probes show `_ifc_binding_is_closed` returns `True` for both
`case [*ifc]` (`ast.MatchStar.name`) and `case {**ifc}`
(`ast.MatchMapping.rest`). Each form creates a local `ifc` binding without a
Store-context `ast.Name`, so the trusted module alias can still be shadowed.
This is the same closed-binding provenance root cause, not a new objective.
Existing exact-30 post-escalation authority continues for `F3-R8` only: reject
both binding forms and add paired negatives. Governance/review artifacts become
read-only during repair; no path 31 or external effect. Stop at
`READY_FOR_INDEPENDENT_REREVIEW_ROUND_9`; no self-approval or FREEZE.
## Independent rereview round 9 — 2026-08-23
- Role declaration: `INDEPENDENT_REVIEWER`; disposition `REVIEW_CHANGES_REQUIRED_ROUND_9`; findings/waivers `F3-R9`/`NONE`; FREEZE/closure eligibility `NO`. HEAD/origin `319c6a809ef29134a0de8c4a9923bb18669c349c`, status/staged `81/0`, exact-30/no path 31 and protected `44/8a7a92f7d99a87f876e4b0b8c2c1693ccf7cda6661ff60cc3b0bc30daf728446` reproduced; six Amendment hashes match §20.1; focused `77 passed, 2 skipped`, full `2809 passed, 130 skipped, 3 warnings`; invariant text/JSON, knowledge, session, catalog, file-size, repository and doctor gates PASS (doctor: 24 plus the retained bounded legacy warning).
- `F3-R9` HIGH, same provenance root: production probes returned `None` (false PASS) for (1) the trusted direct import followed by `from evil import *`, which can overwrite `ifc`, and (2) a valid-looking `probe` nested inside another function or class, because `_find_function` uses unrestricted `ast.walk` rather than requiring a direct module child. Repair must reject wildcard imports when establishing the closed `ifc` binding, require `assertionFunction` to be one unique direct module-level function, and add paired star-import/nested-function/class-method negatives while retaining the valid production adapter positive; remain inside exact-30 with this completion review read-only and return for independent rereview.
## Independent rereview round 10 — 2026-08-23
- Before append, blank-line-only compaction preserved every ordered lineage/finding/disposition/hash: `c40c660335ff481d4e7f7d0a5df7b2d67f222274fb91116e294940dc6b6331e8` (599 lines) -> `50e1df4be836a4b9468fa587a9c363b9100f2ace18d45d3ad5d191b52cc1a375` (592 lines).
- Role `INDEPENDENT_REVIEWER`; disposition `REVIEW_PASS_ROUND_10`; findings/waivers `NONE/NONE`; closure eligibility `YES`. Independent production probes reject wildcard, nested/conditional import, collision, every named binding form, MatchAs/Star/Mapping, nested/class/duplicate assertion functions, evil/bare/unknown/lexical provenance, while the valid module-level production adapter passes.
- Evidence: focused `77 passed, 2 skipped`; full `2809 passed, 130 skipped, 3 warnings`; invariant text/JSON, knowledge, session, catalog, file-size and repository gates PASS; HEAD/origin `319c6a809ef29134a0de8c4a9923bb18669c349c`, status/staged `81/0`, exact-30/no path 31, protected `44/8a7a92f7d99a87f876e4b0b8c2c1693ccf7cda6661ff60cc3b0bc30daf728446`, six Amendment hashes unchanged and `git diff --check` clean. `F3-R9` is closed without waiver; CLOSER may now synchronize continuity and FREEZE within the accepted claim boundary.
## Final independent closure rereview — 2026-08-23
- Disposition `FINAL_REVIEW_PASS / CLOSURE_SYNC_PASS`; findings/waivers `NONE/NONE`; FREEZE eligibility `YES`. Amendment 3 isolation is byte-reproducible: Project Context changes only its authorized stale BUILD block (`2248d996...` preimage), while manifest changes only the two authorized source pins (`c6e0ca6a...` preimage); final hashes are `d8fa59f851df9f7247711c0c83d823fae2b7708b69b135fd9bc1785cff5edb02` and `c0712e1ab456ba29e805cd71a250a08608c59a43d4a0536ce9c871d9d16a5631`.
- Knowledge, session, invariant text/JSON, catalog, file-size, repository and doctor gates PASS (24 plus retained bounded legacy warning); continuity agrees on `FREEZE/CLOSED_BOUNDED`, round-10 `NONE/NONE`, and P4-C fresh-INTAKE-only. Roadmap `600`, required reads `12/12` identical, bootstrap `1318` bytes; HEAD/origin `319c6a8`, status/staged `81/0`, diff clean, no unauthorized new file or provider/credential/install/database/deployment effect and no agent-compliance overclaim. Commit/push may proceed under the operator's separate authority.
