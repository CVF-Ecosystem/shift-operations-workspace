# Agent Handoff — P3-A Refinery

## Disposition

- Tranche: `P3-A-REFINERY-2026-08-03`
- Parent: Project Knowledge Pack closure `107c8fa`
- Risk: `R2`
- Control-chain phase: `SPEC`
- Active role: `SPEC_AUTHOR`
- Status: `DESIGN_AMENDMENT_1_REVIEW_PASS_READY_FOR_SPEC`
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

## Next governed move

Review Design Amendment 1. It moves dedupe after redaction and separates exact
source, source-free dedupe-content and final-candidate fingerprints. Only a
pass returns to SPEC_AUTHOR. No WORK_ORDER, BUILD, provider call or later-queue
authority exists.

Independent review returned `DESIGN_AMENDMENT_REVIEW_PASS`, no waiver, bound to
parent ADR `57ec06fc…e696e` and Amendment 1 `dc091f2b…f0e4a`. SPEC authoring may
resume with the corrected nine-stage order; later authority remains absent.
