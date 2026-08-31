# Independent Authorization Review — CVF Public-Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-29`
- Review date: `2026-08-29`
- Role: `INDEPENDENT_AUTHORIZATION_REVIEWER`
- Risk: `R2`
- Reviewed Work Order raw SHA-256:
  `6498b5cbd49f98caa368f719190d01fb62348af1ca2cee5478df0d1f731425d6`
- Disposition: `AUTHORIZATION_REVIEW_CHANGES_REQUIRED`

## Review boundary

This review rehydrated current canonical continuity and then used only
allowlisted local reads and deterministic local guards. Its sole mutation is
this reviewer-owned artifact. It performed no network or doctor call,
reconciler or initializer execution, hidden-Core/workspace-root/product/
continuity mutation, provider call, credential use, installation, database
action, deployment, commit or push. It did not touch, read, hash or inventory
the protected operator assessment and performed no broad untracked inventory.

An eventual `AUTHORIZATION_REVIEW_PASS` would make the corrected contract
eligible only for a later explicit BUILD/external-effect boundary decision. It
would not itself authorize BUILD, network use, Core/root mutation or any other
external effect.

## Recomputed contract bindings

| Artifact | Raw SHA-256 | Result |
|---|---|---|
| Accepted DESIGN | `2e383c0918a77d3262b9a065e8cbeca5a4e5798dfd7e4771c311f4f0af049443` | matches Work Order |
| Accepted DESIGN amendment | `2f250e98914f671b19f7be3a820f2b216c277e8f8900e2f77ceaab69255a44e0` | matches Work Order |
| Final SPEC | `03932a375516ff100e452a40c92fa4886e5e4b1bb10488d446dc8faa162b4f01` | matches Work Order |
| Final SPEC review | `5b77e40c103cdab1a648a06d60595cc0a07aaeb65e856688c36d664e265b5890` | matches Work Order |
| Invariant matrix raw/canonical digest | `5f6e477d8d76e11965c91c0034f0ff4f7d82e1beab5d41c2266526957a5a8025` | matches Work Order and machine pin |
| Registry | `ec2ff31d7a72154b7a2f21c189e9164e455360228f44591b1a45842babf971d5` | family/path/owner/risk/lifecycle match |
| Machine pin | `6ad871371d551ff55ca263a0d605573176e5218108b8e3032888e4cfe84511ae` | pinned symbol equals canonical digest |

The manifest still binds the old full Core commit
`a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`; policy requires live evidence,
allows mock only for UI, enforces phase transitions and has risk ceiling `R2`.

## Independently verified authorization properties

1. Workspace, project, Core, public remote and fresh contained evidence paths
   are fixed. The sanctioned reconciler and initializer commands use exact
   paths and arguments; manual network commands, extra flags, retries,
   credentials and a separate worker doctor are forbidden.
2. The reconciler is bounded to the exact ordered 17 workspace-root targets,
   with `17/17` accounting for success and complete rollback. The initial
   worker ceiling is exactly 13 tracked downstream paths plus one ignored
   binding effect.
3. The two full-pin edits occur only after the reconciler proves the frozen
   target and before initializer execution. Success requires the ordered
   three-operation worker graph and five-way target equality.
4. Preflight freezes containment, old-Core/downstream state, command/contract
   hashes, active profile, fresh destinations, future evidence pre-states,
   recoverable Core/root/carrier preimages, parked P4-E hashes and prior backup
   inventory. Every mismatch stops before external effect.
5. Initial worker, completion reviewer, target-movement repair worker,
   terminal rereviewer, closer and inactive commit steward are separated.
   Reviewer-owned paths cannot be created by a worker, and no reviewer may
   approve an artifact it authored.
6. The immutable root receipt, worker return and target-movement completion
   review remain outside repair mutation authority. The conditional rollback
   JSON and terminal rereview Markdown retain separate owner-only
   `ABSENT → CREATE` lifecycles and non-circular final-hash ownership.
7. Reviewer-time movement permits only the reviewed temporal intersection for
   restoration and truthful failure continuity. It never permits a new target,
   reconciliation retry, product/provider effect, commit or push.
8. Initial and conditional incomplete rollback states forbid fabricated
   restoration facts and retain narrow observed-state reporting. The one open
   verifier-cardinality defect below prevents final authorization.

## Invariant-family proof

- **Applicability decision:** registered active family
  `CVF-CORE-REFRESH-OUTCOMES-2026-08-29`; R2 shared receipts, conditional
  outcome fields, counters, multiple validator surfaces and prior adjacent
  findings make it applicable.
- **Matrix id / canonical digest:**
  `CVF-CORE-REFRESH-OUTCOMES-2026-08-29` /
  `5f6e477d8d76e11965c91c0034f0ff4f7d82e1beab5d41c2266526957a5a8025`.
- **Adapter / test paths:** matrix-declared inline synthetic identity
  `CVF_CORE_REFRESH_WORKER_AND_MOVEMENT_ROLLBACK_INLINE_ADAPTER_V2` with no
  tracked adapter path; evidence tests are
  `tests/unit/test_invariant_family_contract.py` and
  `tests/integration/test_invariant_family_repository_guard.py`.
- **Mutation exclusions:** `NONE`; independently acknowledged.
- **Exact commands:** `python scripts/check_invariant_families.py --json` and
  `python -m pytest -q tests/unit/test_invariant_family_contract.py
  tests/integration/test_invariant_family_repository_guard.py`.
- **Evidence owner:** initial `IMPLEMENTATION_WORKER` or conditional
  `REPAIR_WORKER`; independent terminal reviewer/rereviewer recomputes the
  returned conformance evidence.
