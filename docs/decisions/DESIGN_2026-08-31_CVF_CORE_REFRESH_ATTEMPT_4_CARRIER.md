# DESIGN — CVF Core Refresh Attempt 4 Retained Carrier

- Tranche: `CVF-CORE-REFRESH-ATTEMPT-4-CARRIER-2026-08-31`
- Date: `2026-08-31`
- Phase: `DESIGN`
- Status: `READY_FOR_INDEPENDENT_DESIGN_REREVIEW`
- Risk: `R2`
- Active role: `REPAIR_WORKER`
- Accepted INTAKE SHA-256:
  `910ca62b6e7e13ea28cc5e28a1b867d80dd49f023a67cc18b3af425e962062e7`
- INTAKE review SHA-256:
  `f431793766683b249a9eb17d75fc2784896c8e215cb9261d04003e1903815307`
- Parent DESIGN SHA-256:
  `8c1f2a67dcd9f3e67b4b04f4cb950f990889bf3f811417b3ca087d4799ef9e13`
- Parent DESIGN review SHA-256:
  `8b259c3823589d17937f5b25b85fa0c7ac8559003f68a360d96c8a04d3d85ede`
- First DESIGN review SHA-256:
  `d75327f07c7f4296c93e70cb1e10947336fda65fd94cff7e10a77180e537095a`
- Repair scope: `CDR4-RR3-F1`, bounded round 4 after an independent new
  interface-boundary root cause; all earlier closures preserved
- BUILD authority: `NOT_GRANTED`
- External-effect authority: `NOT_GRANTED`

## 1. Decision and boundary

This tranche will produce a retained PowerShell carrier and a deterministic
Python contract test through its own complete governance chain. Its eventual
implementation ceiling is exactly:

```text
scripts/cvf_core_refresh_target_rebase_0281e93_attempt_4_carrier.ps1
tests/cvf/test_cvf_core_refresh_target_rebase_0281e93_attempt_4_carrier.py
```

The carrier is an inert prerequisite during this tranche. Its source may
contain the statically reviewable future parent-rebase effect graph, but this
tranche may exercise `Execute` only far enough to validate inputs and refuse
before a write, native child or network boundary. No accepted parent rebase
SPEC, Work Order, authorization review or external-authority decision exists
yet. Carrier FREEZE therefore cannot activate reconciliation.

The parent tranche
`CVF-CORE-REFRESH-TARGET-REBASE-0281E93-ATTEMPT-4-2026-08-31` remains parked
at `DESIGN_REVIEW_PASS`. Only a later explicit parent phase transition may
bind the frozen carrier and test hashes, create the parent artifacts needed by
`DryRun` and `Execute`, independently review those exact artifacts, and grant
an exact external-effect window. The parent Work Order may activate the frozen
carrier bytes; it may not patch, copy, regenerate or reinterpret them.

## 2. Exact carrier lifecycle and acyclic hashes

The immutable, phase-owned artifact paths for this carrier tranche are:

```text
docs/decisions/DESIGN_2026-08-31_CVF_CORE_REFRESH_ATTEMPT_4_CARRIER.md
docs/decisions/DESIGN_REVIEW_2026-08-31_CVF_CORE_REFRESH_ATTEMPT_4_CARRIER.md
docs/specs/CVF_CORE_REFRESH_ATTEMPT_4_CARRIER_2026-08-31_SPEC.md
docs/cvf/invariants/cvf-core-refresh-attempt-4-carrier-modes-2026-08-31.json
docs/specs/cvf_core_refresh_attempt_4_carrier_2026_08_31_invariant_pin.py
docs/decisions/SPEC_REVIEW_2026-08-31_CVF_CORE_REFRESH_ATTEMPT_4_CARRIER.md
docs/work_orders/CVF_CORE_REFRESH_ATTEMPT_4_CARRIER_2026-08-31_WORK_ORDER.md
docs/decisions/AUTHORIZATION_REVIEW_2026-08-31_CVF_CORE_REFRESH_ATTEMPT_4_CARRIER.md
scripts/cvf_core_refresh_target_rebase_0281e93_attempt_4_carrier.ps1
tests/cvf/test_cvf_core_refresh_target_rebase_0281e93_attempt_4_carrier.py
docs/decisions/CVF_CORE_REFRESH_ATTEMPT_4_CARRIER_WORKER_RETURN_2026-08-31.md
docs/decisions/CVF_CORE_REFRESH_ATTEMPT_4_CARRIER_COMPLETION_REVIEW_2026-08-31.md
```

Once an independent review binds a phase artifact by raw SHA-256, that artifact
is immutable. A repair creates new bytes only under an explicitly recorded
same-phase repair role and a later review binds the replacement hash. It does
not silently edit an already accepted phase input. The existing carrier
handoff is not an immutable decision artifact.

The exact transition-update continuity set is:

```text
SESSION/handoffs/CVF_CORE_REFRESH_ATTEMPT_4_CARRIER_2026-08-31.md
SESSION/ACTIVE_SESSION_STATE.json
SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json
SESSION/SESSION_MEMORY.md
CVF_SESSION/ACTIVE_SESSION_STATE.json
```

At each explicit `DESIGN -> SPEC`, `SPEC -> WORK_ORDER`, reviewed
`WORK_ORDER -> BUILD`, worker-return `BUILD -> REVIEW`, and reviewed
`REVIEW -> FREEZE` transition, the `ORCHESTRATOR` first rehydrates the current
front doors and records the transition acknowledgment in the active handoff.
It then transitions to `SESSION_SYNC_STEWARD` solely to make the other four
front doors agree with the handoff, with the compatibility mirror written
from canonical state rather than treated as authority. That bounded sync must
finish before the first material action in the receiving phase. In particular,
the reviewed Work Order hash, authorization-review hash, exact two-path BUILD
ceiling, worker identity and `BUILD` acknowledgment must already be in the
handoff before the implementation worker may create either BUILD path.

These five continuity records are governance transition records. They are
never phase-author artifacts and never enter the implementation worker's
ceiling, which remains exactly the PowerShell source and Python test named in
section 1. `docs/cvf/invariants/registry.json` is the only shared SPEC-owned
path. Terminal synchronization after completion REVIEW PASS is a separate
`CLOSER -> SESSION_SYNC_STEWARD` operation: it may update the same five
continuity paths plus exactly `IMPLEMENTATION_STATUS.json`, `docs/INDEX.md`,
`docs/catalog/MODULE_REGISTRY.json` and generated
`docs/catalog/MODULE_CATALOG.md` when their source-truth rules require it.
No terminal catalog/status/index path may be changed during BUILD or counted
inside its two-path ceiling. Exact local path predicates found all twelve
phase paths above absent before this DESIGN was created, except this DESIGN
path as created by the authorized role.

