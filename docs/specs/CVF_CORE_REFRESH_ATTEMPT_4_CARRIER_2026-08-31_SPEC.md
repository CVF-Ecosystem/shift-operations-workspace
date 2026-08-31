# SPEC — CVF Core Refresh Attempt 4 Retained Carrier

- Tranche: `CVF-CORE-REFRESH-ATTEMPT-4-CARRIER-2026-08-31`
- Phase: `SPEC`
- Status: `SPEC_REPAIR_BLOCKED_PREREQUISITE_AMENDMENT`
- Risk: `R2`
- Active role: `SPEC_AUTHOR`
- BUILD authority: `NOT_GRANTED`
- External-effect authority: `NOT_GRANTED`
- Invariant family:
  `CVF-CORE-REFRESH-ATTEMPT-4-CARRIER-MODES-2026-08-31`
- Matrix canonical digest: `21aad333256b76f857b2cf985f91744118fb780c9c501783c8de82b7515d3c60`

## Repair-round disposition

The consolidated repair closes `CSR4-F1`, `CSR4-F3` and `CSR4-F4` in the
SPEC-owned matrix without waiver. It does not claim closure of `CSR4-F2` or
`CSR4-F5`:

- the current shared invariant-family schema has no JSON-null field-domain
  type, while the accepted DESIGN requires the canonical `execution_id` value
  to be a token or JSON null; substituting a string sentinel, omitting the
  field, or wrapping null in an object would change the accepted receipt;
- every schema-supported ownership strategy in the current repository guard
  first requires `consumerPath` to resolve to an existing regular file. The
  exact carrier and carrier-test consumers are intentionally absent before
  BUILD, so declaring either as a consumer would make the guard fail and
  pretending the static pin alone proves their future consumption would be a
  false ownership claim.

The frozen pin records the exact two future consumer paths and the repaired
matrix digest as a pre-BUILD manifest, but explicitly marks their binding
deferred. A separately governed prerequisite amendment must add realizable
null ownership and a fail-closed deferred/future-consumer strategy to the
shared schema, contract and guard before this SPEC can be independently
rereviewed for PASS. Work Order, BUILD and all external effects remain
unauthorized.

## R1 — Accepted lineage and exact ownership

This SPEC is authorized only by these immutable accepted bytes:

| Artifact | Raw SHA-256 |
|---|---|
| `docs/decisions/INTAKE_2026-08-31_CVF_CORE_REFRESH_ATTEMPT_4_CARRIER.md` | `910ca62b6e7e13ea28cc5e28a1b867d80dd49f023a67cc18b3af425e962062e7` |
| `docs/decisions/INTAKE_REVIEW_2026-08-31_CVF_CORE_REFRESH_ATTEMPT_4_CARRIER.md` | `f431793766683b249a9eb17d75fc2784896c8e215cb9261d04003e1903815307` |
| `docs/decisions/DESIGN_2026-08-31_CVF_CORE_REFRESH_ATTEMPT_4_CARRIER.md` | `8f5ab09aac72a99ea706444e2f57d47a20a5bd928544cbccf799129333be3a95` |
| `docs/decisions/DESIGN_REVIEW_2026-08-31_CVF_CORE_REFRESH_ATTEMPT_4_CARRIER.md` | `91d43cfa5e596312e3473bfbe8cbb1b170f13a81137dbeb352d52850c2ca07e7` |

The matrix named in the header is the sole semantic owner of outcomes,
receipt fields, field domains, counter relations, conformance case ids,
mutation obligations and ownership bindings. This SPEC defines algorithms and
acceptance procedures and must not be interpreted as a second outcome table.

Only a later reviewed Work Order may authorize creation of:

```text
scripts/cvf_core_refresh_target_rebase_0281e93_attempt_4_carrier.ps1
tests/cvf/test_cvf_core_refresh_target_rebase_0281e93_attempt_4_carrier.py
```

No source, test, carrier execution, parent rebase movement or external effect
is authorized by this SPEC.

## R2 — Canonical raw-token interface

