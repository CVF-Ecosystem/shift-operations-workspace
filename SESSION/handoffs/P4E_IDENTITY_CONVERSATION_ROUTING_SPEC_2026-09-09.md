# Handoff - P4-E Identity Mapping and Conversation Routing

- Tranche: `P4E-IDENTITY-CONVERSATION-ROUTING-2026-09-09`
- Status: `FREEZE / CLOSED_BOUNDED`
- Risk: `R2`
- Active role: `ORCHESTRATOR` (project parked after closure sequence)
- Branch: `docs/p4e-spec`
- Updated: `2026-09-10`

## 2026-09-10 Amendment 2 Finalization

Amendment 1 repair is independently accepted without waiver. Successor finding
`P4E-AM1-REV-F1` is closed at the SQL and InMemory write stores; focused tests
passed `219/2`, disposable PostgreSQL passed `12`, and catalog paths 93-94 are
canonical. Material commit
`131a38b0c817903df2148107078c25dbe50d5f38` records the exact accepted
79-path product/review/catalog set. No provider call, install, shared database,
deployment, or push was performed.

Catalog generation changed a Project Knowledge source pin while the prior
choreography deferred paths 83-92 until after material commit, creating a
machine-reproduced closeability cycle. Exact-manifest/Work Order Amendment 2
received independent `AUTHORIZATION_REVIEW_PASS`, findings/waivers `NONE/NONE`,
and was activated at `c82d9e0`; correction commit `9809852` binds the terminal
path-82 evidence commit explicitly. It authorizes the pre-material
continuity candidate, a complete candidate gate, conditional independent
material-commit authorization, then post-material actual-SHA finalization,
another complete gate/review, and a separate continuity commit.

Final disposition: `FREEZE / CLOSED_BOUNDED` after the post-material complete
gate, terminal independent review, exact path-82 evidence commit, and separate
paths83-92 continuity commit. Next allowed move is no project mutation; the
operator returns to CVF Core to open the ADIF-0057 machine-enforcement tranche.
Phase 5, external absorption, catalog schema migration, and XR1 debt remain
parked.

## 2026-09-10 Amendment 1 Activation (superseded current-move text)

Startup acknowledged: current mode=
`p4e_identity_conversation_routing_amendment1_repair_ready`; active handoff=
this file; next allowed move=dispatch exactly one Claude `REPAIR_WORKER` for
the Amendment 1 successor cluster; parked checkpoint=independent successor
completion review, closer catalog regeneration, final gates/commit, Phase 5,
external absorption, governed-catalog schema migration, and XR1 debt.

The first worker returned uncommitted implementation evidence and the
independent completion-review chain reached round 3. Current open findings are
`P4E-COMP-REREV2-F1` through `F4`: split signature/timestamp authentication,
fifteen necessary paths outside the original ceiling, incomplete write-time
CAS, and inaccurate worker-return evidence. The implementation is preserved
but remains unaccepted.

The operator required CVF learning absorption before project repair. Private
Core material commit `3fcd426dc7c2c6d03fc915b884711df118a0563f`
records the outcome-bounded agent-intelligence and first-return reviewer duty;
continuity commit `fe62894f861c34a25a16c6267f557bf771ea9e2c` is now the
operator-local provenance/rule-pack pin.

The successor repair packet is:

- exact-manifest Amendment 1 SHA-256
  `921805758327226c77a0d238925b9dd2445b3d023bafd8386176042917a620d2`;
- Work Order Amendment 1 SHA-256
  `582a48f3296a4e32acf6ab1d98c082356826717d1884093a9528c010d26741ca`;
- independent authorization review SHA-256
  `bc510c1262d1f76bb8d7408a15763dcb18d3ccfd7c6573342db24601bf07d9e2`,
  disposition `AUTHORIZATION_REVIEW_PASS`, findings/waivers `NONE/NONE`.

Exactly one external Claude repair dispatch is authorized. The worker owns
only original paths 15-80 plus amendment paths 95-109, must preserve useful
earlier work, must make the PostgreSQL runner local-image-only/fail-closed, and
must update existing path 80. It must not call Alibaba/a product provider,
pull an image, install, use a shared database, edit paths 82-94, regenerate the
catalog, stage, commit, push, deploy, or declare closure.

## Startup truth

This first-party project inherits public CVF Core
`483c5e33d188b6b2d35d6cd19ee38a3c8548abc4` and the mandatory operator-local
rule pack materialized from private provenance
`fe62894f861c34a25a16c6267f557bf771ea9e2c`. Both sources remain read-only.
The prior provenance-inheritance recovery is closed bounded.

## Current authority

The 2026-09-09 predecessor record below is retained for provenance. Where it
describes the active worker ceiling, role, pin, or next move, the 2026-09-10
Amendment 1 Activation above supersedes it.

The operator explicitly advanced accepted P4-E DESIGN to SPEC on 2026-09-09.
`docs/specs/P4E_IDENTITY_CONVERSATION_ROUTING_SPEC.md` is now
`1.0-draft-r1 / SPEC_REVIEW_PASS`. It consumes accepted DESIGN
digest `2d0975a301a15c7b8a85eba121410391ddca2f067b16d9c5089d79edb9c397b9`
and defines the bounded identity-linkage, authorization, durable inbox,
conversation-placement, privacy, retention, idempotency, and refusal contract.
Its repaired byte SHA-256 is
`de3af4a90425ee70f8e285fc31e12774497f7a190b776beab3ed3d32fdc90618`.

