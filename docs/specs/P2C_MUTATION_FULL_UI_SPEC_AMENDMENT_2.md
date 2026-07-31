# SPEC Amendment 2 — P2-C C3a1 Legacy Runner Compatibility

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3a1`
- Risk: `R2`
- Status: `REVIEW_PASS`

## Amendment

Add `R31 — legacy governed-runner compatibility`:

> Every existing live-governance runner that calls `ShiftService.create` MUST
> seed the exact persisted active principal used by that call. Tests MUST
> exercise the real runner behavior and MUST NOT monkeypatch ledger
> construction to hide an unseeded production runner. Refusal→durable
> proof→provider-call ordering and historical receipt claims remain intact.

Add to R26:

> C3a1 edits to already-authorized test hosts at or above the hard limit MUST
> be line-neutral through compact fixtures or delegation to the authorized
> assignment OpenAPI module. No new split/debt/exemption path is permitted.

R1-R30 and AC-01..AC-35 remain unchanged. This amendment resolves only
`P2C-C3A1-BUILD-BLOCK-F1` and grants no authority beyond the amended Work
Order ceiling.
