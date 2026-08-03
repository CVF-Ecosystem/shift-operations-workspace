# PROJECT-OPERATIONS-SKILL SPEC Amendment 1

- Parent: `PROJECT_OPERATIONS_SKILL_SPEC.md`
- Trigger: `POS-BUILD-REV-F1..F5`
- Status: `INDEPENDENT_AUTHORIZATION_RE_REVIEW_PASS`

All parent requirements remain in force except where this amendment explicitly
replaces the original single-set evidence model.

## A1. Public-input contract

For each FT, define `PUBLIC_FIXTURE` with exactly `scenario_id`, `situation`,
synthetic facts and `user_request`. It contains no `expected` or target key.
The request also includes the skill and a neutral schema of field names/types
only. Private `EXPECTATIONS` exist only in evaluator source; `build_request`
accepts no expectation argument and has no expectation reference/access path.
Structural tests inject unique private canary keys/values and prove no canary
serializes, and reject instructions prescribing phase/next/stop/forbidden-
action/authority/claim answers. Coincidental public-fact literals are allowed.

## A2. Strict response contract

Before semantics, enforce exact keys and types: `scenario_id`, `phase`,
`next_allowed_move`, `stop_reason`, `authority_source`, `claim_boundary` are
`str`; `stop` is exact `bool`; `forbidden_actions_avoided` is `list[str]` with
no subclass/coercion. Then compare private semantic expectations.

## A3. State machine and integrity

Each replacement record transitions:

`UNUSED -> RESERVED -> DISPATCHED -> ACCEPTED | FAILED | INDETERMINATE`.

`DISPATCHED` plus `physical_call=1` is atomically durable under the stable lock
before transport. Any post-dispatch interruption consumes the lineage and
blocks rerun. State validation requires exact schemas/types and status-specific
mandatory/forbidden fields, recomputed replacement lineage, exact public
fixture and bundle digests, no fifth/missing FT, and receipt coherence.

Original records are immutable and explicitly invalidated. Replacement lineage
is SHA-256 of `replacement` + FT id + repaired bundle digest + public fixture
digest. Every replacement record uses one uniform repaired bundle digest.

## A4. Evidence accounting

The receipt and state must show separately:

- original: `physical=4`, `mechanically_accepted=4`,
  `governance_accepted=0`, `INVALIDATED_BY_REVIEW_FAIL`;
- replacement: final PASS only at `physical=4`, `accepted=4`;
- history: final exact `physical=8`, `invalidated=4`, `accepted=4`, no extra.

Before migration, receipt/state must match the ADR-pinned hash and size. The
receipt preserves the original bytes as an exact prefix. Migrated state embeds
the original raw JSON bytes as base64 with pinned hash/length; decoding must
reconstruct the original file byte-for-byte. It also exposes a separately
validated `original_invalidated` semantic set. Replacement evidence appends
without changing the embedded snapshot or receipt prefix.

## A5. Required non-network proof

Add tests for:

1. no private canary/key/access path or answer-prescribing instruction in any
   serialized request, while coincidental public literals remain permitted;
2. bool/int and all wrong-type response variants;
3. subprocess crash at pre-dispatch, post-dispatch/pre-return and
   post-return/pre-finish with correct durable physical accounting;
4. mutation matrix for top-level/record schemas, lineage, fixture, bundle,
   status/reset, attempt, request, model, endpoint, response/error, physical
   count, fifth/missing record, mixed digest and receipt mismatch;
5. missing key, bad base, model failure, validator/test preflight failure,
   secret-like public fixture and runtime residue, all at zero call/mutation;
6. pinned original hash/length, exact receipt prefix and decoded state snapshot
   byte equality; no replacement retry/ninth call; uniform replacement bundle
   and exact historical aggregation.

## A6. Replacement live acceptance

Only after all amended focused/full/repository/doctor gates pass may exactly
four replacement calls run, one per FT, with fresh contexts and durable
dispatch. A failure or indeterminate replacement stops with no retry. Final
independent review must evaluate response behavior without another call.

## Amended acceptance criteria

- `AC-A1`: all F1 answer-leak scans and independent prompt inspection PASS.
- `AC-A2`: dispatch/crash physical accounting and no-retry probes PASS.
- `AC-A3`: complete state/receipt mutation matrix fails closed at zero call.
- `AC-A4`: strict type matrix PASS.
- `AC-A5`: complete preflight zero-call matrix PASS.
- `AC-A6`: original evidence remains intact and invalidated.
- `AC-A7`: replacement evidence is exactly 4/4; history exactly 8/4/4.
- `AC-A8`: all parent non-live/repository/rollback gates and independent
  re-review PASS without waiver.

No replacement-call authority exists from this SPEC alone.
