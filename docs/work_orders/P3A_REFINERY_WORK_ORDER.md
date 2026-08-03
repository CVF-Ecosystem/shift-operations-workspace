# Work Order — P3-A Deterministic Refinery BUILD

- Work order id: `P3-A-REFINERY-BUILD-2026-08-03`
- Tranche: `P3-A-REFINERY-2026-08-03`
- Risk: `R2`
- Control-chain phase: `WORK_ORDER`
- Status: `WORK_ORDER_CANDIDATE_PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Parent ADR SHA-256: `57ec06fc72e6ec2baad95079cdeff7eabfe7eb2837841dfc7c11cdba256e696e`
- Design Amendment 1 SHA-256: `dc091f2ba00334e58d8755ebfb33e5ec868bf802e8233f36e0f470a6b96f0e4a`
- Design Amendment 2 SHA-256: `393ca069c6ead96bfc7de52f453952cf12dcab1799fbbdccb5836668632291dc`
- SPEC SHA-256: `d23ec439cc3ef50b885b1d49e1d58942942b5fde637ab73fc619597b320e9eaf`
- Final SPEC review SHA-256: `9910196960af8dc97a9328fb4b7b6b6a658e77e81f99d0b43fed077151732f18`
- Provider calls: `0`
- Network calls during BUILD: `0`
- Remote ingest calls: `0`

## Objective

Implement the reviewed P3-A contract as a deterministic, pure local Python
package. The BUILD must convert only structurally admitted explicit input into
typed receipts/candidates, reject unconstructible input without reflecting or
fabricating provenance, and fail closed on every reviewed ambiguity, protection,
dedupe, quality or invariant condition.

This work order authorizes no runtime application caller, provider path,
database, external/channel ingestion, persistence, retrieval/RAG, P3-B/P3-C,
learning or production behavior.

## Source baseline and authority binding

The BUILD baseline is the clean pushed authorization checkpoint containing this
unchanged work order, its independent authorization review and synchronized
continuity. `COMMIT_STEWARD` must record that exact commit before BUILD begins.
The human R2 acknowledgment must bind the exact work-order SHA-256, exact 26
BUILD paths and zero-call boundary below. Any byte change to the reviewed work
order, SPEC or DESIGN lineage invalidates authority.

## Exact BUILD changed-set ceiling — 26 paths

BUILD may create or modify exactly these paths and no others:

1. `pyproject.toml`
2. `packages/refinery-bridge/README.md`
3. `packages/refinery-bridge/pyproject.toml`
4. `packages/refinery-bridge/contracts/refinery_contract.yaml`
5. `packages/refinery-bridge/src/refinery_bridge/__init__.py`
6. `packages/refinery-bridge/src/refinery_bridge/enums.py`
7. `packages/refinery-bridge/src/refinery_bridge/canonical.py`
8. `packages/refinery-bridge/src/refinery_bridge/controls.py`
9. `packages/refinery-bridge/src/refinery_bridge/input_models.py`
10. `packages/refinery-bridge/src/refinery_bridge/receipt_models.py`
11. `packages/refinery-bridge/src/refinery_bridge/output_models.py`
12. `packages/refinery-bridge/src/refinery_bridge/normalization.py`
13. `packages/refinery-bridge/src/refinery_bridge/protection.py`
14. `packages/refinery-bridge/src/refinery_bridge/dedupe.py`
15. `packages/refinery-bridge/src/refinery_bridge/pipeline.py`
16. `fixtures/refinery/normalized_message.json`
17. `fixtures/refinery/qualified_time_message.json`
18. `tests/unit/_refinery_fixtures.py`
19. `tests/unit/test_refinery_models.py`
20. `tests/unit/test_refinery_canonical.py`
21. `tests/unit/test_refinery_pipeline.py`
22. `tests/unit/test_refinery_adversarial.py`
23. `tests/unit/test_refinery_contract.py`
24. `docs/catalog/MODULE_REGISTRY.json`
25. `docs/catalog/MODULE_CATALOG.md`
26. `IMPLEMENTATION_STATUS.json`

Every path is mandatory. A missing path, extra path, rename, generated cache,
lockfile, snapshot or continuity edit during BUILD is an immediate stop. Phase
transition/authorization continuity belongs to the separate governance
checkpoint, not this BUILD changed set.

## Implementation contract

### 1. Package and imports

- Add `packages/refinery-bridge/src` to the root pytest python path and define a
  standalone package with no new dependency.
- Package code must not import application routers, ledgers, provider adapters,
  retrieval code or `cvf_runtime.data_scope`.
- No boundary/control callable may access network, provider, database,
  filesystem/environment discovery, secrets, wall clock or randomness.

### 2. Exact public models

- Implement every closed enum, identifier/bound/time constraint and unknown
  field rejection in SPEC R1–R6.
- Implement `ControlBundleV1` as a typed precondition with nine exact explicit
  version sources; invalid construction invokes no refinery pipeline and leaks
  no input.
- Implement `RefineryBoundaryOutputV1` as the exact closed union. Arbitrary
  envelope payload plus a valid control bundle is total: structurally invalid
  input returns only safe `PreAdmissionRejectionV1`; admitted input returns only
  `RefineryResultV1`.
- Never fabricate or echo unsafe/mismatched provenance. A structurally admitted
  fingerprint mismatch uses the locally recomputed fingerprint.

### 3. Deterministic transforms and fingerprints

- Implement the exact canonical JSON algorithm and distinct source,
  dedupe-content and candidate fingerprint types/preimages.
- Normalization is NFC/line-ending/whitespace syntax only and idempotent. It
  must not convert `11h40` to `23:40`, translate, paraphrase, guess timezone or
  reinterpret action state.
- Terminology matching is exact token-boundary, versioned and deterministic.
- Classification never lowers declared sensitivity; topic labels convey no
  placement authority.
- Conflict/ambiguity detection fails without choosing an interpretation.
- Redaction uses deterministic non-overlapping spans and verifies residue; no
  matched value appears in a public surface.

### 4. Dedupe, receipts, quality and disposition

- Validate the inclusive caller-supplied scope/window and maximum 500 unique
  records; there is no dedupe store.
- Compare only same fingerprint types. Full-triple equality is the only match;
  unequal triples with either digest equal are collision-suspected.
- DEDUPE public `dedupe_status` follows the reviewed exact matrix. `UNIQUE` and
  advisory `REDACTED_TEXT_MATCH` pass. `EXACT_SOURCE_MATCH` fails stage 7,
  forces later stage receipts to `NOT_RUN`, leaves integrity at zero and selects
  duplicate disposition/candidate null.
- Emit the exact nine ordered receipts with exact mapped `control_version` and
  only the legal `PASS^9` or `PASS* FAIL NOT_RUN*` language.
- Emit the separate always-present quality receipt for every admitted result;
  four components are only 0/25 and candidate admission requires 100/100.
- Enforce total disposition and mutually exclusive candidate/duplicate/
  quarantine/fallback receipt invariants at model construction.

### 5. Fixtures, contract and status truth

- Rewrite the existing `11h40` fixture as a structurally complete negative
  synthetic case; retain the original ambiguous raw text and remove the
  invented `23:40`/processing truth.
- Add a distinct fully qualified-time positive fixture.
- Update the YAML contract to the exact reviewed V1 boundary, not a looser
  compatibility claim.
- Update registry/catalog/status only to `partial` deterministic local package
  truth. State explicitly: no runtime caller, provider, remote ingest,
  persistence, `data_scope` enforcement, retrieval/RAG or production claim.

## Required evidence and acceptance commands

Run locally, fail at the first non-zero result and do not retry a failed gate:

1. focused models/canonical/contract tests;
2. focused pipeline/adversarial tests, including at least the 28 SPEC fixtures;
3. full non-live repository pytest suite;
4. `python scripts/generate_catalog.py --write`, followed by catalog check;
5. `python scripts/check_session_state.py`;
6. `python scripts/check_file_size.py`;
7. `python scripts/testing/validate_repository.py`;
8. JSON/YAML parse checks, forbidden-import/I/O static checks, secret scan,
   `git diff --check` and exact 26-path diff audit.

The evidence receipt must record interpreter/tool versions, exact test counts,
every command/result, source baseline, changed-set audit and zero-call account.
No test may monkeypatch a real provider and no mocked provider output may be
presented as governance evidence. This BUILD makes no AI-governance claim, so
real-provider evidence is neither required nor authorized.

## Stop conditions

Stop immediately on the first:

- missing fresh human R2 acknowledgment or authorization-review pass;
- source baseline, work-order/SPEC/DESIGN hash drift;
- missing or extra BUILD path;
- provider/network/remote-ingest attempt, secret read or external write;
- ambiguous contract requiring DESIGN/SPEC interpretation;
- raw/matched-value/provenance disclosure or fabricated provenance;
- candidate on a failed/skipped stage, quality below 100 or invalid receipt
  combination;
- failed test/gate, catalog drift, file-size violation or dirty generated/cache
  residue.

There is no retry. A failure returns to the appropriate governed phase with a
new reviewed amendment if needed. Do not continue to another gate after the
first failure.

## Required independent review and human acknowledgment

An independent reviewer must return `WORK_ORDER_AUTHORIZATION_REVIEW_PASS`, no
waiver, for the unchanged work-order SHA and exact 26 paths. After the reviewed
authority checkpoint is committed and pushed, BUILD remains blocked until the
operator sends this fresh acknowledgment with the exact computed hash:

> Tôi phê duyệt R2 cho P3-A-REFINERY-BUILD-2026-08-03, Work Order SHA-256
> `<exact_sha256>`, đúng 26 BUILD paths, zero provider/network/remote-ingest
> calls.

That acknowledgment authorizes one BUILD invocation only. It grants no provider
call, retry, path expansion, remote ingest, later-lane work, commit or closure.

