# Work Order Amendment 20 — Exact-Two Catalog LF Normalization

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-20-2026-08-04`
- Consumed A19 SHA-256: `3b78afc6492c19de192cae4f86ac0cda2234055f2e984b523a100e2b5ace11f7`
- A19 authorization review SHA-256: `329c345464120bd8bf6e02a7f9427f3279949831d06a56963f27f27fbde5276d`
- A19 authority / R2 acknowledgment checkpoints: `e802d1ba8dab5452383ff7bffa50b8f0de9ea9f6` / `f3539a9da41c565f4163f3c9d14aab42fb7bbdfa`
- Risk / phase: `R2 / WORK_ORDER`
- Status: `PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Calls: `0 provider / 0 network / 0 remote-ingest`

## Trigger and retained stop truth

A19 preflight passed. Its frozen generator-function payload wrote the registry
and catalog, and its fixed one-line knowledge-manifest pin patch completed.
The first post-repair hash assertion then failed, so execution stopped with no
retry. The Knowledge validator, focused Knowledge Pack suite, catalog check,
full suite and later gates were `NOT_RUN`. No provider, network or remote-ingest
call occurred. A19 and its fresh R2 are consumed.

Read-only diagnosis established that both generated catalog files have exactly
the reviewed semantic bytes except that Windows text output translated every
LF to CRLF. Normalizing CRLF to LF reproduces both A19 expected hashes exactly.
`knowledge/manifest.json` already has the final expected LF bytes and must not
change. The retained candidate remains exact 32 dirty paths, with no BUILD
commit, REVIEW_PASS, FREEZE or later-lane authority.

## Exact retained candidate binding

Using ordinal case-sensitive path sorting and UTF-8 records
`path + NUL + lowercase_file_sha256 + LF`:

- exact dirty paths: `32`;
- stable paths excluding the two volatile continuity front doors: `30`;
- stable-30 manifest SHA-256: `f9bcbbc6e0bed42283c7aad994f6b1563311bcb216954e80c81016ad8734e056`;
- protected paths excluding the exact-two repair ceiling from stable30: `28`;
- protected-28 manifest SHA-256: `0b87e6d8eec3d551d1106d1a5475bc45d845ecd0c39f9807786c5632e5f4e09e`;
- staged path count: `0`.

The exact-two byte bindings are:

| Path | Pre-repair SHA-256 | CRLF / lone LF | Required LF SHA-256 |
|---|---|---:|---|
| `docs/catalog/MODULE_REGISTRY.json` | `9447544840c4f526d1d39769b63b84c4223ce689e2061e36a9416f9a4a741013` | `626 / 0` | `1c1463d992a8ffe362059db3efded0a7a90664aebdbcec06bb9b13b922b7d727` |
| `docs/catalog/MODULE_CATALOG.md` | `49a082972cbd4955e5932ed39f90390cb3bf281ca34dbe5a988498d2f9aaf995` | `324 / 0` | `32fe4ecbb7f7b493ba1536975d81aa95a895ca1424309dd580f232b8ee1bb484` |

`knowledge/manifest.json` is immutable at SHA-256
`cbf115da32e5ad9418f1d91678d2ec2f875e174ee434f5762648325f63da4f80`.
The generator is immutable at SHA-256
`fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b`.
All A18 repair-output, archive, suffix, link and line-count bindings retained
by A19 remain binding.

## Exact repair ceiling — two paths

Only these already-dirty paths may change:

1. `docs/catalog/MODULE_REGISTRY.json`;
2. `docs/catalog/MODULE_CATALOG.md`.

No other path may change. In particular, `knowledge/manifest.json`, source,
tests, status, continuity archives, contracts, fixtures and generator source
are immutable. Final dirty scope remains exact 32.

## Deterministic binary normalization

After preflight, run exactly one binary normalization payload. It must verify
both pre-hashes and exact newline counts before either write, then replace only
`CRLF` with `LF` and write bytes directly so host newline translation cannot
occur:

```powershell
@'
import hashlib
from pathlib import Path
items = {
    'docs/catalog/MODULE_REGISTRY.json': ('9447544840c4f526d1d39769b63b84c4223ce689e2061e36a9416f9a4a741013', 626),
    'docs/catalog/MODULE_CATALOG.md': ('49a082972cbd4955e5932ed39f90390cb3bf281ca34dbe5a988498d2f9aaf995', 324),
}
loaded = {}
for name, (expected, count) in items.items():
    data = Path(name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == expected
    assert data.count(b'\r\n') == count
    assert data.count(b'\n') == count
    assert data.count(b'\r') == count
    loaded[name] = data.replace(b'\r\n', b'\n')
for name, data in loaded.items():
    Path(name).write_bytes(data)
'@ | python -
```

No generator write, text-mode write, `apply_patch`, formatter or manifest edit
is permitted in the repair payload.

## One ordered continuation

Run once, stop at the first non-zero command or contract failure, no retry:

1. verify pushed A20 authority/R2 lineage, bound A20/review hashes, empty staged
   set, exact32/stable30/protected28, exact-two pre-hashes/newline counts,
   immutable manifest/generator and retained A18 archive/suffix/link/line/output
   bindings;
2. run the exact binary normalization payload once;
3. assert exact-two required LF hashes, zero CR bytes, immutable manifest,
   exact32, protected28 and staged zero;
4. run `python scripts/check_project_knowledge.py` once;
5. run the two-file focused Knowledge Pack suite once;
6. run `python scripts/generate_catalog.py --check` once;
7. run `python -m pytest -q` once;
8. run session-state, repository validator, JSON/YAML, Refinery contract,
   forbidden import/I/O, secret and `git diff --check` gates once;
9. run the final exact32/exact2/protected28/post-hash/manifest/archive/suffix/
   link/line/staged audit once.

Retain without rerun: A18 probe `4/4`, Refinery `57`, pre-repair Knowledge
validator/`86`, and file-size PASS. The A19 failed post-hash assertion is not
retried or relabeled; A20 performs a new post-normalization assertion.

## Stop and claim boundary

No provider/network/remote-ingest/POST call, retry, alternate normalization,
new helper, BUILD commit, self-review, FREEZE, waiver, debt or later-lane
expansion is authorized. PASS yields only a dirty exact32 local candidate
pending fresh independent BUILD review.

Independent authorization review, a bounded partially staged authority
checkpoint, and fresh exact human R2 naming this Amendment SHA, exactly two
repair paths, final exact32 and zero provider/network/remote-ingest calls are
mandatory before continuation.
