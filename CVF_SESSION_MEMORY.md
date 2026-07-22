# Project Session Memory (Pointer)

Memory class: POINTER_RECORD

Status: POINTER_ONLY — this file is NOT the canonical session memory for this
project.

## Why this file exists

This project (`shift-operations-workspace`) already had a mature, actively
maintained continuity system under `SESSION/` before the CVF Project Bootstrap
Continuity Contract introduced the `CVF_SESSION_MEMORY.md` /
`CVF_SESSION/ACTIVE_SESSION_STATE.json` naming convention. Renaming the
existing `SESSION/` tree would have broken every cross-reference in 11+
historical handoffs, `CONTRIBUTING.md`, and `docs/cvf/CVF_CONTROL_MAPPING.md`,
and was out of scope for a bootstrap-continuity reconciliation.

This file exists only so an agent that starts from the contract-standard
filename lands on the real canonical files instead of treating this pointer
itself as source of truth, and so no agent ever reads two different "active
handoff" or "active state" sources.

## Canonical files (read these, not this file, for actual state)

1. **Canonical session memory (human):** [`SESSION/SESSION_MEMORY.md`](SESSION/SESSION_MEMORY.md)
2. **Canonical active state (machine):** [`SESSION/ACTIVE_SESSION_STATE.json`](SESSION/ACTIVE_SESSION_STATE.json)
3. **Active handoff:** the file under `SESSION/handoffs/` named by
   `active_handoff` in the active state above.
4. **Implementation truth:** [`IMPLEMENTATION_STATUS.json`](IMPLEMENTATION_STATUS.json)
5. **Documentation index:** [`docs/INDEX.md`](docs/INDEX.md)
6. **Business/delivery roadmap:** [`docs/implementation/EXECUTION_ROADMAP.md`](docs/implementation/EXECUTION_ROADMAP.md)
   (this project's own five-phase roadmap — distinct from the seven-step
   control chain in `AGENTS.md`)

## Startup Order

Follow the order in `AGENTS.md`'s First-Request Protocol, which resolves
continuity through the canonical files listed above under `SESSION/...`.

## Compatibility directory note

A `CVF_SESSION/` directory **does exist** in this project
(`CVF_SESSION/ACTIVE_SESSION_STATE.json`). It was added as a compatibility
mirror only, required because `scripts/check_cvf_workspace_agent_enforcement.ps1`
looks for that exact literal path. It is **not** a second canonical state
source — it duplicates a bounded set of fields from
`SESSION/ACTIVE_SESSION_STATE.json` for the doctor's benefit and must always
agree with the canonical file. See that file's own `note`/`canonicalSource`
fields and `docs/CVF_BOOTSTRAP_LOG_2026-07-22.md` for the full explanation, and
`scripts/check_session_state.py` for the drift check that keeps the two in
sync.

Provider-local files (chat history, provider-specific memory) may assist
execution but are not project source authority.

## Mandatory Continuity Rehydration

Repeat the startup order before material work at every new or resumed
chat/session, after context loss or compaction, at the start of every new
tranche or work order, and whenever responsibility or the active handoff
changes. Re-read the canonical `SESSION/` files; do not rely on chat history,
provider-local memory, or a declaration from a previous session.

Emit a fresh `CVF Agent Declaration` before the first material action. At a
tranche transition, record the acknowledgment in the active handoff before
BUILD. If the canonical summary, active state, and handoff disagree, stop and
report `BLOCKED_CONTINUITY_DRIFT`.
