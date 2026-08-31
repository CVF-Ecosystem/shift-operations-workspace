# Independent DESIGN Review — CVF Core Refresh Attempt 4 Retained Carrier

- Tranche: `CVF-CORE-REFRESH-ATTEMPT-4-CARRIER-2026-08-31`
- Date: `2026-08-31`
- Reviewed phase: `DESIGN`
- Review role: `INDEPENDENT_DESIGN_REVIEWER`
- Disposition: `DESIGN_REVIEW_CHANGES_REQUIRED`
- Findings: `CDR4-F1` through `CDR4-F6`
- Waivers: `NONE`
- BUILD authority: `NOT_GRANTED`
- External-effect authority: `NOT_GRANTED`

## 1. Exact review bindings and boundary

This review binds these local artifacts by raw SHA-256:

| Artifact | SHA-256 |
|---|---|
| `docs/decisions/DESIGN_2026-08-31_CVF_CORE_REFRESH_ATTEMPT_4_CARRIER.md` | `a5ea2766829298e13d9e9c3815e5bd106019c9fd0353d83debc73014b985da5e` |
| `docs/decisions/INTAKE_2026-08-31_CVF_CORE_REFRESH_ATTEMPT_4_CARRIER.md` | `910ca62b6e7e13ea28cc5e28a1b867d80dd49f023a67cc18b3af425e962062e7` |
| `docs/decisions/INTAKE_REVIEW_2026-08-31_CVF_CORE_REFRESH_ATTEMPT_4_CARRIER.md` | `f431793766683b249a9eb17d75fc2784896c8e215cb9261d04003e1903815307` |
| `SESSION/handoffs/CVF_CORE_REFRESH_ATTEMPT_4_CARRIER_2026-08-31.md` | `ff3e4ac153ad151e538eca70880e1c4942bcd65e7f71675ac3e9bdbacc596432` |
| `docs/decisions/DESIGN_2026-08-31_CVF_CORE_REFRESH_TARGET_REBASE_0281E93_ATTEMPT_4.md` | `8c1f2a67dcd9f3e67b4b04f4cb950f990889bf3f811417b3ca087d4799ef9e13` |
| `docs/decisions/DESIGN_REVIEW_2026-08-31_CVF_CORE_REFRESH_TARGET_REBASE_0281E93_ATTEMPT_4.md` | `8b259c3823589d17937f5b25b85fa0c7ac8559003f68a360d96c8a04d3d85ede` |
| `docs/cvf/INVARIANT_FAMILY_STANDARD.md` | `c360655acb89c6fc8e412f87289d5ef990f62c5795605a95b1d4327cd6dff402` |
| `docs/cvf/invariants/registry.json` | `3022d323782e2fd3cf18f377f4293b43e1637a1f14ccef96a1b3717a2ac9f0e2` |

The reviewed DESIGN hash equals the expected review input. The hidden Core was
observed locally, without fetch, at clean pinned `HEAD`
`a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`; its existing local
`origin/main` is `0281e93bab4a75083973eb7242fd2bc8f65055d3`. This is a
local repository-maintenance review only. It made no AI/agent-governance
claim and required no provider call.

Review operations were restricted to exact named local reads, hashes and path
predicates. No DESIGN repair, continuity/source/test edit, doctor, initializer,
fetch, reconcile, network, provider, credential, carrier execution, broad
inventory, commit or push occurred. The protected assessment was not opened,
read, hashed, named or inventoried.

## 2. Accepted architecture that does not require repair

The DESIGN correctly preserves the exact two-path future BUILD ceiling, keeps
the parent rebase parked, assigns the carrier implementation to a distinct
post-Work-Order worker, makes carrier Execute probes negative-only in this
tranche, separates the carrier invariant family from the later parent family,
and retains explicit independent gates, stop rules and bounded claims. The
raw option order, no-`param(...)` carrier interface, static top-level plus
transitive-AST review strategy, pinned-tool intent, canonical receipt family
and harness-effect attribution are appropriate design directions. They do not,
however, close the six contradictions below.

## 3. Numbered findings

### CDR4-F1 — lifecycle forbids continuity updates that governance requires

The lifecycle says the handoff is already existing, then states that
continuity may change only during terminal synchronization after REVIEW PASS.
That is incompatible with the project's mandatory tranche-transition
contract. The active handoff/state must remain current as responsibility and
phase move, and at minimum the BUILD transition acknowledgment must be
recorded in the active handoff before BUILD begins. The current process already
used such a bounded handoff/state transition from accepted INTAKE to DESIGN.

As written, a conforming orchestrator cannot both obey this DESIGN and record
the required DESIGN-to-SPEC, SPEC-to-WORK_ORDER or reviewed WORK_ORDER-to-BUILD
authority. Conversely, updating the handoff/state would violate the claimed
path timing and changed-set boundary.

Required repair: distinguish phase-owned immutable decision artifacts from
orchestrator/session-sync continuity records. Enumerate the exact continuity
paths that may be updated at each explicit transition, assign their owner, and
keep terminal catalog/index/status synchronization separate. These governance
updates must never enter the two-path implementation-worker ceiling.

