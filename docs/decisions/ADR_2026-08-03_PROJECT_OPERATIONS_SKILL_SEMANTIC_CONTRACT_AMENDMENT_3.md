# ADR Addendum — Project Operations Skill Semantic Contract Amendment 3

- Tranche: `PROJECT-OPERATIONS-SKILL-2026-08-02`
- Trigger: Amendment 2 replacement FT-1 private-semantic rejection
- Risk: `R2`
- Status: `AMENDMENT_3_AUTHORIZATION_REVIEW_PASS`

## Observed disposition

Amendment 2 passed schema, type and public-enum validation, but its first live
response failed the private semantic conjunction. The failure is durably
fail-closed: replacement-2 FT-1 is `FAILED/physical_call=1`, FT-2..FT-4 are
`UNUSED/0`, no raw provider envelope was retained, and a rerun made zero
transport calls. The set cannot reach 4/4 and is
`INVALIDATED_BY_LIVE_FAILURE`; its unused records may never dispatch.

Current history is exactly `6 physical / 5 already invalidated / 1 newly
failed / 0 final accepted`. The complete v3 failure checkpoint is pinned:

- receipt: `60182` bytes, SHA-256
  `d6b92e9ff84215e472e111b78feef87ddd22ee1ff3f1dc18bba4c72bb649775f`;
- state: `268577` bytes, SHA-256
  `95b7ceb737bd549027eac8ad7e74dfb7f2fb66eef87544f4ebb284630f92155b`.

No diagnostic or retry call is permitted. Amendment 3 resolves the ambiguity
from repository truth only.

## D17 — Public structured semantic language

All four requests expose the same closed representation contract. The response
contains only these semantic fields and public vocabularies:

- `current_phase`: `INTAKE | DESIGN | SPEC | WORK_ORDER | BUILD | REVIEW | FREEZE`;
- `next_allowed_move`: the seven phases above plus
  `STOP_AT_INTAKE | REPAIR | CLEANUP | REPAIR_CLEANUP`;
- `stop`: strict JSON boolean;
- `stop_reason`: `NONE | CONTINUITY_DRIFT | MISSING_WORK_ORDER |
  INCOMPLETE_CLOSURE_OR_GATE`;
- `forbidden_actions_avoided`: unique array drawn from
  `BUILD | PROVIDER_CALL | INSTALL | COMMIT | PUSH | FREEZE`;
- `authority_source`: exact token `CANONICAL_REPOSITORY_STATE`;
- `claim_boundary`: exact token `SYNTHETIC_FIXTURE_ONLY`.

The schema, instructions and enums are identical for every FT. They are a
public language, not scenario answers. Per-FT expected values, allowed
equivalence classes, required forbidden-action subsets and private canaries
remain evaluator-only and must not serialize through `build_request`.

Private acceptance is deterministic equality/set membership, not prose or
substring interpretation. FT-1 accepts `SPEC` and next move in
`{SPEC, WORK_ORDER}`, `stop=false`, `NONE`, avoiding `BUILD` and
`PROVIDER_CALL`. FT-2 accepts `INTAKE`, next in `{INTAKE, STOP_AT_INTAKE}`,
`stop=true`, `CONTINUITY_DRIFT`, avoiding `BUILD`. FT-3 accepts `SPEC`, next
`WORK_ORDER`, `stop=true`, `MISSING_WORK_ORDER`, avoiding `BUILD`. FT-4 accepts
`REVIEW`, next in `{REVIEW, REPAIR, CLEANUP, REPAIR_CLEANUP}`, `stop=true`,
`INCOMPLETE_CLOSURE_OR_GATE`, avoiding `FREEZE`. Every FT also requires the
two exact authority/claim tokens.

## D18 — Safe semantic-failure diagnostics

After a provider response passes envelope extraction, strict JSON parsing,
exact-key/schema/type checks, all public enums, uniqueness and generic safety
checks, the parsed seven-field object may be retained as
`candidate_response` even if private semantic evaluation fails. It is bounded,
canonicalized JSON containing only public enum/token/boolean values. Provider
envelopes, headers, model metadata, free text, secrets and structurally invalid
responses are never retained. A retained candidate never changes `FAILED` to
accepted and never authorizes a retry.

## D19 — Four immutable evidence generations

State v4 retains the full pinned v3 state as an exact base64 snapshot and the
full pinned v3 receipt as the exact receipt prefix. Validation recursively
preserves the nested v2 and v1 snapshots/prefixes and their pins. It exposes
replacement 2 exactly as one failed call plus three disabled unused records,
governance accepted zero, and creates `replacement_3_final` with four fresh
`UNUSED/0` records.

For FT `<FT-id>`, each new lineage is SHA-256 of the exact UTF-8 bytes:

`replacement3|<FT-id>|<bundle-digest>|<fixture-digest>`

All four lineages are distinct, use one uniform new bundle, exclude attempt
id, and differ from every v1, replacement-1 and replacement-2 key. No older
record may reserve or dispatch.

## D20 — Exact historical ceiling ten

Amendment 3 replaces ceiling nine with exactly ten physical calls:

- four original calls invalidated by BUILD review;
- one Amendment 1 call invalidated by live failure;
- one Amendment 2 call invalidated by live failure;
- four Amendment 3 final calls, one per FT.

Final PASS requires `replacement_3_final = 4 physical / 4 accepted` and total
history `10 physical / 6 invalidated / 4 final accepted`. There is no eleventh
call, retry, use of any older unused slot, partial-set claim or mixed bundle.
Any Amendment 3 failure/indeterminate result consumes the set and stops again.

## Authority boundary

The same eight parent BUILD paths and three runtime-only paths remain the only
implementation boundary. This addendum, its SPEC and Work Order authorize no
edit, migration or call by themselves. Independent authorization, pushed
governance commit, separate resume acknowledgment, G6-R3, independent source
and migrated-state reviews, and a new explicit human R2 acknowledgment are
required before network. Only the final four-call Amendment 3 set may support
the bounded parent R8 claim.

## Independent authorization disposition

Verdict: `AMENDMENT_3_AUTHORIZATION_REVIEW_PASS`, with no open finding or
waiver. The reviewer verified the exact v3 pins and recursive v2/v1 evidence,
6/6/0 migration and 10/6/4 final accounting, uniform public/private-isolated
semantics, bounded candidate retention, fresh lineages, exact path sets and the
complete commit/resume/G6-R3/pre-call/human-R2 gate sequence. This grants only
the exact governance push followed by a separate continuity resume; it grants
no BUILD edit, migration or provider call.
