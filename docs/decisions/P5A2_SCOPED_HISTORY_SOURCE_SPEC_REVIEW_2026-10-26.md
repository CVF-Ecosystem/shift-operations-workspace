# P5-A2 scoped history source — independent SPEC and family review

docType: completion_review
Status: REVIEW_PASS_BOUNDED
Date: 2026-10-26
Reviewer: independent REVIEWER; no SPEC, matrix or implementation ownership

## Decision

`CHANGES_REQUIRED_BOUNDED`; one contract finding, no waiver. This review covers
the source SPEC and registered static invariant family only. It grants no query
adapter BUILD, database/provider effect, operational coverage or milestone
closure. The DRAFT Work Order remains non-dispatchable by its own status and
listed missing native path, oracle, emitter and complete gate graph.

| Finding | Evidence | Finite correction |
|---|---|---|
| SOURCE-SPEC-F1 | SPEC R2 requires `SCOPE_INCOMPLETE` when eligible shifts, candidate report versions or per-snapshot incident references reach 501. The SOURCE_REFUSED table and matrix's closed `reason` domain also permit `CAP_EXCEEDED`, but no condition assigns that reason. An adapter could return either at the exact cap boundary while appearing to satisfy one of these surfaces. | Keep the parent-compatible 501 → `SCOPE_INCOMPLETE` rule and remove the unused `CAP_EXCEEDED` reason from the SPEC/matrix, or assign it an exact, distinct condition and reconcile R2. Recompute the SPEC source pin, matrix canonical digest, static pin and registry/guard evidence, then request independent rereview. Do not derive the decision from adapter behavior. |

## Contract and invariant-family proof consumed

The accepted Core-only correction and synthetic PostgreSQL receipt are closed
bounded at material `3de6c50e3f7932a1e79dba68c8dc21672a5d6579` and
continuity `7134f9eafbf2b19cbb8e24081d4b8bacecc3154b`. They prove the
recorded fixture version/time/lineage mechanics, not this source query. The
current source SPEC canonical UTF-8 universal-newline digest is
`a2e2b48a324ee69a95351426a66c75b1e19e39ed0f78dcbc1dbeab8de7d7002b`;
the registered `P5A2-SCOPED-SOURCE-OUTCOMES` matrix canonical digest is
`821042889859aa29ebb08d2413611a255ce218b8d001c12663f745f5bbf4a41a`
and matches `docs/specs/p5a2_scoped_source_invariant_pin.py`. The matrix's
contract-source pin matches the SPEC. Its `CANONICAL_DIGEST` ownership binding
points to the static pin, its two outcome shapes have closed field domains and
relations, and its excluded nested-object mutation declares a reason and
independent review requirement. I accept that exclusion only for this flat
static receipt; canonical manifest internals, backend counts and source
authorization remain future emitter tests. The planned emitter identity is
not implemented.

`python scripts/check_invariant_families.py` PASS. The targeted existing
generic corpus, `tests/unit/test_invariant_family_contract.py` plus
`tests/integration/test_invariant_family_repository_guard.py`, returned
35 passed and 2 skipped. This is structural/mutation coverage of declared
matrix shapes and pins; there is no raw emitted SOURCE_READY or SOURCE_REFUSED
runtime sample yet. The standard's real-emitter, mutation and positive-sample
review obligations remain for the future BUILD Work Order. Core inheritance,
project session, knowledge and file-size guards PASS. No CVF repository,
database, provider or network effect was used in this review.

The fixture-only cohort decision uses current ACTIVE assignment plus aware
`Shift.ends_at` in `[start,end)`, including reportless shifts, while the
existing numeric policy retains Report cutoff/as-of selection. Both policy
versions bind source identity without rewriting old runs. Denial comes before
data-quality diagnostics; SOURCE_REFUSED excludes actor/scope/time, counts,
IDs, manifest and payload. The 500/501 pre-materialization caps, consistent
snapshot/fresh assignment, aware time, immutable content and trusted fixture
coverage are requirements, not implemented evidence. Unknown production
enrollment/retention remains fail-closed. No automatic SOURCE_READY implies
forecast READY, production truth or human approval.