### CDR4-F2 — the external-authority block still has a self-hash cycle

The DESIGN requires Execute to use the complete displayed tuple, including
`--ExternalAuthoritySha256`. It also says the external-authority block contains
the exact Execute tuple while claiming that block contains no self-hash. Those
requirements cannot all be true: an exact tuple containing the raw hash of the
file in which the tuple is embedded creates a fixed-point dependency on future
bytes. Saying that the block contains no self-hash does not remove the value
from the specified complete tuple.

This is not merely a formatting ambiguity. Negative carrier-tranche Execute
fixtures could always refuse on the impossible binding and still appear to
pass, while no later parent authority could materialize a byte-exact positive
tuple under the stated graph.

Required repair: define an acyclic authority envelope explicitly. For example,
the authority bytes may bind a canonical Execute tuple template that omits
only the external-authority raw hash, while the final hash is supplied and
verified out-of-band by both worker and carrier; or use another exact
non-self-referential construction. Freeze which fields are inside the hashed
authority, which are runtime envelope fields, and the canonical comparison
algorithm. Do not call a tuple “exact” if one value is implicitly excluded.

### CDR4-F3 — the carrier cannot observe or enforce the claimed host form

The raw `$args` dispatcher sees only tokens after the script path. It cannot
determine whether the host executable was the pinned `pwsh.exe`, whether
`-NoProfile`, `-NonInteractive` and the other required host switches were
present exactly once and in order, whether an extra host-level option was
accepted, or whether a profile performed an effect before the carrier began.
Nevertheless, the DESIGN presents one host form as the only supported form
and says every invocation emits exactly one canonical JSON object. Host parse
errors and pre-script profile behavior occur before the carrier can serialize
anything.

The test harness using the intended argument-array launch is useful evidence
for that one launch, but it is not carrier-side enforcement of the host
contract. The current authority block also binds the carrier tuple, not an
independently observed OS process command line.

Required repair: state the host invocation as an external caller/worker
precondition rather than a raw-dispatcher guarantee; bind the exact absolute
host path/hash and full host argv array in the parent Work Order and external
authority; require the worker receipt to record the recomputed host hash and
actual array supplied to a non-shell process API; and narrow the one-JSON claim
to invocations that successfully reach the carrier script. SPEC must own host-
level negative cases separately from carrier-token refusal cases.

### CDR4-F4 — Git config closure does not close transitive child/network behavior

Clearing the process environment and disabling system/global config does not
neutralize repository/worktree config. The listed `git status` and related
queries can still consult local configuration. In particular,
`core.fsmonitor` may invoke an external hook/process, and config include paths
can read config outside the declared root. URL rewrite, pager, object/alternate
layout and other local configuration can also change observed semantics. The
DESIGN denies `-c`, sets `GIT_CONFIG_COUNT=0`, and does not specify an
independent pre-launch rejection of these local config surfaces. The carrier's
single child gateway therefore does not own every transitive process or read
caused inside `git.exe`, and its child/network counters cannot prove the
claimed closure.

`--no-optional-locks` is useful for suppressing optional repository refresh
writes, but it is not a complete local-config, external-fsmonitor or transitive
child sandbox.

Required repair: freeze an exact fail-closed Git configuration contract before
any Git launch. It must cover repository/worktree config and includes, external
fsmonitor, pager/editor, alternates/object/work-tree/common-dir, hooks and any
other child/transport-affecting surface, and it must define how that contract
is checked without ambient Git behavior. Alternatively, inject exact pinned
configuration overrides through a reviewed mechanism and update the permitted
argv/environment grammar accordingly. Add adversarial fixtures that prove an
external fsmonitor command, include outside root and equivalent transitive
configuration cannot launch or escape the declared read boundary.

### CDR4-F5 — Execute child grammar both inherits and excludes DryRun Git

The mode table describes Execute's child set as Python and PowerShell, while
`Enter-Execute` must first perform the same checks as DryRun. DryRun requires
the seven Git child query forms. Section 6 then says future Execute permits
only the displayed Python/PowerShell structural forms, omitting Git again.
Thus the same Execute path is required to launch Git and required to deny it.

This prevents SPEC from constructing one closed mode matrix and gives a
worker/reviewer no unique answer for `local_child_count`, ordered child ledger,
or whether a Git invocation during Execute is authorized.

Required repair: provide one cumulative or non-cumulative native-child table
with no inherited prose ambiguity. If Execute reuses DryRun Git probes, list
all seven forms explicitly in Execute's allowed sequence and define the exact
ledger/counter relations. If it does not, define the in-process substitute and
remove the claim that Execute performs the same DryRun checks.

### CDR4-F6 — the proposed root snapshots cannot prove the stated no-write claim

The harness says it snapshots the complete test-owned temporary root plus the
exact named project/workspace/Core paths, while also prohibiting recursive
enumeration of repository or workspace roots. A digest of directory metadata
or a root path does not change when an existing descendant file is modified.
The DESIGN does not enumerate which descendant files/metadata are captured,
how Git administrative paths and linked-worktree/common-dir targets are
covered, or how writes outside the named roots through config/reparse/hardlink
surfaces are observed. Therefore “byte/path equality” over the stated
allowlist is not yet a realizable proof of the carrier's bounded filesystem
effect claim.

