# DESIGN Amendment 1 — P4-C path 67 Knowledge source pins

- Tranche: `P4C-INTEGRATION-EDGE-2026-08-23`
- Phase: `DESIGN`
- Risk: `R2`
- Parent DESIGN: `DESIGN_2026-08-23_P4C_INTEGRATION_EDGE.md` (unchanged)
- BUILD: `STOPPED`

## Authority and cause

The operator authorized `knowledge/manifest.json` as the sole additional
P4-C BUILD path and approved Core target `9c018329...`. Mandatory catalog
generation changed the registry hash; the Core refresh changed the hashes of
`AGENTS.md` and `.cvf/manifest.json`. All three are existing canonical sources
pinned by the Knowledge manifest, so the guard must fail until they agree.

## Selected design

Add only `knowledge/manifest.json` as path 67. P4-C may replace only these
three stale `sourcePins[].sha256` values with hashes recomputed from source:

1. `docs/catalog/MODULE_REGISTRY.json`:
   `4a7c621126cc1237bc8ec43bc67dba69ca1ccfc94a402ac65a8131d18fe5710f`;
2. `AGENTS.md`:
   `6b2629d21f49b6841ffccad3dd1912dca50b5ea9a9eb6c6c2a1edf56c1b3fecf`;
3. `.cvf/manifest.json`:
   `2f319767aadce1da76650bfe4b682ad993d664746157dd4b80a49a85f6f8d79a`.

The pre-existing `IMPLEMENTATION_STATUS.json` pin delta in this working file
belongs to Core-refresh lineage and must be preserved, not re-authored by
P4-C. No metadata, source path, classification, eligibility, consumer,
retention/correction rule, validator or other pin may change.

The parent DESIGN and both registered invariant families remain byte-exact.
No provider, credential, install, deployment, database, commit or push is
authorized.

## Gate

Independent review must recompute the three hashes and confirm the
one-file/three-value boundary before SPEC amendment. BUILD stays stopped.

## Disposition

`READY_FOR_INDEPENDENT_DESIGN_AMENDMENT_REVIEW`.
