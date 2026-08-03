# Work Order Amendment 5 — P3-A Post-Inventory-Command Resume

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-5-2026-08-03`
- Parent Work Order SHA-256: `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
- Consumed Amendment 4 SHA-256: `0f79fcc75ae468c0c56a2db39d821738e0b863bf94710f2eebcbf845020fd0dd`
- Amendment 4 authorization review SHA-256: `e18217e6c41a958fdd3dc38f0e334c9153e4521929ca1b8758f33a7f856bb320`
- Corrected BUILD review SHA-256: `ccc6c4c25fc00000be34d443ffdb4d59c665f1436641e3f89b06b4906480b405`
- SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- BUILD diff base: `b93e403cf0ab6d659de0706c058d1cd7250e75d0`
- Amendment 4 acknowledgment checkpoint: `9dd0900486d961f53bf673a22133bd78f7cccbad`
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Status: `AMENDMENT_CANDIDATE_PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Provider/network/remote-ingest calls: `0/0/0`

## Trigger and retained stop truth

The fresh Amendment 4 R2 was consumed after its pushed checkpoint and preflight
PASS. REPAIR_WORKER then changed exactly five authorized source paths:

1. `controls.py`
2. `receipt_models.py`
3. `output_models.py`
4. `protection.py`
5. `pipeline.py`

Before any focused test, a read-only inventory command returned non-zero because
the Windows `rg` invocation used the unsupported literal glob
`tests/unit/test_refinery*`. Execution stopped immediately. The command was not
retried. No test, probe, catalog write, knowledge update or later gate ran.
Zero provider/network/remote-ingest calls occurred. The five partial source
edits are retained without a correctness claim.

This is an execution-resume authority repair only. DESIGN, SPEC and corrected
BUILD-review findings F2-F6 do not change.

## Exact retained binding

The dirty BUILD set remains the same exact 28 paths. Using typed ordinal,
case-sensitive sorting and records
`path + NUL + lowercase_file_sha256 + LF`:

- path count: `28`;
- current manifest SHA-256:
  `c785597e0f15a8a9c4710f65bd21d15713206edfce929a1ad7be7dbe81ece17a`;
- unchanged protected-15 SHA-256:
  `ce531fb7fe4b8fa7c97aa29863cf1980a8665f5d74d21fb3d17259af37644784`;
- staged path count: `0`.

The retained hashes of the five partially edited source paths are:

| Path | SHA-256 |
|---|---|
| `controls.py` | `cdf42a528bffac7b031ed100c0d94f067d7e725884dfbe939a9340e4e9651a14` |
| `receipt_models.py` | `32bdf786127faa773b8b6a83128c178d45098bb44871e144b03667d7ba7133d3` |
| `output_models.py` | `240a76f60c14691acd7af255405ece6f381d157b836dad4a5f031b24f8b1f8b9` |
| `protection.py` | `1ff509d87747bcfb864823029ee5edfbfff5d8176e2a1612a1391d61f6425219` |
| `pipeline.py` | `616a0baa1ef58a042e4a4e17914e6dae134b28b1c48eb2314baa6453a5ed343e` |

Any preflight mismatch stops the new invocation.

## Exact repair ceiling and contract

The repair ceiling remains exactly the same 13 paths authorized by Amendment 4:

1. `packages/refinery-bridge/src/refinery_bridge/controls.py`
2. `packages/refinery-bridge/src/refinery_bridge/receipt_models.py`
3. `packages/refinery-bridge/src/refinery_bridge/output_models.py`
4. `packages/refinery-bridge/src/refinery_bridge/protection.py`
5. `packages/refinery-bridge/src/refinery_bridge/pipeline.py`
6. `tests/unit/_refinery_fixtures.py`
7. `tests/unit/test_refinery_models.py`
8. `tests/unit/test_refinery_pipeline.py`
9. `tests/unit/test_refinery_adversarial.py`
10. `tests/unit/test_refinery_contract.py`
11. `docs/catalog/MODULE_REGISTRY.json`
12. `docs/catalog/MODULE_CATALOG.md`
13. `knowledge/manifest.json`

All Amendment 4 repair requirements remain normative: bind public result,
quality, candidate fingerprint/provenance and disposition invariants; implement
total sanitized policy-drift/stage-unavailable/unexpected-invariant paths;
enforce safe identifiers/collections/offsets without silent deduplication;
execute at least 28 named one-to-one R27 cases; restore only
`cvf-application-profile.status=contract-only`; keep
`refinery-bridge.status=partial`; regenerate catalog once; and update only the
registry source pin in the active knowledge manifest entry.

The 15 other BUILD paths remain byte-immutable. No new BUILD path may be
created. Final diff remains exact 28 paths.

## Ordered continuation

Run once in this exact order and stop on the first non-zero command or contract
failure:

1. verify pushed authority lineage, all bound hashes, empty staged set, exact
   retained 28-path digest and protected-15 digest;
2. complete/revise only the ten authorized source/test paths for F2-F5; do not
   run a separate inventory/search command;
3. run the focused refinery test command once;
4. run the dedicated public-invariant/fail-stop/disclosure probe once;
5. restore only the unrelated registry status and run catalog `--write` once;
6. update only the registry source-pin digest in `knowledge/manifest.json`;
7. run project-knowledge validator once;
8. run focused Knowledge Pack unit/local-helper rehearsal once;
9. run catalog `--check` once;
10. run the full non-live pytest suite once;
11. run session-state, file-size, repository, JSON/YAML, forbidden import/I/O,
    secret and diff checks once;
12. verify final exact 28 paths, repair touches within the 13-path ceiling,
    unchanged protected-15 digest and empty staged set.

The failed `rg` inventory command is not retried and is not a gate. No failed
or successful Amendment 4 command is relabeled as Amendment 5 evidence.

## Stop and claim boundary

This continuation permits zero provider, network and remote-ingest calls and no
retry. A pass yields only a dirty exact 28-path deterministic local BUILD
candidate pending fresh independent BUILD review. It authorizes no BUILD
commit/push, self-review, FREEZE, runtime caller, persistence, `data_scope`,
retrieval/RAG, learning, production or Phase 3 completion claim.

## Required review and fresh R2

An independent reviewer must return
`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`, no waiver, bound to this exact
Amendment SHA, retained/protected/partial-source hashes, exact 13 repair paths,
final exact 28 paths, ordered gates and zero-call/no-retry boundary. After the
reviewed authority checkpoint is committed/pushed, the operator must send:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-5-2026-08-03,
> Work Order Amendment SHA-256 `<exact_sha256>`, đúng 13 repair paths và final
> exact 28 BUILD paths, zero provider/network/remote-ingest calls.

The acknowledgment authorizes one continuation invocation only and no retry.