Static AST checks do cover direct carrier APIs, but the unresolved Git
transitive behavior in `CDR4-F4` makes a concrete observation boundary
necessary; gateway telemetry alone sees only the parent Git process.

Required repair: define a finite, exact before/after observation set and why it
is complete for every permitted child and filesystem API, including Git dir,
common dir, index/lock/config/log/object locations and reparse/hardlink rules;
or adopt a fail-closed process/filesystem observation mechanism whose coverage
is explicit and locally available. Keep pytest fixture setup/cleanup counters
separate, and do not claim whole-root equality from non-recursive root metadata.

## 4. Invariant-family, role, stop and claim review

Invariant-family applicability is correctly `TRIGGERED`, and the proposed id
`CVF-CORE-REFRESH-ATTEMPT-4-CARRIER-MODES-2026-08-31` is collision-free in the
current registry and distinct from the later parent family. Ownership of the
new matrix, static pin and registry entry correctly remains with a future
`SPEC_AUTHOR`; this review has not created them.

Role separation is otherwise sound: the DESIGN author owns only DESIGN, the
future Work Order author cannot create source/test, the implementation worker
is distinct, carrier Execute remains negative-only, and completion review is
independent. The protected-state, no-provider, no-doctor/fetch/reconcile,
no-commit/push and bounded-claim rules remain accepted and must not be weakened
by repair.

## 5. Waivers, disposition and next allowed move

- Numbered findings: `CDR4-F1`, `CDR4-F2`, `CDR4-F3`, `CDR4-F4`, `CDR4-F5`,
  `CDR4-F6`.
- Waivers: `NONE`.
- Disposition: `DESIGN_REVIEW_CHANGES_REQUIRED`.

The exact DESIGN at
`a5ea2766829298e13d9e9c3815e5bd106019c9fd0353d83debc73014b985da5e`
must not advance to SPEC. A distinct bounded DESIGN repair role may amend only
the carrier DESIGN to close these findings, after which a distinct independent
DESIGN rereviewer must review the new exact hash. This review does not itself
authorize that role transition.

Carrier SPEC, matrix/pin/registry mutation, Work Order, BUILD, source/test
creation, positive Execute, parent phase movement, doctor/fetch/reconcile,
network, external effects, fixture/P4-E/XR1 movement, product/runtime/database
work, installation, deployment, release, continuity mutation, commit and push
remain unauthorized.

---

## Independent DESIGN Rereview — repair round 1

- Rereview role: `INDEPENDENT_DESIGN_REREVIEWER`
- Repaired DESIGN raw SHA-256:
  `6347c1a1349c4cae9e4744a65caa8711bc49cba4640bbe1ad98f5da6838afa1d`
- Prior review pre-append raw SHA-256:
  `d75327f07c7f4296c93e70cb1e10947336fda65fd94cff7e10a77180e537095a`
- Active handoff raw SHA-256:
  `8c6b86fb8d1a8faf2f24ada92fe1911293635339b24399f6d023389e50d23e1a`
- Rereview disposition: `DESIGN_REREVIEW_CHANGES_REQUIRED`
- Final findings: `CDR4-RR1-F1`, `CDR4-RR1-F2`
- Waivers: `NONE`
- Date: `2026-08-31`

### Rereview boundary

The rereviewer rehydrated the current carrier DESIGN continuity and compared
the complete repaired DESIGN at the exact hash above with the accepted carrier
INTAKE/review, parent Attempt-4 DESIGN/final review, active handoff, invariant-
family standard and the six findings in this review. The repair remains inside
the authorized same-phase DESIGN scope. Carrier source/test, SPEC, matrix, pin,
registry and Work Order remain absent by authority of this review.

Checks used only exact named local reads and hashes. No DESIGN repair,
continuity/source/test edit, doctor, initializer, fetch, reconcile, provider,
credential, network, carrier execution, broad inventory, commit or push was
performed. The protected assessment was not opened, read, hashed, named or
inventoried.

### Per-finding disposition

