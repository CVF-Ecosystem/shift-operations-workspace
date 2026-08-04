# Work Order Amendment 15 — P3-A Final-Review Defect Repair

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-15-2026-08-04`
- Parent Work Order SHA-256: `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
- Final SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- Failed final BUILD review SHA-256: `4f5099c5647c715de9e1ae9e5a833dd444c2498ca1ea282d553935cd04f11cf1`
- Amendment 14 SHA / review: `a1a76cbfa979855cf64d650ccca5ede807470b12bf5e9930a7cc7a1cb15bbe17` / `f50ffde1259973cca317d091e8ce13bc8622a9cf44265b9de4d9207e34d916d1`
- Amendment 14 authority / acknowledgment: `5990efe44162ed2aa7c5bec39bfd57c740efecef` / `847c96b0b82cf922265eef2364b7814e7f5e27fb`
- BUILD-candidate continuity checkpoint: `49cf7ecd8151b64b0fde5d75cdc2d316687d6e78`
- Risk / phase: `R2 / WORK_ORDER`
- Status: `PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Provider/network/remote-ingest calls: `0/0/0`

## Trigger and retained review truth

Amendment 14 completed its verification-only continuation with focused `53`,
catalog, full non-live `1593/128`, session/repository/static and final audits
passing. Independent final BUILD review nevertheless returned
`FINAL_REVIEW_CHANGES_REQUIRED`, no waiver. It reproduced exact32/stable30,
the A13 source move, lossless rotations and focused suite, then directly proved
four public-boundary defects plus material AC-03/05/06/07 and status-evidence
gaps. No provider/network/remote-ingest call occurred.

## Exact pre-repair binding

The candidate is exact 32 dirty paths and staged zero. Excluding the two
volatile continuity front doors gives stable 30 paths / manifest
`a50cebb5f4f4b2e6b6ae79bc56ebc70ac17c1fdd28b7242267a17e96e9c6a436`.
Excluding the exact nine repair paths below from stable30 gives immutable
protected21 / manifest
`68cbd2430a85e1cafc5a79b46a72d6479a9c2b0a09629cfb387f78c78d7a6070`.

Repair pre-hashes:

| Path | SHA-256 |
|---|---|
| `packages/refinery-bridge/src/refinery_bridge/output_models.py` | `62333c0a2fb0734e50b6a3b564af6303c3488db8e14ec4ac97b86db624b0bd9a` |
| `packages/refinery-bridge/src/refinery_bridge/protection.py` | `d909c740e1a2e93859ca47a596c3dac2afaf740648044523b5d5e9de3e58a3f5` |
| `packages/refinery-bridge/src/refinery_bridge/pipeline.py` | `69a55e2e7ad3b115176ae853f2756d3115f69aa12d0d1f7a6088ab15bb8371bf` |
| `tests/unit/test_refinery_models.py` | `d99c48ef9fa7b8a29d762c28965ed719039adcd5d2ec5d15ceb2158703732dc8` |
| `tests/unit/test_refinery_canonical.py` | `1d6ac9bdcec387e3c5dcd0e8d259275d5fd08d1b1be2aec6dddba31b99f22e88` |
| `tests/unit/test_refinery_pipeline.py` | `8a2503128927333d33e439a29d562724b5ab45460ea882a6ce02a2a83a7f7104` |
| `tests/unit/test_refinery_adversarial.py` | `1fc79f95f928656988736c10e9456550c61f2836a36662f344935ae87acdb768` |
| `IMPLEMENTATION_STATUS.json` | `0403f6170dbcab9fc912ea63b003f1d8325a71f36fc408887c23445cfcaacf10` |
| `knowledge/manifest.json` | `b7c0d5ccc70284a07453f80b37e51f8f5feed04dedea393497d9f16ef9ff2cc9` |

Retain exact archive hashes and normalized payloads, memory suffix
`243/6a055880…ac6`, handoff suffix `2/46f46615…b357`, resolving links, all
four Markdown files under 600 lines, registry/catalog status boundaries and
staged zero.

## Exact repair ceiling — 9 already-dirty paths; final exact32

Only these paths may change:

1. `packages/refinery-bridge/src/refinery_bridge/output_models.py`
2. `packages/refinery-bridge/src/refinery_bridge/protection.py`
3. `packages/refinery-bridge/src/refinery_bridge/pipeline.py`
4. `tests/unit/test_refinery_models.py`
5. `tests/unit/test_refinery_canonical.py`
6. `tests/unit/test_refinery_pipeline.py`
7. `tests/unit/test_refinery_adversarial.py`
8. `IMPLEMENTATION_STATUS.json`
9. `knowledge/manifest.json`

All nine already belong to exact32, so final dirty scope remains exact32. No
new path, debt entry, waiver or protected21 mutation is permitted.

## Required implementation repair

1. Bind every candidate normalization, terminology, classification and
   redaction rules-version field to the corresponding stage receipt version;
   any mismatch must fail public construction.
2. Require a quarantined result's public route to be available; unavailable
   route must not validate as `NO_CANDIDATE_QUARANTINED`.
3. Apply the existing R4 safe-string/URI policy to fallback top-level
   `source_owner_id` and `source_link`; whitespace owner and URI-userinfo must
   fail public construction without leaking the unsafe values.
4. Preserve R16 chronological selection by `(observed_at, prior_source_id)`
   while emitting sorted unique public `match_ids`; valid two-match input must
   return a closed duplicate result and never escape `refine`.
5. Keep the A13 helper location and all public union/fail-stop semantics.

## Required acceptance/status repair

- AC-03: independently recompute golden bytes for dedupe-content and candidate
  fingerprints and reject cross-fingerprint-type substitution.
- AC-05: cover deterministic outputs, invalid-envelope stable bytes and dedupe
  permutation invariance.
- AC-06: cover inclusive window edges, out-of-window exclusion and deterministic
  multi-match selection with public lexical `match_ids`.
- AC-07: cover the complete control-construction/receipt/exception/log/snapshot
  disclosure matrix relevant to these public paths.
- Update `IMPLEMENTATION_STATUS.json.p3a_refinery` to exact32 current evidence,
  completed gates and current authority/review lineage without claiming final
  PASS or P3-A closure.
- Change only the resulting `IMPLEMENTATION_STATUS.json` source pin in the
  active project-context entry of `knowledge/manifest.json`.

All edited Python/test files must remain at or below 300 lines. Catalog metrics
and module statuses must remain unchanged.

## Exact direct repair probe

After repair, one local probe must require all four cases to pass:

1. candidate control-version drift is rejected;
2. unavailable quarantine route is rejected;
3. unsafe fallback owner/link provenance is rejected;
4. two exact-source matches (`z-earlier` 10:00, `a-later` 11:00) return closed
   duplicate output with selected id `z-earlier` and public match ids
   `("a-later", "z-earlier")`, with no exception escape.

The probe must print only case labels/results, never unsafe values.

## Ordered continuation

Run once, stopping first non-zero command or contract failure:

1. verify pushed authority/R2 lineage, artifact hashes, exact32/staged0,
   stable30/protected21 manifests, nine pre-hashes and retained archives/suffixes;
2. edit exactly the nine repair paths;
3. run the exact four-case direct probe once;
4. run the explicit five-file focused Refinery suite once, require all tests
   pass and at least `57` collected cases;
5. run project-knowledge validation and focused Knowledge Pack suite once;
6. run file-size and catalog `--check` once; catalog must not mutate;
7. run full non-live pytest once;
8. run session/repository/JSON-YAML/import-I/O/secret/diff checks once;
9. final exact32/exact-nine/protected21/source/archive/suffix/link/line/staged
   and claim-boundary audit once.

No provider/network/remote-ingest call, retry, BUILD commit, self-review,
FREEZE or later lane is authorized. PASS yields only a dirty exact32 candidate
pending fresh independent BUILD re-review.

## Required review and fresh R2

Independent authorization review, a partial-staged authority checkpoint that
commits only governance preambles/A15/review/state/mirror while preserving all
exact32 repair hunks dirty, and a fresh exact human R2 are required. The R2
must name Amendment 15 SHA, exactly nine repair paths, final exact32 and zero
provider/network/remote-ingest; it authorizes one invocation and no retry.
