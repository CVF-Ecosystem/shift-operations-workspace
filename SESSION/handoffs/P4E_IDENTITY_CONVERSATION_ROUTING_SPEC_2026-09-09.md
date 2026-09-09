# Handoff - P4-E Identity Mapping and Conversation Routing SPEC

- Tranche: `P4E-IDENTITY-CONVERSATION-ROUTING-2026-09-09`
- Status: `SPEC / REPAIRED_PENDING_INDEPENDENT_SPEC_REREVIEW`
- Risk: `R2`
- Active role: `ORCHESTRATOR`
- Branch: `docs/p4e-spec`
- Updated: `2026-09-09`

## Startup truth

This first-party project inherits public CVF Core
`483c5e33d188b6b2d35d6cd19ee38a3c8548abc4` and the mandatory operator-local
rule pack materialized from private provenance
`bee38695ebac452e0ea6b3487706ed5c84f5fc2e`. Both sources remain read-only.
The prior provenance-inheritance recovery is closed bounded.

## Current artifact

The operator explicitly advanced accepted P4-E DESIGN to SPEC on 2026-09-09.
`docs/specs/P4E_IDENTITY_CONVERSATION_ROUTING_SPEC.md` is now
`1.0-draft-r1 / READY_FOR_INDEPENDENT_SPEC_REREVIEW`. It consumes accepted DESIGN
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
Only an independent rereviewer may close those findings.

## Verification

- invariant-family guard: `PASS`
- declared matrix evidence command:
  `python -m pytest -q tests/unit/test_invariant_family_contract.py tests/integration/test_invariant_family_repository_guard.py`
  -> `35 passed, 2 skipped`
- extended repository invariant regression command:
  `python -m pytest -q tests/unit/test_invariant_family_contract.py tests/unit/test_invariant_family_contract_repair_round2.py tests/integration/test_invariant_family_repository_guard.py tests/integration/test_invariant_family_repository_guard_repair_round2.py`
  -> `72 passed, 2 skipped`
- whitespace/error scan: `PASS`
- no product source, dependency, schema migration, provider call, live call,
  credential, deployment, or external effect was introduced

These are deterministic authoring checks, not an independent SPEC review and
not runtime or governance-behavior proof.

## Next allowed move

Assign an independent `SPEC_REVIEWER` to rereview the unchanged Generation 1
review, the rework response, accepted DESIGN, repaired SPEC, all three
re-pinned matrices, registry entry, digest consumer, and scope README changes.
The author must not self-approve. Only an independent `SPEC_REVIEW_PASS` with
all findings closed may authorize a separate Work Order authoring transition.
BUILD remains unauthorized.

## Parked

- P4-E Work Order and BUILD
- Phase 5
- external-repository absorption
- governed-catalog schema migration
- XR1 historical-object debt

## Predecessor

`SESSION/handoffs/CVF_PROVENANCE_INHERITANCE_RECOVERY_2026-09-09.md` remains
settled historical evidence and must not be rewritten.
