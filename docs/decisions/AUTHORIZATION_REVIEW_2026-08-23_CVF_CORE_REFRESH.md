# Independent Authorization Review — CVF Public-Core Refresh

- Work order: `CVF-CORE-REFRESH-WO-2026-08-23`
- Reviewed phase: `WORK_ORDER` only
- Reviewer role: `INDEPENDENT_AUTHORIZATION_REVIEWER`
- Risk ceiling: `R2`
- Review date: `2026-08-23`
- Disposition: `AUTHORIZATION_REVIEW_CHANGES_REQUIRED`

## Review boundary and recomputed evidence

The review compared
`docs/work_orders/CVF_CORE_REFRESH_2026-08-23_WORK_ORDER.md` with final
`SPEC_REVIEW_PASS`, the accepted DESIGN and conditional-network amendment,
the reconciler, workspace-root installer, initializer and doctor source, and
current canonical continuity, Core/downstream refs and dirty/staged state.

Independent read-only recomputation produced:

- Work Order raw-byte SHA-256:
  `969782ddf5034ed952eb5478dfe65ce01e4e87d7fec1f1c9da8f175ac098791e`
  — matches the handoff;
- downstream increment ceiling: exactly 12 unique paths — matches DESIGN and
  SPEC;
- workspace-root ceiling: exactly 17 unique targets; the declared first 14
  exist and the three obsolete-overlay deletion candidates are absent;
- pre-Work-Order set after excluding the evidence-ineligible assessment and
  the Work Order itself: exactly 26 unique sorted paths;
- LF-terminated path-list digest:
  `edcb7d6a85efeeb11937898d91f42be314b081883f6452b87235555d9f5820ce`
  — matches the Work Order;
- LF-terminated current `path<TAB>raw-file-sha256` digest:
  `64e1f8dc81ba3cd975f02bcadbc35b13ff8c3099a8d15eeec1205664691f3de7`
  — does not match the declared
  `4f1602695624a92685da44318fbfc68dfcde1f21749b55594707724a39175eed`;
- downstream `HEAD == origin/main ==
  0b89016df8483a4904d2c64b1a6560ccbc6b27ae`, staged set empty;
- hidden Core clean at
  `7d9f360a3df11ac998972728000785799399c02b`, fetched target
  `3b031fec35473e6ee6a554c4c72400e7a23b06c5`, ancestry exactly `0` ahead /
  `1` behind; and active workspace profile `operator-local`.

`python scripts/check_session_state.py` and `git diff --check` passed. No
network, reconciliation or other external effect was performed. The operator
assessment was not opened, hashed, inventoried, edited, staged or used.

## Numbered findings

1. **CORE-REFRESH-WO-AUTH-REV-F1 — The mandatory protected-content baseline
   is not reproducible.** The 26-path set and its path digest reproduce, but
   hashing those same current 26 files yields
   `64e1f8dc81ba3cd975f02bcadbc35b13ff8c3099a8d15eeec1205664691f3de7`, not
   the required `4f160269...`. The Work Order supplies neither the individual
   frozen `path<TAB>sha256` manifest nor byte preimages for the claimed
   historical moment, so an authorization reviewer or worker cannot reproduce
   the declared historical content digest after Work-Order continuity updates.
   Repair by binding a reproducible current baseline and its complete
   per-path manifest, or remove the unverifiable historical predicate in favor
   of the already required BUILD-start freeze. Do not treat the matching path
   count/digest as content proof.