- **Reviewer recomputation:** canonical digest matched the pin; all `5/5`
  in-memory matrix-derived raw positives matched exactly one intended shape;
  sample digests were `f014ba5e…`, `0c719689…`, `b404e540…`, `0cb51049…` and
  `24dbfb6e…`; the complete generated corpus contained `400` one-fact
  mutations and all `400/400` were rejected. The focused 40-case stage/
  verifier cross-product returned `20` accepted, `20` rejected and zero
  mismatch. No BUILD output exists at this authorization gate, so these
  expectations were derived only from the pinned matrix; completion review
  must independently recompute the later worker evidence.

## Numbered finding

1. **`CORE-REFRESH-AUTH-REV-F1` — complete rollback verifier cardinality is
   weaker than the accepted SPEC and matrix.** Work Order section 3 permits a
   rollback worker to run the verifier “at most once,” and section 7 says it
   may “optionally” run the verifier before recording either a complete or
   incomplete rollback outcome. Final SPEC R10 and both complete matrix shapes
   require exactly `ONE_RECORDED` for `FAILURE_ROLLED_BACK` and
   `REVIEW_TARGET_MOVEMENT_ROLLED_BACK`. As written, an implementation worker
   could claim complete rollback with zero verifier while conforming to the
   Work Order but violating the accepted SPEC and invariant contract.

   Repair the Work Order so every complete initial or reviewer-movement
   rollback must execute and record exactly one rollback-verifier doctor after
   restoration. Preserve `NOT_RUN` only for an incomplete rollback that fails
   before the verifier and the closed transcript-dependent incomplete tokens
   already defined by final SPEC/matrix. Do not add a retry, extra doctor,
   command, path or external-effect authority.

## Waivers

`NONE`.

## Deterministic local guards

- Authorization-review artifact pre-state: `ABSENT`.
- JSON parsing for manifest, policy, matrix and registry: `PASS`.
- Session-state/mirror guard: `PASS`.
- Project Knowledge guard: `PASS`.
- Invariant-family repository guard: `PASS` with no diagnostics.
- Focused invariant tests: `35 passed, 2 skipped`.
- Five positive/full mutation/cross-product conformance: `PASS`.
- Catalog drift guard: `PASS` (`26` modules).
- File-size guard: `PASS`.
- Scoped Work Order diff check before reviewer receipt: `PASS`.
- Staged set: empty.

## Final disposition

`AUTHORIZATION_REVIEW_CHANGES_REQUIRED` — finding
`CORE-REFRESH-AUTH-REV-F1` is open; waivers `NONE`.

Return only F1 to a declared `REPAIR_WORKER`, then route the repaired Work
Order to a fresh independent authorization rereviewer. BUILD,
reconciliation/network/root effects, P4-E SPEC, commit and push remain
unauthorized.

---

## Independent authorization rereview — F1 closure — 2026-08-29

- Role: `INDEPENDENT_AUTHORIZATION_REREVIEWER`
- Recomputed repaired Work Order raw SHA-256:
  `1de50c0f4545f975aa415cde4924db02b401a191a7703c6ec2d272d6c994518f`
- Finding `CORE-REFRESH-AUTH-REV-F1`: `CLOSED`
- Adjacent findings: `NONE`
- Waivers: `NONE`
- Disposition: `AUTHORIZATION_REVIEW_PASS`

### Rereview boundary

This fresh rereview rehydrated current canonical continuity and inspected only
the repaired Work Order, prior authorization review and already accepted local
contract artifacts. Its sole mutation is this appended reviewer-owned section.
It performed no network or doctor call, reconciler or initializer execution,
hidden-Core/workspace-root/product/continuity mutation, provider call,
credential use, installation, database action, deployment, commit or push. It
did not touch, read, hash or inventory the protected operator assessment and
performed no broad untracked inventory.

### Closure of `CORE-REFRESH-AUTH-REV-F1`

`CLOSED`. The repaired Work Order now matches final SPEC R10 and the pinned
matrix:

1. Any complete initial rollback or complete reviewer-movement rollback must
   invoke and record exactly one rollback-verifier doctor after restoration.
2. An incomplete rollback that fails before the verifier records `NOT_RUN` and
   cannot claim complete restoration.
3. Failure of the verifier itself records only the closed transcript-observable
   incomplete verifier state selected by the matrix; it cannot become a
   complete outcome.
4. The existing post-verifier initial-worker and shared-continuity write tokens
   remain unchanged and matrix-owned.

The repair adds no command, path, retry, doctor count, target, credential,
network endpoint, role authority or external-effect permission.

### Adjacent-risk result

No adjacent finding was identified. Exact two-pin sequencing, the ordered
three-operation success graph, 17-root and 13-initial-path ceilings, temporal
reviewer-movement rollback ownership, immutable prior evidence, owner-only
conditional evidence paths, stop conditions and invariant-family proof remain
unchanged.

### Deterministic local guards

- Session-state/mirror guard: `PASS`.
- Project Knowledge guard: `PASS`.
- Invariant-family repository guard: `PASS` with no diagnostics.
- Focused invariant tests: `35 passed, 2 skipped`.
- Catalog drift guard: `PASS` (`26` modules).
- File-size guard: `PASS`.
- Scoped Work Order/review diff check before this append: `PASS`.
- Staged set: empty.

### Final rereview disposition

`AUTHORIZATION_REVIEW_PASS` — F1 is closed; findings `NONE`, waivers `NONE`.

This pass only accepts the bounded Work Order as eligible for a later explicit
BUILD/external-effect boundary decision. It does not grant BUILD, network,
reconciliation, hidden-Core/workspace-root mutation, P4-E SPEC, commit or push.
