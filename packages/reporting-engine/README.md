# reporting-engine

P5-A renders validated, persisted `Report` snapshots as bounded PDF or XLSX
attachments. The package has no ledger, network, provider, or status mutation.
The API caller authenticates and scopes the report before invoking it.

`render_bounded(report, view, format)` accepts `shift-summary`,
`customer-report`, `incident-report`, or `handover-report` and `pdf` or `xlsx`.
It validates the canonical aggregate digest, runs a killable isolated renderer,
and returns bytes only after the child completes within ten seconds. Controlled
`ExportFailure.code` values map to the API's bounded refusal contract.

The packaged `assets/DejaVuSans.ttf` and `LICENSE_DEJAVU` are required for PDF
Unicode coverage. XLSX includes literal source cells plus typed version cells
and a `Date values` sheet with explicit UTC Excel derivatives; canonical ISO
strings remain in primary cells. Packaging proof builds a local wheel and checks
both assets by SHA-256 and a clean import without the source package on `sys.path`.