2. **CORE-REFRESH-WO-AUTH-REV-F2 — The SPEC-mandated validator bodies are not
   actually bound.** Final SPEC requires the Work Order to provide exact
   inline command bodies and frozen path arrays without changing the five
   named predicates. The Work Order contains predicate summaries and literal
   placeholders such as `<core>`, `<workspace-root>` and
   `@'...Python assertions...'@ | python -`; there is no executable
   `PIN_EQUALITY_PROBE`, `ROOT_EFFECTS_PROBE`, `INCREMENTAL_SCOPE_PROBE`,
   `JSON_PARSE_PROBE` or `REVIEW_OWNERSHIP_PROBE`. Consequently reviewers
   cannot run the stated acceptance oracle, and command/output embedding
   cannot prove that no predicate was omitted. Bind exact containment-safe
   commands, full frozen 12/17/protected arrays, inputs and expected outputs in
   the Work Order before BUILD authorization.

3. **CORE-REFRESH-WO-AUTH-REV-F3 — The required per-operation network receipt
   cannot be produced by the exact command graph as written.** The initializer
   performs its fetch and then invokes the doctor, which performs another
   fetch, inside one outer command. The initializer does not emit the full
   `origin/main` observed immediately after its fetch or an operation-scoped
   receipt; the doctor prints only a shortened commit on success. The
   reconciler likewise reports a shortened clone commit and its outer exit
   code covers later root installation too. Post-command inspection exposes
   only the final ref and cannot prove each nested operation's full observed
   tip and exit code, especially if the public tip moves between fetches.
   `networkOperations` would therefore be reconstructed assertion rather than
   raw evidence. Provide a reviewed, non-credentialed observation mechanism
   that preserves the exact command/source and records each operation's owner,
   exact URL, full observed target and exit code, or narrow the evidence claim
   through an accepted SPEC amendment. The same mechanism must cover the
   conditional `ROLLBACK_VERIFIER` and reviewer-owned doctor without mixing
   ownership.

4. **CORE-REFRESH-WO-AUTH-REV-F4 — Install authority is internally
   ambiguous.** The header grants `install` authority `0`, while the exact
   reconciler necessarily invokes
   `install_cvf_workspace_root_wrappers.ps1` and writes the authorized root
   wrapper set. Accepted DESIGN prohibits dependency/package installation but
   explicitly includes this workspace-root wrapper installer in the 17-target
   reconciliation effect. State that distinction exactly: dependency/package
   install authority remains zero, while the reconciler-invoked root-wrapper
   installer is authorized only for the enumerated 17-target effect. As
   written, the command both violates and relies on the literal authority
   header.

## Waivers

1. `NONE`. No finding is waived or deferred.

## Accepted Work Order boundaries

Apart from F1-F4, the Work Order correctly preserves role separation, the
12-path downstream and 17-target root ceilings, P4-C byte protection,
BUILD-start preimages, exact local/public refs, three-operation success and
zero-to-three-prefix-plus-one rollback-verifier failure accounting,
preservation-only rollback, reviewer-only completion artifact, stop
conditions, invariant-family `NOT_APPLICABLE` decision, and zero provider/
credential/dependency/database/deployment/commit/push boundary.

## Disposition

`AUTHORIZATION_REVIEW_CHANGES_REQUIRED`.

Return only `CORE-REFRESH-WO-AUTH-REV-F1..F4` for bounded Work Order repair
and independent rereview. Reconciliation and BUILD remain unauthorized.

## Bounded rereview — CORE-REFRESH-WO-AUTH-REV-F1..F4

- Rereview role: `INDEPENDENT_AUTHORIZATION_REVIEWER`
- Rereview scope: repaired F1-F4 only
- Rereview disposition: `AUTHORIZATION_REVIEW_CHANGES_REQUIRED`

### Independently recomputed state

- repaired Work Order raw-byte SHA-256:
  `44a2c88f09ae11923fbddd09cc56226ad5c3f1e3fbdf373bcb70a0d560e13da0`
  — matches the current handoff;
- downstream increment ceiling: exactly 12 unique paths;
- workspace-root ceiling: exactly 17 unique targets, with 14 existing and
  three absent deletion candidates;
- protected pre-Work-Order baseline after excluding the assessment, Work
  Order and authorization-review artifact: exactly 26 unique paths, with
  LF-terminated path digest
  `edcb7d6a85efeeb11937898d91f42be314b081883f6452b87235555d9f5820ce`;
