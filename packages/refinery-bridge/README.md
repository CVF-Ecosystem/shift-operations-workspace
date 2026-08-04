# refinery-bridge

Deterministic local P3-A refinement boundary. It validates a safe admission
envelope, normalizes syntax, applies reviewed terminology, classifies
sensitivity/topics, rejects ambiguity, redacts high-confidence values, performs
caller-scoped advisory dedupe, and emits typed fail-closed receipts.

The package has no runtime application caller and performs no provider,
network, database, filesystem discovery, environment-secret, persistence,
remote-ingest or retrieval work. A ready context candidate is control coverage,
not confirmed operational truth or AI-governance evidence.

Contract: [`contracts/refinery_contract.yaml`](contracts/refinery_contract.yaml).
Public Python package: `src/refinery_bridge`.