The carrier has no `param(...)` block, alias, pipeline binding, positional
binder or module import. Its first executable top-level statement copies the
original unbound `$args` array. The dispatcher consumes only alternating
option-name/value strings and validates the whole vector before reaching a
mode entry node.

The sole option order is:

```text
--Mode --ProjectRoot --WorkspaceRoot --CoreRoot --BackupRoot --OldPin
--TargetPin --PublicRemote --CarrierSha256 --WorkOrderPath --WorkOrderSha256
--SpecPath --SpecSha256 --MatrixPath --MatrixSha256 --PinPath --PinSha256
--SpecReviewPath --SpecReviewSha256 --AuthorizationReviewPath
--AuthorizationReviewSha256 --ExternalAuthorityPath
--ExternalAuthoritySha256 --ExecutionId
```

`ParseOnly` ends after `--CarrierSha256`. `DryRun` ends after
`--SpecReviewSha256`, followed by `--ExecutionId`. `Execute` uses the complete
order. `--PublicRemote` is followed directly by `--CarrierSha256`; the raw
surface, host schema and authority arrays contain no `ProjectRemote` option,
deferred node or value. The Project remote is read only from the verified
parent Work Order's closed `project_git_config_v1.ProjectRemote` field.

Every option and value is non-empty. Names are ASCII and ordinal
case-sensitive. Reject odd length; missing, duplicate, reordered, extra,
unknown, abbreviated, case-folded or Unicode-confusable names; `--%`, bare
`--`, positional tokens, `name=value`, slash/single-dash/combined forms;
array, expression or scriptblock-shaped tokens; control/NUL characters; and
coercion-shaped values. Values may not be repaired by PowerShell binding,
profiles, aliases or environment state.

`OldPin` and `TargetPin` are lowercase 40-hex. Every SHA is lowercase 64-hex.
`PublicRemote` is exactly
`https://github.com/Blackbird081/Controlled-Vibe-Framework-CVF.git`.
`ExecutionId` matches `^[A-Z0-9][A-Z0-9_-]{7,63}$`. Paths are absolute,
ordinal-round-tripping, normalized, contained by their declared physical root
and have no reparse component. Drive-relative and UNC paths refuse.

## R3 — Acyclic artifact and hash stages

The parent Work Order block `CVF-CARRIER-WORK-ORDER-V1` contains closed tagged
`execute_tuple_schema_v1` and `host_argv_schema_v1` arrays. Each node is
exactly a literal `{kind,value}` or deferred `{kind,field}` object. The only
deferred fields are `AuthorizationReviewPath`,
`AuthorizationReviewSha256`, `ExternalAuthorityPath` and
`ExternalAuthoritySha256`; option names are literal and no placeholder or
null node is allowed.

The later authorization review hashes the already-final Work Order. The later
external-authority artifact replaces the first three deferred values with
final bytes and consumes without emission exactly the literal
`--ExternalAuthoritySha256` node plus its deferred value node. Its two reduced
arrays contain no placeholder or self hash. A later parent worker hashes the
final authority bytes out of band and inserts exactly that pair at the frozen
position. The carrier removes exactly that runtime pair and compares the
remaining tuple byte-for-byte to the authority's reduced carrier array.
Every node must be classified exactly once. Host path/hash and actual host argv
are worker/reviewer evidence, never inferred from `$args`.

Every parent artifact contains exactly one UTF-8 JSON block between its
versioned literal sentinels. Parsing rejects BOM, invalid UTF-8, duplicate
keys, extra keys and type/domain drift. All duplicated finalized paths,
hashes, tranche, worker, execution id and effect fields agree ordinally.

## R4 — Host and tool preconditions

The supported caller form is exactly `pwsh.exe -NoLogo -NoProfile
-NonInteractive -File <carrier> <tuple>`. The parent Work Order binds the
absolute normalized host path/hash and structural host schema. Carrier tests
record the actual host path/hash and argv independently. Host failures before
the script begins are harness evidence and cannot be called a one-JSON carrier
result.

`git.exe`, future `python.exe` and future `pwsh.exe` paths and raw hashes come
only from a verified parent Work Order. `PATH`, `Get-Command`, `where.exe`,
registry and first-match resolution are forbidden. Before launch the carrier
recomputes the selected executable hash and refuses on mismatch.

