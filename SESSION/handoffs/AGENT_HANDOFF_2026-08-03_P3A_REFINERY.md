# Agent Handoff — P3-A Refinery

## Disposition

- Tranche: `P3-A-REFINERY-2026-08-03`
- Parent: Project Knowledge Pack closure `107c8fa`
- Risk: `R2`
- Control-chain phase: `BUILD`
- Active role: `IMPLEMENTATION_WORKER`
- Status: `FRESH_R2_ACK_ACCEPTED_PREBUILD_CHECKPOINT_PENDING`
- INTAKE commit: `32cb7f233f40fcfb3736f0f26487a36231c7d24e`
- INTAKE review: `INTAKE_REVIEW_PASS` at `558b193`

## Current truth

`refinery-bridge` is contract-only. Its YAML omits roadmap-required quarantine,
provenance, data-quality and fallback results; submodules have no runtime code
or tests. `data_scope` is callable but has no runtime caller and does not verify
minimization evidence. The existing normalized fixture invents an unsupported
`11h40 → 23:40` conversion and is not golden truth.

## Intake boundary

P3-A may design only a deterministic local, fail-closed transformation boundary
that preserves source linkage, refuses ambiguity/fabrication, separates
sensitivity from topic classification, emits quarantine/data-quality receipts
and produces no context candidate on failure. It does not own confirmed truth,
raw persistence, external ingest, provider calls, retrieval/RAG, P3-B/P3-C,
learning or production behavior.

## Evidence boundary

No provider call is needed or authorized for INTAKE. Future deterministic local
claims may use contract/unit evidence. Any future claim about actual AI/provider
governance requires a separately approved real-provider call and sanitized
receipt under AGENTS.md.

## Design candidate

ADR `docs/decisions/ADR_2026-08-03_P3A_REFINERY.md` resolves the eight INTAKE
decisions with a pure local package, versioned text-field provenance, fixed
fail-closed stages, syntax-only normalization, caller-scoped advisory dedupe,
separate sensitivity/topic fields, versioned redaction, typed no-candidate
outcomes, strict 100/100 control-coverage admission and minimal
`ContextCandidateV1`. The current fixture remains a negative case.

## Retained DESIGN review

Independent review returned `REVIEW_FAIL`, no waiver:

- F1 dedupe tuple/window/collision mechanics underspecified;
- F2 quarantine/source ownership and no-sink semantics underspecified;
- F3 stage failure/quality/disposition mapping ambiguous;
- F4 candidate schema and digest preimage not reproducible.

The ADR repairs all four: fingerprints are SHA-256+SHA-512+length over bounded
scope/window records; quarantine has explicit distinct owners/route and closed
reasons; nine receipts plus precedence make candidate absence total; and
ContextCandidateV1 has an exact canonical JSON preimage/fingerprint.

Independent re-review returned `DESIGN_REVIEW_PASS`, no waiver, bound to ADR
SHA-256 `57ec06fc72e6ec2baad95079cdeff7eabfe7eb2837841dfc7c11cdba256e696e`.
Any ADR byte change requires fresh review.

## SPEC candidate

`docs/specs/P3A_REFINERY_SPEC.md` binds immutable parent ADR
`57ec06fc…e696e` and Amendment 1 `dc091f2b…f0e4a` into R1-R30 and AC-01 through
AC-12. It fixes the nine-stage order, three typed fingerprint preimages, closed
failure/disposition schemas, 100/100 control-coverage admission, deterministic
and disclosure properties, synthetic fixture matrix and zero-I/O claim boundary.

## Retained SPEC review and repair

Independent review of SPEC SHA-256 `3471bc9b…e8511` returned `REVIEW_FAIL`, no
waiver. F1 found wrong normative R-number references; F2 found the stage-reason
vocabulary open; F3 found orphan `NOT_RUN` was not rejected; F4 found the
dual-digest-equal/length-different collision case ambiguous.

The repaired candidate changes only those findings: fingerprint preimages now
bind R19/R23 and missing context binds R21; `StageReason` and permitted
stage/outcome pairs are closed; the receipt language is exactly `PASS^9` or
`PASS* FAIL NOT_RUN*`; and collision is unequal full triples with either digest
equal, with explicit acceptance vectors. The failed receipt remains immutable.

