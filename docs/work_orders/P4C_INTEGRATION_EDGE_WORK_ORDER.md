# WORK ORDER — P4-C Integration Edge

- Work order id: `P4C-INTEGRATION-EDGE-WO-2026-08-23`
- Phase: `WORK_ORDER`
- Risk ceiling: `R2`
- Author: `WORK_ORDER_AUTHOR`
- Execution base: `0b89016df8483a4904d2c64b1a6560ccbc6b27ae`
- Parent SPEC: `docs/specs/P4C_INTEGRATION_EDGE_SPEC.md`
- SPEC review: final `SPEC_REVIEW_PASS`, findings/waivers `NONE/NONE`
- BUILD authority: `NOT GRANTED`
- Commit/push/provider/credential/install/deployment authority: `0`

## Objective

Implement only the reviewed P4-C provider-neutral Integration Edge boundary:
dual admission budgets, verified encrypted raw evidence, replay/collision and
quarantine state, canonical untrusted proposals, signed internal ports,
provider-neutral outbound state and deterministic receipts conforming to both
registered invariant matrices.

## Exact BUILD ceiling (66 paths)

1. `pyproject.toml`
2. `apps/integration-edge/pyproject.toml`
3. `database/migrations/010_integration_edge.sql`
4. `packages/channel-sdk/pyproject.toml`
5. `packages/channel-sdk/src/channel_sdk/__init__.py`
6. `packages/channel-sdk/src/channel_sdk/service_assertion.py`
7. `packages/channel-sdk/src/channel_sdk/ports.py`
8. `apps/integration-edge/src/integration_edge/__init__.py`
9. `apps/integration-edge/src/integration_edge/main.py`
10. `apps/integration-edge/src/integration_edge/config.py`
11. `apps/integration-edge/src/integration_edge/errors.py`
12. `apps/integration-edge/src/integration_edge/models.py`
13. `apps/integration-edge/src/integration_edge/canonical.py`
14. `apps/integration-edge/src/integration_edge/invariants.py`
15. `apps/integration-edge/src/integration_edge/verification/hmac.py`
16. `apps/integration-edge/src/integration_edge/verification/service_assertion.py`
17. `apps/integration-edge/src/integration_edge/crypto/__init__.py`
18. `apps/integration-edge/src/integration_edge/crypto/envelope.py`
19. `apps/integration-edge/src/integration_edge/storage/__init__.py`
20. `apps/integration-edge/src/integration_edge/storage/protocol.py`
21. `apps/integration-edge/src/integration_edge/storage/memory.py`
22. `apps/integration-edge/src/integration_edge/storage/tables.py`
23. `apps/integration-edge/src/integration_edge/storage/sql.py`
24. `apps/integration-edge/src/integration_edge/rate_limit/__init__.py`
25. `apps/integration-edge/src/integration_edge/rate_limit/store.py`
26. `apps/integration-edge/src/integration_edge/deduplication/store.py`
27. `apps/integration-edge/src/integration_edge/inbound/__init__.py`
28. `apps/integration-edge/src/integration_edge/inbound/service.py`
29. `apps/integration-edge/src/integration_edge/quarantine/__init__.py`
30. `apps/integration-edge/src/integration_edge/quarantine/service.py`
31. `apps/integration-edge/src/integration_edge/routing/__init__.py`
32. `apps/integration-edge/src/integration_edge/routing/service.py`
33. `apps/integration-edge/src/integration_edge/outbound/__init__.py`
34. `apps/integration-edge/src/integration_edge/outbound/service.py`
35. `apps/integration-edge/src/integration_edge/health/__init__.py`
36. `apps/integration-edge/src/integration_edge/health/status.py`
37. `apps/integration-edge/src/integration_edge/webhook/__init__.py`
38. `apps/integration-edge/src/integration_edge/webhook/router.py`
39. `apps/workspace-api/src/workspace_api/external_ingress/__init__.py`
40. `apps/workspace-api/src/workspace_api/external_ingress/models.py`
41. `apps/workspace-api/src/workspace_api/external_ingress/repository.py`
42. `apps/workspace-api/src/workspace_api/external_ingress/service.py`
43. `apps/workspace-api/src/workspace_api/external_ingress/router.py`
44. `apps/workspace-api/src/workspace_api/main.py`
45. `contracts/channel/service-assertion.schema.json`
46. `contracts/channel/edge-ingress.schema.json`
47. `contracts/channel/edge-outbound.schema.json`
48. `tests/security/test_hmac.py`
49. `tests/security/test_p4c_preauth_rate_limit.py`
50. `tests/unit/test_p4c_service_assertion.py`
51. `tests/unit/test_p4c_models_schema.py`
52. `tests/unit/test_p4c_crypto.py`
53. `tests/unit/test_p4c_rate_replay.py`
54. `tests/unit/test_p4c_invariant_emitters.py`
55. `tests/unit/test_p4c_dependency_boundary.py`
56. `tests/unit/test_p4c_outbound.py`
57. `tests/integration/test_p4c_inmemory_edge.py`
58. `tests/integration/test_p4c_sqlite_edge.py`
59. `tests/integration/test_p4c_workspace_ingress.py`
60. `tests/integration/test_p4c_postgres_live.py`
61. `tests/integration/test_p4c_postgres_live_runner.py`
62. `tests/unit/test_invariant_family_contract.py`
63. `tests/integration/test_invariant_family_repository_guard.py`
64. `tests/integration/test_schema_parity_integration_edge.py`
65. `docs/catalog/MODULE_REGISTRY.json`
66. `docs/catalog/MODULE_CATALOG.md`

