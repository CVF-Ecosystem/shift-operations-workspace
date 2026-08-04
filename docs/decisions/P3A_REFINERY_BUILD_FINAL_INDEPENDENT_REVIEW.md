# P3-A Refinery BUILD — Final Independent Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent from BUILD and repair authorship)
- Risk / phase: `R2 / REVIEW`
- Review baseline: `HEAD == origin/main == 49cf7ecd8151b64b0fde5d75cdc2d316687d6e78`
- Final SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- Parent Work Order SHA-256: `3a2bf12e7a207510a2779b68b7548afe4db2aa8fb6738eb08ca505f840bcd3c5`
- Corrected earlier BUILD review SHA-256: `ccc6c4c25fc00000be34d443ffdb4d59c665f1436641e3f89b06b4906480b405`
- Amendment 14 SHA-256: `a1a76cbfa979855cf64d650ccca5ede807470b12bf5e9930a7cc7a1cb15bbe17`
- Amendment 14 review SHA-256: `f50ffde1259973cca317d091e8ce13bc8622a9cf44265b9de4d9207e34d916d1`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`FINAL_REVIEW_CHANGES_REQUIRED`

The candidate cannot pass final independent BUILD review. Scope, immutable
bindings, the A13 helper move, lossless continuity rotations and the focused
`53` suite all reproduce. A fresh direct public-boundary probe nevertheless
confirmed four accepted/escaping invalid cases. These leave corrected-review
F2/F4/F5 and SPEC R16/R18/R21/R23/R24 incompletely closed. The implementation
status surface also retains pre-repair path/evidence truth.

There is no waiver. No BUILD commit, FREEZE or expanded claim is permitted.

## Authority, exact scope and immutable bindings

The reviewer read the final SPEC, parent Work Order, corrected prior BUILD
review, Amendments 4–14 and their authorization reviews. Git and artifact
checks establish the pushed baseline above, an empty staged set and exact 32
dirty BUILD/continuity paths.

Using ordinal case-sensitive sorting and UTF-8 records encoded as
`path + NUL + lowercase_file_sha256 + LF`, excluding only the two volatile
continuity front doors gives:

| Binding | Expected | Reproduced | Result |
|---|---:|---:|---|
| Dirty BUILD/continuity paths | `32` | `32` | `PASS` |
| Staged paths | `0` | `0` | `PASS` |
| Stable paths | `30` | `30` | `PASS` |
| Stable-30 manifest | `a50cebb5f4f4b2e6b6ae79bc56ebc70ac17c1fdd28b7242267a17e96e9c6a436` | same | `PASS` |
| `pipeline.py` | 285 / `69a55e2e7ad3b115176ae853f2756d3115f69aa12d0d1f7a6088ab15bb8371bf` | same | `PASS` |
| `protection.py` | 260 / `d909c740e1a2e93859ca47a596c3dac2afaf740648044523b5d5e9de3e58a3f5` | same | `PASS` |
| Memory archive | 335 / `e218cbc150d03bd9c42f623f972e43ee33ee00b530882195e2c8c145ab918f86` | same | `PASS` |
| Handoff archive | 394 / `c50d4bfd7c7745fa1bb3e5758eddb57c905f5d10fac5da5fda8707f63aee0d44` | same | `PASS` |
| Memory suffix | 243 / `6a055880ab97e542fa122ff6cbe3025d993aa521d3b4e9098abf82fa97237ac6` | same | `PASS` |
| Handoff suffix | 2 / `46f46615b06dff42a2c44b55321e30c862881146a58a98549fe06f06aaceb357` | same | `PASS` |

The two archive payloads independently reproduce the pre-rotation normalized
blocks exactly: memory `331/d7d902ea…348e` and handoff
`390/d8b6f8d8…ec14`. Both relative links resolve. Current canonical front doors
are 305/531 lines and the archives 335/394, all below 600. The helper now lives
in `protection.quarantine_reason`, is imported by `pipeline` under the retained
private alias, and preserves the closed reason mapping. The A13 source move and
both rotations therefore pass final review without finding.

## Finding F1 — HIGH: public result invariants remain incomplete

`RefineryResultV1` delegates candidate/failure binding to `protection.py`, but
the helpers do not bind all public facts required by R18/R21/R23/R24:

1. candidate normalization, terminology, classification and redaction rule
   versions are not compared with their corresponding stage receipt versions;
2. quarantine disposition does not require its public route to be available;
3. fallback results do not apply the R4 safe-string policy to top-level source
   owner/link provenance.

One direct probe started from valid pipeline results and proved all three:

- changing only `normalization_rules_version` to another safe value and
  recomputing the candidate fingerprint was accepted;
- changing a quarantine receipt's `sink_available` to `False` was accepted as
  `NO_CANDIDATE_QUARANTINED`;
- changing fallback top-level provenance to surrounding-whitespace owner text
  and URI-userinfo link text was accepted.

This is the same public-construction class as corrected-review F2/F5, not a
pipeline-output cosmetic issue. A consumer may validate a contradictory public
result successfully.

