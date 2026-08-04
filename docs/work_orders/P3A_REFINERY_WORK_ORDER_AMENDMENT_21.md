# Work Order Amendment 21 — Corrected Acknowledgment Lineage and Exact-Two LF Normalization

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-21-2026-08-04`
- Consumed A20 SHA-256: `58b576d779dec3e3b1a934f24f2b90e4b18910d5594c383c20f4eb8d3d6a38d4`
- A20 authorization review SHA-256: `8711138128b52140c79c9f3fc2107bad95ec046b9cc345257c4be028ff6dfbc4`
- A20 authority / R2 acknowledgment checkpoints: `227a385045bc7a8db0a67d9a5e26cbce27d8ccf6` / `d5e4a7bb6a5f96933be28260384fec5e544c0bc5`
- Risk / phase: `R2 / WORK_ORDER`
- Status: `PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Calls: `0 provider / 0 network / 0 remote-ingest`

## Trigger and retained stop truth

A20 acknowledgment checkpoint was pushed. Its invocation passed the two Git
lineage commands, then stopped at the first Python preflight assertion before
normalization because the orchestration compared current HEAD to the mistyped
literal `d5e4a7b78d56713acde35ba33a562da1d72d274e`; pushed HEAD and
`origin/main` are actually `d5e4a7bb6a5f96933be28260384fec5e544c0bc5`.
No repair path was touched, no later preflight assertion or gate ran, and no
retry, provider, network or remote-ingest call occurred. A20 and its R2 are
consumed. This amendment corrects only that orchestration binding.

The two catalog files remain byte-for-byte at their A20 pre-state and
`knowledge/manifest.json` remains final. The dirty candidate remains exact 32
paths with staged zero and no BUILD commit, REVIEW_PASS or FREEZE.

## Exact retained bindings

Using ordinal case-sensitive records
`path + NUL + lowercase_file_sha256 + LF`:

- exact dirty paths: `32`;
- stable30 manifest: `f9bcbbc6e0bed42283c7aad994f6b1563311bcb216954e80c81016ad8734e056`;
- exact repair paths: `2`;
- protected28 manifest: `0b87e6d8eec3d551d1106d1a5475bc45d845ecd0c39f9807786c5632e5f4e09e`;
- staged paths: `0`.

| Path | Pre SHA-256 | CRLF / lone LF | Required LF SHA-256 |
|---|---|---:|---|
| `docs/catalog/MODULE_REGISTRY.json` | `9447544840c4f526d1d39769b63b84c4223ce689e2061e36a9416f9a4a741013` | `626 / 0` | `1c1463d992a8ffe362059db3efded0a7a90664aebdbcec06bb9b13b922b7d727` |
| `docs/catalog/MODULE_CATALOG.md` | `49a082972cbd4955e5932ed39f90390cb3bf281ca34dbe5a988498d2f9aaf995` | `324 / 0` | `32fe4ecbb7f7b493ba1536975d81aa95a895ca1424309dd580f232b8ee1bb484` |

`knowledge/manifest.json` is immutable at
`cbf115da32e5ad9418f1d91678d2ec2f875e174ee434f5762648325f63da4f80`;
the generator is immutable at
`fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b`.
All retained A18 output/archive/suffix/link/line bindings remain mandatory.

## Exact repair ceiling and payload

Only these already-dirty paths may change:

1. `docs/catalog/MODULE_REGISTRY.json`;
2. `docs/catalog/MODULE_CATALOG.md`.

The exact binary payload from A20 is retained unchanged: first read and verify
both raw hashes and newline inventories; only after both pass, replace CRLF
with LF in memory and use `Path.write_bytes()` on the two paths. No generator,
text-mode write, formatter, `apply_patch`, manifest or other edit is permitted.

## Corrected preflight lineage

The fresh invocation must verify dynamically:

```text
HEAD == origin/main
HEAD^ == the A21 authority checkpoint recorded in committed canonical state
HEAD changes exactly the four acknowledgment continuity paths from HEAD^
git show HEAD:SESSION/ACTIVE_SESSION_STATE.json records the exact fresh A21 R2,
freshR2Accepted=true, invocationConsumed=false and PENDING_COMMIT_PUSH
```

The invocation must not expect the acknowledgment commit to contain its own
hash. It must not guess or embed a future full commit literal. The dynamic
topology and exact committed canonical content above prove that the pushed
HEAD is the one bounded acknowledgment checkpoint whose direct parent is the
reviewed authority checkpoint.

## One ordered continuation

Run once, stop at the first non-zero command or contract failure, no retry:

1. verify pushed A21 authority/R2 lineage by dynamic HEAD/origin/parent/change-
   set topology plus exact committed R2/state content, bound A21/review hashes,
   staged zero, exact32/stable30/protected28, exact-two raw hashes/counts,
   immutable manifest/generator and retained A18 bindings;
2. run the retained exact binary normalization payload once;
3. assert exact-two LF hashes, zero CR, immutable manifest, exact32,
   protected28 and staged zero;
4. run the project Knowledge validator once;
5. run the two-file focused Knowledge Pack suite once;
6. run catalog `--check` once;
7. run full non-live `pytest -q` once;
8. run session/repository/JSON/YAML/Refinery-contract/import-I/O/secret/diff
   gates once;
9. run the complete final exact32/exact2/protected28/posthash/manifest/archive/
   suffix/link/line/staged audit once.

Retain without rerun A18 probe `4/4`, Refinery `57`, pre-repair Knowledge
validator/`86` and file-size PASS. Do not retry or relabel the A20 preflight
failure.

## Stop and claim boundary

No provider/network/remote-ingest/POST call, retry, alternate payload, helper,
BUILD commit, self-review, FREEZE, waiver, debt or later-lane expansion is
authorized. PASS yields only an exact32 dirty local candidate pending fresh
independent BUILD review.

Independent authorization review, a bounded authority checkpoint and fresh
exact human R2 naming this Amendment SHA, exactly two repair paths, final
exact32 and zero provider/network/remote-ingest calls are mandatory first.
