# Operations Glossary

This document is advisory. The cited domain models, lifecycle guards, and
workspace contracts define the exact current types and fields.

## Stable domain language

- **Shift:** the operational parent model with an explicit status enum and
  bounded identifying, timing, and version fields.
- **Message:** a shift-bound communication model with source, sender, text,
  state, created time, and evidence fields.
- **Operational event:** a proposed or confirmed occurrence associated with a
  shift and governed evidence state.
- **Task:** actionable shift work with an explicit lifecycle and versioned
  transition boundary.
- **Customer request:** a request record with its own lifecycle; a shift link
  may be optional according to the canonical model.
- **Incident:** a shift-bound issue model with risk class,
  summary/description, status, owner, evidence, version, and created time.
- **Handover:** a source-to-destination shift model with typed items, status,
  creator/reviewer/receiver identities, timestamps, and version.
- **Report:** a shift-bound versioned report model with type, status/current
  marker, structured content, source manifest/digests, cutoff, and created
  time.
- **Assignment:** a shift-to-user staffing grant with active/revoked status,
  assignment/revocation actors and times, and version.
- **Evidence reference:** a typed reference containing an identifier, source
  type, source identifier, and optional SHA-256 value.
- **Correction:** the explicit post-confirmation path for changing recorded
  truth without erasing prior history.
- **Audit:** a named domain blueprint area; the cited package README does not
  claim a standalone audit model is implemented there.

The operations-domain package owns canonical Python domain definitions and
lifecycle guards. Compatibility shims do not become a second model authority.
JSON Schemas in workspace-contracts define provider-neutral interchange
boundaries; a schema's existence does not prove runtime behavior.

Sources: `packages/operations-domain/README.md`; `packages/operations-domain/src/operations_domain/models.py`; `packages/operations-domain/src/operations_domain/lifecycle.py`; `packages/operations-domain/src/operations_domain/assignment_models.py`; `packages/operations-domain/src/operations_domain/report_models.py`; `packages/workspace-contracts/README.md`