| Original finding | Rereview disposition | Evidence |
|---|---|---|
| `CDR4-F1` | `CLOSED` | Section 2 now separates immutable phase artifacts from the exact five transition-update continuity paths, assigns `ORCHESTRATOR -> SESSION_SYNC_STEWARD`, requires acknowledgment before receiving-phase work, and keeps terminal catalog/index/status synchronization outside the exact two-path BUILD ceiling. |
| `CDR4-F2` | `PARTIALLY_CLOSED`; residual `CDR4-RR1-F1` | The external-authority artifact no longer predicts its own hash: its reduced tuple/host templates omit exactly the authority-hash pair and the worker/carrier insertion-removal algorithm is explicit. A different future-artifact dependency remains in the parent Work Order host template. |
| `CDR4-F3` | `CLOSED` | Host form is now explicitly a caller/worker precondition. The later authority and worker receipt bind the absolute host path/hash and actual non-shell argv; carrier `$args` does not pretend to observe the host prefix, and the one-JSON claim is narrowed to invocations that reach the script. |
| `CDR4-F4` | `PARTIALLY_CLOSED`; residual `CDR4-RR1-F2` | Ordinary physical Git/admin paths, direct config parsing, fixed `-c` neutralization, environment closure and adversarial transitive-config fixtures are defined. The accepted-config rule nevertheless rejects the required origin URL. |
| `CDR4-F5` | `CLOSED` | Section 6 is now the sole cumulative child authority. G1..G8, E1..E4, negative Execute, success/failure/rollback prefixes and exact local/network counter relations are unambiguous. |
| `CDR4-F6` | `CLOSED` | Section 7 replaces the whole-root implication with a finite manifest over exact input/named files and the two ordinary Git admin trees, rejects reparse/alternate/common-dir expansion, makes hardlink scope explicit, and separates harness setup/cleanup writes. |

### CDR4-RR1-F1 — the parent Work Order template still depends on a future review hash

The repaired authority artifact itself is acyclic, but sections 3 and 4 now
require the earlier parent Work Order to bind the canonical full host argv
template while omitting **only** the external-authority-hash pair. The carrier
Execute tuple embedded in that host template still contains
`--AuthorizationReviewSha256`. The parent Work Order necessarily exists before
its independent authorization review, so it cannot contain that review's final
raw hash. The artifact graph says Work Order then authorization review, while
the template rule requires the reverse dependency.

Calling this an argv “template” does not close the cycle because the DESIGN
says it omits exactly one pair and later reconstructs only that one pair. No
placeholder or deferred slot is allowed for the future authorization-review
hash. An exact parent Work Order satisfying the stated block cannot therefore
be authored.

Required repair: keep the Work Order binding limited to already finalized
inputs, the exact host executable path/hash and a structural host/carrier argv
schema with explicitly deferred authorization-review and external-authority
fields. The later external-authority block, created after authorization review,
may bind the final reduced Execute/host arrays containing the real
authorization-review path/hash while omitting only its own hash pair. Freeze
the distinct Work-Order structural-template comparison and final-authority
reconstruction algorithms; do not describe the pre-review Work Order as
containing future exact values.

### CDR4-RR1-F2 — the Git config policy rejects the origin URL that G1 requires

Section 6 requires G1, `remote get-url origin`, and the runtime contract has an
exact `PublicRemote`. An ordinary Git repository therefore needs an accepted
`remote.origin.url` value (or an explicitly designed equivalent). The same
section says the direct config parser forbids any value that names a URL. No
exception is stated for the exact public origin. Consequently, a valid target
repository either refuses during config preflight because its required origin
is a URL, or lacks the origin URL and cannot satisfy G1. The eight-launch
DryRun/Execute sequence is unreachable under its own accepted-config rule.

Required repair: define a closed accepted Git-config schema that permits
exactly the necessary `remote "origin".url` equal under the specified ordinal
rule to `PublicRemote`, while continuing to reject `url.*` rewrite sections,
push URLs, additional remotes and credential/proxy/transport helpers. Bind that
single accepted URL field and its parsed representation in the Work Order and
mutation corpus. If origin is supplied by another non-ambient mechanism,
remove G1's repository-config dependency and specify that mechanism exactly.

### New-contradiction and unchanged-boundary review

No further contradiction was found in the repaired continuity ownership,
raw-token dispatcher, carrier-side host limitation, top-level/transitive AST
contract, cumulative child/counter table, negative-only carrier Execute,
finite observation scope, invariant-family identity, role separation, stop
conditions or bounded claim. The two residuals above are design-time
realizability defects; they are not waivable implementation details and cannot
be delegated silently to SPEC.

The repair does not authorize any Core/root/pin/binding effect, network,
provider call, fixture/P4-E/XR1 movement, product/runtime/database change,
installation, deployment, release, commit or push. Findings and waivers remain
explicit; no live AI-governance claim is made.

### Final disposition and next allowed move

- Closed original findings: `CDR4-F1`, `CDR4-F3`, `CDR4-F5`, `CDR4-F6`.
- Partially closed original findings: `CDR4-F2`, `CDR4-F4`.
- Final findings: `CDR4-RR1-F1`, `CDR4-RR1-F2`.
- Waivers: `NONE`.
- Final disposition: `DESIGN_REREVIEW_CHANGES_REQUIRED`.

The repaired exact DESIGN at
`6347c1a1349c4cae9e4744a65caa8711bc49cba4640bbe1ad98f5da6838afa1d`
must not advance to SPEC. The next eligible move is an orchestrator-authorized,
bounded second DESIGN repair addressing only `CDR4-RR1-F1` and
`CDR4-RR1-F2`, followed by another independent rereview of the new exact hash.
This rereview does not itself authorize that transition.

Carrier SPEC, matrix/pin/registry mutation, Work Order, BUILD, source/test
creation or execution, parent phase movement, doctor/fetch/reconcile/network
and every external effect remain unauthorized.

---

