# WORK ORDER — P4-D Channel Adapters

- Work order id: `P4D-CHANNEL-ADAPTERS-WO-2026-08-26`
- Phase: `WORK_ORDER`
- Risk ceiling: `R2`
- Author: `WORK_ORDER_AUTHOR`
- Execution base: `b3f2431aceebb401072c806ed876059cf5f85a52`
- Parent SPEC: `docs/specs/P4D_CHANNEL_ADAPTERS_SPEC.md`
- SPEC review: `SPEC_REVIEW_PASS`, findings/waivers `NONE/NONE`
- Amendment lineage: `2026-08-28 / P4D-COMP-REV-F2 / SPEC R3, review-gate sequencing, and accepted A7A Core prerequisite-base reconciliation`
- BUILD authority: `SUSPENDED` pending independent amendment review and
  authorization rereview
- Provider/credential/install/database/deploy authority: `NONE`

## 1. Objective and bounded claim

Implement only the accepted P4-D boundary: packaged typed channel delivery
contracts, one digest-only HMAC-signed generic outbound webhook adapter, and
deterministic Zalo/WhatsApp `CONFORMANCE_ONLY` mocks. Integration Edge remains
the sole P4-C receipt/state owner and receives only the minimal activation,
scope-tuple and adapter-result mapping amendment.

The BUILD may create network-capable stdlib transport code, but no BUILD,
test, review or FREEZE command may make an external HTTP/DNS/provider call or
read a real credential. Evidence is deterministic zero-network contract
evidence. It proves neither live delivery, vendor conformance, receiver replay
enforcement, CVF governance behavior, production readiness nor deployment.

The separately governed exact-seven A7A Core target refresh received independent
`COMPLETION_REVIEW_PASS` and was committed and pushed as
`b3f2431aceebb401072c806ed876059cf5f85a52`. That prerequisite changed no P4-D
exact-54 path; all 54 current paths and their P4-D bytes/existence were
preserved. Objective, risk, changed-set ceiling, ownership and external-effect
authority are unchanged. Every final diff, staged-set comparison and
base/remote check in this Work Order is measured against `b3f2431aceebb401072c806ed876059cf5f85a52`.

## 2. Exact final changed-set ceiling — 54 paths

The final tranche diff against the execution base shall contain exactly these
54 paths. Every path has one owner class. No role may create, rename, delete or
edit another path. A missing or extra path stops work and requires an
independently reviewed Work Order amendment.

### A. Settled governance packet — paths 1–8

These paths are read-only to the IMPLEMENTATION_WORKER, REVIEWER and CLOSER,
except that this Work Order may receive an independently authorized amendment.

1. `docs/decisions/DESIGN_2026-08-26_P4D_CHANNEL_ADAPTERS.md`
2. `docs/decisions/P4D_CHANNEL_ADAPTERS_DESIGN_REVIEW_2026-08-26.md`
3. `docs/specs/P4D_CHANNEL_ADAPTERS_SPEC.md`
4. `docs/decisions/P4D_CHANNEL_ADAPTERS_SPEC_REVIEW_2026-08-26.md`
5. `docs/cvf/invariants/p4d-adapter-result-outcomes.json`
6. `docs/specs/p4d_invariant_pins.py`
7. `docs/cvf/invariants/registry.json`
8. `docs/work_orders/P4D_CHANNEL_ADAPTERS_WORK_ORDER.md`

### B. IMPLEMENTATION_WORKER — paths 9–40 (exactly 32)

9. `pyproject.toml`
10. `packages/channel-sdk/README.md`
11. `packages/channel-sdk/src/channel_sdk/__init__.py`
12. `packages/channel-sdk/src/channel_sdk/delivery.py`
13. `packages/channel-sdk/src/channel_sdk/invariants.py`
14. `packages/channel-sdk/src/channel_sdk/ports.py`
15. `packages/channel-adapters/README.md`
16. `packages/channel-adapters/pyproject.toml`
17. `packages/channel-adapters/src/channel_adapters/__init__.py`
18. `packages/channel-adapters/src/channel_adapters/egress.py`
19. `packages/channel-adapters/src/channel_adapters/transport.py`
20. `packages/channel-adapters/src/channel_adapters/signing.py`
21. `packages/channel-adapters/src/channel_adapters/generic_webhook.py`
22. `packages/channel-adapters/src/channel_adapters/conformance.py`
23. `apps/integration-edge/pyproject.toml`
24. `apps/integration-edge/src/integration_edge/main.py`
25. `apps/integration-edge/src/integration_edge/outbound/__init__.py`
26. `apps/integration-edge/src/integration_edge/outbound/service.py`
27. `apps/integration-edge/src/integration_edge/outbound/scope.py`
28. `contracts/channel/adapter-delivery.schema.json`
29. `tests/unit/test_p4d_channel_sdk.py`
30. `tests/contract/test_p4d_adapter_schema.py`
31. `tests/unit/test_p4d_adapter_invariants.py`
32. `tests/unit/test_p4d_generic_webhook.py`
33. `tests/security/test_p4d_webhook_egress.py`
34. `tests/security/test_p4d_webhook_hmac.py`
35. `tests/unit/test_p4d_conformance_mocks.py`
36. `tests/unit/test_p4d_outbound_mapping.py`
37. `tests/integration/test_p4d_composition.py`
38. `tests/unit/test_p4d_dependency_boundary.py`
39. `tests/unit/test_p4c_outbound.py`
40. `docs/decisions/P4D_CHANNEL_ADAPTERS_WORKER_RETURN_2026-08-26.md`