The artifact graph is acyclic:

```text
INTAKE/review -> DESIGN -> DESIGN review
  -> SPEC + carrier matrix + static matrix pin + registry entry
  -> SPEC review -> carrier Work Order -> authorization review
  -> carrier source + carrier test -> worker return
  -> completion review -> separately owned FREEZE continuity/catalog sync
  -> later parent SPEC/review -> parent Work Order/review
  -> external-authority decision -> parent Execute/receipt/review
```

The carrier matrix pin contains only the canonical matrix digest and contract
identity. The carrier Work Order binds accepted pre-BUILD artifacts but cannot
contain the not-yet-created carrier or test hashes. Neither BUILD file embeds
its own hash or the other's hash. Completion review computes both raw hashes.
Only the later parent Work Order may bind those frozen hashes. Runtime inputs
bind finalized parent artifacts through the non-self-referential envelope in
sections 4 and 8; no artifact self-hashes or depends on future bytes.

## 3. Raw-token dispatcher and exact mode tuples

The carrier has no `param(...)` block, aliases, pipeline binding, positional
binder or module import. Apart from inert function/type declarations, its
first top-level operation copies the original unbound `$args` string array.
A single raw dispatcher validates the complete token vector after the script
has been reached and before any mode entry node is reachable. The supported
host form is an external caller/worker precondition, not something `$args`
can observe or enforce:

```text
pwsh.exe -NoLogo -NoProfile -NonInteractive -File <exact-carrier-path> <tuple>
```

The later parent Work Order binds the absolute normalized `pwsh.exe` path,
its raw SHA-256, the exact carrier path and a canonical structural schema for
the host argv and carrier Execute tuple. It does not bind an exact argv array
that depends on a future review. Each schema is an ordered JSON array of
closed tagged nodes: `{"kind":"literal","value":"..."}` for every value
already final when the Work Order is authored, or
`{"kind":"deferred","field":"..."}` at exactly the value slots for
`AuthorizationReviewPath`, `AuthorizationReviewSha256`,
`ExternalAuthorityPath` and `ExternalAuthoritySha256`. Option-name tokens are
always literal nodes. No other deferred field, free-form placeholder or null
is permitted.

The later external-authority artifact, authored after authorization review,
binds the same host path/hash and final reduced host/Execute string arrays.
Those arrays contain the real authorization-review path/hash and the real
external-authority path, and omit only the complete
`--ExternalAuthoritySha256 <raw-hash>` pair to avoid self-reference. A
distinct parent worker recomputes the authority hash, inserts that one pair at
its frozen position and launches the resulting full argv array through a
non-shell process API. Its receipt records the recomputed host hash and actual
array supplied. Carrier output can prove only behavior after the script
begins; host parse failures, profile behavior or invocations that never reach
the script are caller/harness evidence and are outside the one-JSON carrier
claim.

The carrier option names are ASCII, case-sensitive and in this sole canonical
order:

```text
--Mode
--ProjectRoot
--WorkspaceRoot
--CoreRoot
--BackupRoot
--OldPin
--TargetPin
--PublicRemote
--CarrierSha256
--WorkOrderPath
--WorkOrderSha256
--SpecPath
--SpecSha256
--MatrixPath
--MatrixSha256
--PinPath
--PinSha256
--SpecReviewPath
--SpecReviewSha256
--AuthorizationReviewPath
--AuthorizationReviewSha256
--ExternalAuthorityPath
--ExternalAuthoritySha256
--ExecutionId
```

Every option has exactly one non-empty string value. The exact tuples are:

- `ParseOnly`: the ordered prefix from `--Mode ParseOnly` through
  `--CarrierSha256 <sha>` and no later token;
- `DryRun`: the ordered sequence from `--Mode DryRun` through
  `--SpecReviewSha256 <sha>`, then `--ExecutionId <id>`, and no authority
  options; and
- `Execute`: all displayed options in the displayed order, with
  `--Mode Execute`. The runtime pair
  `--ExternalAuthoritySha256 <raw-hash>` is present in the carrier invocation;
  only the authority's stored comparison template omits it.

The raw carrier and host tuple surface is parent-frozen: `--PublicRemote` is
followed directly by `--CarrierSha256` in every mode and schema. There is no
Project-remote CLI option, deferred node, tuple value or external-authority
duplicate. The distinct Project config fact described in sections 4 and 6 is
read only from the already raw-hash-bound parent Work Order block after
ParseOnly; it does not amend the raw dispatcher interface.

Before value conversion or mode logic, the dispatcher rejects odd length,
empty name/value, missing, duplicate, reordered, extra, unknown, abbreviated,
case-folded or Unicode-normalized/confusable names; positional tokens;
PowerShell `--%` or generic `--`; `name=value`; `/name`, `-name` or combined
switch syntax; array/expression/scriptblock-shaped tokens; NUL/control
characters; and coercion-shaped values. Invalid mode spelling and every
cross-mode required/forbidden option fail closed. No ambient alias, profile,
environment variable or semantic binder may repair or reinterpret a token.

Pins and SHAs are lowercase 40- or 64-character hexadecimal as applicable.
The public remote and execution-id grammar are frozen by SPEC. Paths must be
absolute, normalized, contained under their declared root and reparse-safe;
the normalized value must round-trip to the supplied token under ordinal
comparison. SPEC owns the exhaustive mutation corpus ids, exact refusal codes,
counts and digest; DESIGN defines the required families without pre-empting
that semantic matrix.

## 4. Machine-readable parent contract blocks

`DryRun` and future parent `Execute` must not discover authority-bearing data
from `PATH`, the registry, Git configuration, profiles or environment. Each
raw-hash-bound parent artifact contains exactly one canonical UTF-8 JSON block
between literal versioned sentinels. The carrier parses it with duplicate-key
rejection and a closed schema before use:

