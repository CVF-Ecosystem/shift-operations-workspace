# P4-B AI Provider Foundation — DESIGN Review

- Role: `REVIEWER`
- Disposition: `DESIGN_REVIEW_PASS`
- Findings / waivers: `NONE / NONE`

The design preserves P4-A as the sole external dispatch point and assigns
closed, non-overlapping semantics to all three existing AI modes. Deterministic
rules cannot execute code or perform I/O; unknown/no-match cases fail closed.
Mock behavior is explicitly test-only, disabled by default and
evidence-ineligible. Registry-owned kind/placement facts prevent caller
relabeling, and external identity is rechecked against the nested gateway
request/receipt.

The receipt and dependency boundaries prevent prompt/output/credential
leakage and avoid production-adapter, durability, route or deployment claims.
The one-call live checkpoint remains separate from BUILD and cannot use mock
output. `DESIGN_REVIEW_PASS`; SPEC may proceed, BUILD remains prohibited.
