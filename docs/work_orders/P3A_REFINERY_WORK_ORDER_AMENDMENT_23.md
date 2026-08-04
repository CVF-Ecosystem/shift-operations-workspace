# Work Order Amendment 23 — Adequate Runner Ceiling and Exact-Two LF Normalization

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-23-2026-08-04`
- Consumed A22 SHA-256: `59ba66ea9bb48032f50a910f3919fe20cd373123e6de22543bb33ef2d7315e3e`
- A22 review SHA-256: `8da89d4f56c1233fdd231082b4463645da61732977516848364080e959eb4dff`
- A22 authority / R2 acknowledgment checkpoints: `b226ac7d3df6a9bf9fab3a6496960d4ed3accd3a` / `e3da80bcc32b8218b6e867d89d60ed2e1a53b1d1`
- Risk / phase: `R2 / WORK_ORDER`
- Status: `PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Calls: `0 provider / 0 network / 0 remote-ingest`

## Trigger and retained truth

A22 was launched as one outer runner with a 120-second ceiling. The process
exceeded that ceiling while pytest warnings were being emitted; the runner was
terminated with exit `124` and stdout flush raised `OSError 22`. No conclusive
per-step PASS transcript survived. Read-only post-stop inspection found no
pytest process and found both exact-two files still at their original CRLF
pre-hashes. Therefore no A22 repair or gate result is retained or relabeled.
No retry, provider, network or remote-ingest call occurred. A22/R2 are consumed.

A23 changes only execution infrastructure: the one outer invocation must have
a minimum 600-second command timeout and `PYTHONUNBUFFERED=1`. Stop-first and
no-retry semantics remain unchanged.

## Retained exact bindings

- exact dirty paths: `32`;
- stable30 manifest: `f9bcbbc6e0bed42283c7aad994f6b1563311bcb216954e80c81016ad8734e056`;
- exact repair paths: `2`;
- protected28 manifest: `0b87e6d8eec3d551d1106d1a5475bc45d845ecd0c39f9807786c5632e5f4e09e`;
- staged paths: `0`.

| Path | Pre SHA-256 | CRLF / lone LF | Required LF SHA-256 |
|---|---|---:|---|
| `docs/catalog/MODULE_REGISTRY.json` | `9447544840c4f526d1d39769b63b84c4223ce689e2061e36a9416f9a4a741013` | `626 / 0` | `1c1463d992a8ffe362059db3efded0a7a90664aebdbcec06bb9b13b922b7d727` |
| `docs/catalog/MODULE_CATALOG.md` | `49a082972cbd4955e5932ed39f90390cb3bf281ca34dbe5a988498d2f9aaf995` | `324 / 0` | `32fe4ecbb7f7b493ba1536975d81aa95a895ca1424309dd580f232b8ee1bb484` |

Manifest stays immutable at `cbf115da32e5ad9418f1d91678d2ec2f875e174ee434f5762648325f63da4f80`;
generator stays immutable at `fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b`.
All A18 output/archive/suffix/link/line bindings remain mandatory.

## Exact execution contract

Only the two catalog paths above may change. Retain unchanged:

- A22 dynamic HEAD/origin/parent/exact-four acknowledgment topology;
- committed R2 comparison via ASCII UTF-8 digest only;
- all-reads-before-any-write binary CRLF-to-LF payload;
- immediate posthash/exact32/protected28 checks;
- ordered Knowledge, focused, catalog, full and remaining gates;
- final complete audit.

The outer runner must set `PYTHONUNBUFFERED=1`, expose step markers, and use a
timeout of at least 600 seconds. The full non-live suite is not retried under
A22; A23 runs a new full suite only after fresh A23 authority.

## One ordered invocation

Run once, stop at first non-zero/contract failure, no retry:

1. dynamic pushed A23 topology, ASCII R2 digest, artifacts, staged0,
   exact32/stable30/protected28, exact-two raw and immutable bindings;
2. exact-two binary LF normalization once;
3. posthash/zero-CR/manifest/exact32/protected28 audit;
4. project Knowledge validator once;
5. two-file focused Knowledge Pack suite once;
6. catalog `--check` once;
7. full non-live `pytest -q` once;
8. session/repository/JSON/YAML/contract/import-I/O/secret/diff gates once;
9. final complete exact32/exact2/protected28/continuity audit once.

No provider/network/remote-ingest/POST call, alternate payload, helper, BUILD
commit, self-review, FREEZE, waiver, debt or later-lane expansion is authorized.
Independent review, authority checkpoint and fresh exact A23 R2 are mandatory.
