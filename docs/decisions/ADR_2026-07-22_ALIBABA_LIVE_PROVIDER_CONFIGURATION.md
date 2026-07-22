# ADR: Alibaba live-provider credential and quota-aware model selection

- Status: Accepted for specification
- Risk: R2 (external provider credential and paid/quota-bearing API)
- Decision owner: operator request dated 2026-07-22
- Tranche: PROVIDER-ALIBABA-LIVE-CONFIG

## Context

CVF governance claims require a real provider call. The operator supplied an
Alibaba workspace credential CSV outside the repository and authorized its use
for live CVF runs. The credential must remain outside Git and out of command
output. Available free-quota models have different expiration dates, so a
static default can fail after quota exhaustion or expiry.

## Decision

Store the Alibaba key only in the current user's persistent environment under
`ALIBABA_API_KEY`, which the pinned CVF core resolves and aliases to
`DASHSCOPE_API_KEY` for its canonical release gate. Do not copy the source CSV
or secret value into the project.

Track non-secret model availability in a versioned JSON catalog under
`packages/ai-providers/alibaba/`. A small selector validates the catalog and
chooses an enabled, unexpired model with remaining quota. Preference is first
by explicit priority, then by the nearest usable expiration so quota that
expires sooner is consumed before longer-lived quota. Models with no remaining
quota or an expiration date earlier than the run date are ineligible.

The selector is advisory configuration for live tooling. It does not wire the
application AI gateway or make data-scope, cost, or termination controls
load-bearing.

## Security boundary

- Raw provider credentials are never committed, echoed, logged, or written to
  evidence.
- The source CSV remains outside the repository.
- Live evidence records provider, model, timestamp, redacted request intent,
  HTTP outcome, and response excerpt only.
- User authorization to use the key does not authorize unrelated external
  actions or bypass CVF phase gates.

## Consequences

The model catalog is a dated operator snapshot, not a live billing API. Before
material use, the selector must reject expired/exhausted entries; quota values
must be refreshed when the Alibaba console changes. A failed live call is
recorded as failure and must not be restated as governance proof.
