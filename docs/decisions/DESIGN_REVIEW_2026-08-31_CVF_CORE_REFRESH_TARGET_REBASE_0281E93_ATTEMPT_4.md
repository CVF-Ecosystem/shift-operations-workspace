# Independent DESIGN Review — CVF Public-Core Exact-Target Rebase 0281e93 — Attempt 4

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-0281E93-ATTEMPT-4-2026-08-31`
- Phase reviewed: `DESIGN`
- Risk: `R2`
- Role: `INDEPENDENT_DESIGN_REVIEWER`
- Date: `2026-08-31`
- Reviewed artifact:
  `docs/decisions/DESIGN_2026-08-31_CVF_CORE_REFRESH_TARGET_REBASE_0281E93_ATTEMPT_4.md`
- Final reviewed raw SHA-256:
  `8c1f2a67dcd9f3e67b4b04f4cb950f990889bf3f811417b3ca087d4799ef9e13`
- Original reviewed raw SHA-256:
  `dd84719f858355e0babbb4fedd6fb63a17884527be1d6b67e8cb4367f98385b1`
- Disposition: `DESIGN_REVIEW_PASS`
- Prior findings: `DR4-F1`, `DR4-F2`, `DR4-F3`, `DR4-F4` — `CLOSED`
- Findings: `NONE`
- Waivers: `NONE`

## Review boundary and independence

This reviewer is distinct from the Attempt-4 DESIGN author, INTAKE author and
INTAKE reviewer, and from the Attempt-3 Work Order, implementation and
completion roles. Review used only exact local allowlisted reads, hashes,
explicit path-existence checks and read-only Git/object facts. It did not run
doctor, fetch, reconciler, initializer, provider, P0, fixture tests, broad
downstream inventory, commit or push. It did not open, name, hash, inventory,
stage or use the protected operator assessment.

This review creates only this artifact. It does not edit the DESIGN or
continuity and does not create the carrier, SPEC, Work Order, invariant
matrix/pin, execution/evidence directory, worker receipt, completion review,
rollback record or terminal rereview.

## Accepted lineage and collision checks

The exact reviewed DESIGN hash matches the delegated review target. Its
accepted INTAKE and INTAKE-review hashes match the current accepted lineage:

| Artifact | SHA-256 |
|---|---|
| Attempt-4 INTAKE | `83261bd4186e2aac0b16962332c3f8691c2ef9777b4493ff831ba856bd9dba2f` |
| Attempt-4 INTAKE review | `d4f6c530db95f1d8d19c3c867107157cc3f0a62b12a31bb31613801b427a6293` |
| Attempt-3 completion review | `004ce65b653abe23270d8da01528584eef52aeccd06a5e706ba6925ab0b59239` |
| Attempt-3 Work Order | `9e44eb5540fec4b7b3c35e035bf57d26a9be0be2c5d92dbd2963ef7946f7e8b5` |

Attempt 3 is correctly treated as an immutable, reviewed zero-effect
preflight refusal caused by worker-authored temporary wrapper bytes, not by
the prior Work Order bytes. Attempt 4 neither retries nor repairs Attempt 3
in place.

Exact `Test-Path -LiteralPath` checks found all six proposed Attempt-4
execution/review paths, all six proposed pre-BUILD lifecycle paths and both
proposed invariant-family paths absent. Their names are collision-free with
Attempts 1–3. This is only a current local design fact; the future Work Order
must recheck absence, resolved containment and reparse escape.

## Sound portions of the design

Subject to the blocking findings below, these boundaries are coherent and
should be retained:

- exact old pin, frozen target and public remote, with no in-attempt retarget;
- one-attempt, no-retry/no-hotfix behavior and preservation-first rollback;
- explicit `P0-A` regression and `P0-B` Attempt-4 family layers before
  evidence creation or external effect;
- exact `17/17` workspace-root accounting, the `13`-path initial downstream
  ceiling, ignored binding boundary and conditional reviewer-movement roles;
- ordered successful network prefix
  `RECONCILER_CLONE/INITIALIZER_FETCH/INITIALIZER_DOCTOR_FETCH` and separate
  reviewer/rollback-doctor authority windows;
- `TRIGGERED` invariant-family applicability with a new matrix and pin owned
  by SPEC, leaving the Attempt-3 matrix immutable;
- protected fixture, P4-E, XR1, assessment, product/runtime/database,
  install/deploy/release and commit/push boundaries; and
- bounded claims that do not assert AI/provider governance and therefore do
  not require a provider call in this DESIGN review.

## Findings

### DR4-F1 — Executable carrier authoring is assigned to the wrong phase

Section 2 assigns the `WORK_ORDER_AUTHOR` to create a `.ps1` containing the
complete executable effect graph, then calls that creation inert because the
script is not invoked. Non-invocation prevents an external effect, but it
does not turn implementation source into a Work Order artifact. The project
control chain says WORK_ORDER authorizes a bounded changed set and BUILD
implements only that authorized set. The accepted predecessor SPEC likewise
states that the Work Order author translates requirements into commands,
paths, hashes and stop conditions, while the implementation worker owns P0,
preservation and execution. The predecessor Work Order makes the boundary
still more explicit: `WORK_ORDER_AUTHOR owns only this document`.

Writing the operational carrier during WORK_ORDER therefore implements the
wrapper before BUILD and makes the Work Order authorize bytes that its own
author created outside an already reviewed implementation scope. Labeling the
file a governance companion does not resolve the phase inversion.

Required repair: select a phase-valid lifecycle. One valid shape is a
separate zero-external-effect carrier tranche that goes through its own
INTAKE→DESIGN→SPEC→WORK_ORDER→BUILD→REVIEW→FREEZE, after which this rebase
tranche may reference the frozen carrier path/hash. Another design is
acceptable only if it preserves the same reviewed-before-activation property
without authoring executable implementation in WORK_ORDER. The repaired
DESIGN must state exact role ownership and changed-set ceilings for both
carrier creation and later activation.

### DR4-F2 — The authority chain is not fully hash-bound and is temporally incomplete

The proposed tuple includes `AuthorizationReviewPath` but not the
authorization review's raw SHA-256. It contains neither an external-authority
record path nor its SHA-256. Section 2 says the later authority record refers
to the accepted Work Order and review, while the worker externally hashes
only the Work Order and carrier. Section 4 then requires `Execute` to validate
the authority-review identity, but a path and self-declared contents do not
identify immutable accepted bytes. A modified review at the same path, or a
different later authority decision, is not cryptographically rejected by the
declared tuple.

There is also a time-order gap: the authorization review is produced only
after it records `ParseOnly`/`DryRun` results, yet the design describes one
exact parameter tuple containing `AuthorizationReviewPath` and an exact
pre-effect decision graph. At rehearsal time that finalized review does not
exist. If DryRun validates it, rehearsal is circular; if DryRun does not, it
is not the same authority/preflight graph described for Execute.

Required repair: define an acyclic artifact graph and mode-specific input
contract. At minimum, Execute must be bound to the finalized authorization
review hash and to a separately finalized external-authority decision
path/hash. The authority decision may contain carrier, Work Order and review
hashes; the Execute invocation may then contain the authority-decision hash,
so no artifact self-hashes. ParseOnly/DryRun must use a non-circular reviewed
input set and explicitly disclose which Execute-only authority checks are
substituted or deferred. The later worker must independently recompute every
accepted hash before invocation.

### DR4-F3 — The claimed closed PowerShell parameter interface is not specified feasibly

Section 3 requires absence, duplication, abbreviation and every non-enumerated
Mode value to fail before carrier logic. Section 4 nevertheless gives only an
`at minimum` parameter list and relies on a normal PowerShell parameter
contract. PowerShell's native binder accepts unambiguous abbreviated parameter
names before the script body; `$PSBoundParameters` does not preserve the
original spelling. The design therefore neither freezes the complete
parameter set nor defines a mechanism that can prove `-Mo ParseOnly`, aliases,
positional binding and duplicate spellings are rejected before logic.

Required repair: freeze the full parameter surface and exact separate tuples
for ParseOnly, DryRun and Execute. Specify a realizable raw-argument dispatcher
or another reviewed invocation mechanism that observes original tokens before
semantic binding and rejects abbreviation, aliases, positional arguments,
duplicates, coercion and unknown tokens. If native PowerShell abbreviation is
intended to remain accepted, remove the contrary claim and update the exact
contract and mutation corpus accordingly. P0-B must own adversarial cases for
every rejected invocation form.

### DR4-F4 — No-effect rehearsal has a process/reachability contradiction

Section 3 says the reachable ParseOnly/DryRun graph contains no process
launcher or PowerShell invocation, while also permitting pinned read-only Git
object queries and a Python child process with
`PYTHONDONTWRITEBYTECODE=1`. Ordinary `git` and `python` calls from PowerShell
are process launches. The DESIGN does not select an in-process Git/parser
implementation, a separately reviewed read-only probe executable, or a static
reachability model capable of distinguishing forbidden launch from permitted
probe launch. `process-level network disabled where available` is also not an
exact fail-closed network-denial contract.

Consequently an authorization reviewer cannot prove the claimed closed
reachable graph from the future carrier bytes, nor demonstrate that DryRun
executes the exact local pre-effect decisions while being structurally unable
to cross the prohibited boundary.

Required repair: specify the exact rehearsal architecture. It must enumerate
every callable command/API by mode, identify whether each is in-process or a
pinned child, define a deterministic AST/call-graph rule, and define an exact
network-denial or zero-network observation contract. If read-only `git` or
Python children are permitted, narrow the prohibition to an explicit child
allowlist and prove that their arguments cannot select a network/mutating
verb. The SPEC must bind this allowlist and its negative mutation corpus into
P0-B.

## Waivers and disposition

- Waivers: `NONE`.
- Disposition: `DESIGN_REVIEW_CHANGES_REQUIRED`.

The reviewed DESIGN must not advance to SPEC. A distinct repair role may
amend the DESIGN within these four findings, after which a distinct
independent DESIGN rereviewer must review the new exact hash. Carrier
authoring, SPEC, Work Order, BUILD, doctor/fetch/reconcile, initializer,
Core/root/pin/binding/continuity or evidence mutation, fixture repair,
provider/credential use, installation, product/database work, deployment,
release, commit and push remain unauthorized.

---

## Independent DESIGN Rereview — repaired exact hash

- Rereview role: `INDEPENDENT_DESIGN_REREVIEWER`
- Repaired DESIGN raw SHA-256:
  `8c1f2a67dcd9f3e67b4b04f4cb950f990889bf3f811417b3ca087d4799ef9e13`
- Prior review pre-append raw SHA-256:
  `3e171ac9fa80b41793692606cc9e2ea8504618be026553a7612d6b10a7c5b0b9`
- Rereview disposition: `DESIGN_REVIEW_PASS`
- Prior findings: `DR4-F1`, `DR4-F2`, `DR4-F3`, `DR4-F4` — `CLOSED`
- Final findings: `NONE`
- Waivers: `NONE`
- Date: `2026-08-31`

### Rereview boundary

The rereviewer rehydrated the current DESIGN-phase continuity and reviewed
the complete repaired DESIGN at the exact hash above against the accepted
Attempt-4 INTAKE/review, the Attempt-3 refusal/completion truth, the prior
SPEC/Work Order role boundary and the invariant-family standard. Checks were
limited to exact local allowlisted reads, hashes and named path predicates.
No doctor, fetch, reconciler, initializer, carrier, P0, fixture test, provider,
credential, broad downstream inventory, external effect, commit or push was
run. The protected assessment remained excluded.

The canonical continuity front doors still project DESIGN and no external
effect. Their next-role prose predates the repaired bytes but does not claim a
different phase, target, risk or BUILD authority. This rereview changes only
the final header and appends this section to the existing review artifact. It
does not edit DESIGN or continuity and does not create any carrier or future
Attempt-4 lifecycle path.

### DR4-F1 closure — phase-valid carrier prerequisite

`DR4-F1` is closed. Attempt 4 no longer assigns executable source creation to
its Work Order author. The repaired DESIGN parks the rebase and requires the
separate `CVF-CORE-REFRESH-ATTEMPT-4-CARRIER-2026-08-31` prerequisite to pass
its own complete
`INTAKE -> DESIGN -> SPEC -> WORK_ORDER -> BUILD -> REVIEW -> FREEZE` chain.
That prerequisite has an exact implementation BUILD ceiling of only:

```text
scripts/cvf_core_refresh_target_rebase_0281e93_attempt_4_carrier.ps1
tests/cvf/test_cvf_core_refresh_target_rebase_0281e93_attempt_4_carrier.py
```

Its Work Order author owns only its Work Order; a distinct worker owns the two
implementation paths after independent authorization review. Carrier BUILD
has zero Core/root/pin/binding/continuity/rebase-lifecycle/network/provider or
deployment effect. Independent carrier REVIEW/FREEZE must publish the exact
two hashes before the rebase can transition onward. The later rebase Work
Order may reference and activate the frozen carrier but cannot create, patch,
copy, regenerate or reinterpret it. This restores phase ownership and keeps
the carrier/test protected outside the rebase BUILD ceiling.

This rereview does not open the carrier tranche. A separate ORCHESTRATOR
transition to its INTAKE remains required.

### DR4-F2 closure — acyclic mode and authority hashes

`DR4-F2` is closed. The repaired graph is ordered and acyclic:

```text
frozen carrier/review
  -> rebase SPEC/matrix/pin/review
  -> rebase Work Order
  -> ParseOnly/DryRun authorization review
  -> external-authority decision
  -> Execute/worker receipt
  -> completion review