### C. INDEPENDENT REVIEWER — paths 41–42

41. `docs/decisions/P4D_CHANNEL_ADAPTERS_WORK_ORDER_AUTHORIZATION_REVIEW_2026-08-26.md`
42. `docs/decisions/P4D_CHANNEL_ADAPTERS_COMPLETION_REVIEW_2026-08-26.md`

Path 41 may authorize BUILD only after independently checking this Work Order.
Path 42 is the sole completion-review record and may be appended for bounded
rereviews and final closure audit. Neither reviewer path is worker-editable.

### D. CLOSER / SESSION_SYNC_STEWARD — paths 43–54

43. `CVF_SESSION/ACTIVE_SESSION_STATE.json`
44. `IMPLEMENTATION_STATUS.json`
45. `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json`
46. `SESSION/ACTIVE_SESSION_STATE.json`
47. `SESSION/SESSION_MEMORY.md`
48. `SESSION/handoffs/P4D_CHANNEL_ADAPTERS_2026-08-26.md`
49. `docs/INDEX.md`
50. `docs/implementation/EXECUTION_ROADMAP.md`
51. `knowledge/PROJECT_CONTEXT.md`
52. `knowledge/manifest.json`
53. `docs/catalog/MODULE_REGISTRY.json`
54. `docs/catalog/MODULE_CATALOG.md`

The CLOSER may edit paths 43–54 only after source review permits closure sync.
The module registry is updated for actual SDK, adapter and Edge truth; the
Markdown catalog is generated, never hand-edited. Knowledge pins are refreshed
only after status, registry and roadmap reach their final reviewed bytes.

## 3. BUILD obligations

### 3.1 Packaged SDK contract

- Implement the frozen, extra-forbid `AdapterDeliveryRequestV1`,
  `AdapterDeliveryResultV1`, `AdapterMode`, `AuthorizedEndpointV1` and narrow
  ports exactly as SPEC R4–R6 and R11–R12 require.
- `OutboundAdapterPort.deliver` accepts only the typed request plus exact
  idempotency key and returns only the typed result. Remove the authoritative
  `evidence_eligible`/arbitrary-mapping behavior; no second contract owner is
  introduced.
- `channel_sdk.invariants` shall pin and validate
  `P4D-ADAPTER-RESULT-OUTCOMES` at canonical digest
  `f09811c29e94de7a93300a1dc4aa8ed6eae3a9bd83418840089c5156224bfb6d`.
  The P4-C receipt pin remains
  `41f42d0b2585201a41fbed3b9f2d7e6bfd9f2adf4f2f587890addc0a7d4604a6`.
- The schema at path 28 shall be closed Draft 2020-12 and remain semantically
  equivalent to the Python request/result models for every accepted matrix
  positive and deterministic one-fact mutation.

### 3.2 Generic webhook package

- `channel-adapters` may depend only on the existing pinned Pydantic runtime,
  `channel-sdk`, and Python standard library. Add no `requests`, `httpx`, SDK,
  plugin framework or other external dependency.
- Implement immutable validated config, endpoint authorization, injected DNS
  resolution, the two-step resolved HTTPS port, exact HMAC v1 construction,
  the one-send adapter and deterministic result classification from the SPEC.
- The concrete stdlib transport may use only `socket`, `ssl`, `http.client`
  and related standard-library primitives. It must not use ambient proxies,
  perform a second DNS resolution, follow a redirect, change authority or send
  before peer/TLS validation.