- downstream `HEAD == origin/main ==
  0b89016df8483a4904d2c64b1a6560ccbc6b27ae`, staged set empty; hidden Core
  clean at `7d9f360a3df11ac998972728000785799399c02b`, exactly `0` ahead / `1`
  behind frozen fetched target
  `3b031fec35473e6ee6a554c4c72400e7a23b06c5`.

### Finding dispositions

1. **CORE-REFRESH-WO-AUTH-REV-F1 — CLOSED.** The unreproducible historical
   content-manifest digest is no longer an acceptance predicate. The 26-path
   count and path digest remain reproducible orientation only; the fresh
   BUILD-start per-path raw SHA-256 manifest and byte preimages are explicitly
   authoritative for protection and rollback.

2. **CORE-REFRESH-WO-AUTH-REV-F2 — RESIDUAL
   `CORE-REFRESH-WO-AUTH-REV-F2-R1`.** The frozen 12/17 arrays and validator
   body are now concrete, but the body does not semantically enforce the
   predicates it claims:

   - set equality allows duplicate `beforeRootTargets`/`afterRootTargets`
     entries and does not require each array length to be exactly 17;
   - receipt dictionaries collapse duplicate inventory paths, and no predicate
     requires the return path set to equal the BUILD-start set plus only the
     two worker evidence paths;
   - no current `git status` inventory is compared with the receipt, so an
     undeclared path 13 can be omitted from the receipt and pass;
   - receipt SHA strings are compared with each other but never recomputed
     from current protected/P4-C files, root targets or preserved preimages;
   - root existence/hash fields, backup existence/containment, command records
     and completion-review author role are not validated;
   - `trace2RawPath` and `packetRawPath` need only be non-empty strings; their
     files, raw contents and one-to-one operation correlation are not checked;
   - every network entry is required to have target equality and exit code
     zero even on the accepted failure branch, so a failed/moved-target Git
     operation that correctly triggers rollback cannot satisfy the validator.

   Bind an executable validator that recomputes rather than trusts these
   receipts, enforces exact unique sets and actual dirty delta, validates
   contained preserved evidence, and distinguishes success-operation rules
   from faithfully recorded failure-operation evidence.

3. **CORE-REFRESH-WO-AUTH-REV-F3 — RESIDUAL
   `CORE-REFRESH-WO-AUTH-REV-F3-R1`.** `GIT_TRACE2_EVENT` plus
   `GIT_TRACE_PACKET` is a feasible non-network-observation mechanism for
   preserving top-level/nested argv and exit events together with advertised
   full refs. Prompt and credential-helper disabling, exact remote/target,
   secret-stop, raw preservation and timestamp/process correlation are now
   stated. However, the receipt schema records only two raw-path strings per
   operation and the validator never parses either trace, so it cannot prove
   the required one-to-one owner/argv/exit/advertised-ref correlation or the
   exact three-operation/conditional-verifier provenance. Also, environment
   variables set by the BUILD worker cannot be inherited by a later independent
   REVIEW/rereview process as claimed; each reviewer must establish fresh,
   separately owned trace paths and disabled-credential environment for its
   single doctor fetch. Bind correlation identifiers/trace spans and parsing
   predicates, and state the independent per-review environment setup.

4. **CORE-REFRESH-WO-AUTH-REV-F4 — CLOSED.** Authority now distinguishes zero
   dependency/package installation from the reconciler-invoked workspace-root
   wrapper refresh, which is limited to the exact 17-target root ceiling.

### Rereview waivers

1. `NONE`. No finding is waived or deferred.

Role separation, P4-C protection, rollback/stop semantics, the exact
three-operation success graph, failure prefix `0..3` plus at most one
conditional rollback verifier (maximum four), separate one-doctor-fetch
ownership per independent review/rereview, and zero provider/credential/
dependency/database/deployment/commit/push boundaries otherwise remain
unchanged. BUILD authority remains `NOT GRANTED`.

