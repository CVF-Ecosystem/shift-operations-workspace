# Work Order Amendment 18 — Precomputed Direct Repair Invocation

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-18-2026-08-04`
- Parent A17 SHA-256: `01e6392dfc72c257d121091466e221431e5cb43c2ed8e2dd211499dddcef1a7c`
- A17 review SHA-256: `a0c670c6f00d6826b32338fd270378440e807f95bf58ec7177bdf9eeafe3519d`
- A17 authority / R2 ack: `6ab305610c9065dbc0590ac8727bc67e6ccdf6ba` / `f775b7c4b3d32872c24fc5b8518109c8797e5764`
- Initial review SHA-256: `d72136737ec3afe428b8390b1c3f60e4c7c3dff2c42f12670113af81465ec55c`
- First re-review SHA-256: `919bf51f485bdcc8060adfb0e542a57c0e508b52a24271e33872428520e1f36c`
- Re-review 2 SHA-256: `e0a374410073164167f8ffbb3e2c15eeb131b998f8d17b7cb407317d213c8b88`
- Frozen execution sheet SHA-256: `deff7d1ae7289a4af3a07d8696fb02a47a3411d4a5ba7fa936b5afcab523e2f3`
- Risk / phase / status: `R2 / WORK_ORDER / PENDING_INDEPENDENT_AUTHORIZATION_REREVIEW`
- Calls: `0 provider / 0 network / 0 remote-ingest`

## Consumed A17 truth

A17's canonical multiline preflight passed. Its first post-preflight command
then failed PowerShell parsing at `foreach($p in$paths)` while attempting a
read-only source/test inventory. Parsing failed before that command read any
file. Stop-first/no-retry was honored: no repair, probe, test, later gate or
BUILD commit ran; calls remained zero. Exact32 bytes, nine repair pre-hashes,
archives and stable suffixes are unchanged. A17/R2 are consumed.

## Sole orchestration correction

All source/test/status/manifest inspection is complete. The exact patch,
four-function assertion matrix and direct command sequence are frozen at
`docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_18_EXECUTION_SHEET.md`
under the SHA above. The invocation has no inventory step.
After preflight it may use no PowerShell loop, conditional, switch or function
and no generated/compressed shell command. It uses one precomputed atomic
`apply_patch` for the exact nine paths, followed only by explicit direct
probe/gate commands copied from the reviewed execution sheet. No synthesis,
retry, alternate selector or recovery branch is allowed.

## Exact nine repair paths and pre-hashes

1. `packages/refinery-bridge/src/refinery_bridge/output_models.py` — `62333c0a2fb0734e50b6a3b564af6303c3488db8e14ec4ac97b86db624b0bd9a`
2. `packages/refinery-bridge/src/refinery_bridge/protection.py` — `d909c740e1a2e93859ca47a596c3dac2afaf740648044523b5d5e9de3e58a3f5`
3. `packages/refinery-bridge/src/refinery_bridge/pipeline.py` — `69a55e2e7ad3b115176ae853f2756d3115f69aa12d0d1f7a6088ab15bb8371bf`
4. `tests/unit/test_refinery_models.py` — `d99c48ef9fa7b8a29d762c28965ed719039adcd5d2ec5d15ceb2158703732dc8`
5. `tests/unit/test_refinery_canonical.py` — `1d6ac9bdcec387e3c5dcd0e8d259275d5fd08d1b1be2aec6dddba31b99f22e88`
6. `tests/unit/test_refinery_pipeline.py` — `8a2503128927333d33e439a29d562724b5ab45460ea882a6ce02a2a83a7f7104`
7. `tests/unit/test_refinery_adversarial.py` — `1fc79f95f928656988736c10e9456550c61f2836a36662f344935ae87acdb768`
8. `IMPLEMENTATION_STATUS.json` — `0403f6170dbcab9fc912ea63b003f1d8325a71f36fc408887c23445cfcaacf10`
9. `knowledge/manifest.json` — `b7c0d5ccc70284a07453f80b37e51f8f5feed04dedea393497d9f16ef9ff2cc9`

Final dirty scope remains exact32, staged zero. Excluding two volatile
continuity front doors retains stable30
`a50cebb5f4f4b2e6b6ae79bc56ebc70ac17c1fdd28b7242267a17e96e9c6a436`;
excluding exact9 retains protected21
`68cbd2430a85e1cafc5a79b46a72d6479a9c2b0a09629cfb387f78c78d7a6070`.

Retain memory archive 335 / `e218cbc150d03bd9c42f623f972e43ee33ee00b530882195e2c8c145ab918f86`,
handoff archive 394 / `c50d4bfd7c7745fa1bb3e5758eddb57c905f5d10fac5da5fda8707f63aee0d44`,
memory suffix 243 / `6a055880ab97e542fa122ff6cbe3025d993aa521d3b4e9098abf82fa97237ac6`,
handoff suffix 2 / `46f46615b06dff42a2c44b55321e30c862881146a58a98549fe06f06aaceb357`,
and all four Markdown continuity/archive files at or below 600 lines.

## Precomputed repair contract

The one patch must only:

1. apply `validate_safe_string` to result-level owner/link provenance;
2. bind candidate normalization/terminology/classification/redaction versions
   to their canonical stage receipts while retaining quality/fingerprint binds;
3. require `quarantine_receipt.route.sink_available is True`;
4. preserve chronological selected prior id while using one sorted-unique
   public match-id tuple for stage/duplicate receipts, counts and results;
5. add exactly four collected functions, one in each authorized test file:
   models rejects recomputed-fingerprint version drift, unavailable route and
   both unsafe fallback provenance mutations; canonical independently hashes
   exact bytes for all three typed constructors and rejects candidate-to-source
   substitution; pipeline proves inclusive edges/out-of-window rejection,
   chronological selection, lexical ids and permutation-identical JSON;
   adversarial proves stable invalid-union bytes plus no matched value in union,
   receipt, sanitized exception result, log or snapshot alongside failed
   control construction. Baseline `53` plus four must collect exactly `57`;
6. update `IMPLEMENTATION_STATUS.json.p3a_refinery` to exact32, retained A14
   PASS evidence, final-review CHANGES_REQUIRED and A18 repair-in-progress,
   without claiming BUILD PASS/closure/runtime wiring;
7. change only the resulting implementation-status source pin in the
   `project-context` entry of `knowledge/manifest.json`.

No dedupe algorithm, receipt model, contract, registry/catalog, archive,
suffix, dependency, API, provider, remote-ingest or later-lane change.

## One ordered invocation

Run once, no retry, stop at the first failure:

1. reviewed preflight: pushed A18 authority/R2 lineage including this Work
   Order, initial review and frozen sheet; exact32/staged0/
   stable30/protected21; nine pre-hashes; archive/suffix/link/line bindings;
2. one atomic exact-nine patch copied byte-for-byte from the frozen sheet;
3. one direct four-case public-invariant/multi-match probe;
4. explicit five-file focused suite, all pass and collected count >=57;
5. local Knowledge Pack validator and focused tests;
6. file-size and non-mutating catalog `--check`;
7. full non-live pytest;
8. session/mirror, repository, JSON, static, security and diff checks;
9. final exact32/exact9/protected21/archive/suffix/line/staged audit.

No provider/network/remote-ingest/POST/helper call, BUILD commit, self-review,
FREEZE, waiver, debt or expansion. PASS yields only a dirty exact32 local
candidate pending independent BUILD review. Independent authorization review,
governance-only exact-nine checkpoint (this Work Order, execution sheet,
initial review, first re-review, re-review 2, canonical state, mirror, memory
and handoff)
and fresh exact R2 naming this SHA/exact9/final32/zero calls are mandatory
before invocation.
