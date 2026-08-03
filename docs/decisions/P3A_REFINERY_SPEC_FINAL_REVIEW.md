# P3-A Refinery — Fresh Independent SPEC Final Review

- Tranche: `P3-A-REFINERY-2026-08-03`
- Risk: `R2`
- Review role: `REVIEWER`
- Parent ADR SHA-256: `57ec06fc72e6ec2baad95079cdeff7eabfe7eb2837841dfc7c11cdba256e696e`
- Design Amendment 1 SHA-256: `dc091f2ba00334e58d8755ebfb33e5ec868bf802e8233f36e0f470a6b96f0e4a`
- Design Amendment 2 SHA-256: `393ca069c6ead96bfc7de52f453952cf12dcab1799fbbdccb5836668632291dc`
- Amendment 2 review SHA-256: `23132024214f271235104f93ce8a5561cf6c557c7564e91fd3fba1f5dc00643c`
- Retained SPEC review SHA-256: `dba16f97407a7e0f1e49afa462346acf68bc0224d48e718f7b11c5b402898549`
- Retained SPEC re-review SHA-256: `a39555ab980adb5e28148763e4d28764b845da5590ca07eaed32a317cc78e3a4`
- Reviewed SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- Disposition: `SPEC_REVIEW_PASS`
- Waiver: `NONE`
- Review date: `2026-08-03`

## Reviewed scope and changed-set observation

This fresh review checked the complete repaired SPEC, every R1–R30 requirement
and AC-01 through AC-12 against the immutable three-artifact DESIGN lineage,
the retained failed SPEC reviews and the Amendment 2 pass receipt. It did not
rely on the repair author's closure statement as evidence.

Immediately before this receipt was created, the unstaged set contained:

- `docs/specs/P3A_REFINERY_SPEC.md`;
- `docs/decisions/ADR_2026-08-03_P3A_REFINERY_AMENDMENT_2.md`;
- `docs/decisions/P3A_REFINERY_DESIGN_AMENDMENT_2_REVIEW.md`;
- `docs/decisions/P3A_REFINERY_SPEC_REVIEW.md`;
- `docs/decisions/P3A_REFINERY_SPEC_REREVIEW.md`;
- `SESSION/SESSION_MEMORY.md`;
- `SESSION/ACTIVE_SESSION_STATE.json`;
- `CVF_SESSION/ACTIVE_SESSION_STATE.json`;
- `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md`.

The staged set was empty. This reviewer added only this final-review path and
did not edit the SPEC, DESIGN lineage, retained reviews or continuity.

No provider, network, WORK_ORDER, BUILD, staging, commit or push action was
performed.

## Retained finding regression

- **F1 closed:** fingerprint preimages bind exactly to R19/R23 and missing
  dedupe context binds to R21; AC-04 verifies normative cross-references.
- **F2 closed:** quarantine, fallback and stage reasons are separate closed
  enums. R17 exhaustively maps each stage/outcome/reason and rejects unknown or
  cross-type substitution.
- **F3 closed:** the only admitted receipt languages are `PASS^9` and
  `PASS* FAIL NOT_RUN*`; NOT_RUN is bidirectional with an earlier FAIL, has no
  execution data and is rejected when orphaned or premature.
- **F4 closed:** collision is unequal full triples with either digest equal,
  including both-digests-equal/length-different; tests cover all boundaries.
- **F5 closed:** the public union separates total provenance-free structural
  rejection from the nine-stage `RefineryResultV1`. Invalid input is neither
  echoed nor fingerprinted and no source evidence is fabricated.
- **F6 closed:** executed DEDUPE receipts expose typed `dedupe_status` with an
  exhaustive outcome/reason/nullability matrix. Ready `UNIQUE` and advisory
  `REDACTED_TEXT_MATCH` are publicly distinguishable without heuristics.
- **F7 closed:** all nine receipts map one-to-one to explicit non-defaulted
  `ControlBundleV1` versions through `control_version`; substitution and
  cross-stage reuse are rejected while fixed fingerprint preimages remain
  unchanged.

No finding is waived.

## Full contract regression

### Public union, admission and disclosure — PASS

`RefineryBoundaryOutputV1` has unambiguous closed branches: exact
`kind="PRE_ADMISSION_REJECTION"` selects only the provenance-free R9 schema,
and `RefineryResultV1` forbids `kind`. Structural pre-admission is a parser gate,
not a tenth stage. It is total over arbitrary envelope payload and emits only
fixed field-error codes, never input values, provenance, receipts, route or
candidate data.