- parent SPEC/review identify the accepted matrix id/digest and P0 contract;
- parent Work Order block `CVF-CARRIER-WORK-ORDER-V1` identifies tranche,
  target, roots, frozen carrier/test hashes, tool paths and hashes, exact
  per-child argv tuples, the exact absolute host path/hash, accepted lineage
  and effect ceilings. Its closed `project_git_config_v1` object contains the
  distinct canonical `ProjectRemote` string alongside the normalized Project
  config path, raw config SHA-256 and canonical parsed key/value map. That
  credential-free value is a read-only Project config fact, not a carrier CLI
  token or transport grant. Its `execute_tuple_schema_v1` and
  `host_argv_schema_v1` are the closed tagged-node structural schemas from
  section 3; they defer both later artifact path/hash value families and do
  not contain, predict or compare any future authorization-review or
  external-authority value;
- authorization-review block identifies the exact accepted ParseOnly/DryRun
  tuples, outputs and Work Order hash; and
- external-authority block `CVF-CARRIER-EXECUTE-AUTHORITY-V1` identifies the
  parent tranche, final review path/hash, worker, single execution id, effect
  ceiling and ordered network window. It contains an
  `execute_tuple_template_without_external_authority_sha256` and a
  `host_argv_template_without_external_authority_sha256`; each is a canonical
  ordered string array that omits exactly the option name and value for
  `--ExternalAuthoritySha256`, and it contains no placeholder and no raw hash
  of its own bytes. It separately binds the normalized external-authority
  path, absolute normalized host path and host raw SHA-256.

The external-authority block cross-binds the already-final parent Work Order
path/hash. It does not duplicate `ProjectRemote` or introduce any Project
remote value into its reduced carrier/host arrays; carrier validation obtains
that field solely by parsing the verified Work Order block.

The staged comparison and authority-envelope algorithms are exact and
acyclic:

1. The pre-review Work Order is canonicalized and hashed with only its tagged
   structural schemas. A validator compares them by node count, order, tag,
   literal bytes and the exact four deferred field names; it never substitutes
   or compares a later path/hash at this stage.
2. The authorization review hashes the already-final Work Order; its final
   path/hash become inputs only to the later authority artifact, and the Work
   Order is not rewritten. After that review exists, the external-authority
   author projects each Work Order schema into a reduced array: every literal
   node is emitted unchanged; the real authorization-review path/hash and
   external-authority path replace their three deferred value nodes; and the
   adjacent literal `--ExternalAuthoritySha256` node plus its deferred value
   node are consumed but deliberately emit nothing. The resulting canonical
   string arrays must equal the authority block's reduced Execute/host arrays
   byte-for-byte. Projection must classify every schema node exactly once and
   reject an extra, missing, reordered or type-invalid node.
3. The worker reads the final authority bytes, computes lowercase raw SHA-256
   out of band, inserts `--ExternalAuthoritySha256`, `<computed-hash>` at the
   frozen slot in both reduced arrays, and requires the reconstructed host
   argv's carrier suffix to equal the reconstructed carrier tuple. It supplies
   that full host argv through a non-shell process API.
4. After the script is reached, the carrier hashes the same authority bytes,
   compares the digest ordinally with the supplied runtime hash, removes
   exactly that pair from its received tuple, canonical-decodes the remaining
   ordered strings and compares them byte-for-byte with the authority's
   reduced carrier array. The carrier does not claim to observe the host
   prefix; the worker receipt and later parent reviewer perform the equivalent
   exact comparison against the authority's reduced host array.

Carrier and worker also require equality of every duplicated finalized path,
hash, worker, execution-id and effect field across the artifacts that can
legally know it. Missing, extra, duplicate, misplaced or differently cased
runtime pairs refuse. The worker receipt records authority path, recomputed
authority hash, host path/hash and the full actual argv. Neither the Work
Order nor the authority artifact predicts a future or self hash.

The `git.exe` absolute normalized path and raw executable SHA-256 come only
from the already-hashed parent Work Order block. `Get-Command`, `where.exe`,
ambient `PATH` search and first-match resolution are forbidden. DryRun reads
that exact file, recomputes its hash, extracts the exact pin, recomputes the
executable hash and refuses before launch on any mismatch. The same rule
applies to future `python.exe` and `pwsh.exe` pins in Execute.

Carrier REVIEW has no dependency on future parent artifacts. The Python test
constructs schema-valid synthetic artifact bytes under one pytest-owned
temporary root before launching the carrier, computes their real hashes and
passes them only to local contract probes. Synthetic fixtures are explicitly
non-authoritative and cannot satisfy future parent activation because their
tranche id, roots, lineage and authority disposition are test-only values.

## 5. Closed mode reachability and AST proof

The carrier exposes three literal entry functions and one child gateway. The
static verifier begins at the complete top-level script block as well as
`Enter-ParseOnly`, `Enter-DryRun` and `Enter-Execute`; it computes transitive
closure across every function definition. It classifies `CommandAst`,
`InvokeMemberExpressionAst`, member access, type construction, redirection,
the invocation and dot-source operators, nested scriptblocks and trap/catch/
finally paths. A call is rejected if it is dynamic, unresolved, aliased,
unqualified, reflective, dot-sourced or absent from the applicable mode
matrix.

Top level may contain only declarations, strict literal initialization, the
raw `$args` copy, dispatcher validation, one literal mode selection, canonical
serialization and process exit. `Invoke-Expression`, `ScriptBlock.Create`,
`Add-Type`, reflection, COM, jobs, remoting, WMI/CIM, module loading, event
handlers, arbitrary `.Invoke()`, native invocation operators, shell command
strings and dynamic type/member names are forbidden. Direct process creation
through `Start-Process`, `System.Diagnostics.Process.Start`, WMI, COM or a
shell is forbidden everywhere except the one literal
`Invoke-AllowlistedChild` implementation. The verifier proves every path to
that implementation is mode-gated and ledgered.

The closed capability sets are:

| Mode | In-process capability | Native children |
|---|---|---|
| `ParseOnly` | raw dispatch; ordinal validation; `System.IO.Path` normalization/containment; `File.ReadAllBytes`; SHA-256; PowerShell `Language.Parser.ParseFile`; closed collections; canonical `System.Text.Json` serialization | none |
| `DryRun` | ParseOnly plus `File/Directory.Exists`, `File.GetAttributes`, `File.ReadAllText`, exact Git-admin-tree enumeration, reparse checks, duplicate-key JSON parsing and finite read-only observation manifests | only the hash-pinned `git.exe` through the gateway, in the exact eight-launch sequence in section 6 |
| `Execute` | shared in-process ParseOnly/DryRun validation plus SPEC-named preimage, evidence, atomic pin bridge and rollback functions; it does not call `Enter-DryRun` or launch a child before activation | after activation only: the cumulative Git/Python/PowerShell sequence in section 6 |