- `generic-webhook` is exact `DEPLOYABLE`. The Zalo and WhatsApp mocks and the
  matrix emitter live in `conformance.py`, are permanently
  `CONFORMANCE_ONLY`, perform zero I/O and contain no vendor format/SDK claim.
- All request data remains digest-only. Endpoint, key id and key bytes never
  come from the delivery command. Tests may use only explicitly labeled
  synthetic bytes such as `b"unit-test-key"`.

### 3.3 Minimal Integration Edge amendment

- `integration_edge.main:create_app` is the only production import/composition
  owner for `channel_adapters`; domain modules never import a concrete adapter.
- The exact indivisible scope tuple is checked before adapter invocation.
  Zero or duplicate matches, missing prerequisite, unknown/missing adapter or
  either conformance-only id retains P4-C zero-attempt
  `ADAPTER_UNAVAILABLE`.
- `OutboundService` projects only the typed digest request, invokes the adapter
  at most once and maps valid results through the SPEC's total cross-family
  mapping. It remains the sole receipt/persistence owner.
- Escaped exceptions and malformed results conservatively persist attempted
  `OUTCOME_UNKNOWN`; no generic webhook path emits `DELIVERED`; no retry is
  added.
- Do not change ingress, raw evidence, quarantine, rate-limit semantics,
  storage, public routes, P4-E identity/conversation placement or business
  truth.

### 3.4 Dependency and size boundaries

- Root pytest configuration may add only `packages/channel-adapters/src`.
- Edge packaging may declare only the local `channel-adapters` dependency; no
  package is installed or upgraded in this tranche.
- Every new/changed Python file stays within the hard 300-line guard. Split
  behavior only among the already listed paths; a new path requires amendment.
- The legacy `packages/channel-sdk/adapter-interface/adapter.py` remains
  untouched, non-authoritative and outside the exact-54 changed set. No BUILD
  action may remove, replace or edit it. Tests shall prove no product/test
  import reaches it or violates the accepted dependency direction. This is the
  amended SPEC R3 disposition submitted to resolve the contract contradiction
  recorded as `P4D-COMP-REV-F2`; it does not change objective, risk, external effects,
  worker scope or the exact 54 paths.

## 4. Shared invariant-family proof

- **Applicability:** `APPLICABLE`, registered family
  `P4D-ADAPTER-RESULT-OUTCOMES`; P4-C receipt mapping separately references
  `P4C-OUTBOUND-TERMINAL-OUTCOMES`.
- **Canonical digests:** P4-D `f09811c29e94de7a93300a1dc4aa8ed6eae3a9bd83418840089c5156224bfb6d`;
  P4-C outbound `41f42d0b2585201a41fbed3b9f2d7e6bfd9f2adf4f2f587890addc0a7d4604a6`.
- **Declared emitter:** `channel_adapters.conformance:emit_adapter_result`,
  deterministic and synthetic only.
- **Declared evidence paths:**
  `tests/unit/test_invariant_family_contract.py` and
  `tests/integration/test_invariant_family_repository_guard.py`; path 31 adds
  real P4-D model/schema/adapter samples without becoming another semantic
  owner.
- **Mutation exclusions:** only the matrix-declared flat-shape
  `RECURSE_NESTED_OBJECTS` exclusions apply, with their recorded reasons and
  required independent acknowledgment. No worker-added exclusion or waiver is
  permitted.
- **Evidence owner:** IMPLEMENTATION_WORKER returns the conformance summary and
  raw samples; the independent reviewer recomputes and approves or rejects it.
- **Reviewer recomputation:** recompute both canonical digests, rerun the full
  mutation corpus, sample at least one raw emitted positive for every P4-D
  outcome, validate every declared surface, and prove expected values were
  read from the pinned matrix rather than derived from BUILD output.

Exact invariant commands:

```powershell
python scripts/check_invariant_families.py --json
python -m pytest -q tests/unit/test_invariant_family_contract.py tests/integration/test_invariant_family_repository_guard.py tests/unit/test_p4d_adapter_invariants.py
```

Any digest, registry, ownership, positive, mutation or parity mismatch stops
BUILD/REVIEW; no pin refresh is permitted inside this Work Order.

## 5. Pre-BUILD gate

Immediately before the first BUILD edit, the IMPLEMENTATION_WORKER shall:

1. rehydrate current continuity, declare `IMPLEMENTATION_WORKER`, and append
   the Work Order acknowledgment to path 48 through the ORCHESTRATOR or
   SESSION_SYNC_STEWARD; the worker itself may not edit path 48;