## Independent DESIGN Rereview — repair round 2

- Rereview role: `INDEPENDENT_DESIGN_REREVIEWER`
- Repaired DESIGN raw SHA-256:
  `c4fd35428336516f7aed85ea9da41372f5f367958edd82225f48e667f05987c6`
- Prior review pre-append raw SHA-256:
  `6c15a5322a4f8948817af60d64732adc4451859b4901623b06d3b481ba840615`
- Active handoff raw SHA-256:
  `cc47cf8c84adf4d4e0003296bffa0b43df1b4a257362c781832113a91d2e4a42`
- Rereview disposition: `DESIGN_REREVIEW_CHANGES_REQUIRED`
- Final findings: `CDR4-RR2-F1`, `CDR4-RR2-F2`
- Waivers: `NONE`
- Date: `2026-08-31`

### Rereview boundary

The rereviewer rehydrated the active carrier DESIGN continuity and reviewed
the complete round-2 DESIGN at the exact hash above against both earlier
review sections, the accepted carrier INTAKE/review, parent Attempt-4
DESIGN/final review, active handoff and invariant-family standard. The local
continuity agrees on DESIGN, R2, the parked parent, and no BUILD or external-
effect authority. Round 2 remains inside the handoff's two-residual repair
boundary.

Review checks used exact named local reads/hashes and one secret-suppressing
local Git-config existence/count probe. That probe returned exactly one local
Project remote-URL entry but did not print or record its value. No DESIGN
repair, continuity/source/test edit, doctor, initializer, fetch, reconcile,
network, provider, credential, carrier execution, broad inventory, commit or
push occurred. The protected assessment was not opened, read, hashed, named or
inventoried.

### Residual and preserved-closure disposition

| Finding family | Rereview disposition | Evidence |
|---|---|---|
| `CDR4-RR1-F1` | `CLOSED` | Sections 3 and 4 now give the pre-review Work Order only closed tagged structural schemas with four explicit deferred value nodes. The authorization review finalizes before the external authority projects real values; the authority omits only its own hash pair, and worker/carrier insert/remove/compare it out of band. No earlier artifact predicts a later review hash. |
| `CDR4-RR1-F2` | `PARTIALLY_CLOSED`; residual `CDR4-RR2-F2` | The Core config now permits exactly one normalized `remote.origin.url = PublicRemote`, binds its canonical map and validates G1 output while rejecting adjacent rewrite/credential/proxy/transport surfaces. The Project half of the same direct-parser contract remains unrealizable against the named current repository. |
| `CDR4-F1` | `REMAINS_CLOSED` | Exact transition continuity paths, owners/timing and terminal synchronization remain unchanged and outside the two-path BUILD ceiling. |
| `CDR4-F3` | `REMAINS_CLOSED` | Host path/hash/argv remain an externally evidenced caller/worker precondition; `$args` and the one-JSON claim retain their corrected boundaries. |
| `CDR4-F5` | `REMAINS_CLOSED`, subject to `CDR4-RR2-F1` | The cumulative child ordering itself remains G1..G8/E1..E4 with negative Execute before G1; the newly exposed defect is an omitted post-launch semantic-refusal outcome, not a return to the old inherited-child ambiguity. |
| `CDR4-F6` | `REMAINS_CLOSED` | The finite Git-admin/named-file observation manifest and explicit non-whole-root claim remain intact. |

### CDR4-RR2-F1 — G1 semantic refusal cannot have both zero and one launched child

The repaired Git parser section adds G1 multi-line/output-mismatch mutations
and then requires **all** rejection cases to have zero launched children and
zero network counters. A G1 output mismatch cannot be detected before G1 is
launched: the carrier must run the allowed local child and inspect its stdout.
Its truthful ledger therefore has one launched `LOCAL_READ` entry and
`local_child_count = 1`, while network counters remain zero.

The cumulative table has no row for this or any other allowed local child that
exits zero but fails post-launch semantic validation. `DryRun, prelaunch
refusal` requires an empty ledger; `launched-child failure` is defined only for
a nonzero child and only under later Execute; `denied candidate` is explicitly
non-launched. SPEC is forbidden to add a sequence row, so it cannot repair the
receipt equations downstream.

Required repair: separate prelaunch config/token refusal from post-launch
local-query semantic refusal. Add exact DryRun and later-Execute prefix rows in
which G1 (or another applicable G node) was launched, the first nonzero exit or
invalid canonical output ends the ordinary sequence, `local_child_count`
equals the launched G prefix, and both network counters remain zero. Restrict
the zero-child sentence to prelaunch parser/config cases. Freeze whether the
ledger distinguishes nonzero exit from zero-exit/invalid-output without
changing the G1..G8 order.

### CDR4-RR2-F2 — current Project config has a remote URL that the closed parser forbids

The repaired contract permits one URL-bearing key only in the Core repository
and says the Project repository has no accepted remote URL. However, the
exact current Project repository used by the carrier has one local remote-URL
entry; the rereview established only presence/count and deliberately did not
emit its possibly sensitive value. Because the carrier directly parses the
entire Project `<admin>\config` and rejects every other URL-bearing value, it
must refuse before the Project staged-diff query on the actual named target.