## Retained SPEC re-review

Independent re-review of repaired SPEC `f836f5d3…49ffc` closed F1-F4 exactly,
then returned `REVIEW_FAIL`, no waiver, for F5-F7. F5 shows an invalid or
disclosure-unsafe envelope cannot construct the parent-mandated non-null safe
provenance result without echoing or fabrication. F6 shows ready `UNIQUE` and
`REDACTED_TEXT_MATCH` outcomes have no typed public field. F7 shows ENVELOPE,
DEDUPE and CANDIDATE_ADMISSION receipt versions have no normative source.

Because F5 changes a parent DESIGN invariant, the tranche returns to DESIGN.
Amendment 2 must define a pre-admission rejection union branch, executed-stage
typed dedupe status, and one exact version source for every stage. The existing
SPEC is retained as a failed candidate and may change only after Amendment 2
receives independent review pass.

## Design Amendment 2 candidate

`docs/decisions/ADR_2026-08-03_P3A_REFINERY_AMENDMENT_2.md` resolves only
F5-F7. It makes the public output a closed union with a provenance-free,
disclosure-safe `PreAdmissionRejectionV1` for structurally unconstructible
input; adds typed `dedupe_status` with exact outcome/nullability rules; and maps
nine explicit control versions to the nine receipts. It also makes exact-source
matching a DEDUPE failure so duplicate disposition and later `NOT_RUN` receipts
are mechanically consistent. Parent candidate/dedupe preimages stay unchanged.

Independent review returned `DESIGN_AMENDMENT_REVIEW_PASS`, no waiver, bound to
Amendment 2 SHA-256 `393ca069c6ead96bfc7de52f453952cf12dcab1799fbbdccb5836668632291dc`.
F5-F7 are closed at DESIGN. Any byte change requires fresh DESIGN re-review.

## Repaired SPEC candidate

SPEC SHA-256 `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
retains F1-F4 and binds reviewed Amendment 2: structural invalid input returns
the exact provenance-free pre-admission branch; admitted fingerprint mismatch
uses safe locally recomputed provenance; `dedupe_status` is typed with
exact-source fail-stop semantics; and every receipt has one exact mapped
`control_version`. The fixture/acceptance matrix covers both union branches,
version substitution, public dedupe status and no-fabrication disclosure.

Fresh independent final review returned `SPEC_REVIEW_PASS`, no waiver, bound to
SPEC SHA-256 `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`.
F1-F7 and all R1-R30/AC-01..12 are closed. Any SPEC byte change requires fresh
review.

## Work Order candidate

`docs/work_orders/P3A_REFINERY_WORK_ORDER.md` SHA-256
`3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
authorizes exactly 26 mandatory BUILD paths only after independent authorization
review and fresh exact human R2 acknowledgment. BUILD has zero
provider/network/remote-ingest calls, stops at the first failed gate with no
retry, and cannot activate any runtime/later-lane claim.

Independent review returned `WORK_ORDER_AUTHORIZATION_REVIEW_PASS`, no waiver,
bound to Work Order `3a2bf12e…bcd3c5`. It confirms the 26-path split is
sufficient/non-expansive and the zero-call/no-retry boundary is executable. This
pass is not BUILD authority.

## Fresh human R2 acknowledgment

Accepted verbatim on 2026-08-03:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-2026-08-03, Work Order SHA-256
> 3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5,
> đúng 26 BUILD paths, zero provider/network/remote-ingest calls.

It binds exactly one invocation. Clean pushed authority baseline is
`72a712d51ad53c2de38f0784b257c42428f80738`; Work Order/SPEC hashes match and
the worktree was clean at acceptance. The acknowledgment is not consumed until
this four-path continuity checkpoint is committed/pushed and the first BUILD
path is changed. No retry, provider/network/remote-ingest call or expansion.

## Next governed move

Commit and push exactly this four-path acknowledgment checkpoint. Then consume
the accepted acknowledgment for one BUILD invocation changing exactly 26 paths.
Run gates in order, stop at the first failure and do not retry. Zero
provider/network/remote-ingest calls; no later-lane authority.