`python scripts/check_session_state.py` and `git diff --check` passed; the
staged set is empty. No network, reconciliation, initializer, provider,
installation, deployment, commit or push action occurred. The operator
assessment was not opened, edited, hashed, staged, inventoried or used.

## Final disposition after bounded rereview

`AUTHORIZATION_REVIEW_CHANGES_REQUIRED`.

Return only `CORE-REFRESH-WO-AUTH-REV-F2-R1` and
`CORE-REFRESH-WO-AUTH-REV-F3-R1` for bounded repair and independent rereview.
F1 and F4 are closed without waiver. Reconciliation and BUILD remain
unauthorized.

## Second bounded rereview — residual F2-R1 / F3-R1

- Rereview role: `INDEPENDENT_AUTHORIZATION_REVIEWER`
- Rereview scope: repaired residuals F2-R1 and F3-R1 only
- Rereview disposition: `AUTHORIZATION_REVIEW_CHANGES_REQUIRED`

### Recomputed evidence

- Work Order raw-byte SHA-256:
  `aadb91be972953637570eed0b576d0ab1b2165703b706f58be175d44c067be02`
  — matches current continuity;
- frozen arrays: `PROTECTED=26`, `ROOTS=17`, `CEILING=12`, each unique;
- independently recomputed LF-terminated protected-path digest:
  `edcb7d6a85efeeb11937898d91f42be314b081883f6452b87235555d9f5820ce`;
- validator Python body compiles successfully;
- the current non-assessment dirty set is the 26 protected paths plus the Work
  Order and authorization review, exactly 28 paths;
- `.cvf/manifest.json`, `AGENTS.md`, `knowledge/manifest.json` and
  `IMPLEMENTATION_STATUS.json` are currently clean but are four authorized,
  required mutable carriers that success must change;
- session-state and `git diff --check` guards pass; staged set is empty.

### Residual findings

1. **CORE-REFRESH-WO-AUTH-REV-F2-R1 — RESIDUAL
   `CORE-REFRESH-WO-AUTH-REV-F2-R1-R1`: the exact inventory oracle makes the
   success path impossible.** The validator requires BUILD-start inventory to
   equal `PROTECTED + Work Order + authorization review` (28 paths) and return
   inventory to equal that set plus only the two worker evidence paths (30).
   Actual success must also modify the four currently clean carriers named
   above, so actual porcelain at return is at least 34 paths. The validator
   then compares actual porcelain exactly with the 30 receipt entries and must
   fail. Freeze all ten mutable-carrier preimages independently of dirty
   status, model clean-to-dirty authorized transitions explicitly, and require
   actual return porcelain to equal the protected baseline plus precisely the
   actually changed clean carriers and two evidence paths—never an omitted or
   invented receipt set.

2. **CORE-REFRESH-WO-AUTH-REV-F2-R1 — RESIDUAL
   `CORE-REFRESH-WO-AUTH-REV-F2-R1-R2`: failure/rollback predicates remain
   contradictory and incomplete.** The outcome-independent validator requires
   `coreBackupPath` to exist strictly under `_cvf-core-backups`, although
   rollback restores that prior Core by moving it back to the canonical hidden
   Core path; the sanctioned reconciler and accepted rollback do not leave a
   second prior-Core copy at the original backup path. Failure mode also does
   not require the ten mutable carriers to equal their BUILD-start preimages,
   despite mandatory rollback requiring their restoration, and it trusts
   `restoredRootTargets`, failed-Core/failed-root-delta paths and failure
   command exit records without validating their preserved contents or command
   exit evidence. In particular, a failure command entry need not even contain
   `exitCode`, because that key is only read on success. Bind outcome-specific
   backup-location semantics, exact downstream restoration, preserved failed
   delta hashes and complete command schemas/evidence.