## Finding F2 — HIGH: deterministic multi-match dedupe escapes the boundary

R16 selects the first exact source match by `(observed_at, prior_source_id)`
while public match-id collections are sorted independently. `analyze_dedupe`
currently returns its match tuple in chronological order, but `make_receipt`
and `DuplicateReceiptV1` require lexical order.

The direct probe supplied two exact-source records: `z-earlier` at 10:00 UTC
and `a-later` at 11:00 UTC. Instead of returning duplicate disposition with
`selected_prior_source_id="z-earlier"` and sorted public match ids, validation
raised out of `refine`. The closed R24 union and total fail-stop boundary are
therefore violated for valid R15 input. Existing tests use only one exact-source
record and do not exercise deterministic multi-match selection/permutation.

## Finding F3 — MEDIUM: required acceptance evidence is incomplete

The R27 label-only defect is closed: the suite now creates 28 separately
collected cases and the independent focused invocation passed all `53` tests.
However, the complete SPEC acceptance evidence is still not present:

- AC-03 lacks independent golden-byte recomputation for dedupe-content and
  candidate fingerprints and lacks a cross-fingerprint-type substitution test;
- AC-05 lacks property coverage for deterministic outputs, invalid-envelope
  stable bytes and dedupe permutation invariance;
- AC-06 lacks inclusive window-edge, out-of-window record and multi-match
  deterministic selection coverage;
- AC-07 does not establish the complete control-construction/receipt/
  exception/log/snapshot disclosure matrix.

The newly reproduced F1/F2 failures demonstrate that this is material missing
evidence rather than test-style preference. Worker counts cannot substitute for
the absent assertions.

## Finding F4 — MEDIUM: implementation-status truth is stale

`IMPLEMENTATION_STATUS.json.p3a_refinery` still says the candidate is exactly
the original 26 Work Order paths and that ordered focused/full/repository gates
are pending. The current governed candidate is exact 32 after the authorized
knowledge additions and continuity/source-size repair, while the recorded
ordered evidence through Amendment 14 has completed. Its authority-commit text
also stops at the initial Work Order/R2 lineage. Registry/catalog correctly keep
`refinery-bridge=partial`, restore `cvf-application-profile=contract-only`, and
retain the no-runtime-caller claim; the stale status surface is the remaining
catalog/status truth defect.

## Evidence assessment

| Order | Evidence | Result |
|---:|---|---|
| 1 | Exact-32/staged-zero/stable-30/source/archive/suffix/link/line audit | `PASS` |
| 2 | Complete source, contract, fixture, test, catalog, status, knowledge and continuity diff inspection | `FINDINGS F1–F4` |
| 3 | Five-file focused Refinery suite, one independent invocation | `PASS — 53 passed` |
| 4 | Four-case direct public-invariant/multi-match probe, one invocation | `FAIL — four invalid cases reproduced` |

Canonical execution receipts consistently retain Amendment 8 direct probe
`7/7`, Knowledge Pack `86`, catalog PASS, full non-live `1593 passed / 128
skipped`, and Amendment 14 file-size/session/repository/static/final PASS.
Their lineage is accepted as retained worker evidence, including zero
provider/network/remote-ingest calls, but they do not cure the fresh direct
boundary failure. No later suite/gate was rerun after that failure.

## Exact minimum repair scope

A fresh reviewed WORK_ORDER amendment and fresh R2 are required. The minimum
repair-touch ceiling is exactly these nine already-dirty paths; final dirty
scope can remain exact 32:

1. `packages/refinery-bridge/src/refinery_bridge/output_models.py`
2. `packages/refinery-bridge/src/refinery_bridge/protection.py`
3. `packages/refinery-bridge/src/refinery_bridge/pipeline.py`
4. `tests/unit/test_refinery_models.py`
5. `tests/unit/test_refinery_canonical.py`
6. `tests/unit/test_refinery_pipeline.py`
7. `tests/unit/test_refinery_adversarial.py`
8. `IMPLEMENTATION_STATUS.json`
9. `knowledge/manifest.json`

The repair must bind candidate control versions to their exact stage receipts;
reject unsafe top-level provenance and unavailable quarantine routes; preserve
chronological selected-id semantics while emitting sorted unique public match
ids; add the missing AC-03/05/06/07 assertions; update current status truth;
and change only the resulting implementation-status source pin in the
knowledge manifest. It must retain the A13 helper location, archive bytes,
stable suffixes, registry/catalog `partial` boundary and zero-call claim.

Fresh focused/direct/knowledge/catalog/full/repository/static/final evidence
and a new independent BUILD re-review are required after repair. No waiver,
debt entry or path expansion is granted by this review.

## Claim boundary

The candidate remains only a dirty deterministic-local Refinery candidate. It
has no runtime application caller and proves no provider behavior, remote
ingest, persistence, `data_scope` enforcement, retrieval, RAG, learning,
confirmed truth, production readiness, P3-A closure or Phase 3 completion.
No provider, network or remote-ingest call was made during this review.
