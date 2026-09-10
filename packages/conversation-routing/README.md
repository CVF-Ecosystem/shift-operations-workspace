# conversation-routing

Provider-neutral route-binding and deterministic placement contracts for P4-E
v1: supported positive targets are `WORKSPACE`, `SHIFT`, and `INCIDENT`, else
a non-privileged `FALLBACK`/`REFUSED`/`RETRY_PENDING` decision. `CUSTOMER` and
`VESSEL` targets remain unsupported and deferred to a separately governed
tranche; the `customer-router/` and `vessel-router/` scaffolds under this
package are documentation-only and excluded from P4-E BUILD ownership.