## Product milestone coverage and next gate

The SPEC reconciles G01–G14 against current source and accepted SQL proof.
This contract can close only the G04–G06 source-query/cohort/coverage/snapshot/
cap *specification*, after SOURCE-SPEC-F1 is settled. G04/G05/G13 fixture
mechanics are accepted; G06 query/auth/caps/cohort/retention and operational
coverage remain open/unknown. G01/A7/G02 are blocked, operational G03/G08–G10/
G13 and G07/G11/G12 remain open, G14 held. Root owns accountability/contracts/
commit; the assigned backend worker, independent reviewer, UI roadmap owner
and operator retain their P5-A2 and P5-B/C/D destinations and business
acceptance. Phase 5 remains 0/5.

After the finite SPEC/family correction, independent rereview may accept the
contract for normal material and dedicated continuity. A later source BUILD
still needs exact native query/unit-of-work paths, actual emitter and mutation
binding, an independent pre-loader fixture oracle, full gate graph, reviewed
Work Order and separate effect admission. The prior PostgreSQL effect ceiling
is spent. No source or effect dispatch follows from this review.

## Return-Time Closeability Recheck

closeabilityDisposition: CLOSEABLE
outsideAuthorityBlockers: NONE
nextRepairRoute: NONE
workerRedispatchAllowed: NO

## Independent SPEC/family repair rereview

`SPEC_REVIEW_PASS_BOUNDED`; SOURCE-SPEC-F1 `RESOLVED`, open findings `NONE`,
waivers `NONE`. The earlier changes-required finding is retained above as the
review history. The revised SPEC makes all three 501-item overflows
`SOURCE_REFUSED` with reason `SCOPE_INCOMPLETE`; `CAP_EXCEEDED` is absent from
the SPEC reason list and matrix's closed reason domain. The added trigger
table makes denial first and assigns each remaining refusal class. It requires
an independent fresh current cohort/membership view after the sealed source
snapshot, includes additions, revokes, assignment versions and Shift enrollment
changes, and refuses if that view cannot be established. Repeating inside the
same repeatable-read snapshot is expressly insufficient. A selected revoke
maps to `ACCESS_DENIED`; an addition/version/enrollment change without revoke
maps to `SCOPE_INCOMPLETE`. Refusals still carry no data-bearing fields.

I recomputed the current SPEC canonical UTF-8 universal-newline digest as
`db1d218083bfadac149f1c4415cfe0bc13213f41f33311a107447cad24abe7bf`;
the matrix's source pin matches it. I recomputed the matrix canonical digest
as `bca9bb9d5d201a6daeb05c58eb850dc53f27c3235a99cb71e15954bd1702273b`;
the static pin and DRAFT Work Order reference it. The registered family remains
one flat static receipt representation with a planned, unimplemented emitter.
The nested mutation exclusion remains bounded to that flat receipt; manifest
internals and real source behavior need later backend mutation evidence.
`python scripts/check_invariant_families.py` PASS. The two targeted existing
generic evidence paths returned 35 passed, 2 skipped on the revised matrix.
Core inheritance and session guards PASS; changed contract/family whitespace
check is clean. No raw SOURCE_READY/REFUSED emitter sample, source query,
transaction, operational coverage, provider call or database proof was
produced by these static checks.

The versioned fixture cohort and frozen numeric policy remain separate and
bound to source identity; SOURCE_READY remains only an internal attested
fixture input, not forecast readiness or production truth. The parent drift,
changed-cohort, scheduled-run, API and approval gates remain open. The DRAFT
Work Order grants no BUILD: exact native query/UOW paths, real emitter and
mutation binding, independent pre-loader oracle, complete gate graph, formal
review and separate effect admission are still required. The accepted prior
physical SQL ceiling stays spent. The complete G01–G14 owners/remainders in
the SPEC remain unchanged, P5-A/P5-A2 remain OPEN and Phase 5 stays 0/5.
Root may proceed with normal contract material and dedicated continuity for
this SPEC/static family only, then return to a separately reviewed bounded
source Work Order.