The contract correctly distinguishes that arbitrary-envelope guarantee from a
valid typed `ControlBundleV1` precondition. Invalid control construction returns
no refinery output and only a sanitized configuration code; it cannot be
misrepresented as an input rejection or admitted result. With a valid bundle,
structurally safe input enters ENVELOPE. A valid-but-mismatched caller
fingerprint produces a full `PROVENANCE_MISMATCH` result using the locally
recomputed fingerprint and validated owner/link, never the mismatched value.

Both union branches, control-construction failures and every receipt/error/log/
snapshot surface prohibit raw input, matched sensitive values, exception
messages and stacks. No branch claims quarantine delivery, storage, deletion,
acknowledgment, retry or upstream retention.

### Stages, dedupe, quality and disposition — PASS

The corrected nine-stage order remains exact after structural admission.
Receipts have closed field sets, one exact mapped control version, one typed
reason and legal dedupe-status nullability. First failure is fail-stop; later
receipts carry their own skipped-control version but are NOT_RUN with empty
execution data.

Stage 7 runs only after redaction PASS and performs same-type source/content
fingerprint comparisons. Collision precedes normal matches. Exact source match
is DEDUPE FAIL with typed `EXACT_SOURCE_MATCH`; QUALITY and admission become
NOT_RUN, the separate quality receipt assigns integrity zero and cannot upgrade
the result, and disposition precedence selects duplicate with candidate null.
Advisory redacted-content match remains PASS and eligible for ready admission.
Invalid/missing context, collision, quarantine-route failure, stage
unavailability and invariant errors all have one deterministic fail-closed
route.

Quality is exactly four 0-or-25 control-coverage components and threshold 100,
not truth, probability, semantic confidence or production quality. Candidate
and candidate fingerprint are non-null if and only if disposition is ready;
all contradictory union/result/receipt combinations are rejected.

### Fingerprints, transformations and evidence — PASS

Source, source-free dedupe-content and final-candidate fingerprints use
distinct non-interchangeable types and non-circular preimages. Canonical JSON,
UTF-8 bytes, digest algorithms, byte length, collection sorting and unknown/
float/null/key rejection are exact. The additional control versions remain in
receipts and do not change the reviewed R19 or R23 preimages.

Normalization remains syntax-only and idempotent: no paraphrase, translation,
action-state reinterpretation, timezone/AM-PM inference or missing-value
invention. Sensitivity is the exact four-value data-policy vocabulary,
non-decreasing from its declared floor and separate from topic labels.
Redaction failures, unsafe spans and residue fail closed without matched-value
leakage.

The 28-case synthetic fixture matrix covers both union branches, admitted
provenance mismatch, version substitution, positive/negative normalization,
redaction, sensitivity, conflicts, every relevant dedupe outcome and fallback.
The existing `11h40` fixture remains negative and cannot be silently corrected.

### I/O, dependency and claim boundary — PASS

The boundary remains pure local and deterministic: no provider/network,
database, filesystem/environment discovery, secret read, wall-clock read or
randomness. The package cannot import routers, ledgers, provider/retrieval code
or `cvf_runtime.data_scope`; data-policy parity is tested without claiming the
runtime gate is load-bearing.

P3-A evidence is limited to deterministic local refinement, typed fail-closed
outputs and reproducible candidate bytes. It cannot claim confirmed truth, raw
or quarantine persistence, external ingest, provider behavior, DLP/
minimization enforcement, P3-B/P3-C, retrieval/RAG, learning, Integration Edge,
AI governance or production readiness. Any future provider-governance claim
still needs a separate R2 work order, real runtime caller and fresh real-provider
evidence.

## Acceptance disposition

R1–R30 are internally consistent, executable and faithful to the reviewed
DESIGN lineage. AC-01 is satisfied by this independent no-waiver review; AC-02
through AC-12 are specific, testable and preserve the same scope and stop
conditions for a future authorized BUILD. No hidden contradiction or open
finding remains at SPEC.

`SPEC_REVIEW_PASS` with no waiver. The unchanged SPEC at SHA-256
`d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
**may transfer to `WORK_ORDER_AUTHOR`**. Any byte change to the SPEC or reviewed
DESIGN lineage invalidates this transfer and requires independent review.

This receipt grants WORK_ORDER authoring only. It grants no BUILD,
provider/network call, remote ingest, persistence, retrieval/RAG, staging,
commit, push or later-lane authority.