3. **CORE-REFRESH-WO-AUTH-REV-F3-R1 — RESIDUAL
   `CORE-REFRESH-WO-AUTH-REV-F3-R1-R1`: raw-trace immutability and operation
   ownership are not yet enforced end to end.** The repaired parser now checks
   raw hashes, SIDs, argv/exit, packet-descendant advertised main refs, extra
   clone/fetch sessions, secrets, and fresh reviewer pairs. However:

   - the Work Order never requires clearing `GIT_TRACE2_EVENT` and
     `GIT_TRACE_PACKET` after the governed operations and before the validator;
     the validator itself runs multiple Git subprocesses, which inherit and
     append to the trace2 file after its receipt hash was frozen, invalidating
     the claimed immutable raw hash in both worker and review mode;
   - text requires a fresh rollback trace pair, but code does not require the
     `ROLLBACK_VERIFIER` pair to differ from the prefix pair;
   - the two initializer-owned fetches have identical argv, and the validator
     does not check trace start chronology or outer-command ancestry, so their
     raw spans can be swapped between `INITIALIZER_FETCH` and
     `INITIALIZER_DOCTOR_FETCH` while still passing one-to-one structural
     checks;
   - review trace-pair disjointness is enforced, but review `operationId` is
     not required to be fresh relative to BUILD operations.

   Freeze/close the trace sinks and clear the trace environment before any
   validator Git subprocess; enforce rollback-pair separation, chronological
   owner binding for the two nested fetches, and review operation-id freshness.

### Second-rereview waivers

1. `NONE`. No finding is waived or deferred.

The validator syntax, exact frozen arrays/digest, actual-porcelain parsing,
preimage/root/raw-trace hash recomputation, backup containment primitives,
P4-C/nonmutable equality, changed-set ceiling, success/failure prefix grammar,
extra network-session rejection, prompt/credential-helper disabling and fresh
reviewer process setup are accepted subject only to the contradictions above.
F1 and F4 remain closed. BUILD authority remains `NOT GRANTED`.

No network, reconciliation, initializer, provider, installation, deployment,
commit or push action occurred. The operator assessment was not opened,
edited, hashed, staged, inventoried or used.

## Final disposition after second bounded rereview

`AUTHORIZATION_REVIEW_CHANGES_REQUIRED`.

Return only `CORE-REFRESH-WO-AUTH-REV-F2-R1-R1`,
`CORE-REFRESH-WO-AUTH-REV-F2-R1-R2` and
`CORE-REFRESH-WO-AUTH-REV-F3-R1-R1` for bounded repair and independent
rereview. Reconciliation and BUILD remain unauthorized.

## Third bounded rereview — residual F2-R1-R1 / F2-R1-R2 / F3-R1-R1

- Rereview role: `INDEPENDENT_AUTHORIZATION_REVIEWER`
- Rereview scope: repaired residuals F2-R1-R1, F2-R1-R2 and F3-R1-R1 only
- Rereview disposition: `AUTHORIZATION_REVIEW_CHANGES_REQUIRED`

### Recomputed evidence

- Work Order raw-byte SHA-256:
  `2a9092ddc83b6a29b751599327f2c902a9d40c90beb2b0d69d5c9f2014d869ad`
  — matches current continuity;
- frozen arrays remain exact and unique: `PROTECTED=26`, `ROOTS=17`,
  `CEILING=12`;
- independently recomputed LF-terminated protected-path digest remains
  `edcb7d6a85efeeb11937898d91f42be314b081883f6452b87235555d9f5820ce`;
- validator Python body compiles successfully;
- current non-assessment porcelain is exactly the 26 protected paths plus the
  Work Order and this authorization review; staged set is empty;
- the success inventory equations now include the exact four
  `CLEAN_TO_MUTATE` paths and two worker evidence paths, and the failure model
  now distinguishes newly dirty carriers from retained failure-evidence
  carriers;