2. verify HEAD and local `origin/main` both equal the execution base, staged
   set is empty, and path 41 contains `AUTHORIZATION_REVIEW_PASS` with
   findings/waivers `NONE/NONE`;
3. recompute the Work Order SHA-256 and both matrix digests;
4. verify Python 3.13.12 and Pydantic 2.10.6 from the installed environment,
   without resolving or installing anything;
5. run session, Project Knowledge, invariant, catalog and file-size guards;
6. record zero provider, external HTTP/DNS, credential, install, database,
   deployment, commit and push counters.

The protected assessment
`docs/decisions/ASSESSMENT_2026-07-23_OPERATIONS_WORKSPACE_REPOSITIONING.md`
shall never be opened, read, hashed, inventoried, staged, edited or used. Do
not use a broad untracked-file inventory or any repository validator that
recursively inventories that path. Use scoped path checks and the direct
constituent guards named here.

## 6. Required deterministic BUILD evidence

### 6.1 Focused test gate

```powershell
python -m pytest -q tests/unit/test_p4d_channel_sdk.py tests/contract/test_p4d_adapter_schema.py tests/unit/test_p4d_adapter_invariants.py tests/unit/test_p4d_generic_webhook.py tests/security/test_p4d_webhook_egress.py tests/security/test_p4d_webhook_hmac.py tests/unit/test_p4d_conformance_mocks.py tests/unit/test_p4d_outbound_mapping.py tests/integration/test_p4d_composition.py tests/unit/test_p4d_dependency_boundary.py tests/unit/test_p4c_outbound.py tests/unit/test_p4c_models_schema.py tests/unit/test_p4c_invariant_emitters.py tests/integration/test_p4c_inmemory_edge.py tests/integration/test_p4c_sqlite_edge.py
```

The focused evidence must include:

- all request/result model and schema positives plus extra-field/alias/type
  negatives and every P4-D matrix mutation;
- exact resolver/connect/secret/send spy counts at every pre-attempt and
  attempted terminal stage, including no retry;
- scheme, user-info, query, fragment, IP literal, host/port/path, percent/
  dot-segment, empty DNS and every non-global address-class refusal;
- all-global mixed IPv4/IPv6 acceptance, mixed disallowed-set refusal, changed
  resolution/substituted peer, ambient proxy variables and TLS-name mismatch;
- wrong-peer tests proving body, signature header and key resolver are not
  disclosed/called before authorization;
- body/audience/key/timestamp/idempotency HMAC mutations, header allowlist,
  response bounds/classification, secret-free telemetry and sender-generated
  delivery-id determinism;
- runtime refusal of Zalo/WhatsApp, their zero-I/O direct conformance corpus,
  sole composition ownership, no reverse/legacy/dynamic import and unchanged
  P4-C receipt/state ownership.

All socket, resolver and HTTPS objects in tests are injected fakes/spies or
fully patched stdlib boundaries. A test that reaches OS DNS/socket/network is
a failure, not evidence.

### 6.2 Full regression gate

```powershell
python -m pytest -q --deselect tests/integration/test_xr1s_workspace_link_descriptor.py::test_operations_authorized_contract_is_reciprocal_when_sibling_present
```

The single deselection is the settled XR1 sibling historical-object debt. No
other deselection, ignored failure or expectation rewrite is permitted.

### 6.3 Repository and disclosure gates

Run and record:

```powershell
python scripts/check_invariant_families.py --json
python scripts/check_project_knowledge.py
python scripts/check_session_state.py
python scripts/generate_catalog.py --check
python scripts/check_file_size.py
git diff --check -- <the exact 54 paths>
git diff --cached --name-only
```

The CLOSER runs `python scripts/generate_catalog.py --write` only after source
review, then reruns all five direct guards. The broad repository validator is
not used because its recursive inventory violates the protected assessment
boundary; its relevant direct constituent guards above are mandatory.

Secret/disclosure scan is limited to paths 9–40 and must report no private-key
PEM, bearer token, API/access key assignment, credential URL, real JWT or
provider key pattern. Exact allowlisted test text is limited to explicitly
labeled synthetic HMAC bytes; it must never be logged or represented as a real
credential. Inspect emitted telemetry/receipts separately and record
`SECRET_SCAN_HITS=NONE`.

## 7. Independent REVIEW contract

The independent reviewer shall not have implemented or repaired BUILD source.
It shall compare accepted DESIGN/SPEC, Work Order, all 32 worker paths, raw test
outputs and exact diff; independently rerun focused, invariant and full-suite
gates; inspect one raw positive per P4-D matrix outcome; and adversarially
exercise attempt ambiguity, SSRF/rebinding/proxy/TLS, HMAC audience/key
mutation, mock activation and dependency direction.