All filesystem create/write/delete/move/copy, registry, credential, secret,
socket, HTTP/web, package-manager and dynamic-code APIs are forbidden in
ParseOnly and DryRun. Their output is stdout through one canonical serializer;
file redirection and transcript creation are forbidden. Execute's mutators and
child nodes are statically present but cannot be entered merely because
`--Mode Execute` was supplied: section 8's activation predicate controls the
sole edge into them.

The Python test independently parses the retained PowerShell AST and applies
the same top-level, transitive function, .NET-member and child-launch rules.
Its negative mutations inject one forbidden top-level edge, nested edge,
dynamic member, reflective call, write API, network API, direct process
launch, child or argv at a time and require deterministic rejection.

## 6. Fail-closed Git boundary and one cumulative child sequence

Before any Git launch, the carrier resolves Git administrative paths without
invoking Git. For both `<CoreRoot>` and `<ProjectRoot>`, the supported form is
an ordinary physical `<root>\.git` directory under the corresponding physical
root. A `.git` gitfile, linked worktree, `commondir`, `config.worktree`,
`extensions.worktreeConfig`, alternate object database, shallow/graft/replace
overlay, submodule Git dir, reparse point in any root/admin ancestor or
descendant, or admin path outside its declared root is unsupported and refuses.
The refusal occurs before the gateway can launch Git. This deliberate ordinary-
repository restriction makes the worktree/common-dir boundary finite; no
ambient discovery chooses another Git dir.

The carrier reads `<admin>\config` directly as raw UTF-8 bytes with a closed,
duplicate-rejecting Git-config parser implemented in the carrier and bound by
the invariant matrix. It does not ask Git to interpret configuration. It
forbids `include`/`includeIf`, unknown sections or keys, aliases, external
fsmonitor, `core.hooksPath`, pager/editor/browser/diff/textconv/external-command
settings, credential/proxy/SSH/HTTP/transport/protocol settings, URL rewrites,
object/alternate/work-tree/common-dir overrides, maintenance/GC, and every
URL-bearing value except the two repository-specific
`remote.origin.url` facts defined below. The
parent Work Order binds each accepted config path, raw hash and canonical
parsed key/value map. The carrier recomputes all three before every launch. A
physical admin `hooks` directory may exist only as an observed,
raw-hash-pinned regular-file subtree; `core.hooksPath=NUL` is still mandatory
and G1..G8 invoke no hook.

The only URL-bearing semantic key accepted in either repository is
`remote.origin.url`, exactly once per repository. In the Core repository its
decoded value must equal runtime `PublicRemote` byte-for-byte under ordinal
comparison. In the Project repository its decoded value must equal the
separate canonical `ProjectRemote` field in the verified parent Work Order's
`project_git_config_v1` object byte-for-byte under the same comparison.
`ProjectRemote` is an exact, non-authority config fact inside that raw-hash-
bound Work Order block; it is not a carrier CLI token, is never duplicated in
the external-authority block or host tuple, is never substituted for
`PublicRemote`, is never compared to G1 and never grants a transport
operation. No `pushurl`, second URL value, additional
remote, `url.*.insteadOf`/`pushInsteadOf`, credential, proxy, helper, SSH,
HTTP, protocol, transport or remote-helper key is accepted in either map.

The canonical parsed maps record the Core and Project entries independently
as `{"remote.origin.url":"<PublicRemote>"}` and
`{"remote.origin.url":"<ProjectRemote>"}`. The Work Order binds both config
paths, raw config hashes and canonical maps, plus runtime `PublicRemote` and
its own internal canonical `ProjectRemote` field. After verifying the Work
Order path/hash and closed schema, the carrier extracts that Project field;
no raw option or external-authority value supplies it. Before
accepting either value, the parser rejects control/NUL characters, URI
userinfo, embedded username/password or token material, query/fragment secret
material, secret-shaped values, environment interpolation and remote-helper
syntax. Acceptance is read-only configuration validation: no accepted value,
scheme or key makes `fetch`, `push`, `ls-remote` or any other transport argv
reachable. The carrier requires the Core map/`PublicRemote` equality before
G1 and the Project map/`ProjectRemote` equality before G8. G1 stdout, after
removal of exactly one optional terminal LF or CRLF, must be one non-empty
line equal ordinally to `PublicRemote`; any additional line, control character
or differing byte is a post-launch semantic refusal.

Parser normalization is closed and independent of ambient Git behavior. Raw
config must be strict UTF-8 without BOM or continuation lines. Section and key
identifiers are ASCII-folded to lowercase for semantic duplicate detection;
the quoted subsection is escape-decoded and must be exactly lowercase
`origin`; surrounding syntax whitespace is discarded, while value bytes are
trimmed only according to the SPEC-frozen Git-config subset and are otherwise
preserved. Only canonical `[remote "origin"]` plus the repository-specific
exact `url = <PublicRemote>` or `url = <ProjectRemote>` may produce an
accepted URL entry, with the latter placeholder sourced solely from the
Work Order's `project_git_config_v1.ProjectRemote`; legacy dotted sections,
quoted/escaped URL values,
case-variant or escaped subsection spellings, duplicate normalized keys and
mixed newline/control encodings refuse rather than normalize into acceptance.
The mutation corpus includes both exact-origin acceptances; cross-swapped
Core/Project values; wrong scheme/host/path/case/trailing slash; URI userinfo,
embedded or secret-shaped credentials/tokens, query/fragment secrets; second
value; `pushurl`; extra remote; normalized duplicate; `url` rewrite;
credential/proxy/SSH/HTTP/protocol/transport/helper keys; quoted/escaped value;
subsection case/escape; legacy dotted-section; and G1 multi-line/output-
mismatch cases. Parser, config, token, path, hash, environment and denied-argv
rejections detected before launch require an empty child ledger,
`local_child_count = 0`, both network counters zero and
`filesystem_write_attempt_count = 0`. A G1 output mismatch is explicitly not
one of those prelaunch cases; it follows the post-launch row below.
The carrier requires the literal absence of repository/worktree config include
targets, `objects\info\alternates`, `info\grafts`, `refs\replace`, `modules`,
`commondir`, `config.worktree`, `shallow.lock`, `index.lock`, `HEAD.lock`,
`packed-refs.lock` and config lock files. Adversarial fixtures must cover an
external fsmonitor command, include and conditional-include outside the root,
pager/editor/alias/URL rewrite, invalid or additional remote URL, alternates,
hooks, linked-worktree/common-dir, and every equivalent case-folded
configuration surface; each prelaunch fixture must refuse with zero child and
network counters. Separate G-output fixtures exercise the launched-prefix
rows below.