- outcome-specific moved-back `coreBackupPath`, failed-root inventory,
  root-restoration comparison, parent/Python trace-environment clearing, final
  raw-trace rehash, rollback-pair separation, chronological span ordering,
  extra-session rejection and reviewer operation-id separation are now coded.

### Residual findings

1. **CORE-REFRESH-WO-AUTH-REV-F2-R1-R1 — RESIDUAL
   `CORE-REFRESH-WO-AUTH-REV-F2-R1-R1-R1`: rollback still lacks authoritative
   BUILD-start preimages for every mutable carrier and widens the accepted
   failure return set.** `buildStartInventory` intentionally contains only
   paths dirty at BUILD start, so it excludes the four currently clean
   `CLEAN_TO_MUTATE` carriers. The Work Order nevertheless requires all ten
   mutable carriers to be restored from BUILD-start preimages, while neither
   the receipt nor validator freezes and recomputes raw preimages for those
   four clean carriers. Git-clean status after rollback is useful but is not
   the required independent byte preimage proof. In addition,
   `FAILURE_EVIDENCE_ALLOWED = MUTABLE[3:]` permits up to seven mutable
   governance/continuity carriers to remain changed as failure evidence. The
   accepted DESIGN requires restoration of all ten carriers and retains
   failure evidence in the two separately authorized worker evidence paths;
   no accepted amendment authorizes this mutable-carrier widening. Freeze all
   ten carrier preimages regardless of initial porcelain state, require their
   byte restoration on failure, and keep failure evidence within the already
   authorized evidence artifacts unless the governing DESIGN/SPEC is amended.

2. **CORE-REFRESH-WO-AUTH-REV-F2-R1-R2 — RESIDUAL
   `CORE-REFRESH-WO-AUTH-REV-F2-R1-R2-R1`: partial/replacement-Core preservation
   and command/network correlation remain optional or receipt-trusting.** A
   failure receipt may set `replacementCorePreservedPath` to null even after a
   successful `RECONCILER_CLONE`; the validator neither derives required
   presence from the observed network prefix nor proves that no partial clone
   directory existed when it is absent. When a valid replacement is retained,
   its HEAD is compared only with the receipt's `replacementCoreHead`, not
   with the frozen target required after a successful clone. The complete
   command-item schema and exit ordering are improved, but `commands` is not
   derived from actual operation owners: a failed clone can be reported with
   no `RECONCILER` command, and an initializer-owned fetch can be accepted
   without an `INITIALIZER` command. Derive preservation obligations and
   command-prefix/exit requirements from the validated network prefix, bind a
   completed clone to the frozen target, and prove absence or quarantine of
   every partial replacement directory.

3. **CORE-REFRESH-WO-AUTH-REV-F3-R1-R1 — RESIDUAL
   `CORE-REFRESH-WO-AUTH-REV-F3-R1-R1-R1`: trace pairs are structurally
   separated but their freshness window is not proved.** The repaired trace
   controls close the prior environment-clearing, final-rehash,
   rollback-pair, chronological-order, extra-span and operation-id issues.
   However, worker trace start timestamps are merely sorted; they are not
   bounded by receipt `buildStart` and `buildReturn`. Old raw trace pairs can
   therefore be reused if their hashes and structural fields match. REVIEW
   receipts do not carry a required review start/return window at all, so pair
   disjointness from BUILD and a new process/operation id do not prove that a
   pair is fresh for this independent review or rereview. Require parsed trace
   event timestamps to fall within the owning receipt's authenticated
   execution window, add the equivalent window to REVIEW receipts, and reject
   reuse across prior reviewer receipts.

### Third-rereview waivers

1. `NONE`. No residual is waived or deferred.