This is not an optional unused-key detail: the Work Order must bind the exact
Project config hash and canonical parsed map, so it cannot omit the existing
entry, and the carrier's closed parser cannot accept that map. The Core-only
exception therefore closes the original G1 contradiction but leaves the
carrier unrealizable in its current ProjectRoot.

Required repair: define a separate, credential-free Project remote-URL rule.
It may accept exactly the current normalized Project `remote.origin.url` as an
independently hash-bound, non-authority value after rejecting userinfo,
credentials, control characters, rewrite/push/helper/proxy/transport keys and
additional remotes; or define another exact mechanism that prevents Git from
reading the Project remote entry without altering the repository. Keep the
Core `PublicRemote` equality unique to Core/G1 and add Project acceptance plus
secret-shaped/extra-remote negative vectors to the matrix.

### No-new-drift review

Apart from the two findings above, the round-2 edits do not introduce a new
future/self-hash edge, host-observability claim, dynamic AST/call edge,
Execute-positive carrier test, observation-scope expansion, invariant-family
collision, role overlap, phase skip or external-effect authority. The findings
are independently exposed realizability gaps in the newly detailed round-2
Git contract, not waivers or implementation preferences.

### Final disposition and next allowed move

- Closed: `CDR4-RR1-F1`.
- Partially closed: `CDR4-RR1-F2`.
- Preserved closures: `CDR4-F1`, `CDR4-F3`, `CDR4-F5`, `CDR4-F6`.
- Final findings: `CDR4-RR2-F1`, `CDR4-RR2-F2`.
- Waivers: `NONE`.
- Final disposition: `DESIGN_REREVIEW_CHANGES_REQUIRED`.

The exact DESIGN at
`c4fd35428336516f7aed85ea9da41372f5f367958edd82225f48e667f05987c6`
must not advance to SPEC. The next eligible move is an orchestrator-authorized
bounded DESIGN repair of only `CDR4-RR2-F1` and `CDR4-RR2-F2`, followed by a
fresh independent rereview of the resulting exact hash. This review does not
itself authorize that transition.

Carrier SPEC, matrix/pin/registry mutation, Work Order, BUILD, source/test
creation or execution, parent phase movement, doctor/fetch/reconcile/network,
external effects, fixture/P4-E/XR1 movement, product/runtime/database work,
installation, deployment, release, commit and push remain unauthorized.

---

## Independent DESIGN Rereview — repair round 4 final

- Rereview role: `INDEPENDENT_DESIGN_REREVIEWER`
- Final repaired DESIGN raw SHA-256:
  `8f5ab09aac72a99ea706444e2f57d47a20a5bd928544cbccf799129333be3a95`
- Prior review pre-append raw SHA-256:
  `f45e8ad7845e7fa321f2f7749fc438cd00dbf2b72272c9db5559c6cf20316511`
- Active handoff raw SHA-256:
  `48df6a0a003c3fe53f0b8ff739cb19cd8d3b78338e118ad30653c2899c3cf7a6`
- Accepted parent DESIGN raw SHA-256:
  `8c1f2a67dcd9f3e67b4b04f4cb950f990889bf3f811417b3ca087d4799ef9e13`
- Rereview disposition: `DESIGN_REVIEW_PASS`
- Final findings: `NONE`
- Waivers: `NONE`
- Review-cost escalation: `NOT_REQUIRED_FINDING_CLOSED`
- Date: `2026-08-31`

### Rereview boundary

The rereviewer rehydrated the active DESIGN-phase continuity and reviewed the
complete round-4 carrier DESIGN at the exact hash above against every earlier
review section, the accepted carrier INTAKE/review, accepted parent Attempt-4
DESIGN/final review, active handoff and invariant-family standard. Round 4 is
bounded to `CDR4-RR3-F1`; parent Attempt 4 remains parked and no later phase or
external effect is inferred from this PASS.

Checks used only exact named local reads, hashes and literal occurrence/order
probes. No DESIGN repair, continuity/source/test edit, doctor, initializer,
fetch, reconcile, network, provider, credential, carrier execution, broad
inventory, commit or push occurred. The protected assessment was not opened,
read, hashed, named or inventoried.

### CDR4-RR3-F1 closure — exact parent interface restored

`CDR4-RR3-F1` is `CLOSED`:

- Exact literal probing found zero occurrences of the raw option token
  `--ProjectRemote` in the repaired DESIGN.
- The canonical carrier option block now matches the accepted parent sequence:
  `--PublicRemote` is followed directly by `--CarrierSha256`, with no inserted
  option, deferred tuple node or authority-array value.
- ParseOnly again ends at the parent-frozen `--CarrierSha256`; DryRun and
  Execute preserve the accepted parent option order and mode boundaries.
- `ProjectRemote` exists only as the credential-free, non-authority field
  `project_git_config_v1.ProjectRemote` inside the already raw-hash-bound
  parent Work Order config block, alongside the normalized Project config
  path, raw hash and canonical parsed map.
