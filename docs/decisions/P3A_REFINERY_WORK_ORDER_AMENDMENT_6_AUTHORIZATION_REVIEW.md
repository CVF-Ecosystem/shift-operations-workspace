# P3-A Refinery Work Order Amendment 6 — Independent Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Amendment 6 SHA-256: `57c8322d82126b4202bbbe5bbbd6df6b3a3aae27ba5a28e1e67b8e6832fe4317`
- Consumed Amendment 5 SHA-256: `44c2576895356e8cb83a7df1d99c945e3a5a354a11e7655521e5288e54e07726`
- Amendment 5 authorization review SHA-256: `3b5d9a01b6c96f8f84f5010d583c0f36433bd8ffba51ff1a50a5e312e96fd7f8`
- Corrected BUILD review SHA-256: `ccc6c4c25fc00000be34d443ffdb4d59c665f1436641e3f89b06b4906480b405`
- SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- Amendment 5 acknowledgment checkpoint: `0e809031f69ef497e8bfc411c5ce0ed0b37e7871`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 6 truthfully binds the retained post-source/test candidate, keeps all
completed source/test work immutable, authorizes exactly the three remaining
catalog/knowledge surfaces, supplies the missing probe import environment, and
orders only the unrun gates. It is sufficient and non-expansive for the
remaining F2-F6 verification and catalog correction. There are no open
authorization findings and no waiver.

This PASS does not itself authorize the continuation. The reviewed authority
checkpoint must be committed/pushed and followed by Amendment 6's fresh exact
human R2 acknowledgment before one no-retry invocation may begin.

## Consumed Amendment 5 truth

Independent repository and continuity checks establish:

- `HEAD == origin/main == 0e809031f69ef497e8bfc411c5ce0ed0b37e7871`;
- that commit is the pushed Amendment 5 R2 acknowledgment checkpoint;
- Amendment 5 preflight passed;
- the authorized source/test repair completed;
- the focused Refinery command ran exactly once and passed `53` tests;
- the immediately following stdin probe stopped before every probe case with
  `ModuleNotFoundError: refinery_bridge`, because plain `python -` did not
  inherit pytest's configured package path;
- the failed probe was not retried or adopted as evidence;
- catalog write, knowledge update/validation, catalog check, full suite and
  later repository/static/final gates were `NOT_RUN`;
- no BUILD commit/push and no provider/network/remote-ingest call occurred.

Amendment 5 and its R2 are consumed. Amendment 6 correctly retains the focused
evidence, does not rerun it, and treats the corrected probe as a fresh command
under a new reviewed Amendment and fresh R2—not as a retry or relabeling of the
failed command.

## Independent binding reproduction

The reviewer used typed `string[]` collections,
`[Array]::Sort(..., [StringComparer]::Ordinal)`, UTF-8, and records encoded as
`path + NUL + lowercase_file_sha256 + LF`.

| Binding | Expected | Reproduced | Result |
|---|---|---|---|
| Exact BUILD paths | `28` | `28` | `PASS` |
| Exact BUILD manifest | `c9e021d3f58bc996daac0d1ec3d21513419d465ab948555b7b62f18d62183d4e` | same | `PASS` |
| Immutable source/test paths | `10` | `10` | `PASS` |
| Immutable source/test manifest | `addb052c9bafb6cd977435268304d43396b304d65ea730db0060890447ab7352` | same | `PASS` |
| Exact repair paths | `3` | `3` | `PASS` |
| Protected paths | `25` | `25` | `PASS` |
| Protected manifest | `513ba54f7af8b0b44fd4143009aa87bb21faa19c82adc671c99c01fe2676dda1` | same | `PASS` |
| Staged paths | `0` | `0` | `PASS` |

The three writable surfaces also reproduce their bound pre-continuation hashes:

| Path | SHA-256 |
|---|---|
| `docs/catalog/MODULE_REGISTRY.json` | `d3b848506f788efd658cf2be9ac05c2e81a60c45450c34cb0a157a68d3859f38` |
| `docs/catalog/MODULE_CATALOG.md` | `6b5ad6a2220da94457fe2a39fd2732210d2531127fd24b54840d4904ea933e92` |
| `knowledge/manifest.json` | `461e6b5a4f72ba9f86e71c1562455176392c30e14d838a6fcef09cf62e6bb429` |

## Three-path sufficiency and non-expansion

The ten source/test files are now evidence inputs, not writable repair
surfaces. Protecting them byte-for-byte prevents post-focused-test source or
test drift. The only remaining authorized mutations are sufficient:

1. `docs/catalog/MODULE_REGISTRY.json` restores only
   `cvf-application-profile.status=contract-only` while retaining
   `refinery-bridge.status=partial`;
2. `docs/catalog/MODULE_CATALOG.md` receives only generator-derived catalog
   output;
3. `knowledge/manifest.json` receives only the resulting registry SHA-256 pin.

No new BUILD path, source/test change, new behavior, runtime caller, contract,
fixture, dependency or wider documentation change is permitted. Final BUILD
diff remains the same exact 28 paths.

## Corrected probe environment

The two required import roots are:

- `packages/refinery-bridge/src` for `refinery_bridge`;
- `tests/unit` for `_refinery_fixtures` used by the seven-case stdin probe.

On Windows, their `PYTHONPATH` separator is `;`. Amendment 6 requires that
value in the same PowerShell process as the single `python -` invocation, which
is sufficient to repair the environment-only failure without changing source,
tests or project configuration. Operationally, the worker must assign the
process environment variable, for example
`$env:PYTHONPATH = 'packages/refinery-bridge/src;tests/unit'`, immediately
before that one probe command. The assignment is not a second probe, and the
environment dies with the bounded shell process.

The fresh probe must execute all seven named cases: zero-quality ready,
unbound fingerprint, invalid offsets, disposition mismatch, policy drift,
stage unavailable and sanitized unexpected exception. Any import failure,
missing case, unsafe disclosure or invariant failure stops the invocation.

## Ordered remaining gates and no-retry review

The continuation order is complete and fail-closed:

1. authority, hashes, empty staged set and exact 10/25/28 binding preflight;
2. one corrected seven-case probe;
3. isolated registry correction and one catalog `--write`;
4. one exact registry-pin update;
5. project-knowledge validator and focused local-helper rehearsal once;
6. catalog `--check`, full non-live suite and repository/static gates once;
7. final exact-28, exact-three-touch, immutable 10/25 and staged-set audit.

The focused `53 passed` command is retained and expressly not rerun. The failed
Amendment 5 stdin probe is neither retried nor relabeled. No standalone
inventory/search command is authorized. Every Amendment 6 evidence command
runs at most once and the invocation stops at its first non-zero result or
contract failure.

## Claim boundary and next governed move

The continuation permits zero provider, network and remote-ingest calls. A
successful invocation yields only a dirty exact 28-path deterministic-local
BUILD candidate pending fresh independent BUILD review. It establishes no
runtime caller, persistence, `data_scope`, retrieval/RAG, learning, production,
P3-A closure or Phase 3 completion claim.

Open authorization findings: `NONE`. Waivers: `NONE`.

After this review and synchronized continuity are committed/pushed while all
28 BUILD paths remain unstaged, the operator must provide Amendment 6's exact
fresh R2 acknowledgment. That acknowledgment authorizes one continuation
invocation only and no retry. It does not authorize BUILD commit/push,
self-review, FREEZE or a later lane.
