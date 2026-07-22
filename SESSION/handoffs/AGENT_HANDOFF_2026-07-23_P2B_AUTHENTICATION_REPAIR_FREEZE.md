# Agent Handoff — 2026-07-23 (P2-B Authentication Repair — FREEZE)

## Disposition

- Tranche: `P2B-AUTHENTICATION-REPAIR`
- Control-chain phase: `FREEZE`
- Risk: R2
- Result: `CLOSED_BOUNDED`
- Live governance evidence: PASS

The corrective tranche restored the required sequence:
INTAKE → DESIGN → SPEC → operator-approved WORK_ORDER → BUILD → independent
REVIEW → FREEZE. Commit `cd36b27` remains untouched as historical evidence of
the original unauthorized build candidate.

## Evidence and repair history

- Authorization artifacts: `0662780`
- BUILD: `2c397f7`
- Eight review findings repaired: `10e57e1`
- REVIEW_PASS recorded: `61cadcb`
- Alibaba provider configuration committed separately: `0064f4a`, hygiene
  follow-up `c1f7661`
- First identity-bound live attempt reached Alibaba but returned HTTP 401
  because the evidence script used the domestic endpoint with an international
  credential. This was recorded as FAIL, not reframed as proof.
- Regional endpoint repair: `bf7c328`
- Authorized rerun: PASS — valid JWT admitted, forged JWT refused, then a real
  Alibaba `qwen3.7-max` call returned HTTP 200 and
  `CVF_IDENTITY_EVIDENCE_OK`.
- Sanitized receipt:
  `docs/decisions/P2B_IDENTITY_LIVE_EVIDENCE_RECEIPT.md`

## Verified boundary

The `identity` control is load-bearing for workspace API governed routes and
is governance-approved within the receipt's boundary. The closure does not
claim approval quorum identity is authenticated, PostgreSQL was live-tested,
or that refresh tokens, revocation, self-service registration, password reset,
login rate limiting, or production admin provisioning exist.

High Finding #4 remains open: `known-principals.yaml` is still a registry and
has not been reconciled with the authenticated users table.

## Next governed move

Start a new control chain at INTAKE for exactly one selected lane: remaining
P2-A incidents/handovers (with a governed migration first),
`known-principals.yaml` ↔ users reconciliation, or P2-C frontend. Do not begin
BUILD from a loose chat instruction.
