# Independent SPEC Review — CVF Public-Core Exact-Target Rebase 0281e93

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-0281E93-2026-08-30`
- Phase reviewed: `SPEC`
- Risk: `R2`
- Role: `INDEPENDENT_SPEC_REVIEWER`
- Disposition: `SPEC_REVIEW_PASS`
- Findings: `NONE OPEN` (`SPEC-REV-F1` CLOSED)
- Waivers: `NONE`
- Date: `2026-08-30`

## Review boundary and independence

The reviewer did not author or repair the SPEC, matrix, digest pin or registry
entry. This review compared their exact bytes with accepted INTAKE/DESIGN
lineage, the invariant-family standard and schema, the frozen conformance
machinery, the parked fixture-repair state and the sanctioned Core scripts at
both old pin and target. The protected operator assessment was not opened,
read, hashed, inventoried, staged or used. Broad downstream untracked inventory
was not performed.

No doctor, fetch, reconciler, initializer, provider call, credential access,
installation, Core/workspace-root/pin/binding/product/database/deployment
mutation, continuity edit, commit or push occurred. This review artifact is the
reviewer's sole mutation and intentionally does not self-hash.

## Exact reviewed hashes

| Artifact | SHA-256 |
|---|---|
| SPEC | `db255f14076c73bb60b6be5d1bf05ae3d939ce476fe6629e25c34de3a9e2ab82` |
| Matrix raw | `a13ecc2df613b16f4e888a085ee8d86bda40cd35aec9460aefbe1aae5c1e6333` |
| Matrix canonical UTF-8/universal-newline digest | `a13ecc2df613b16f4e888a085ee8d86bda40cd35aec9460aefbe1aae5c1e6333` |
| Static digest pin | `d69a6781fb66af563ec66d2eb7c1686029a57677deb716780a3079f9d4b288de` |
| Invariant registry | `3022d323782e2fd3cf18f377f4293b43e1637a1f14ccef96a1b3717a2ac9f0e2` |
| Invariant-family standard | `c360655acb89c6fc8e412f87289d5ef990f62c5795605a95b1d4327cd6dff402` |
| Invariant-family schema | `7313f9c9f631eacf160f2ce0ad2fdef5757eb10427fdb3574354f9a3564714e0` |
| Accepted DESIGN | `1fc8c00dd19bfd08a4b185f1fdc41fbe58991a7006248a593a5fc6fc371cb8b5` |
| Accepted DESIGN review | `78eaf8c9e7e01af721c877ed6aaa89b6446baea40e3ef05df85f8772d1088c56` |

The SPEC's accepted INTAKE and INTAKE-review hashes also recompute to
`28e1160993d2638554bdb810dd36f393eebb65db62b47b8f92b8049fc290ba53`
and `4c754b7cc47ef247453075e0633848534d121959aba7fb845d49f12975da1b8c`.
The registry has exactly one entry for the reviewed family id and matrix path.
The pin symbol equals the matrix canonical digest and the ownership binding
resolves to that exact consumer.

## Independent structural and conformance evidence

Strict duplicate-key parsing and Draft 2020-12 schema validation passed. The
matrix is a closed top-level object with eight unique outcomes and eight unique
single shapes. Required/forbidden field boundaries, scalar domains, counter
relations, field-equality relations, target/pin constants, evidence lifecycle
paths and role-owned hash fields were evaluated independently.

An inline reviewer implementation synthesized positives and implemented its
own strict domain, closed-object, relation and mutation-obligation checks. It
used the repository matcher as the second surface and compared the tracked
generator's ids against a separately derived inline oracle. Results:

| Check | Result |
|---|---:|
| Exclusive positives | `8/8` |
| Unique generated/oracle mutations | `1249/1249` |
| Temporal cross-product judgments | `40/40` (`38` accepted, `2` rejected) |
| Literal `"x"` SHA-pattern probes | `6/6` rejected by both surfaces |

Mutation counts by shape were `126`, `156`, `161`, `168`, `125`, `132`,
`211` and `170`, totaling `1249`. Operator counts were: required deletion
`301`; forbidden insertion `79`; unknown field `8`; discriminator replacement
`64`; wrong type `301`; const mismatch `275`; enum mismatch `20`; counter
mutation `168`; pattern mismatch `6`; one-sided relation change `27`. No
operator exclusion or waiver exists.

`python scripts/check_invariant_families.py --json` returned `PASS` with no
diagnostics. The required focused unit/integration command returned `28 passed,
2 skipped, 7 failed`; all seven failures have the same parked fixture-plumbing
cause: the disposable repository omits the mutation generator/oracle modules,
causing `ModuleNotFoundError` before the expected guard diagnostic. This is the
already reviewed open fixture-repair baseline, not a target-family conformance
failure. The SPEC correctly forbids repairing, suppressing or presenting it as
an unrestricted passing suite.

The read-only P0 approach is feasible with the frozen generic functions. Their
hashes match the SPEC: contract `19616eca...497`, generator
`d5f2e133...82ae`, ownership validator `71ec4c54...aac7`, independent oracle
`f9bf70a8...6cdc`, and strict harness `cae96b6e...adb9`; the two parked test
preimages remain `49dba6d8...14a7` and `44cdf845...79e6`. The adapter can call
the generic synthesis/validation functions without invoking the fixture-
specific hard-coded top-level runner.

## Target, tool, effect and temporal bindings

Local read-only Git checks confirmed clean hidden Core HEAD at
`a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`, local `origin/main` at frozen
target `0281e93bab4a75083973eb7242fd2bc8f65055d3`, and the expected public
remote. At both revisions, reconciler raw/blob are
`96ac0cce...58196c`/`4b705c6b...f4945`, doctor raw/blob are
`2410bbab...96b`/`2ad83efe...c8c`, new-workspace raw/blob are
`7e5567c5...27032`/`5f311a1a...3c5a`, and the operation tree is
`23fe8bd3...bbb6`. Downstream initializer and active profile hashes are
`bb37b162...209c8` and `f51bacd2...c855`.

The accepted 17-root ceiling, 13-path initial tracked ceiling, one ignored
binding effect, six collision-free attempt-3 paths, successful three-network
operation sequence, rollback `17/2/9/1` restoration counters, conditional
repair `11 + 1` tracked ceiling, reviewer doctor ownership and no-retry/no-
provider boundaries match the accepted DESIGN. Complete and incomplete
rollback shapes are disjoint, and the six pre/post evidence hashes belong only
to the terminal rereviewer in the reviewer-movement rollback path.

## Finding

### `SPEC-REV-F1` — parked fixture state does not determine the success outcome

The matrix does not make its two BUILD-success outcomes semantically
exclusive. Both `SUCCESS_VALID` and
`BUILD_SUCCESS_FREEZE_BLOCKED_BY_PARKED_FIXTURE_REPAIR_VALID` require
`fixture_repair_status == AUTHORIZATION_REREVIEW_CHANGES_REQUIRED`. The first
then declares `FREEZE_ELIGIBLE_IF_INDEPENDENT_REVIEW_ACCEPTS` and forbids the
blocking fields; the second declares
`FREEZE_BLOCKED_BY_PARKED_FIXTURE_REPAIR` and requires self-declared blocking
fields. No matrix-owned field, relation or conditional rule determines when
those blocking fields must exist.

Consequently, the same operational state — successful target adoption while
the fixture lineage remains parked at the exact current status — can be
reported as either terminal meaning merely by choosing the outcome,
freeze-disposition and blocking labels. One-fact mutation rejection remains
green because that ambiguity requires a correlated relabel; syntactic
discriminator exclusivity therefore does not close semantic outcome
exclusivity.

This conflicts with SPEC R3's statement that BUILD success cannot be
conflated with FREEZE eligibility while the fixture lineage remains at
`AUTHORIZATION_REREVIEW_CHANGES_REQUIRED`, and with R8's assignment of sole
semantic ownership to the matrix. R11's phrase "if the controlling FREEZE rule
requires" does not identify such a rule or owner and cannot repair the closed
grammar.

Required repair: make one matrix-owned, testable predicate select exactly one
of the two outcomes for every accepted fixture state. For the currently frozen
parked state, the grammar must not permit unrestricted `SUCCESS`/FREEZE
eligibility. Update the matrix, digest pin and SPEC references together, then
rerun independent positive, full mutation, correlated outcome-selection,
temporal and literal-`"x"` probes. Do not repair the parked fixture lineage in
this tranche.

## Waivers

`NONE`.

## Disposition and authority boundary

`SPEC_REVIEW_CHANGES_REQUIRED`.

The target/tool/effect architecture and deterministic conformance machinery
are otherwise feasible, but `SPEC-REV-F1` leaves terminal FREEZE semantics
ambiguous and must close before Work Order authoring. This review authorizes
only a bounded SPEC/matrix/pin repair and independent SPEC rereview. It does
not authorize Work Order progression, BUILD, reconciler, doctor/fetch,
Core/workspace-root/pin/binding mutation, fixture repair, provider/credential
use, installation, product/runtime/database change, deployment, commit, push
or P4-E SPEC.

## Independent bounded F1 rereview — 2026-08-31

### Role, boundary and reviewed bytes

A new distinct `INDEPENDENT_SPEC_REVIEWER` rereviewed only the bounded
`SPEC-REV-F1` repair. The reviewer did not author or repair the SPEC, matrix,
pin or registry. The exact pre-append SHA-256 of this original review was
`02a3e81791f42272a488a4a008f93b21ec2561c6cf0e9d9cfa1af97ef7a380b2`.

| Artifact | SHA-256 |
|---|---|
| Repaired SPEC | `7264fb1e142062be9c60cbfd486ec93e671fe384347fd98567c22346d4e527c4` |
| Matrix raw | `e39de7e9ed3199ec8f9033b1c90af9eca993655470f675a0ed3ae93846dbe45c` |
| Matrix canonical UTF-8/universal-newline digest | `e39de7e9ed3199ec8f9033b1c90af9eca993655470f675a0ed3ae93846dbe45c` |
| Static digest pin | `855b02058e1a358cb02187dd852cf8b6c0e47f6d6d4d5642b7b27a093dada852` |
| Unchanged invariant registry | `3022d323782e2fd3cf18f377f4293b43e1637a1f14ccef96a1b3717a2ac9f0e2` |

Strict duplicate-key loading and the repository invariant-family guard passed
with no diagnostics. The registry still contains exactly one matching family
id/path entry; its ownership binding resolves to the exact pin consumer, whose
symbol equals the canonical matrix digest.

No doctor, fetch, reconciler, initializer, provider call, credential access,
installation, Core/workspace-root/pin/binding/fixture/continuity mutation,
commit or push occurred. This appended rereview section and the header
disposition/findings update are the reviewer's only mutation.

### F1 semantic closure and reconstructable delta

Both BUILD-success shapes now require `fixture_freeze_gate_status`, constrain
it to the same exact status as `fixture_repair_status`, and own one explicit
`FIELD_EQUALITY` relation between those fields. `SUCCESS_VALID` requires both
to equal `AUTHORIZATION_REREVIEW_PASS`; the freeze-blocked shape requires both
to equal `AUTHORIZATION_REREVIEW_CHANGES_REQUIRED`. The current parked fixture
state therefore selects only
`BUILD_SUCCESS_FREEZE_BLOCKED_BY_PARKED_FIXTURE_REPAIR_VALID`.

Two independent correlated relabel probes changed the outcome-owned
discriminator, freeze disposition and blocking-field presence together while
retaining the observed fixture gate/status. Both repository and independent
strict validators rejected both probes (`4/4` judgments). In particular, the
parked `AUTHORIZATION_REREVIEW_CHANGES_REQUIRED` payload cannot be relabeled
as unrestricted `SUCCESS`.

The claimed repair delta was reversed entirely in memory without editing any
file. Removing the required gate field, its domain and equality relation from
exactly the two BUILD-success shapes, and restoring the eligible shape's old
parked fixture status, reproduced the original matrix SHA-256 exactly as
`a13ecc2df613b16f4e888a085ee8d86bda40cd35aec9460aefbe1aae5c1e6333`.
Replacing only its digest in the pin reproduced the original pin SHA-256
exactly as
`d69a6781fb66af563ec66d2eb7c1686029a57677deb716780a3079f9d4b288de`.
This independently bounds the matrix repair to two required-field additions,
two domains, two equality relations and the one eligible-status correction;
target, effect, network, rollback, evidence, role and claim boundaries are
unchanged.

### Independent conformance evidence

An inline read-only reviewer adapter imported the frozen generic synthesis,
repository matcher, mutation generator, independent mutation oracle and
independent strict validator. It did not invoke the fixture-specific
hard-coded top-level runner. Results were:

| Check | Result |
|---|---:|
| Exclusive positive shapes | `8/8` |
| Unique generated/oracle mutations with exact-set equality | `1257/1257` |
| Temporal cross-product judgments | `40/40` (`38` accepted, `2` rejected) |
| Literal `"x"` SHA-pattern probes | `6/6` rejected by both surfaces |
| Correlated BUILD-success outcome-selection judgments | `4/4` rejected |

Mutation counts by shape were `126`, `160`, `165`, `168`, `125`, `132`,
`211` and `170`, totaling `1257`. Operator counts were required deletion
`303`; forbidden insertion `79`; unknown field `8`; discriminator replacement
`64`; wrong type `303`; const mismatch `277`; enum mismatch `20`; counter
mutation `168`; pattern mismatch `6`; and one-sided relation change `29`.
Relative to the accepted original review, only the two BUILD-success shapes
changed (`156 -> 160`, `161 -> 165`), and the operator delta is exactly
required deletion `+2`, wrong type `+2`, const mismatch `+2`, and one-sided
relation change `+2`.

The frozen generic source hashes remained exact: contract `19616eca...8497`,
generator `d5f2e133...82ae`, ownership validator `71ec4c54...aac7`, oracle
`f9bf70a8...6cdc` and strict harness `cae96b6e...adb9`. The parked fixture
preimages also remained exact at `49dba6d8...14a7` and `44cdf845...79e6`.

`python scripts/check_invariant_families.py --json` returned `PASS` with no
diagnostics. The required focused unit/integration command preserved the
disclosed parked baseline: `28 passed, 2 skipped, 7 failed`, with the same
seven disposable-repository `ModuleNotFoundError` failures for the omitted
mutation generator/oracle modules. This rereview neither repairs nor
suppresses that fixture lineage and does not present the focused command as an
unrestricted pass.

### Final disposition and authority boundary

`SPEC_REVIEW_PASS`. Findings/waivers: `NONE/NONE`; `SPEC-REV-F1` is closed.

This disposition permits the ORCHESTRATOR to record the next governed phase
transition and route a distinct `WORK_ORDER_AUTHOR`. It does not itself
authorize Work Order acceptance, BUILD, reconciler, doctor/fetch, external
effects, fixture repair, provider/credential use, Core/workspace-root/pin/
binding mutation, installation, product/runtime/database work, deployment,
commit, push or P4-E SPEC.