Any finding returns only named repair scope to a separate REPAIR_WORKER within
paths 9–40. At repair round three without an independently new root cause,
stop, record `REVIEW_COST_ESCALATION_REQUIRED` in path 42, and obtain a
reviewed amendment before more repair. Failed tests, incomplete samples,
waivers, path drift or secret/external-effect ambiguity prohibit REVIEW PASS.

Independent `SOURCE_REVIEW_PASS` with findings/waivers `NONE/NONE` may release
only paths 43–54 for closure sync. Catalog-only metric/generated-Markdown drift
caused by the accepted worker source may be recorded at source review as
deferred CLOSER-owned evidence; no product or test failure may be deferred,
waived or converted into catalog drift. `SOURCE_REVIEW_PASS` is not final and
does not authorize FREEZE, commit or push.

`FINAL_REVIEW_PASS` may be issued only after closure sync and the post-closure
test/guard/diff rerun have received an independent audit with findings/waivers
`NONE/NONE`. It is required before FREEZE, commit or push. The reviewer cannot
self-close, edit paths 43–54, commit or push.

## 8. CLOSER / SESSION_SYNC contract

After `SOURCE_REVIEW_PASS`, the CLOSER and SESSION_SYNC_STEWARD shall update
only paths 43–54, in source-pin order:

1. update real module facts for `channel-sdk`, `channel-adapters` and
   `integration-edge`, then generate path 54 from path 53;
2. record P4-D bounded implementation truth in status and roadmap without
   claiming live delivery, vendor conformance, governance behavior, production
   or P4-E;
3. refresh Project Knowledge text and only the source pins whose bytes changed;
4. index the accepted SPEC, Work Order and reviews;
5. synchronize canonical session memory/state, bootstrap, compatibility mirror
   and active handoff as `REVIEW / FINAL_AUDIT_PENDING`, with exact evidence
   and P4-E fresh INTAKE recorded only as the proposed post-FREEZE move;
6. rerun focused/full tests when closure edits can affect collection, plus all
   direct guards, exact-54 diff, secret scan and staged-zero check;
7. return the closure set and post-closure rerun evidence for the independent
   reviewer’s final audit in path 42. If that audit does not issue
   `FINAL_REVIEW_PASS`, remain in REVIEW and repair only accepted findings;
8. only after `FINAL_REVIEW_PASS`, mechanically synchronize paths 43–54 to
   `FREEZE / CLOSED_BOUNDED` and make P4-E fresh INTAKE the next governed move,
   without changing product source, catalog facts or reviewed evidence; rerun
   the direct guards, exact-54 diff and staged-zero check before commit.

No CLOSER may fill missing product evidence, suppress a failure or infer a live
claim from mock/spy output.

## 9. External effects and commit ownership

BUILD/REVIEW/CLOSURE permits no external HTTP/DNS/provider request, real
credential access, dependency install/upgrade, database action, deployment,
destructive operation, commit or push.

After `FINAL_REVIEW_PASS`, synchronized `FREEZE / CLOSED_BOUNDED`, exact-54
diff, all guards PASS and staged zero, the sole commit owner is
`COMMIT_STEWARD`. Under the operator’s retained full-tranche authority, it may
stage only the 54 paths, verify the staged set equals them exactly, create one
new non-amended commit named for P4-D and its deterministic verification, and
push that commit to `origin/main`. Force-push, amend, history rewrite, tag,
release and deployment are forbidden. The Git push is the only closure network
effect; it grants no product/provider network authority.

Any base/remote drift before commit or push returns to the ORCHESTRATOR for
reconciliation; it is not silently merged.

## 10. Stop and return conditions

Stop immediately on any failed gate, unexpected path, changed matrix/pin,
missing dependency, install need, OS network attempt, provider/credential
discovery, secret disclosure, second composition owner, non-digest outbound
data, retry, ambiguous external effect, deployment need, protected-assessment
contact, or objective/risk/claim/commit-owner change.

The IMPLEMENTATION_WORKER writes path 40 and returns
`READY_FOR_INDEPENDENT_COMPLETION_REVIEW` only with the exact worker set and
all deterministic evidence. It shall not author path 42, declare FREEZE,
commit or push.

Amendment disposition:
`READY_FOR_INDEPENDENT_AMENDMENT_AUTHORIZATION_REVIEW`.

BUILD repair remains suspended until independent SPEC amendment review passes
and path 41 records an independent amendment authorization rereview with
findings/waivers `NONE/NONE`.
