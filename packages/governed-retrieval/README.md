# governed-retrieval

Pure P4-A1 local governed retrieval foundation. It owns the V1 request and
result contracts, immutable server corpus descriptors, deterministic query
normalization and lexical ranking, evidence projection and context-budget
trimming, and canonical receipt/citation hashing.

This package performs no ledger, filesystem discovery, environment, network,
provider, API, wall-clock, secret, or database access. It accepts all
evidence and execution metadata explicitly from its caller and may import
only the standard library, Pydantic, and the public `retrieval_contracts`
package.

`PROJECT_KNOWLEDGE_LOCAL_V1` is the only corpus this tranche can admit
positive evidence for. `SHIFT_CONFIRMED_OPERATIONS_V1` and
`SHIFT_ADVISORY_MESSAGES_V1` remain `DEPENDENCY_BLOCKED` and unreadable.

This package has no runtime application caller of its own and performs no
answer generation, provider key handling, LLM call, RAG, vector/index
persistence, durable audit, production route, UI, or live deployment. A
positive result is bounded local evidence, not a proof of confirmed
operational-record retrieval or AI-governance behavior.

Normative source:
[`docs/specs/P4A1_GOVERNED_RETRIEVAL_SPEC.md`](../../docs/specs/P4A1_GOVERNED_RETRIEVAL_SPEC.md)
and
[`docs/specs/P4A1_GOVERNED_RETRIEVAL_RECEIPT_CONTRACT.md`](../../docs/specs/P4A1_GOVERNED_RETRIEVAL_RECEIPT_CONTRACT.md).

Contract schema:
[`contracts/governed_retrieval.schema.json`](contracts/governed_retrieval.schema.json).
Public Python package: `src/governed_retrieval`.