Three repository-governed invariant families are registered and pinned:

- `P4E-MAPPING-ACTION-OUTCOMES`:
  `ea2af8122016a7b8ee10d9a8aa097f1b692a168a4914425172c555cd4d003e1a`
- `P4E-IDENTITY-RESOLUTION-OUTCOMES`:
  `4ef64cf1f53633974b0e585018148a8f6bbe7a16ce4683329aa29d51c0000bdc`
- `P4E-CONVERSATION-PLACEMENT-OUTCOMES`:
  `fd351b6670292e82835b4ec34c270768174758a6d8a3f1558e4e4b3a8ec8cc56`

Generation 1 independent review is retained unchanged at SHA-256
`a4ee2f643186ca11be7d08c8e555aa55372c63b20d58bb3ab81b24e5b83d17f8`.
Its seven findings were repaired without waiver. The author response, including
qualified disagreement with three diagnostic phrasings, is
`docs/decisions/P4E_IDENTITY_CONVERSATION_ROUTING_SPEC_REWORK_2026-09-09.md`.
The independent rereview at
`docs/decisions/SPEC_REREVIEW_2026-09-09_P4E_IDENTITY_CONVERSATION_ROUTING.md`
has SHA-256
`e9c21bd7c5627a0529b4d15d5a1533bd834ec886d13002c77ecdaa2a8094c3cc`
and closes F1-F7 with zero new finding and zero waiver.

Material commit `82e00a2` records that rereview and the separate Work Order
authoring transition. Independent authorization review at SHA-256
`96e0328720a78f45883cbb2298d695c79eda57ecd49d680a8cc7c126251a498d`
returned three citation-integrity findings with no waiver. Material repair
commit `64cf02c` corrects only the Work Order. On 2026-09-09 the operator
explicitly accepted those mechanical repairs, waived rereview, and directed
handoff to the worker. Commit `e7d480d` records that authorization in the Work
Order. The execution packet now consists of:

- `docs/baselines/CVF_GC018_BASELINE_P4E_IDENTITY_CONVERSATION_ROUTING_2026-09-09.md`;
- `docs/implementation/P4E_IDENTITY_CONVERSATION_ROUTING_EXACT_MANIFEST_2026-09-09.md`, SHA-256
  `edb56012d87e7c4e9b3c715feba6d32a65a90b70064c9fa7d0d3b2abdc03a846`;
- `docs/work_orders/CVF_AGENT_WORK_ORDER_P4E_IDENTITY_CONVERSATION_ROUTING_2026-09-09.md`, SHA-256
  `b83eef2bd29ce9a9e436e68050efaab0ed4d9174ee645a56b66a53c83bbe9891`.

The packet fixes 94 exact paths and assigns worker ownership only to paths
15-80. It makes customer/vessel scaffolds protected exclusions, requires a real
import/composition probe for AC-16, and assigns
`TOKEN_KEY_RETIREMENT_BLOCKED` solely to the Integration Edge sender-key
authority. BUILD is authorized only for implementation-worker paths 15-80
under `WORKER_MUST_NOT_COMMIT` and the zero-external-effect ceiling.

Authorization F1-F3 repairs are bounded to four corrected manifest ordinals,
`93` to `94` in the Review Gate, and private-provenance annotations on two
standards. The exact manifest and all three matrices remain byte-identical.

## Verification

- invariant-family guard: `PASS`
- declared matrix evidence command:
  `python -m pytest -q tests/unit/test_invariant_family_contract.py tests/integration/test_invariant_family_repository_guard.py`
  -> `35 passed, 2 skipped`
- extended repository invariant regression command:
  `python -m pytest -q tests/unit/test_invariant_family_contract.py tests/unit/test_invariant_family_contract_repair_round2.py tests/integration/test_invariant_family_repository_guard.py tests/integration/test_invariant_family_repository_guard_repair_round2.py`
  -> `72 passed, 2 skipped`
- whitespace/error scan: `PASS`
- current dispatch-quality, handoff-boundary, review-cost and ADIF disclosure
  checkers: `PASS` against the project root
- exact manifest: `94/94` sequential and unique; pinned SHA-256 matches
- file-size and repository validators: `PASS`; Work Order exactly 600 lines
- workspace doctor: `PASS WITH NOTE` (`24` pass, one bounded legacy-catalog
  warning)
- no product source, dependency, schema migration, provider call, live call,
  credential, deployment, or external effect was introduced

These are deterministic authoring checks plus the retained independent SPEC
rereview, authorization review, mechanical repair, and explicit operator
authorization. They are not implementation, completion-review, runtime, or
governance-behavior proof.

## Next allowed move

Dispatch exactly one Claude `REPAIR_WORKER` invocation under Work Order
Amendment 1. The worker must capture the fresh activation commit as execution
base while preserving the already uncommitted product changes, verify empty
staging and all pins, resolve F1-F4, run the exact local/P4-E/PostgreSQL/gate
commands, update path 80, and release the lane with all worker changes unstaged
and uncommitted. Paths 1-14 and 81-94 remain read-only to the worker; additive
paths 95-109 are authorized.

## Parked

- P4-E independent successor completion review, closer-owned catalog
  regeneration, final full suite, commit, closure and final session sync
- Phase 5
- external-repository absorption
- governed-catalog schema migration
- XR1 historical-object debt

## Predecessor

`SESSION/handoffs/CVF_PROVENANCE_INHERITANCE_RECOVERY_2026-09-09.md` remains
settled historical evidence and must not be rewritten.
