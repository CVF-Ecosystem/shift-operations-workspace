# Handoff - P4-E Identity Mapping and Conversation Routing

- Tranche: `P4E-IDENTITY-CONVERSATION-ROUTING-2026-09-09`
- Status: `WORK_ORDER / REPAIRED_PENDING_INDEPENDENT_AUTHORIZATION_REREVIEW`
- Risk: `R2`
- Active role: `INDEPENDENT_AUTHORIZATION_REREVIEWER`
- Branch: `docs/p4e-spec`
- Updated: `2026-09-09`

## Startup truth

This first-party project inherits public CVF Core
`483c5e33d188b6b2d35d6cd19ee38a3c8548abc4` and the mandatory operator-local
rule pack materialized from private provenance
`bee38695ebac452e0ea6b3487706ed5c84f5fc2e`. Both sources remain read-only.
The prior provenance-inheritance recovery is closed bounded.

## Current authority

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
commit `64cf02c` corrects only the Work Order. The authorization packet now
consists of:

- `docs/baselines/CVF_GC018_BASELINE_P4E_IDENTITY_CONVERSATION_ROUTING_2026-09-09.md`;
- `docs/implementation/P4E_IDENTITY_CONVERSATION_ROUTING_EXACT_MANIFEST_2026-09-09.md`, SHA-256
  `edb56012d87e7c4e9b3c715feba6d32a65a90b70064c9fa7d0d3b2abdc03a846`;
- `docs/work_orders/CVF_AGENT_WORK_ORDER_P4E_IDENTITY_CONVERSATION_ROUTING_2026-09-09.md`, SHA-256
  `21edaf285eb94812f922197c9737b2a54c01ae49cd80930fd7e4b29fd3c75530`.

The packet fixes 94 exact paths and assigns worker ownership only to paths
15-80. It makes customer/vessel scaffolds protected exclusions, requires a real
import/composition probe for AC-16, and assigns
`TOKEN_KEY_RETIREMENT_BLOCKED` solely to the Integration Edge sender-key
authority. BUILD remains unauthorized.

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
rereview and authorization changes-required review. They are not an
authorization rereview PASS and not runtime or governance-behavior proof.

## Next allowed move

Assign an `INDEPENDENT_AUTHORIZATION_REREVIEWER` to verify only authorization
findings F1-F3 against the repaired Work Order. Recompute its SHA-256, confirm
the exact manifest and matrices are unchanged, and verify the repaired ordinal,
94-path count, and private-provenance annotations. Only
`AUTHORIZATION_REVIEW_PASS` with findings/waivers `NONE/NONE` may permit a
separate IMPLEMENTATION_WORKER handoff. Do not start BUILD during rereview.

## Parked

- P4-E BUILD pending independent Work Order authorization review
- Phase 5
- external-repository absorption
- governed-catalog schema migration
- XR1 historical-object debt

## Predecessor

`SESSION/handoffs/CVF_PROVENANCE_INHERITANCE_RECOVERY_2026-09-09.md` remains
settled historical evidence and must not be rewritten.
