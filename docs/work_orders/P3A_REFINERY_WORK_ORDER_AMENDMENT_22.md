# Work Order Amendment 22 — ASCII-Safe R2 Binding and Exact-Two LF Normalization

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-22-2026-08-04`
- Consumed A21 SHA-256: `f6fa72b3a8e7a19654c6181242b2b2a7bb5ce20523d9913a84f38094afa4040c`
- A21 final authorization review SHA-256: `98874fb2829b7109199f94b006a2c2ae4a39a5b8a4a1febd8ad83cbbc4453abe`
- A21 authority / R2 acknowledgment checkpoints: `e78317f0eddf9a20a476cd6520b411d7dd81ab32` / `7daf89e7d3637c1268074f6a941bee7066863cad`
- Risk / phase: `R2 / WORK_ORDER`
- Status: `PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Calls: `0 provider / 0 network / 0 remote-ingest`

## Trigger and retained stop truth

A21 dynamic Git topology passed through committed fresh-R2 status. The next
Python assertion compared the committed Vietnamese acknowledgment with a
non-ASCII literal transported through a PowerShell-to-Python stdin boundary
and returned false. Execution stopped before exact-two normalization; all
later assertions and gates were `NOT_RUN`. No repair touch, retry, provider,
network or remote-ingest call occurred. A21 and its R2 are consumed.

Read-only diagnosis confirms the canonical acknowledgment is correct and its
UTF-8 SHA-256 is
`5a42f8d4b957617424e0bba693c9f5f31aa3b99f9711824a74f1525b9f7e1bf4`.
A22 changes only that runner binding: it hashes the value parsed from committed
JSON and compares the lowercase ASCII digest. It embeds no non-ASCII expected
literal in the invocation.

## Retained scope and byte bindings

- exact dirty paths: `32`;
- stable30 manifest: `f9bcbbc6e0bed42283c7aad994f6b1563311bcb216954e80c81016ad8734e056`;
- exact repair paths: `2`;
- protected28 manifest: `0b87e6d8eec3d551d1106d1a5475bc45d845ecd0c39f9807786c5632e5f4e09e`;
- staged paths: `0`.

| Path | Pre SHA-256 | CRLF / lone LF | Required LF SHA-256 |
|---|---|---:|---|
| `docs/catalog/MODULE_REGISTRY.json` | `9447544840c4f526d1d39769b63b84c4223ce689e2061e36a9416f9a4a741013` | `626 / 0` | `1c1463d992a8ffe362059db3efded0a7a90664aebdbcec06bb9b13b922b7d727` |
| `docs/catalog/MODULE_CATALOG.md` | `49a082972cbd4955e5932ed39f90390cb3bf281ca34dbe5a988498d2f9aaf995` | `324 / 0` | `32fe4ecbb7f7b493ba1536975d81aa95a895ca1424309dd580f232b8ee1bb484` |

`knowledge/manifest.json` remains immutable at
`cbf115da32e5ad9418f1d91678d2ec2f875e174ee434f5762648325f63da4f80`;
generator SHA remains
`fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b`.
All A18 output/archive/suffix/link/line bindings remain mandatory.

## Exact repair and preflight correction

Only `docs/catalog/MODULE_REGISTRY.json` and
`docs/catalog/MODULE_CATALOG.md` may change. Retain A21's reviewed all-reads-
before-any-write binary CRLF-to-LF payload unchanged.

Retain A21's dynamic topology checks: `HEAD == origin/main`; committed
`freshR2Accepted=true`, `invocationConsumed=false`, `PENDING_COMMIT_PUSH`;
`HEAD^` equals committed `authorityCheckpointCommit`; and HEAD changes exactly
the four acknowledgment continuity paths. Replace only the direct Unicode
equality assertion with:

```python
assert hashlib.sha256(
    auth["freshR2Acknowledgment"].encode("utf-8")
).hexdigest() == "<reviewed A22 acknowledgment UTF-8 SHA-256>"
```

The placeholder is filled in canonical state and the invocation only after
fresh A22 R2 is received; the review must predefine how that digest is computed
from the exact required acknowledgment template plus final A22 Work Order SHA.
No Unicode acknowledgment literal may cross the PowerShell stdin boundary.

## One ordered continuation

Run once, stop first non-zero/contract failure, no retry:

1. verify dynamic pushed A22 authority/R2 topology, ASCII digest of committed
   acknowledgment, bound artifacts, staged0, exact32/stable30/protected28,
   exact-two raw counts/hashes, immutable and retained bindings;
2. run the retained exact-two binary normalization once;
3. assert required LF hashes, zero CR, immutable manifest, exact32/protected28;
4. project Knowledge validator once;
5. two-file focused Knowledge Pack suite once;
6. catalog `--check` once;
7. full non-live `pytest -q` once;
8. session/repository/JSON/YAML/contract/import-I/O/secret/diff gates once;
9. complete final exact32/exact2/protected28/posthash/continuity audit once.

Retain without rerun A18 probe `4/4`, Refinery `57`, pre-repair Knowledge
validator/`86` and file-size PASS. Do not retry or relabel A21.

No provider/network/remote-ingest/POST call, alternate payload, helper, BUILD
commit, self-review, FREEZE, waiver, debt or later-lane expansion is authorized.
Independent review, authority checkpoint and fresh exact A22 R2 are mandatory.