- The carrier extracts that field only after verifying the Work Order
  path/hash and closed schema, before Project config validation and G8. The
  external-authority block cross-binds the Work Order hash and does not
  duplicate a Project remote value in a carrier or host tuple.
- The Project config field remains distinct from Core `PublicRemote`, G1 and
  every transport authority; the closed parser still rejects credentials,
  userinfo, secret-shaped values, rewrite/push/helper/proxy/transport settings
  and additional remotes.

The repair therefore retains the realizable Project-config closure from
`CDR4-RR2-F2` without amending the parent-frozen raw interface.

### Complete closure and new-root-cause review

The exact final DESIGN preserves all earlier accepted corrections:

- `CDR4-F1`: transition continuity ownership/timing remains separate from the
  exact two-path BUILD ceiling and terminal synchronization.
- `CDR4-F2` and `CDR4-RR1-F1`: the Work Order uses closed structural schemas
  for future fields; final authority arrays omit only their own hash pair, so
  no future/self-hash dependency returns.
- `CDR4-F3`: host executable/path/argv evidence remains a caller/worker
  precondition and carrier output remains bounded to script-reached execution.
- `CDR4-F4`, `CDR4-RR1-F2` and `CDR4-RR2-F2`: ordinary Git/admin resolution,
  direct closed config parsing, Core `PublicRemote`, Work-Order Project remote,
  pinned tool/config hashes and transitive config denials remain coherent.
- `CDR4-F5` and `CDR4-RR2-F1`: G1..G8/E1..E4 ordering, negative-only carrier
  Execute, zero-child prelaunch refusal and truthful launched-prefix semantic/
  nonzero-child ledgers and counters remain exact.
- `CDR4-F6`: the finite named-file/Git-admin observation manifest remains
  bounded and does not become a whole-root equality or broad inventory claim.

No new root cause, stale partial disposition, phase skip, role overlap,
invariant-family collision, dynamic reachability, external-effect authority or
claim expansion was found. The final carrier family remains distinct from the
later parent family, and SPEC still owns exact matrix outcomes, corpus ids,
counts, refusal codes and digests rather than inheriting implementation truth.

### Review-cost policy and final disposition

The same parent-interface drift does not persist. Therefore
`REVIEW_COST_ESCALATION_REQUIRED` is not triggered; round 4 closes the sole
authorized residual rather than starting another repair cycle.

- Closed findings: `CDR4-F1..F6`, `CDR4-RR1-F1/F2`,
  `CDR4-RR2-F1/F2`, `CDR4-RR3-F1`.
- Final findings: `NONE`.
- Waivers: `NONE`.
- Final disposition: `DESIGN_REVIEW_PASS`.

This PASS accepts only the carrier DESIGN at raw SHA-256
`8f5ab09aac72a99ea706444e2f57d47a20a5bd928544cbccf799129333be3a95`.
It does not silently perform or authorize a phase transition. The next eligible
move is an explicit `ORCHESTRATOR` `DESIGN -> SPEC` acknowledgment and exact
five-path continuity synchronization, followed by a distinct `SPEC_AUTHOR`
creating only the SPEC, carrier invariant matrix, static pin and registry entry
at the collision-free paths already defined by DESIGN. A distinct independent
SPEC review remains required before any Work Order.

Carrier Work Order, authorization review, BUILD, source/test creation or
execution, parent phase movement, doctor/fetch/reconcile/network, external
effects, fixture/P4-E/XR1 movement, product/runtime/database work,
installation, deployment, release, commit and push remain unauthorized.

---

## Independent DESIGN Rereview — repair round 3

- Rereview role: `INDEPENDENT_DESIGN_REREVIEWER`
- Recovered DESIGN raw SHA-256:
  `29e8f518625282c23fe6ac2f42019f446d05ecdd94137ffc9b88befda1468169`
- Prior review pre-append raw SHA-256:
  `18e8e83b5c9cfa686e833fb2ef39880b1770ac5df29e2f09e9308726b31fcf69`
- Active handoff raw SHA-256:
  `48df6a0a003c3fe53f0b8ff739cb19cd8d3b78338e118ad30653c2899c3cf7a6`
- Accepted parent DESIGN raw SHA-256:
  `8c1f2a67dcd9f3e67b4b04f4cb950f990889bf3f811417b3ca087d4799ef9e13`
- Rereview disposition: `DESIGN_REREVIEW_CHANGES_REQUIRED`
- Final finding: `CDR4-RR3-F1`
- Waivers: `NONE`
- Review-cost escalation: `NOT_TRIGGERED_NEW_ROOT_CAUSE`
- Date: `2026-08-31`

### Rereview boundary

The rereviewer rehydrated the current DESIGN-phase continuity and compared the
complete recovered round-3 DESIGN at the exact hash above with all prior review
sections, accepted carrier INTAKE/review, accepted parent Attempt-4 DESIGN and
its final review, active handoff and invariant-family standard. The handoff
explicitly authorizes round 3 only for `CDR4-RR2-F1/F2`; parent Attempt 4,
SPEC, BUILD and every external effect remain parked.