The gateway adds the following fixed config-neutralization prefix after
`--no-optional-locks` and before `-C` on every permitted Git invocation:

```text
-c core.fsmonitor=false
-c core.hooksPath=NUL
-c core.pager=cat
-c pager.status=false
-c credential.helper=
-c http.proxy=
-c protocol.allow=never
```

Those are the only permitted `-c` tokens; their names, values and order are
literal and matrix-owned. The direct preflight remains mandatory even with
these overrides, so an override cannot hide an escape-bearing local config.
The entire Git argv grammar then has these seven literal forms, populated only
with already validated canonical values:

```text
git.exe <fixed-neutralization-prefix> -C <CoreRoot> remote get-url origin
git.exe <fixed-neutralization-prefix> -C <CoreRoot> rev-parse --verify HEAD^{commit}
git.exe <fixed-neutralization-prefix> -C <CoreRoot> rev-parse --verify origin/main^{commit}
git.exe <fixed-neutralization-prefix> -C <CoreRoot> cat-file -t <OldPin-or-TargetPin>
git.exe <fixed-neutralization-prefix> -C <CoreRoot> merge-base --is-ancestor <OldPin> <TargetPin>
git.exe <fixed-neutralization-prefix> -C <CoreRoot> status --porcelain=v1 --untracked-files=no
git.exe <fixed-neutralization-prefix> -C <ProjectRoot> diff --cached --name-only
```

No operand may start with `-`, contain a URI scheme, drive-relative or UNC
form, remote-helper syntax, control character or leave the declared root.
The gateway denies all other executables, Git global options, verbs and
arguments, including any nonliteral `-c`, `--config-env`, `--exec-path`, aliases, external
subcommands, hooks, remote helpers, transports, URLs, `fetch`, `pull`, `push`,
`clone`, `ls-remote`, `submodule`, `remote update`, `checkout`, `reset`,
`clean`, `commit`, `merge`, `rebase`, `gc`, `maintenance`, config mutation,
credential helpers, proxy and SSH options.

The child uses the Work-Order-pinned absolute executable path and an argument
array. Its environment is cleared and rebuilt from a SPEC-frozen minimal
non-secret allowlist required by Windows process startup, plus
`GIT_TERMINAL_PROMPT=0`, `GIT_CONFIG_NOSYSTEM=1`,
`GIT_CONFIG_GLOBAL=NUL`, `GIT_CONFIG_COUNT=0`, `GIT_OPTIONAL_LOCKS=0`,
`GCM_INTERACTIVE=Never`, `LANG=C` and `LC_ALL=C`. All other `GIT_*`,
`GCM_*`, askpass, credential, proxy, SSH, protocol, object-directory,
alternate-object, work-tree, common-dir, trace and config-parameter channels
are absent. The carrier never repurposes `HOME`, `CODEX_HOME` or another
ambient system option.

There is one cumulative mode/sequence table; no prose inheritance adds a
child. `cat-file` is one argv form used twice, so successful DryRun has eight,
not seven, child launches:

| Mode/outcome | Exact ordered gateway sequence | `local_child_count` | `network_attempt_count` / `network_child_count` |
|---|---|---:|---:|
| `ParseOnly`, any disposition | empty | `0` | `0 / 0` |
| `DryRun`, prelaunch refusal | empty | `0` | `0 / 0` |
| `DryRun`, G1 post-launch semantic refusal | exactly G1, launched as `LOCAL_READ`, exit code `0`, stdout/stderr digests recorded; canonical-output validation records `LOCAL_QUERY_SEMANTIC_REFUSAL` and no later entry launches | `1` | `0 / 0` |
| `DryRun`, G-prefix child/query refusal at Gk, `1 <= k <= 8` (excluding the G1 zero-exit case above) | exactly G1..Gk; Gk is the first entry with nonzero exit (`LOCAL_CHILD_NONZERO`) or zero exit plus invalid canonical output (`LOCAL_QUERY_SEMANTIC_REFUSAL`); no later entry launches | `k` | `0 / 0` |
| `DryRun`, success | G1 remote URL; G2 HEAD; G3 origin/main; G4 `cat-file OldPin`; G5 `cat-file TargetPin`; G6 merge-base; G7 Core status; G8 Project staged diff | `8` | `0 / 0` |
| carrier-tranche negative `Execute` | empty; activation refuses before G1 | `0` | `0 / 0` |
| later parent Execute, activated G1 post-launch semantic refusal | exactly G1, launched as `LOCAL_READ`, exit code `0`, stdout/stderr digests recorded; canonical-output validation records `LOCAL_QUERY_SEMANTIC_REFUSAL` and no later entry launches | `1` | `0 / 0` |
| later parent Execute, activated G-prefix child/query refusal at Gk, `1 <= k <= 8` (excluding the G1 zero-exit case above) | exactly G1..Gk with the same first-failure classification as DryRun; E1..E4 do not launch | `k` | `0 / 0` |
| later parent Execute, activated success branch | G1..G8; E1 Python P0; E2 reconciler; E3 initializer | `9` | `2 / 2` |
| later parent Execute, post-G success launched-child failure | exact prefix G1..G8/E1/E2/E3 ending at the first launched nonzero E child; no later ordinary entry | count of launched G/E1 entries | count of launched E2/E3 entries, equal in both counters |
| later parent Execute, authorized rollback verifier | the launched-child-failure prefix ending at E2 or E3, then E4 doctor exactly once; no other entry | count of launched G/E1 entries | count of launched E2/E3/E4 entries, equal in both counters |
| any mode, denied candidate | the applicable row's exact successful prefix plus one final non-launched refusal; no later entry | count of launched local entries | launched network-capable count plus `1` / launched network-capable count |