The success start/return set, changed-set ceiling, absent moved-back backup
handling, failed-root and root-restoration inventory, trace environment
closure, final raw rehash, rollback-pair separation, ordered identical fetch
mapping, extra clone/fetch rejection, reviewer pair/process separation and
completion-artifact REVIEW handling are accepted. The residuals above prevent
authorization because they still permit unproved rollback state, unauthorized
failure-carrier residue, unpreserved replacement Core, incomplete command
lineage, or replayed trace evidence.

This is repair round three and the residuals remain rooted in the same
authorization-oracle and trace-freshness contracts. Per the governance latency
rule, `REVIEW_COST_ESCALATION_REQUIRED` must be recorded before another
same-root repair/rereview cycle.

No network, reconciliation, initializer, provider, installation, deployment,
commit or push action occurred. The operator assessment was not opened,
edited, hashed, staged, inventoried or used. BUILD authority remains
`NOT GRANTED`.

## Final disposition after third bounded rereview

`AUTHORIZATION_REVIEW_CHANGES_REQUIRED`.

Return only `CORE-REFRESH-WO-AUTH-REV-F2-R1-R1-R1`,
`CORE-REFRESH-WO-AUTH-REV-F2-R1-R2-R1` and
`CORE-REFRESH-WO-AUTH-REV-F3-R1-R1-R1` after recording
`REVIEW_COST_ESCALATION_REQUIRED`. Reconciliation and BUILD remain
unauthorized.

## Operator-authorized consolidated escalated rereview

- Role: `INDEPENDENT_AUTHORIZATION_REVIEWER`
- Scope: only F2-R1-R1-R1, F2-R1-R2-R1 and F3-R1-R1-R1
- Work Order raw-byte SHA-256:
  `6ab0929b0d1050c6315fe27d1e18124c7e5b1867106312a7a423e4d8ea906a1a`
- Work Order size: `593` lines, within the authorized 600-line ceiling
- Disposition: `AUTHORIZATION_REVIEW_CHANGES_REQUIRED`

### Accepted closures

1. **F2-R1-R1-R1 — CLOSED.** The exact ten mutable-carrier manifest now
   freezes unique contained preimages for all ten carriers, including the four
   initially Git-clean paths. Dirty carriers bind to BUILD-start inventory;
   clean carriers bind to `HEAD` bytes. Failure requires all ten current bytes
   to match those preimages, restores the six initially dirty entries to their
   exact start hashes, leaves the four initially clean entries absent from
   porcelain, permits no failure-evidence carrier, and constrains actual
   change to exactly the two worker evidence artifacts. Success start/return
   equations correctly add the exact four clean carriers plus those two
   artifacts while retaining the 12-path ceiling and P4-C byte equality.

2. The frozen reconciler source SHA-256
   `96ac0cce3bf9df5733ffe2c6f5a7850db0ccfdc4403daaa70fdb6981dc58196c`
   independently matches both the local pinned and frozen-target blobs. The
   backup timestamp is derived from the actual reconciler backup basename;
   baseline failed-candidate paths must still exist; success rejects a new
   failed candidate; failure binds the one derived candidate and validates a
   complete/partial inventory when that candidate exists.

3. Validator syntax passes. Static branch-equation probes found an honest
   satisfying shape for SUCCESS; zero-prefix, clone, initializer-fetch and
   initializer-doctor FAILURE; first REVIEW; and one appended rereview. Build
   and review UUIDs are disjoint, exact-SID `def_param` binding is present,
   every parsed raw trace2 start/exit is bounded to its declared window, trace
   pairs are distinct, and the path/window-independent span fingerprints are
   rejected across BUILD and the currently declared review chain.

### Residual blockers