The child environment is cleared. The only inherited keys are `SystemRoot`,
`WINDIR`, `ComSpec`, `TEMP` and `TMP`, each validated as a non-empty,
control-free, non-secret host value. Git children additionally receive only
`GIT_TERMINAL_PROMPT=0`, `GIT_CONFIG_NOSYSTEM=1`,
`GIT_CONFIG_GLOBAL=NUL`, `GIT_CONFIG_COUNT=0`, `GIT_OPTIONAL_LOCKS=0`,
`GCM_INTERACTIVE=Never`, `LANG=C` and `LC_ALL=C`. Carrier test hosts may add
only `POWERSHELL_TELEMETRY_OPTOUT=1` and
`POWERSHELL_UPDATECHECK=Off`. All other Git/GCM/askpass/credential/proxy/SSH/
protocol/object/work-tree/common-dir/trace/config channels are absent. `HOME`,
`CODEX_HOME` and ambient system options are never repurposed.

## R5 — Closed callable, AST and child graph

Static validation starts at the complete top-level script block and
`Enter-ParseOnly`, `Enter-DryRun`, `Enter-Execute`; it computes transitive
closure across every function, nested block and trap/catch/finally path. It
classifies commands, invocation/member ASTs, member access, constructors,
redirection and dot-source/invocation operators. Dynamic, unresolved,
aliased, unqualified, reflective or mode-unlisted edges refuse.

Top level permits declarations, literal initialization, raw `$args` copy,
dispatcher validation, one literal mode selection, one canonical serializer
and process exit. Dynamic code, reflection, COM, jobs, remoting, WMI/CIM,
module loading, events, arbitrary `.Invoke()`, shell strings and direct
process creation are forbidden. `Invoke-AllowlistedChild` is the sole literal
process gateway.

`ParseOnly` permits only raw/ordinal/path/hash/AST/closed-collection/canonical-
JSON reads and no child. `DryRun` adds exact existence/attribute/text reads,
ordinary Git-admin enumeration, duplicate-key JSON/config parsing and the
G1..G8 sequence. `Execute` adds only named preimage/evidence/atomic-pin/
rollback functions and, after activation, the matrix-governed G/E sequence.
Filesystem mutators, registry, secrets and direct network APIs are forbidden
in ParseOnly and DryRun.

## R6 — Closed Git/config grammar

Both repositories must have an ordinary physical `<root>/.git` directory.
Gitfiles, linked worktrees, `commondir`, worktree config, alternates, shallow/
graft/replace overlays, submodule Git dirs, locks and reparse surfaces refuse
before a child.

The carrier directly parses strict UTF-8 Git config with duplicate normalized
key rejection. Only canonical `[remote "origin"]` with one `url = ...` is
accepted as URL-bearing state. Core value equals runtime `PublicRemote`;
Project value equals verified Work Order
`project_git_config_v1.ProjectRemote`. The Work Order binds each config path,
raw hash and canonical parsed map. Both values reject controls, userinfo,
credentials/tokens, query/fragment secrets, environment interpolation and
remote-helper syntax. Additional remotes/URLs, `pushurl`, URL rewrites,
includes, aliases, hooksPath, fsmonitor commands, pager/editor/browser/diff/
textconv/external commands, credential/proxy/SSH/HTTP/protocol/transport,
object/work-tree/common-dir, maintenance and GC settings refuse.

Every Git launch uses the pinned executable plus this literal prefix:

```text
--no-optional-locks -c core.fsmonitor=false -c core.hooksPath=NUL
-c core.pager=cat -c pager.status=false -c credential.helper=
-c http.proxy= -c protocol.allow=never
```

It then uses exactly one of seven forms: Core `remote get-url origin`; Core
`rev-parse --verify HEAD^{commit}`; Core `rev-parse --verify
origin/main^{commit}`; Core `cat-file -t <pin>`; Core `merge-base
--is-ancestor <OldPin> <TargetPin>`; Core `status --porcelain=v1
--untracked-files=no`; Project `diff --cached --name-only`. `cat-file` occurs
twice, producing cumulative G1..G8. All other executable/argv forms, any
transport verb, arbitrary `-c`, config mutation or operand beginning `-` are
denied before launch.

