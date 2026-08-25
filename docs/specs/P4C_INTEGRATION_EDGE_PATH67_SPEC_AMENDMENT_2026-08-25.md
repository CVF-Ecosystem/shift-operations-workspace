# SPEC Amendment 1 — P4-C path 67 Knowledge source pins

- Tranche: `P4C-INTEGRATION-EDGE-2026-08-23`
- Phase: `SPEC`
- Risk: `R2`
- Accepted DESIGN amendment:
  `docs/decisions/P4C_INTEGRATION_EDGE_PATH67_DESIGN_AMENDMENT_2026-08-25.md`
- DESIGN amendment review: `DESIGN_AMENDMENT_REVIEW_PASS`, `NONE/NONE`
- BUILD: `STOPPED`

## Requirements

- **A1-R1 — Ceiling:** Add exactly path 67, `knowledge/manifest.json`; the
  original 66 paths and all P4-C runtime requirements remain unchanged.
- **A1-R2 — Exact values:** In that file, replace only these current values:
  - registry `3505654ae154ebca22daea6fbe632d365a648902bac1f459a245de4aa5e30e36`
    → `4a7c621126cc1237bc8ec43bc67dba69ca1ccfc94a402ac65a8131d18fe5710f`;
  - `AGENTS.md` `afce67b2e37fd3072a45b942d4d1d33491726d4d182c8cd4b0f600c8992b5770`
    → `6b2629d21f49b6841ffccad3dd1912dca50b5ea9a9eb6c6c2a1edf56c1b3fecf`;
  - `.cvf/manifest.json`
    `8cd22f2a2129f9d57b61b8587c24d5164935034d2fc59d011f511b205ec9c0da`
    → `2f319767aadce1da76650bfe4b682ad993d664746157dd4b80a49a85f6f8d79a`.
- **A1-R3 — Preservation:** Preserve the existing Core-refresh
  `IMPLEMENTATION_STATUS.json` pin delta and every other byte in the Knowledge
  manifest. Do not change validators, catalog outputs, invariant matrices,
  runtime source or tests merely to make a guard pass.
- **A1-R4 — Verification:** Recompute each source SHA from bytes, run
  `python scripts/check_project_knowledge.py`,
  `python -m pytest -q tests/unit/test_project_knowledge_pack.py`, the original
  P4-C focused/full non-live suites and repository guards. Any stale pin,
  unexpected manifest delta or failing test stops BUILD.
- **A1-R5 — Effects:** No provider, external HTTP, credential, install,
  deployment, database mutation beyond already-authorized disposable-local
  P4-C evidence, commit or push is added.

## Acceptance

1. Final P4-C BUILD union is exactly 67 unique authorized paths.
2. The three named pins equal their source SHA-256 values and no other
   path-67 value changes under P4-C ownership.
3. Knowledge validation and the exact repository-pack test pass without
   weakening either guard.
4. Parent SPEC R1-R16, AC-01..AC-10 and both invariant-family digests remain
   unchanged.

## Disposition

`READY_FOR_INDEPENDENT_SPEC_AMENDMENT_REVIEW`. BUILD remains stopped.
