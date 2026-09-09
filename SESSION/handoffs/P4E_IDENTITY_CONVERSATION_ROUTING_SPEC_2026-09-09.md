# Handoff - P4-E Identity Mapping and Conversation Routing SPEC

- Tranche: `P4E-IDENTITY-CONVERSATION-ROUTING-2026-09-09`
- Status: `SPEC / READY_FOR_INDEPENDENT_SPEC_REVIEW`
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
`1.0-draft / READY_FOR_INDEPENDENT_SPEC_REVIEW`. It consumes accepted DESIGN
digest `2d0975a301a15c7b8a85eba121410391ddca2f067b16d9c5089d79edb9c397b9`
and defines the bounded identity-linkage, authorization, durable inbox,
conversation-placement, privacy, retention, idempotency, and refusal contract.

Three repository-governed invariant families are registered and pinned:

- `P4E-MAPPING-ACTION-OUTCOMES`:
  `9edccf4d39a9b36438c2fde5e66020976f68e2ca46969493ec5e909b859b38ef`
- `P4E-IDENTITY-RESOLUTION-OUTCOMES`:
  `9add3987bc6f5b64f18132a55c0adbd5415a753ded21a670b544556cdd53c800`
- `P4E-CONVERSATION-PLACEMENT-OUTCOMES`:
  `e8500e6b32b5138e6bd99995fe96cfd6f2aa61e30b0537d00caa549a2913584c`

## Verification

- invariant-family guard: `PASS`
- focused invariant suite: `72 passed, 2 skipped`
- whitespace/error scan: `PASS`
- no product source, dependency, schema migration, provider call, live call,
  credential, deployment, or external effect was introduced

These are deterministic authoring checks, not an independent SPEC review and
not runtime or governance-behavior proof.

## Next allowed move

Assign an independent `SPEC_REVIEWER` to review the accepted DESIGN, this SPEC,
all three invariant matrices, registry entry, and digest consumer. The author
must not self-approve. Only an independent `SPEC_REVIEW_PASS` with all findings
closed may authorize a separate Work Order authoring transition. BUILD remains
unauthorized.

## Parked

- P4-E Work Order and BUILD
- Phase 5
- external-repository absorption
- governed-catalog schema migration
- XR1 historical-object debt

## Predecessor

`SESSION/handoffs/CVF_PROVENANCE_INHERITANCE_RECOVERY_2026-09-09.md` remains
settled historical evidence and must not be rewritten.
