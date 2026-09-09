# CVF Provenance Inheritance Recovery - Completion Record

- Tranche: `CVF-PROVENANCE-INHERITANCE-RECOVERY-2026-09-09`
- Risk: `R2`
- Disposition: `FREEZE / CLOSED_BOUNDED / READY_FOR_NEXT_GOVERNED_TRANCHE`
- Branch: `chore/cvf-provenance-inheritance-recovery`
- Baseline: `72858f0c43f4bbdfc0e09418591e1919e5d35c0e`
- Date: `2026-09-09`

## Outcome

This first-party project now inherits the current CVF control plane through
two read-only layers:

1. portable public Core `483c5e33d188b6b2d35d6cd19ee38a3c8548abc4`;
2. required operator-local rule pack materialized from private provenance
   `bee38695ebac452e0ea6b3487706ed5c84f5fc2e`.

The project remains the only writable application workspace. Neither CVF
repository was modified, vendored, or promoted to application truth.

## Repairs

- reconciled manifest, policy, AGENTS, bootstrap and Project Knowledge pins;
- preserved canonical continuity under `SESSION/` and its compatibility mirror;
- added repository LF policy to remove Windows checkout-dependent SHA drift;
- repaired two missing invariant pin consumers and the disposable fixture's
  transitive mutation-helper dependencies;
- repaired bounded file-size exceptions for immutable historical carriers;
- made the pytest async-fixture loop scope explicit;
- updated P4-E from `PARKED_CORE_REFRESH_REQUIRED` to
  `READY_FOR_FRESH_SPEC_TRANSITION` without granting BUILD;
- preserved the mature project catalog instead of destructively forcing the
  incompatible downstream catalog kit schema.

## Verification

| Check | Result |
|---|---|
| invariant-family repository fixture | `17 passed` |
| repaired Project Knowledge/invariant focused set | `91 passed` |
| repository validator | `PASS` |
| workspace doctor | `PASS WITH NOTE` - 24 mandatory checks pass; one bounded legacy-catalog note |
| Project Knowledge guard | `PASS` |
| invariant-family guard | `PASS` |
| file-size guard | `PASS` |
| session-state/mirror guard | `PASS` |
| final full non-live pytest | `2899 passed, 132 skipped, 2 expected adversarial serializer warnings` |
| diff/whitespace check | `PASS` |

The first full regression after the mechanical refresh returned `2888 passed,
132 skipped` plus failures from two shared roots: missing AGENTS invariant
routing and stale Project Context source pins. Both were repaired; the focused
91-test set then passed. The final full rerun on the closed workspace passed.
The two warnings are emitted by adversarial tests that deliberately construct
invalid enum values and assert fail-closed handling; `pytest-asyncio` no longer
emits its former configuration warning.

## Catalog Compatibility Debt

Doctor catalog kit 1.1 expects a new closed schema at the exact paths already
owned by this project's 26-module registry, generated module catalog, and
`scripts/generate_catalog.py` tests. Automatic installation would overwrite
project implementation truth. The doctor-supported `LEGACY_PROJECT` note is
therefore retained. A future migration must be its own governed tranche and
prove a lossless mapping before replacing those sources.

## Claim Boundary

No product source, runtime behavior, database, provider call, credential,
dependency installation, deployment, public release, production-readiness
claim, public-Core mutation, or private-provenance mutation occurred.

## Next Governed Move

Resume P4-E from accepted `DESIGN_REVIEW_PASS` only by recording a fresh
explicit SPEC transition. Independently review its SPEC and bounded Work Order
before any BUILD. Phase 5, external-repository absorption, catalog schema
migration, and XR1 historical-object debt remain parked.
