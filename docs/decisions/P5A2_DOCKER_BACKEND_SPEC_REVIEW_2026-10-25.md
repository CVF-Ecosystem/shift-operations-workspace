# P5-A2 Docker synthetic backend — independent SPEC review

Date 2026-10-25; Root REVIEWER, independent from Sol SPEC_AUTHOR.
Disposition: SPEC_REVIEW_PASS_BOUNDED. Risk R2; no runtime grant here.

Reviewed `docs/specs/P5A2_DOCKER_SYNTHETIC_BACKEND_SPEC.md`, SHA-256
`c97cad4967840e53f41909968a31f61920da754315d78dc3ea004f5a0745a830`, against
the accepted source audit/DESIGN, actual native PostgreSQL runner/migration/
SqlLedger ownership and unchanged parent numeric contract. Root's recipe
clarification DBSPEC-F1 is resolved: exact clock/IDs/window/successor/as-of
values and a pre-BUILD oracle are fixed before the new SQL loader exists.

Root computed the independent fixture oracle using only unchanged accepted
helper/pure code, without a database, Docker, provider or new test invocation.
SHA-256: `12ad36cbd335a8def5e7ac9a6ade6f0bf542cb45af4cec1760a7291a8f6973c0`.
There are 36 shifts/37 report versions. Initial36h and later38h both yield
READY, forecast4, band[4,4]; selected version, lineage and evaluation digests
differ. The oracle excludes verbose history_context but pins its summary
digests and selected immutable metadata. Future implementation cannot rewrite it.

R1–R4 are coherent for a single disposable PostgreSQL rehearsal: native helper
reuse, migration-owned schema, actual reconnect/persistence/aware-time proof,
late-version exclusion, secret-safe evidence and exact owned-resource cleanup.
Ordinary 36-shift fixtures do not imply the unbuilt G06 count/snapshot/auth
query or operational completeness. No invented UTC, production data, .env,
AI provider effect or forecast business-quality claim is accepted.

Invariant-family NOT_APPLICABLE is accepted for this legacy test-driver reuse:
no new shared business receipt/model, field-presence grammar, counter algebra
or emitter contract. Parent family remains unchanged. A new shared query or
receipt schema would require returning to SPEC before implementation.

Full Product Milestone Binding remains the SPEC's G01–G14 table and canonical
parent/source audit. Selected evidence serves SQL portions G04/G05/G13 only;
all remaining owner/destination assignments and P5-B/C/D stay in force.
P5-A/P5-A2 OPEN, Phase5 0/5. Operator retains business acceptance. Root transitions
REVIEWER to WORK_ORDER_AUTHOR for bounded execution/effect authority; independent
authorization review, committed dispatch and dedicated actual-SHA continuity
remain prerequisites to BUILD or any image/package/container/DB effect.
