# INTAKE — Project Knowledge Pack C4 Repair Amendment 1

- Tranche: `PROJECT-KNOWLEDGE-PACK-C4-REPAIR-AMENDMENT-1-2026-08-03`
- Parent C4 authority: `8dd99c02ad27901f416b935a1dcf78ab6ccd4eaa`
- Parent BUILD: `bb3e33668a6d60585455bf0301ba059918a15890`
- Risk: `R2`
- Status: `INTAKE_COMPLETE`

## Trigger

The first C4 verification command, `python scripts/check_project_knowledge.py`,
failed closed with exactly:

- `KPK_ELIGIBILITY_MISMATCH:PROJECT_CONTEXT.md`
- `KPK_SOURCE_PIN_DRIFT:PROJECT_CONTEXT.md`

No later gate ran, no retry occurred, and no provider/helper/network/POST call
occurred. The exact eight C4 closure paths remain unstaged.

## Root cause

C4 requires truthful updates to all three sources pinned by the active
`PROJECT_CONTEXT.md` entry: `IMPLEMENTATION_STATUS.json`,
`docs/catalog/MODULE_REGISTRY.json`, and
`docs/implementation/EXECUTION_ROADMAP.md`. C4 simultaneously protects the
BUILD-owned `knowledge/manifest.json` and requires the knowledge validator to
PASS. The source hashes therefore must drift, and the two requirements cannot
both be satisfied inside the original eight-path closure ceiling.

## Requested correction boundary

Retain the eight current closure paths and add exactly two repair paths:

1. `knowledge/PROJECT_CONTEXT.md`
2. `knowledge/manifest.json`

The first updates advisory current-tranche wording. The second updates only
the three `project-context` source-pin hashes needed to bind the final closure
sources. The other six BUILD paths and all five C4 authority paths remain
byte-identical.

## Exclusions

No helper or integration rehearsal, provider/configuration access, network,
POST, remote ingest, external write, new pack entry, schema/policy change,
Refinery, retrieval, RAG, learning, production claim, stage, closure commit or
push is authorized by this INTAKE.

