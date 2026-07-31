# ADR Addendum — P2-C C3a2 Ceiling Repair

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3a2`
- Phase: `DESIGN AMENDMENT`
- Risk: `R2`
- Status: `REVIEW_PASS — CLOSED_WITHOUT_WAIVER`

## Finding

`C3A2-BUILD-BLOCK-F1 TWO_REQUIRED_HOSTS_OMITTED`: after G6 passed at
`69518100a322b0be1cc53b30b7c8cd6b16d7e15a`, BUILD wired the authorized
central guard and stopped when the full suite proved two required hosts were
outside the exact 79-path ceiling:

- `tests/contract/test_contract_files.py` exercises the real open-work route
  but creates only an unassigned direct-ledger shift;
- `scripts/run_message_admission_live_governance_evidence.py` expects the
  frozen-shift message refusal to reach lifecycle 409 but does not explicitly
  assign that authenticated principal, so correct C3a2 scoping returns 404.
  Its separate fresh-ledger genuine admitted-create branch also lacks that
  assignment and returns 404 before proving one message/one audit.

The observed partial-build full suite was `896 passed / 231 failed / 112
skipped`. The catalog drift test needs no source edit: it reflects expected
candidate metric drift before canonical catalog regeneration. Existing live
runner test files need no edit when their authorized scripts are repaired.

## Decision

Add exactly the two omitted hosts to the C3a2 BUILD ceiling, raising it from
79 to 81. The contract test must explicitly seed its viewer ACTIVE assignment.
The message runner must seed authenticated `msg-ev-op` ACTIVE assignment in
both fresh-ledger branches: frozen refusal preserves 409 with zero message/
audit writes and zero provider calls; genuine admission preserves exactly one message, exact
actor-bound audit and the later exactly-one real provider call.

No bypass, inferred/default assignment, monkeypatch, wildcard, reserve, new
debt or other path is authorized. All original requirements, evidence,
protected boundaries and stop conditions remain unchanged.

## BUILD state

The partial BUILD remains unstaged. No out-of-ceiling edit, provider call,
stage, commit, push, self-review or FREEZE occurred. Resume requires SPEC and
Work Order amendments, independent authorization review, a pushed amendment
commit and a separate pushed four-surface resume checkpoint.
