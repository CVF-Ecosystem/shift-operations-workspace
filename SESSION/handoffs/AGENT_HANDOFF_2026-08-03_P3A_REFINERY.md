# Agent Handoff — P3-A Refinery

## Disposition

- Tranche: `P3-A-REFINERY-2026-08-03`
- Parent: Project Knowledge Pack closure `107c8fa`
- Risk: `R2`
- Control-chain phase: `INTAKE`
- Active role: `ORCHESTRATOR / INTAKE_AUTHOR`
- Status: `OPEN_FOR_INTAKE_REVIEW`

## Current truth

`refinery-bridge` is contract-only. Its YAML omits roadmap-required quarantine,
provenance, data-quality and fallback results; submodules have no runtime code
or tests. `data_scope` is callable but has no runtime caller and does not verify
minimization evidence. The existing normalized fixture invents an unsupported
`11h40 → 23:40` conversion and is not golden truth.

## Intake boundary

P3-A may design only a deterministic local, fail-closed transformation boundary
that preserves source linkage, refuses ambiguity/fabrication, separates
sensitivity from topic classification, emits quarantine/data-quality receipts
and produces no context candidate on failure. It does not own confirmed truth,
raw persistence, external ingest, provider calls, retrieval/RAG, P3-B/P3-C,
learning or production behavior.

## Evidence boundary

No provider call is needed or authorized for INTAKE. Future deterministic local
claims may use contract/unit evidence. Any future claim about actual AI/provider
governance requires a separately approved real-provider call and sanitized
receipt under AGENTS.md.

## Next governed move

Review `docs/decisions/INTAKE_2026-08-03_P3A_REFINERY.md` and resolve its eight
design decisions. No DESIGN, SPEC, WORK_ORDER, BUILD or later-queue authority
is inherited from the Project Knowledge Pack closure.