Checks used only exact named local reads and hashes. No DESIGN repair,
continuity/source/test edit, doctor, initializer, fetch, reconcile, network,
provider, credential, carrier execution, broad inventory, commit or push was
performed. The protected assessment was not opened, read, hashed, named or
inventoried.

### Round-2 finding closure

| Finding | Rereview disposition | Evidence |
|---|---|---|
| `CDR4-RR2-F1` | `CLOSED` | Sections 6 and 7 now distinguish zero-child prelaunch refusal from exact launched G prefixes. G1 zero-exit invalid output records one `LOCAL_READ`, `local_child_count = 1`, zero network/write-attempt counters and no later child. Gk nonzero and canonical-output failures have explicit prefix rows for DryRun and activated later-parent Execute. |
| `CDR4-RR2-F2` | `CLOSED_WITH_NEW_BOUNDARY_DRIFT_CDR4-RR3-F1` | The direct Git-config contract now models the existing Project origin separately, rejects credential/rewrite/helper/transport adjacency, binds config path/hash/map, and never treats the Project remote as Core `PublicRemote` or transport authority. The mechanism chosen to carry that fact changes the frozen parent interface and is therefore not acceptable as written. |

The previous closures of `CDR4-F1..F6`, `CDR4-RR1-F1` and the Core-specific
portion of `CDR4-RR1-F2` remain technically intact. The staged hash graph,
host evidence boundary, cumulative G/E child ordering, finite observation
manifest, invariant-family identity, roles, stops and bounded claim introduce
no additional contradiction in this round.

### CDR4-RR3-F1 — carrier repair changes the parent-frozen exact option surface

The accepted parent Attempt-4 DESIGN states that its full case-sensitive
carrier option surface, in canonical order, is **exactly** the sequence from
`--Mode` through `--ExecutionId`. In that frozen sequence,
`--PublicRemote` is followed directly by `--CarrierSha256`; there is no
`--ProjectRemote` option. Carrier INTAKE requires this prerequisite to retain
and make testable that accepted parent architecture and its exact tuples.

The round-3 carrier DESIGN inserts `--ProjectRemote` between those two parent-
frozen options, includes it in ParseOnly, DryRun and Execute, and propagates it
through the Work-Order structural schema, external authority and worker host
argv. A prerequisite carrier DESIGN cannot silently amend the already accepted
parent DESIGN contract. The later parent SPEC is also not authorized to
reinterpret “exactly” by adding a new option. Therefore the round-3 bytes close
the Project-config fact technically but exceed the tranche's accepted
interface boundary.

Required repair: remove `--ProjectRemote` from the raw carrier/host tuples and
restore the parent-frozen option list byte-for-byte. Keep the credential-free
Project remote as a non-authority field inside the already hash-bound parent
Work Order config block, alongside the Project config path, raw hash and
canonical parsed map. DryRun and Execute already receive and validate the Work
Order path/hash and can obtain that exact Project fact there before G8;
ParseOnly need only validate the parent-frozen raw token surface and can defer
the Work-Order-owned Project config fact. The external authority may cross-bind
the Work Order hash rather than duplicate a new runtime option. Alternatively,
any genuine need to change the parent raw interface requires a separately
authorized parent DESIGN amendment, not an implicit carrier repair.

### Review-cost policy

`REVIEW_COST_ESCALATION_REQUIRED` is not recorded in this rereview. Neither
`CDR4-RR2-F1` nor its post-launch ledger root cause persists, and the original
Project-config inability in `CDR4-RR2-F2` is resolved at the Git-contract
level. `CDR4-RR3-F1` is an independently new phase/interface-boundary root
cause introduced by the round-3 repair mechanism. The policy's round-three
escalation condition applies when the same blocking condition recurs without
an independent new root cause; that condition is not met here. Any later
rereview that finds this same exact parent-interface drift unclosed must stop
and record `REVIEW_COST_ESCALATION_REQUIRED` rather than authorize another
ordinary repair cycle.

### Final disposition and next allowed move

- Closed through round 3: `CDR4-F1..F6`, `CDR4-RR1-F1/F2`,
  `CDR4-RR2-F1/F2` at their substantive architecture roots.
- Final finding: `CDR4-RR3-F1`.
- Waivers: `NONE`.
- Review-cost escalation: `NOT_TRIGGERED_NEW_ROOT_CAUSE`.
- Final disposition: `DESIGN_REREVIEW_CHANGES_REQUIRED`.

The recovered exact DESIGN at
`29e8f518625282c23fe6ac2f42019f446d05ecdd94137ffc9b88befda1468169`
must not advance to SPEC. The next eligible move is an orchestrator-authorized
bounded DESIGN repair of only `CDR4-RR3-F1`, followed by a fresh independent
rereview of the resulting exact hash. This rereview does not itself authorize
that transition.

Carrier SPEC, matrix/pin/registry mutation, Work Order, BUILD, source/test
creation or execution, parent phase movement, doctor/fetch/reconcile/network,
external effects, fixture/P4-E/XR1 movement, product/runtime/database work,
installation, deployment, release, commit and push remain unauthorized.