G1..G8 are exactly the forms above. Every launched G entry has its exit code
and stdout/stderr digests in the child ledger. `LOCAL_CHILD_NONZERO` means the
launched child returned nonzero; `LOCAL_QUERY_SEMANTIC_REFUSAL` means it
returned zero but its canonical output contract failed. Both are post-launch
refusals, preserve the exact launched prefix, set
`filesystem_write_attempt_count = 0`, and keep both network counters zero.
They are distinct from every prelaunch refusal, which has no child entry.
E1 is local and E2/E3/E4 are classified
`NETWORK_CAPABLE_EFFECT` conservatively because the nested reviewed scripts,
not the carrier gateway, own their transitive process/network behavior. The
gateway increments `network_attempt_count` immediately before each authorized
E2/E3/E4 launch and increments `network_child_count` only when that launch is
actually made. A denied candidate increments `network_attempt_count`, appends
a non-launched refusal entry and cannot increment either child count. Every
receipt requires `local_child_count = count(launched entries classified
LOCAL_READ or LOCAL_TEST)` and `network_child_count = count(launched entries
classified NETWORK_CAPABLE_EFFECT)`. `child_ledger_count` equals launched plus
non-launched refusal entries. SPEC freezes the exact outcome-prefix equations;
it may narrow a branch but cannot add or reorder an entry.

Future Execute permits only parent-Work-Order-enumerated argument arrays that
also match these carrier-owned structural forms:

```text
python.exe -B -m pytest -q <exact ordered P0 selectors under ProjectRoot>
pwsh.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File <CoreRoot>\scripts\update_cvf_workspace_public_core.ps1 -WorkspaceRoot <WorkspaceRoot>
pwsh.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File <ProjectRoot>\scripts\initialize_cvf_clone.ps1
pwsh.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File <CoreRoot>\scripts\check_cvf_workspace_agent_enforcement.ps1 -ProjectPath <ProjectRoot>
```

The parent SPEC and independently reviewed Work Order freeze the exact P0
selector arrays and all tool hashes. They may narrow these templates but not
add an executable, verb, option or script. The doctor form is unreachable
unless the external-authority block separately grants the conditional
rollback-verifier window. No shell, retry, alternate tool or manual Git
network command exists.

## 7. Canonical no-effect evidence and finite observation set

Every invocation that successfully reaches the carrier script emits exactly
one UTF-8 canonical JSON object to stdout and no success text to stderr. No
claim is made for host parsing/profile/startup failures that occur before the
script starts. The structural envelope contains version, mode, disposition,
bounded refusal code, execution id or null, input-artifact hash ledger,
ordered check ledger, deferred-Execute-only field list, before/after
observation-manifest digests, counters and ordered child ledger. The counters
include at least `filesystem_write_attempt_count`, `network_attempt_count`,
`network_child_count` and `local_child_count`. A child ledger entry contains
ordinal, pinned executable path/hash, exact argv array, classification,
launched boolean, exit code or null and stdout/stderr digests; it never records
credentials or raw secrets. SPEC and the invariant matrix own exact fields,
relations, refusal codes and canonicalization vectors.

All child launches pass the gateway. In ParseOnly and DryRun, the gateway
classifies an argv before launch: anything outside the local Git set increments
`network_attempt_count`, records a non-launched refusal and exits. In future
parent Execute, a child outside the exact authority-bound P0/P1/P2/P3 class is
handled the same way; an allowed network child receives its separate declared
classification and counter. Direct network APIs are AST-forbidden. ParseOnly
must have an empty child ledger and zero for all four counters. DryRun must
have `filesystem_write_attempt_count = 0`, `network_attempt_count = 0`,
`network_child_count = 0`, and exactly one of: the exact G1..G8 success
ledger; an empty prelaunch-refusal ledger with `local_child_count = 0`; or the
exact launched G1..Gk prefix ending at the first
`LOCAL_CHILD_NONZERO`/`LOCAL_QUERY_SEMANTIC_REFUSAL`, with
`local_child_count = k`. In particular, G1 zero-exit invalid canonical output
has one launched `LOCAL_READ` ledger entry, `local_child_count = 1`, both
network counters zero and `filesystem_write_attempt_count = 0`. Section 6 is
the sole child-count authority.

Immediately before the first allowed child and immediately after the last
child, the carrier builds the same finite observation manifest. Its membership
is frozen before launch and is exactly:

1. every runtime input artifact path and the carrier path, recorded as
   normalized path, kind, length, raw SHA-256 and reparse state;
2. each directly inspected root marker and parent-chain component from every
   supplied path up to its declared physical root, recorded as normalized path,
   kind, attributes and reparse state;
3. for the Core and Project ordinary Git repositories, the two physical
   `<root>\.git` directories and every descendant entry recursively under
   those exact admin directories only, recorded as an ordinal-sorted relative
   path, file/directory kind, attributes, length and raw SHA-256 for files;
4. explicit absence sentinels for `.git` gitfiles, `commondir`,
   `config.worktree`, `objects\info\alternates`, `info\grafts`,
   `refs\replace`, `modules`, all admin lock names accepted by SPEC, and every
   config include target rejected during direct parsing; and
5. the exact named non-admin files read by carrier .NET APIs, with the same
   file record. No other root or descendant is implied.

Membership or record drift is a refusal. Admin-tree enumeration is permitted
only beneath the two already resolved physical `.git` directories; recursive
enumeration of `ProjectRoot`, `WorkspaceRoot`, `CoreRoot`, the workspace
container or untracked working-tree content remains forbidden. The allowed Git
argv cannot write worktree files, and the carrier has no write API before
activation, so this design makes no whole-worktree or whole-root equality
claim.

Reparse points are rejected before traversal, and an entry cannot be followed
outside its manifest root. Hard links do not silently enlarge the claimed
write boundary: a content mutation through any alias changes the bytes/hash at
the observed admin or named-file path, while creating/removing an alias is not
reachable through an allowed carrier API or G1..G8 argv. The harness includes
a test-owned hardlink alias and requires a concurrent alias-content mutation to
produce manifest drift; it also proves that reparse and junction fixtures
refuse before child launch. The bounded proof therefore covers the complete
write-sensitive path set reachable by the allowed carrier .NET APIs and the
two closed Git admin contexts, not arbitrary descendants of a repository or
workspace root.

The pytest harness may create synthetic input artifacts only inside its own
framework-provided temporary directory before a carrier process starts and
may clean that directory only after the process exits. Those harness actions
have separate `harness_setup_write_count` and `harness_cleanup_write_count`
and are never added to carrier counters. Immediately before spawn it computes
the exact expected finite manifest above; immediately after exit and before
cleanup it independently recomputes it and compares carrier before/after
digests and entries. Stdout/stderr are captured through OS pipes, not
redirected files. The harness launches the pinned host with the exact argument
array, `-NoProfile`, telemetry/update checks disabled and a closed environment,
and separately records host precondition evidence. Static AST closure, the
fail-closed Git contract, gateway telemetry and this finite observation set
jointly support only the bounded zero-write/zero-network claim; test-harness
setup is never mislabeled as a carrier effect.