```

ParseOnly and DryRun consume only already-finalized artifacts and explicitly
emit all authorization-review and external-authority identities as
`DEFERRED_EXECUTE_ONLY`; they no longer claim to validate future bytes. The
final authorization review owns the accepted rehearsal tuples/results and
carrier/Work Order hashes. The later external-authority decision owns the
authorization-review path/hash and exact Execute authority without
self-hashing. Execute receives and independently validates carrier, Work
Order, authorization-review and external-authority path/hash pairs. Both the
worker and carrier recompute all four raw hashes before effect. No path-only
identity, self-hash or dependency on future bytes remains.

### DR4-F3 closure — realizable exact raw-token interface

`DR4-F3` is closed. The carrier has no `param(...)` block, alias, pipeline or
positional binding. Its first operation observes the original unbound
`$args`; therefore PowerShell's semantic binder cannot silently accept a
carrier-option abbreviation before the dispatcher sees it. The DESIGN freezes
the complete case-sensitive option list, canonical order and three distinct
tuples:

- ParseOnly ends at `--CarrierSha256`;
- DryRun ends at `--SpecReviewSha256` plus `--ExecutionId`; and
- Execute carries the full finalized authority tuple.

The dispatcher rejects missing/odd/duplicate/reordered/unknown/abbreviated/
case-folded/alias/positional/combined/coercion-shaped/extra tokens before mode
logic. P0-B must freeze exhaustive per-option adversarial families, invalid
modes and cross-mode required/forbidden cases by corpus ids, expected refusal
codes, count and digest. This is sufficiently concrete for SPEC to turn into
testable requirements without relying on native parameter abbreviation.

### DR4-F4 closure — closed per-mode call graph and deterministic no-network proof

`DR4-F4` is closed. The repaired DESIGN distinguishes in-process APIs from
native children and freezes a per-mode transitive-call contract:

- ParseOnly has no child process;
- DryRun adds only hash-resolved `git.exe` behind one gateway and seven exact
  local-object/status argv forms; and
- Execute adds only hash-resolved Python for exact P0 and PowerShell for the
  sanctioned reconciler, initializer and separately authorized conditional
  rollback-verifier doctor.

The static verifier starts from three literal mode entry nodes, resolves the
function AST transitively and rejects dynamic names, unresolved calls,
ungated invocation, dot-sourcing, dynamic scriptblocks, aliases, unqualified
children or any edge absent from the mode matrix. The filesystem and network
API denylists are explicit. DryRun Git operands are root-contained and reject
transport/remote-helper syntax; all network-capable/mutating Git verbs and
configuration/credential mechanisms are denied. The closed child environment
disables prompts, helpers, proxies and optional locks.

Zero-network evidence is deterministic and bounded: all child calls must pass
the gateway; canonical telemetry owns every argv; any call outside the exact
local-query set increments and refuses `network_attempt_count` before launch;
direct network APIs are AST-forbidden; and ParseOnly/DryRun require
`network_attempt_count=0` and `network_child_count=0` with the exact local
child ledger. Carrier REVIEW and rebase authorization review must repeat this
proof on the frozen bytes. SPEC/P0-B still must materialize the mode matrix,
hash identities, mutations, counters and digests; this DESIGN review does not
pretend those future artifacts already exist.

### Remaining architecture and final disposition

The repair does not weaken the previously accepted target, P0-A/P0-B,
preimage, collision-free lifecycle, `17/17` root, `13` downstream, binding,
P1/P2/P3, rollback/reviewer-movement, invariant-family, fixture/P4-E/XR1,
protected-state, role separation, stop or claim boundaries. Exact current
checks confirm the repaired DESIGN hash above; the carrier and its test remain
absent, as required before their separately governed tranche.

Final findings are `NONE`; waivers are `NONE`. The repaired exact DESIGN is
`DESIGN_REVIEW_PASS`.

This PASS authorizes no carrier implementation and no rebase SPEC or BUILD.
The next eligible move is ORCHESTRATOR routing to a separate carrier-tranche
INTAKE. Attempt 4 remains parked until that carrier completes independent
REVIEW/FREEZE and a later explicit Attempt-4 transition binds its exact frozen
path/hash. Doctor/fetch/reconcile, Core/root/pin/binding/continuity or evidence
effects, fixture repair, provider/credential use, install, product/database
work, deployment, release, commit and push remain unauthorized.