The final BUILD changed-set union MUST equal these 66 paths after
deduplication. A missing path is allowed only through a reviewed Work Order
amendment; an extra path is an immediate stop. Deleting or renaming a listed
path also requires amendment.

## Protected pre-BUILD governance set

Before this Work Order was created, the P4-C governance/continuity dirty set was
exactly 17 paths with LF-joined sorted-path SHA-256
`ad586ecfbba2b64ebccd30bd796e771ac62ca48c61f0e7b0b97ef5b67dfccc28`.
Those paths, this Work Order, every independent review artifact and the
pre-existing untracked operator assessment are protected from the
IMPLEMENTATION_WORKER. The assessment must not be opened, edited, staged or
used as evidence.

## Implementation obligations

1. Follow SPEC R1-R16 and AC-01..AC-10 without reinterpreting matrix rules.
2. Pin ingress matrix digest
   `277c5211e914a44858d105cd6f5ceba7fe5d95aa35afaa85f811aba26d858b2b`
   and outbound digest
   `41f42d0b2585201a41fbed3b9f2d7e6bfd9f2adf4f2f587890addc0a7d4604a6`.
3. Use `channel-sdk` as the sole shared service-assertion/port contract;
   edge domain must retain the SPEC dependency prohibitions.
4. Migration 010 owns only edge evidence/proposal tables and exact
   constraints, including `(key_id, nonce)` uniqueness. It must not change
   existing business-truth tables.
5. AES-256-GCM uses injected keys and a server-owned CSPRNG; no plaintext,
   secrets, raw provider errors or bodies may reach logs/responses/receipts.
6. The workspace API route creates only actor-neutral external-ingress
   proposals. It is not `POST /messages` and cannot create confirmed truth.
7. No deployable channel adapter is added. Test fake is local to tests or
   explicitly test-only and evidence-ineligible.
8. Catalog files are generator-owned: update only via
   `python scripts/generate_catalog.py --write` after source truth changes.

## Roles

- IMPLEMENTATION_WORKER: separate from the independent authorization reviewer;
  changes only the exact ceiling.
- INDEPENDENT_COMPLETION_REVIEWER: recomputes scope, matrix digests, contracts,
  source, migrations, tests and claim boundary.
- REPAIR_WORKER: only after accepted findings and within an explicit amended or
  retained ceiling.
- COMMIT_STEWARD: not authorized by this Work Order.

## Shared invariant-family proof

- **Applicability decision:** `APPLICABLE`. This R2 tranche triggers the
  invariant-family standard for both registered families below; their matrix
  files remain the sole source of outcome and mutation rules.