## 8. Execute activation boundary

`Enter-Execute` performs the same in-process raw, hash, path, AST, direct Git-
config and contract validations as DryRun, but does not call `Enter-DryRun`
and does not launch G1..G8 before activation. Before any G1 child, P0 child,
evidence creation, write function or
effect-capable PowerShell child becomes reachable, it requires all of the
following:

1. every runtime artifact is raw-hash-bound and every internal cross-binding
   agrees;
2. the parent tranche id is exactly
   `CVF-CORE-REFRESH-TARGET-REBASE-0281E93-ATTEMPT-4-2026-08-31`;
3. the parent Work Order and authorization review both bind the frozen carrier
   and test path/hash published by carrier FREEZE;
4. the external-authority block has a final `APPROVED_FOR_SINGLE_EXECUTION`
   disposition, exact review path/hash, worker and execution id, and grants
   the exact P0/P1/P2/P3/effect ceilings without self-reference;
5. current carrier bytes equal the frozen hash before and after validation;
   and
6. the carrier's current tuple, after removal of exactly the runtime authority-
   hash pair, equals the authority block's reduced carrier-tuple template
   byte-for-byte after canonical decoding; and
7. the worker-side precondition binds the exact host path/hash and reconstructed
   full host argv using the same out-of-band hash insertion algorithm, with
   those actual values reserved for the worker receipt and parent review rather
   than falsely inferred by `$args`.

Any carrier-tranche artifact, test-only fixture, missing/future placeholder,
wrong tranche, non-final review, unapproved authority, hash drift or tuple
drift returns a refusal before the gateway permits a child and before any
write API. During this prerequisite BUILD/REVIEW, only such negative Execute
probes are authorized. A positive Execute probe, P0 child, reconciler,
initializer, doctor, evidence-directory creation or other effect is a stop
condition, not a test.

The later parent external authority is necessary but not self-executing. A
distinct parent `IMPLEMENTATION_WORKER` must externally recompute carrier,
Work Order, authorization-review, host and external-authority hashes,
reconstruct and compare the exact full host argv, invoke the exact frozen
carrier once through a non-shell process API, and own all resulting effects/
evidence under the parent Work Order. Carrier FREEZE by itself grants none of
those actions.

## 9. Invariant family and test architecture

Applicability is `TRIGGERED`: this R2 carrier has mode-dependent required and
forbidden fields/effects, shared canonical output, exact counters, multiple
validator surfaces, coupled source/test/matrix/pin artifacts and the adjacent
Attempt-3 wrapper failure. SPEC must register the collision-free family:

- family id:
  `CVF-CORE-REFRESH-ATTEMPT-4-CARRIER-MODES-2026-08-31`;
- matrix path:
  `docs/cvf/invariants/cvf-core-refresh-attempt-4-carrier-modes-2026-08-31.json`;
- static pin path:
  `docs/specs/cvf_core_refresh_attempt_4_carrier_2026_08_31_invariant_pin.py`.

This id is distinct from the later parent family
`CVF-CORE-REFRESH-TARGET-REBASE-0281E93-ATTEMPT-4-OUTCOMES-2026-08-31`.
The carrier matrix is the sole semantic owner of carrier modes, shapes,
required/forbidden fields, counter relations, mutations and validator
bindings. Work Order and reviews reference its id/digest through
`docs/templates/INVARIANT_FAMILY_PROOF.md`; they do not copy its rules.

The exact Python test must cover raw-token table cases; canonical JSON vectors;
duplicate-key and hash/path/reparse failures; complete top-level/transitive
AST reachability; .NET and native launch negatives; per-mode child/argv and
environment closure; direct config parsing and adversarial include/fsmonitor/
pager/editor/alias/proxy/credential/transport/alternates/hooks/worktree/common-
dir fixtures, including separate exact Core
`remote.origin.url = PublicRemote` and Project
`remote.origin.url = WorkOrder.project_git_config_v1.ProjectRemote`
acceptance, cross-swapped values,
secret-shaped values, extra remotes and all closed-schema URL/config
normalization mutations; the exact G1..G8
ledger and every permitted Execute prefix;
finite observation membership/drift including reparse, junction and hardlink
cases; ParseOnly and DryRun counters; negative Execute activation; authority-
template insertion/comparison vectors; Work-Order tagged-schema validation,
deferred-field expansion and final-authority reduced-array reconstruction;
host-precondition evidence boundaries; matrix digest/ownership bindings; and
deterministic repeated outputs. SPEC
freezes corpus ids, exact counts, expected codes and digests. Tests may not
invoke a positive Execute path or assert parent reconciliation success.

## 10. Roles, gates and changed-set ownership

- `DESIGN_AUTHOR` owned the first DESIGN bytes; the authorized
  `REPAIR_WORKER` owns only this replacement DESIGN. Round 1 closed
  `CDR4-F1/F3/F5/F6`; round 2 closed `CDR4-RR1-F1` and exposed the two
  independent realizability residuals; round 3 closed `CDR4-RR2-F1/F2` at
  their substantive roots and exposed the parent-interface drift. This
  bounded round 4 closes only `CDR4-RR3-F1` while preserving every prior
  closure.
- `INDEPENDENT_DESIGN_REVIEWER` owns only its review and must report findings
  and waivers explicitly.
- After an explicit transition, `SPEC_AUTHOR` owns only the SPEC, new matrix,
  static pin and registry entry; a distinct reviewer freezes their hashes.
- `WORK_ORDER_AUTHOR` owns only the exact carrier Work Order. It must enumerate
  commands, hashes, the exact two-path BUILD ceiling, evidence and stop rules.
- `INDEPENDENT_AUTHORIZATION_REVIEWER` may run local static/pre-BUILD checks
  only. Source/test are still absent, so it cannot claim their behavior.
- A distinct `IMPLEMENTATION_WORKER` may create only the two implementation
  paths after authorization review PASS. It may run only the Work-Order-listed
  deterministic tests and negative/no-effect carrier probes.
- `INDEPENDENT_COMPLETION_REVIEWER` recomputes all hashes, inspects source and
  test, reruns the exact corpus and verifies changed-set/no-effect evidence.