G1 zero-exit output removes at most one terminal LF or CRLF and must then be
one control-free line ordinally equal to `PublicRemote`. A mismatch is a
post-launch `LOCAL_QUERY_SEMANTIC_REFUSAL`, not a zero-child prelaunch case.
All outcome fields and G1..G8/E1..E4 prefix counter equations are owned by the
matrix.

## R7 — Canonical receipt and finite observation

Every invocation that reaches the script emits exactly one RFC 8259 UTF-8 JSON
object to stdout, with no BOM, insignificant whitespace or success stderr.
Canonicalization recursively sorts object keys ordinally, preserves array
order, uses lowercase JSON literals, rejects non-integer numbers, and escapes
only required JSON characters using lowercase `\u00xx`. SHA-256 is over those
UTF-8 bytes. The matrix owns the exact envelope fields, domains, relations and
dispositions.

The before/after manifest has frozen membership: every runtime artifact and
carrier; every directly inspected root marker and parent-chain component;
both physical `.git` trees only; explicit absence sentinels for rejected Git
admin/config surfaces and locks; and exact named non-admin files read through
.NET. Records are ordinal-sorted and contain normalized path, kind,
attributes, reparse state, length and raw hash when a file. Membership or
record drift refuses. No working-tree, workspace-root or untracked recursive
inventory is permitted.

Reparse points refuse before traversal. Hardlink alias-content mutation must
change an observed hash and refuse. Harness setup/cleanup occurs only inside
pytest's temporary root before/after the carrier process and is counted only
as `harness_setup_write_count`/`harness_cleanup_write_count`, never as carrier
effects. Stdout/stderr use OS pipes.

## R8 — Mode, counter and activation rules

The implementation and independent validator load the matrix by the pinned
digest and select exactly one matrix shape. No prose fallback may add a child
or field. The carrier matrix owns only ParseOnly, DryRun, negative Execute
activation and denied DryRun candidate shapes. Every denied-candidate shape
is one finite reachable G-prefix: after exactly `k` launched local children
for `k = 0..8`, the denied non-launched candidate yields
`local_child_count = k`, `network_child_count = 0`,
`network_attempt_count = 1`, `nonlaunched_refusal_count = 1` and
`child_ledger_count = k + 1`; no independent cartesian range is permitted.

G1..G8 and E1..E4 still mean the exact nodes frozen in DESIGN: E1 local
Python P0; E2 reconciler; E3 initializer; E4 conditional doctor. However,
positive Execute, post-activation G/E prefixes, rollback-verifier and success
receipts are removed from this prerequisite carrier family and deferred in
full to the separately governed parent invariant family
`CVF-CORE-REFRESH-TARGET-REBASE-0281E93-ATTEMPT-4-OUTCOMES-2026-08-31`.
They cannot be selected, inherited or completed by prose here. The carrier
tranche permits only ParseOnly, DryRun and negative Execute tests.

Before any Execute child or write, activation requires all final parent
cross-bindings, frozen carrier/test hashes, correct parent tranche, final
authorization review, `APPROVED_FOR_SINGLE_EXECUTION`, exact worker/execution
id/effect window, unchanged carrier bytes, exact authority-template
reconstruction and worker-side host evidence. Any test/synthetic/future/
placeholder/non-final value selects matrix-owned activation refusal with zero
children and effects. Positive Execute, E1, E2, E3, E4, evidence creation,
reconciler, initializer or doctor is a carrier-tranche stop condition.

## R9 — Deterministic conformance corpus

The matrix's `CONFORMANCE_CASE` shape is the sole list of case ids. Each id is
`<ParseOnly|DryRun|Execute>__<matrix refusal code>__<category-case>`; the
harness derives exact carrier mode and expected refusal code from the first
two segments and treats the third segment only as a collision-free category
label. It must not maintain a second mapping. The repaired corpus contains
exactly 77 unique ids. Sorted case ids are canonicalized as a compact JSON
array plus LF and have SHA-256
`adc38c814195f5f7acf463e13414d3d6cf252689caddf7596da4dbb2ad18d6cc`.
The exact count and SHA-256 must equal the matrix-owned constants. Reordering source
declarations cannot change the sorted digest; adding, removing, renaming or
duplicating a case must.

