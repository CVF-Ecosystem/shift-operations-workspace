# Project Knowledge Pack

This folder contains a small, advisory context pack for the Shift Operations
Workspace. Canonical repository sources remain authoritative; the curated
documents only help humans and locally governed agents orient themselves.

The downstream project currently implements neither remote knowledge ingest
nor retrieval, context injection, RAG, or learning memory. The pinned public
CVF-core helper can transform the three eligible Markdown files into chunks in
a disposable local directory. Its output contains host- and time-specific
metadata, is never committed, and is not evidence of model behavior.

Run the read-only validator from the project root:

```powershell
python scripts/check_project_knowledge.py
```

Only `PROJECT_CONTEXT.md`, `OPERATIONS_GLOSSARY.md`, and
`GOVERNANCE_BOUNDARIES.md` are eligible for the local rehearsal. This README
and `manifest.json` are excluded. Do not place credentials, provider payloads,
customer or production records, or RESTRICTED material here. Static screening
is a bounded safety check, not DLP or data minimization.

Remote collection creation, POST operations, provider calls, and use of this
pack as production governance evidence require separate authority and proof.