- At explicit phase transitions, `ORCHESTRATOR -> SESSION_SYNC_STEWARD` owns
  only the exact five-path continuity update in section 2. After completion
  review PASS, `CLOSER -> SESSION_SYNC_STEWARD` separately owns the exact
  terminal continuity/catalog/status/index set there. Neither role may edit a
  phase artifact or either BUILD path. No commit steward is activated here.

DESIGN review PASS is required before SPEC; SPEC review PASS before Work
Order; exact authorization review PASS before BUILD; completion review PASS
before FREEZE. A phase PASS never silently authorizes the next phase.

## 11. Stop rules and bounded claim

Stop on phase, role, path, hash, registry or continuity drift; any collision;
unreviewed source/test creation; unresolved/dynamic AST edge; ambient tool
resolution; noncanonical token; parser ambiguity; matrix/pin mismatch; write
or network reachability in a no-effect mode; unexpected child/argv/environment
entry; nonzero prohibited counter; snapshot drift; positive Execute reach;
future parent dependency in carrier tests; broad inventory; protected-state
contact; or any need for doctor, fetch, reconcile, credentials, Core/root/pin/
binding mutation, unauthorized continuity mutation, fixture repair, P4-E/XR1 movement, product/
runtime/database change, installation, deployment, release, commit or push.

The protected operator assessment remains excluded from open, read, hash,
name, inventory, stage and use. Verification uses only exact allowlisted local
paths. The inherited fixture baseline `28 passed, 2 skipped, 7 failed`, P4-E
`DESIGN_REVIEW_PASS` and XR1 debt remain parked.

Carrier closure may claim only that the exact frozen PowerShell/Python bytes
passed the reviewed static, parser, mutation and bounded no-effect probes. It
cannot claim that a positive Execute occurred, the Core or pins moved, the
parent rebase is authorized or correct, the fixture/P4-E/XR1 is closed, or
that CVF governs AI/provider behavior. No provider call is required for this
repository-maintenance DESIGN, and mock output is not governance proof.

## 12. Repair closure mapping

| Finding | Consolidated closure |
|---|---|
| `CDR4-F1` | Section 2 separates immutable phase artifacts, the exact five transition-update continuity paths and owners/timing, the exact terminal sync set, and the two-path worker ceiling. |
| `CDR4-F2` | Sections 3, 4 and 8 define the acyclic staged structural-schema, final reduced-array and out-of-band self-hash insertion model; no artifact predicts a future or self hash. |
| `CDR4-F3` | Sections 3, 4, 7 and 8 make the host form a caller/worker precondition, bind exact host path/hash/argv, require a non-shell worker receipt, and limit one-JSON output to script-reached invocations. |
| `CDR4-F4` | Section 6 resolves ordinary Git admin paths without Git, directly parses and pins a closed per-repository config schema, accepts only the exact Core `remote.origin.url = PublicRemote` and Project `remote.origin.url = WorkOrder.project_git_config_v1.ProjectRemote` facts, rejects all adjacent URL/rewrite/transport escape surfaces, neutralizes fixed settings and requires adversarial fixtures. |
| `CDR4-F5` | Section 6 is the sole cumulative child authority: seven Git forms produce exactly G1..G8, negative Execute has no child, and activated branches have explicit sequence and counter equations. |
| `CDR4-F6` | Section 7 defines the finite exact manifest for named API reads and both Git admin trees, explicit absence records, reparse refusal and hardlink observability, while expressly rejecting any whole-root claim. |
| `CDR4-RR1-F1` | Sections 3 and 4 remove future authorization-review values from every Work-Order-bound exact array. The Work Order owns only a tagged structural schema with four deferred value fields; the later authority owns final reduced arrays containing the real review path/hash and omitting only its own hash pair. Exact schema expansion, reduced-array comparison and self-hash insertion are separate acyclic stages. |
| `CDR4-RR1-F2` | Section 6 permits exactly one normalized Core `remote.origin.url` whose decoded value equals `PublicRemote` ordinally, binds its canonical map and G1 output, and keeps that Core authority comparison separate from the Project config fact. |
| `CDR4-RR2-F1` | Sections 6 and 7 separate all zero-child prelaunch refusals from launched-prefix query refusals. A G1 zero-exit invalid-output refusal records exactly one launched `LOCAL_READ`, `local_child_count = 1`, both network counters and the write-attempt counter zero; every later G-prefix ends at its first classified failure without reordering. |
| `CDR4-RR2-F2` | Sections 4, 6 and 9 bind a distinct, credential-free Work-Order `ProjectRemote` to exactly one Project `remote.origin.url`, its config hash and canonical map. It is never Core `PublicRemote`, G1 authority or transport authority; every push URL, extra remote, rewrite, credential, proxy, helper and transport surface refuses before launch. |
| `CDR4-RR3-F1` | Sections 3, 4 and 6 restore the accepted parent raw interface exactly: `--PublicRemote` is followed directly by `--CarrierSha256`, and no raw carrier/host tuple, structural schema or authority array carries a Project-remote option. The verified parent Work Order alone owns canonical `project_git_config_v1.ProjectRemote`; the carrier parses that hash-bound non-authority fact before Project config validation/G8, while the external authority cross-binds only the Work Order hash. |

All six original findings, both round-1 residuals, both round-2 residuals and
the round-3 interface residual are addressed without waivers. Execute remains
negative-only for this carrier tranche, and the zero-network/zero-external-
effect boundary is unchanged. Round-4 status is
`READY_FOR_INDEPENDENT_DESIGN_REREVIEW`.

## 13. DESIGN acceptance and next move

Independent DESIGN review must verify exact lifecycle paths and the acyclic
hash graph; raw tuple realizability and host-token edge cases; non-ambient
tool pinning; closed top-level/transitive AST and per-mode callable/child/argv
architecture; deterministic no-effect attribution; canonical output shape;
Execute activation separation; the CDR4-F1..F6 closure mapping; invariant-
family identity; the preserved `CDR4-RR1-F1/F2` closure mapping; the exact
`CDR4-RR2-F1/F2` closure mapping; the exact `CDR4-RR3-F1` round-4 closure;
roles, gates, stop rules and claim boundary.

Next governed move: independent review of this exact DESIGN only. SPEC,
matrix/pin/registry mutation, Work Order, source/test BUILD, carrier execution,
parent phase movement, doctor/fetch/reconcile/network and all external effects
remain unauthorized.