For every case, both carrier result validation and an independent Python
validator must agree with the expected shape. The required operator coverage
is deletion, insertion, unknown/duplicate/reordered token, discriminator/
case replacement, type/const/enum/pattern mutation, counter mutation,
one-sided relation mutation, duplicate JSON/config keys, path/hash/reparse,
host schema, AST/call/member/process/network/write edges, Git/config/argv/env,
G prefixes, finite observation drift, negative Execute activation and
authority schema/projection/insertion. Matrix-generated invariant mutations
must also be rejected by both surfaces.

Three identical runs of every deterministic case must produce byte-identical
stdout, stderr, exit code and receipt digest after replacing only matrix-
declared test-owned absolute root tokens with their canonical fixture ids.

## R10 — Tests and evidence required later

The frozen pin names the exact future carrier and future Python test paths and
the canonical matrix digest. That manifest is pre-BUILD input, not current
consumer proof: the existing ownership guard verifies only the present pin
consumer and cannot accept absent consumer files. After a prerequisite guard
amendment provides a fail-closed future-consumer strategy, the Work Order must
require both exact BUILD files to consume the same pinned digest and the
future Python test must independently prove both bindings.

The future Python test must independently verify R2–R9, matrix digest and
ownership pin; parse the PowerShell AST and transitive graph; cover every
matrix case id; prove exact raw tuples and absence of a Project-remote CLI;
exercise separate Core/PublicRemote and Project/WorkOrder.ProjectRemote
acceptances plus cross-swap/secret/extra-remote negatives; exercise every
G-prefix including G1 semantic refusal; and compare the finite manifest
before spawn/after exit before cleanup.

Carrier tests may create only synthetic non-authoritative artifacts under a
test temporary root. They must not invoke positive Execute or any network,
doctor, fetch, reconcile, provider, credential, Core/root/pin/binding,
fixture, product, database, installation, deployment, release, commit or push
surface.

## R11 — Roles, stops and bounded claim

`SPEC_AUTHOR` owns only this SPEC, matrix, pin and registry entry. A distinct
SPEC reviewer freezes their raw hashes and recomputes the canonical matrix
digest. `WORK_ORDER_AUTHOR`, authorization reviewer, implementation worker,
completion reviewer, closer and session-sync steward remain separate phase
roles. The eventual implementation worker ceiling is exactly the two paths in
R1.

Stop on phase/role/path/hash/registry/continuity drift; collision; duplicate
JSON; matrix/pin mismatch; dynamic or unresolved edge; ambient tool
resolution; noncanonical token/config/receipt; unexpected child/argv/env;
write/network reachability in a no-effect mode; positive Execute; broad
inventory; protected-assessment contact; or any prohibited external effect.

Carrier closure may claim only that exact frozen carrier/test bytes passed the
reviewed deterministic static, parser, mutation and bounded no-effect probes.
It cannot claim a positive Execute, Core/pin movement, parent authorization,
fixture/P4-E/XR1 closure, AI/provider governance, deployment or production
readiness. No provider call is required for this repository-maintenance SPEC.

## Acceptance and next move

This partial repair is not `READY_FOR_INDEPENDENT_SPEC_REREVIEW`. The next
eligible move is a separately governed prerequisite amendment to the shared
invariant-family schema/contract/ownership guard that can machine-enforce
literal JSON-null receipt domains and ownership of absent-at-SPEC future
consumers without weakening existing families. After that amendment is
independently reviewed and frozen, a fresh bounded carrier-SPEC repair may
close `CSR4-F2/F5`, update the matrix/pin as required and return the exact
four-path set for independent rereview.

Only `SPEC_REVIEW_PASS` plus an explicit phase transition may open Work Order.
BUILD and all external effects remain unauthorized.