1. **CORE-REFRESH-WO-AUTH-REV-F2-R1-R2-R1 — RESIDUAL
   `CORE-REFRESH-WO-AUTH-REV-F2-R1-R2-R1-R1`: the absent-replacement branch is
   not preservation proof.** For a failed clone, validator lines 421-436 accept
   `replacementCorePreservedPath = null` whenever the derived failed path is
   absent at validation time. The frozen reconciler establishes where a
   partial directory is moved when it exists, but the oracle records no
   post-clone/pre-rollback existence snapshot or preimage for that newly
   derived path. A partial candidate can therefore be deleted after the
   reconciler returns and be reported as `NOT_CREATED`; the final scan cannot
   distinguish deletion from honest absence. Likewise, preexisting failed
   candidates are path/existence-bound but not byte/inventory-bound, so their
   contents can change without rejection. This contradicts the mandatory
   preserve-every-candidate/delete-nothing rollback boundary. Bind the
   immediate reconciler-return candidate state and hash inventory before any
   worker rollback, and require final equality/preservation for both prior and
   newly created candidates; `NOT_CREATED` must be derived from that witnessed
   state, not from final absence.

2. **CORE-REFRESH-WO-AUTH-REV-F2-R1-R2-R1 / F3-R1-R1-R1 — RESIDUAL
   `CORE-REFRESH-WO-AUTH-REV-COMMAND-TRACE-R1`: outer-command provenance is
   still not joined to the Git spans.** Command markers and exit JSON bind a
   receipt-declared `processId`, text and time window, while Git operations are
   only checked to fall temporally within that window. No predicate correlates
   the command PID/invocation with a trace SID, process ancestry, or a raw
   transcript child-process record. A different Git clone/fetch executed in
   the same window can therefore satisfy the operation object. More directly,
   `ROLLBACK_VERIFIER` and every `REVIEWER_DOCTOR` have no command object,
   exact PowerShell doctor text, PID transcript or command-exit record at all;
   a direct `git fetch origin main` has the accepted argv and can be presented
   as a doctor fetch. This fails the SPEC's exact doctor-command and
   independently owned doctor proof. Require an independently parsed raw
   parent/child or invocation correlation for every prefix operation, and add
   the same exact-command/transcript/exit binding for rollback and each review
   doctor.

3. **CORE-REFRESH-WO-AUTH-REV-F3-R1-R1-R1 — RESIDUAL
   `CORE-REFRESH-WO-AUTH-REV-F3-R1-R1-R1-R1`: the review chain is internally
   consistent but not append-only against its prior state.** In REVIEW mode,
   `priorReviewRunsSha256` is recomputed from the earlier items in the current
   mutable completion payload, and the validator compares the anchor directory
   only with the anchor paths declared by that same current payload. Before a
   rereview there is no independently frozen previous completion hash,
   previous `reviewRuns` digest, or previous anchor-directory path/content
   manifest. A rereviewer can replace the first run and its anchor, construct a
   new internally valid two-item chain, and pass the exact-set, UUID,
   chronology, pair and fingerprint checks. Thus “preserve existing payload,
   append exactly one” is prose rather than an enforced predicate, and replay
   rejection is limited to the rewritten current chain. Each new review anchor
   must bind an authoritative pre-rereview completion hash plus the exact prior
   anchor-directory inventory/hashes captured before mutation; validation must
   require the old payload and anchors byte-identical and permit exactly one
   appended run/anchor.

### Waivers and final boundary

1. `NONE`. No blocker is waived or deferred.

The consolidated repair closes the ten-carrier rollback residual and makes all
requested outcome equations structurally satisfiable, but the three evidence
gaps above still allow deletion, substitution of a non-owned Git operation, or
rewriting prior independent-review evidence. This single operator-authorized
post-escalation cycle is consumed. Further same-root repair/rereview requires a
new explicit governed move; it is not implicitly authorized here.

Local-only checks used no network, reconciliation, initializer, provider,
installation, deployment, commit or push. The operator assessment was not
opened, read, hashed, inventoried, staged, edited or used. BUILD authority
remains `NOT GRANTED` regardless of this rereview.

## Final disposition after consolidated escalated rereview

`AUTHORIZATION_REVIEW_CHANGES_REQUIRED`.