- **Matrix ids / canonical digests:**
  - `P4C-INGRESS-TERMINAL-OUTCOMES` —
    `277c5211e914a44858d105cd6f5ceba7fe5d95aa35afaa85f811aba26d858b2b`;
  - `P4C-OUTBOUND-TERMINAL-OUTCOMES` —
    `41f42d0b2585201a41fbed3b9f2d7e6bfd9f2adf4f2f587890addc0a7d4604a6`.
- **Declared emitters:** ingress
  `integration_edge.invariants:emit_ingress_terminal_receipt`; outbound
  `integration_edge.invariants:emit_outbound_terminal_receipt`.
- **Declared evidence paths:** `tests/unit/test_invariant_family_contract.py`
  and `tests/integration/test_invariant_family_repository_guard.py` for both
  families. Raw real-emitter samples are exercised by the authorized
  `tests/unit/test_p4c_invariant_emitters.py` path.
- **Mutation exclusions:** both matrices exclude only
  `RECURSE_NESTED_OBJECTS` for their declared flat receipt shapes, with the
  recorded reason `Flat receipt shape.` and `independentReviewRequired: true`.
  The independent SPEC review acknowledged those matrix-declared exclusions;
  no exclusion is waived or inferred by the worker.
- **Exact evidence commands:**
  - `python scripts/check_invariant_families.py --json`
  - `python -m pytest -q tests/unit/test_invariant_family_contract.py tests/integration/test_invariant_family_repository_guard.py tests/unit/test_p4c_invariant_emitters.py`
- **Evidence owner:** `IMPLEMENTATION_WORKER` returns the family-conformance
  summary, command outputs and raw emitted positive samples; it does not
  approve that evidence.
- **Reviewer recomputation:** `INDEPENDENT_COMPLETION_REVIEWER` must recompute
  both canonical digests, rerun the same matrix corpus and exact commands,
  sample at least one raw positive emitted by the declared real emitter for
  every outcome in each family, and verify that no expected value or rule was
  derived from BUILD implementation. Any mismatch is a review failure.

## G6 preflight

Immediately before the first BUILD edit, the worker must record:

- `HEAD == 0b89016df8483a4904d2c64b1a6560ccbc6b27ae` and staged set empty;
- `origin/main` equality or stop on remote drift;
- protected governance set and assessment unchanged;
- exact Work Order SHA-256 and both canonical matrix digests;
- no candidate path outside the 66-path ceiling;
- Python 3.13.12, Pydantic 2.10.6 and installed cryptography version, without
  installing or upgrading anything;
- session, invariant-family, catalog, file-size, repository and doctor gates
  PASS (doctor may retain only the bounded legacy-catalog warning).

## Required BUILD evidence

- focused model/schema/service-assertion/crypto/rate/replay/quarantine/routing/
  outbound/dependency tests;
- both matrix emitters sampled once per outcome plus mutation corpus;
- SQLite parity and migration-created disposable PostgreSQL evidence with exact
  cleanup; no production/managed database claim;
- invalid-signature flood and dual-counter concurrency boundaries;
- nonce reuse/generator failure/concurrent uniqueness probes;
- raw/ciphertext/AAD/tag/digest tamper and rollback probes;
- service assertion audience/operation/body/nonce/key failure probes;
- no-business-truth, no-internal-message and no-real-adapter proofs;
- full non-live test suite and all repository guards;
- exact 66-path diff, zero staged paths and secret/disclosure scan.

## Network and external effects

BUILD budget is zero for provider calls, external HTTP, credentials, installs,
deployment, commit and push. Local disposable PostgreSQL is allowed only if the
existing toolchain is already available and exact cleanup is recorded. Any
governance-behavior proof requiring a real provider call is a separately
authorized post-review checkpoint and is not granted here.

## Stop conditions

Stop on source/remote drift, dirty-set mismatch, missing dependency requiring
install, path 67, matrix/pin drift, migration collision, secret exposure,
database residue, ambiguous external effect, test failure, third same-root
repair round or need for commit/push/provider/deployment authority.

## Return condition

Return `READY_FOR_INDEPENDENT_COMPLETION_REVIEW` only with the exact changed
set and all required deterministic evidence. The worker must not author its own
completion review or declare FREEZE.

## Disposition

`READY_FOR_INDEPENDENT_AUTHORIZATION_REVIEW`. BUILD remains unauthorized.
