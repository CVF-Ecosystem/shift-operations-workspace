# ADR Addendum — Project Operations Skill BUILD Review Repair

- Tranche: `PROJECT-OPERATIONS-SKILL-2026-08-02`
- Trigger: independent BUILD `REVIEW_CHANGES_REQUIRED`
- Risk: `R2`
- Status: `INDEPENDENT_AUTHORIZATION_RE_REVIEW_PASS`

## Disposition of retained evidence

Bundle `a5ac9cc568ca599207203c18f9f663e70deee373c86a80284e95c868a2a04326`
made exactly four physical calls and obtained four responses that passed the
original mechanical evaluator. It is now `INVALIDATED_BY_REVIEW_FAIL`: the
requests disclosed private expected answers, so governance-accepted behavior
evidence is zero. Its state and receipt remain immutable historical evidence;
they must not be deleted, reset, overwritten, relabeled PASS, or counted in a
final skill-behavior claim.

## Accepted findings

1. `POS-BUILD-REV-F1` — public requests leaked the evaluator answers.
2. `POS-BUILD-REV-F2` — a hard interruption after dispatch could leave
   physical-call accounting at zero.
3. `POS-BUILD-REV-F3` — retained state did not validate exact record schema,
   recomputed lineage, transitions, and receipt coherence.
4. `POS-BUILD-REV-F4` — Python equality admitted integer substitutes for
   booleans.
5. `POS-BUILD-REV-F5` — required zero-call preflight matrix was incomplete.

All are accepted without waiver.

## Repair decisions

### D8 — Separate public fixture from private evaluator

Provider input contains only `PUBLIC_FIXTURE`, the skill, neutral field/type
schema and a neutral instruction to decide from the skill. `build_request` has
no parameter, reference or access path to private `EXPECTATIONS`. Tests inject
unique per-FT canary keys/values only into private expectations and prove they
never serialize; they also ban `expected`/target keys and instructions that
prescribe phase/next/stop/forbidden-list/authority/claim answers. Coincidental
literals independently present as public facts remain allowed. A provider
response is judged only after return.

### D9 — Dispatch is the conservative physical boundary

Under the stable lock, immediately before transport, durably transition
`RESERVED -> DISPATCHED` with `physical_call=1`. Only `RESERVED` may dispatch.
A crash after `DISPATCHED` is consumed/indeterminate and can never retry; a
crash before dispatch remains physical zero. Subprocess crash probes cover
pre-dispatch, post-dispatch/pre-return and post-return/pre-finish.

### D10 — Exact retained-state and receipt integrity

State loading validates exact top-level and status-specific schemas, types,
four FT identities, public fixture digests, recomputed lineages, bundle/set
identity, attempt/request/model/safe-endpoint fields, physical counts and
response/error exclusivity. If a receipt exists, its machine-readable summary
must agree with state. Any unknown, missing, fifth, reset-shaped, mixed or
tampered value fails before network.

### D11 — Strict JSON types

`stop` requires `type(value) is bool`; every other scalar field is exact
`str`; forbidden actions are exactly `list[str]` before semantic comparison.
Integers never substitute for booleans.

### D12 — Complete zero-call preflight proof

Tests cover missing credentials, bad base URL, model selection failure,
skill-creator/contract preflight failure, secret-like public fixture, runtime
residue and state/receipt tampering. Every case proves zero reservation/state
mutation, zero transport calls, safe output and zero new runtime residue.

### D13 — Immutable original set plus one replacement set

The original untracked artifacts are pinned before repair:

- receipt: SHA-256 `d21d64467538fee3a8a2608c8b0907975cab523ce4075637322c400ebc233b9e`,
  `39659` bytes;
- state: SHA-256 `e94534b121bdc937d1cb695663d6e1eb3366e6ec0fae41d43ed4a14d072342d5`,
  `42044` bytes.

G6-R fails if either differs. The migrated receipt retains the exact original
bytes as its prefix and only appends invalidation/replacement evidence. Because
JSON cannot retain a byte prefix while remaining one document, migrated state
stores an exact base64 snapshot of all original state bytes plus pinned hash
and length; tests decode and byte-compare it before validating the new schema.

The new state schema retains two evidence sets per FT:

- `original_invalidated`: immutable old bundle, four consumed physical calls,
  disposition `INVALIDATED_BY_REVIEW_FAIL`;
- `replacement_final`: one new lineage per FT bound to the repaired six-path
  bundle and public fixture digest.

No mixed bundle within a set is allowed. Each replacement FT gets exactly one
physical slot and no retry. Historical ceiling is exactly eight physical calls
total: four retained invalidated plus at most four replacement. Final closure
requires replacement `4 physical / 4 accepted`, while historical accounting
must state `8 physical / 4 invalidated / 4 final accepted`. No ninth call.

## Scope and claim boundary

Repair changes the same eight BUILD paths only; no ninth final path or new
runtime artifact is authorized. The final claim remains the original SPEC R8
boundary but may cite only the replacement set. Installation, commit, push,
self-review, FREEZE and later queue work remain separately controlled.

No repair or replacement provider call begins until this addendum, SPEC
Amendment 1 and Work Order Amendment 1 receive independent authorization,
are pushed, and a separate repair-resume acknowledgment plus G6-R pass.

## Independent authorization disposition

Verdict: `AMENDMENT_1_AUTHORIZATION_RE_REVIEW_PASS`, no open finding or
waiver. Initial review's three findings were closed by structural private-
canary noninterference, exact original hash/size plus prefix/base64-snapshot
preservation, and corrected dependency ordering. This verdict authorizes only
the pushed amendment -> separate resume -> G6-R sequence.
