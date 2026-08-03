# PROJECT-OPERATIONS-SKILL C4 STATUS REPAIR SPEC

- Risk: `R2`
- Status: `SPEC_COMPLETE_PENDING_AUTHORIZATION`

## Requirements

- `R1` BUILD changes exactly `IMPLEMENTATION_STATUS.json`.
- `R2` Only the top-level `status` scalar changes; all other parsed JSON is
  canonical-byte equivalent.
- `R3` The new value matches Project Operations Skill CLOSED_BOUNDED and
  Project Knowledge Pack INTAKE, without advancing Knowledge Pack further.
- `R4` Preserve the two untracked Knowledge Pack drafts byte-for-byte and
  unstaged.
- `R5` Run JSON parsing, repository/session/catalog/file-size/doctor gates and
  a structural before/after probe that deletes `status` then compares the
  remaining objects exactly.
- `R6` Make zero provider calls and leave zero runtime/staged residue before
  independent review.

## Acceptance criteria

Exact one-path/one-scalar diff, all R1-R6 checks PASS, independent review PASS,
separate repair commit/push, then clean `HEAD == origin/main` with the two
Knowledge Pack drafts still untracked and unchanged.

