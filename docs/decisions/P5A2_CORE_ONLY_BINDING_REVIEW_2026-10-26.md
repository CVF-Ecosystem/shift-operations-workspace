# P5-A2 Core-only binding — independent authorization review

docType: completion_review
Status: REVIEW_PASS_BOUNDED
Date: 2026-10-26
Reviewer: independent SPEC / WORK_ORDER authorization reviewer; no implementation ownership

## Decision

`SPEC_AUTHORIZATION_PASS_BOUNDED`; findings `NONE`, waivers `NONE`.
The operator's current Core-only direction authorizes correction of the project's
legacy direct private-provenance and latest-remote binding. The SPEC states a
testable pinned public-Core contract and preserves the phase gates, normal hook,
independent implementation review, risk ceiling R2, workspace isolation, and
real-provider rule for any AI-governance claim. This is static authorization,
not live AI-governance evidence.

The Work Order bounds worker script/test paths separately from Root-owned
authority, documentation, and continuity paths. Both CVF repositories remain
read-only. The accepted Docker SQL receipt is carried; all physical effects
are spent. No provider, credential, network, package, image, container, public
release, push, or hook alteration is authorized. BUILD requires Root activation
and a fresh acknowledgment after this review; `DISPATCH_READY` alone grants no
BUILD authority.

## Independent checks

- Project Core pin and clean installed Core HEAD: `aa672d11910ae1982557e4810a2a8002a611e9e6`; public origin matches the manifest. The checker and standard are tracked there. Their working SHA-256 values match the SPEC: `8f00c6421eebe3c1b237e5307ac6e2b0b0343c9a35cf635bbab17aa886e00e8e` and `b3af2fcbd09160d9f2ae88c861bd67d45ba1425bd21e577bf880cb0f1f29ea3c`.
- Unmodified pinned-Core `python -I .../check_gate_to_role_closeability.py --repo-root . --enforce`: `COMPLIANT`, zero violations with this Work Order at active `DISPATCH_READY`. The blocked historical Docker Work Order is correctly reported not applicable. The initial `DRAFT` projection was also checked in memory with zero graph violations; that projection was not mistaken for an active-file gate.
- Project session checker: PASS; Git diff whitespace check: no errors. Legacy `check_cvf_core_machine_inheritance.py --enforce` fails only on moved private HEAD, the explicitly authorized repair target. The native latest-main doctor failure is an upgrade diagnostic, not acceptance of a Core update.
- Active project bootstrap, memory, state, and successor handoff agree on current mode, Core pin, next move, and parked effects. The GC020 handoff marker identifies material parent `a2d189e774ca90b923de2df60bdb313e2e7990b1`, while `7fd67f5e9365c21e7c8a367f6e799ba8e224c5ca` is the dedicated continuity/current HEAD; no new historical dispatch or material commit is claimed.

## Product Milestone Binding / review boundary

The current SPEC reconciles all G01–G14 against source `7fd67f5` and the
carried SQL receipt. This support work only unblocks material closure of the
accepted G04/G05/G13 SQL substrate. G01/A7 and G02 remain blocked; G06 query,
authorization, caps, cohort, and retention remain unknown/open; operational
G03/G08–G10/G13, G07/G11/G12 remain open; G14 remains held. Root is accountable
and owns commits, Sol owns backend/control work, Luna owns UI/independent
implementation review, and the operator owns business acceptance. Remainders
retain the SPEC's P5-A2 and P5-B/C/D roadmap destinations. P5-A/P5-A2 remain
open and Phase 5 remains 0/5. The finite return is the carried SQL result
closure, then G04–G06 source-query/cohort/coverage SPEC; this review grants no
dependent product BUILD or milestone closure.

Implementation acceptance still requires focused negative proofs, the corrected
ordinary adapter and unmodified normal material hook, independent review of the
entire Root/worker changed set, terminal actual-material review, and dedicated
actual-SHA continuity plus clean committed-range closure. These are future
gates, not evidence already passed.

## Authorization-time closeability record

closeabilityDisposition: CLOSEABLE
outsideAuthorityBlockers: NONE
nextRepairRoute: SAME_BOUNDED_WORK_ORDER_AFTER_ROOT_ACTIVATION
workerRedispatchAllowed: YES

## Interim settled config and instruction review (BUILD)

Role: independent REVIEWER; this section is not the final implementation
verdict. I reviewed Root-owned `.cvf/manifest.json`, `.cvf/policy.json`,
`AGENTS.md`, `knowledge/GOVERNANCE_BOUNDARIES.md`,
`knowledge/PROJECT_CONTEXT.md`, and `knowledge/manifest.json` after the BUILD
acknowledgment. Config findings: `NONE`.

The manifest names only the installed public Core and project continuity,
keeps the exact Core pin and seven-phase model, and binds two tracked native
artifacts by the verified hashes. Policy retains live-evidence, UI-only mock,
workspace isolation, phase, role and R2 controls; it adds explicit reviewed
Core updates and read-only reference repositories. AGENTS makes the local
pinned-Core adapter the routine preflight and bounds direct Core CLI use to
this correction before the normal adapter and hook resume. Knowledge guidance
matches that authority and does not elevate the carried SQL substrate to
milestone acceptance. Project knowledge and session checkers PASS; the current
local adapter now returns `COMPLIANT` with zero closeability violations, and
the reviewed config diff has no whitespace errors. Source/tests and the full
changed set still require review after worker return.

## Independent BUILD completion review — consolidated return

`CHANGES_REQUIRED_BOUNDED`; two findings, no waiver. Authorization PASS above
remains historical; this is the current implementation disposition. I consumed
the worker's 15 focused passes and the settled Root config review, inspected
all five worker files plus the source tests and current continuity/SQL metadata,
and verified the five worker SHA-256 values against the return. The installed
Core remains clean at the declared SHA; selected native file hashes, SQL runner
SHA `43e7cfde`, frozen oracle SHA `12ad36cb`, and carried SQL receipt SHA
`1c2eefad` match their accepted pins. The corrected ordinary adapter and
unmodified direct pinned-Core CLI both return `COMPLIANT`, zero violations;
session and knowledge checks PASS. These static passes do not establish AI
governance behavior or close the product milestone.

| Finding | Evidence and effect | Bounded repair / proof |
|---|---|---|
| CORE-BUILD-F1 | `scripts/initialize_cvf_clone.ps1` writes `core.longpaths` and runs `git checkout --detach $pin` for any clean **preexisting** shared Core whose HEAD differs from the project pin. That changes another installed Core user before the final project adapter can validate it. R3 authorizes pin checkout for a newly cloned Core only; a preexisting mismatch needs a stop and separately reviewed adoption/update. | Branch on newly cloned versus preexisting Core. For preexisting Core, verify origin and exact HEAD without repository mutation; stop on mismatch before config write/checkout. Fresh clone may install the declared pin. Add a local disposable PowerShell/Git fixture showing a clean existing Core at a newer commit remains unchanged on mismatch, with no network. Do not run the real initializer. |
| CORE-BUILD-F2 | The new worker return places `Self-declared worker-return artifact: yes` at the end of a prose line. The Work Order requires an exact standalone marker, and native `check_recheck` does not classify that text as a worker return. Focused tests prove malformed active Work Order rejection, but R4 also requires a malformed return probe. The native CLI scans `docs/reviews/` returns, while this project's `docs/decisions/` return is outside that automatic path scan. | Put the marker on its own line in the admitted worker return; verify its four recheck scalars directly with the pinned native checker. Add a temporary-repository malformed self-declared return under the native scanned path and prove the actual Core CLI returns nonzero. Disclose that the current `docs/decisions/` path is reviewed explicitly rather than claiming native automatic return enforcement there. Preserve the existing native checker and hook. |

The same R4 focused-proof family also lacks distinct missing-Core,
malformed-pin, and valid-format wrong-digest cases. Existing tests exercise a
valid-format unavailable pin, missing selected files, and dirty working bytes;
those do not establish the three separate failure branches. Add those local
negative fixtures to the admitted binding test file as part of CORE-BUILD-F2.

The remaining implementation meets the bounded design on current evidence:
the adapter verifies the exact local public origin/HEAD, tracked selected
working bytes against pinned Git blobs and LF hashes before isolated native
execution, forwards CLI arguments and exit code, rejects weakened live flags,
and does not read private pack/session or remote-main freshness. Root's active
manifest/policy/instructions and carried SQL metadata retain the G01–G14
owners and destinations, G06 unknown/open, provider hold, and Phase 5 0/5.
Existing historical Docker drift remains recorded as the reason its result is
still uncommitted; the corrected Core-only route is not a SQL rerun grant.

Both findings fit the current worker script/test/return families, risk R2,
effect ceiling NONE, and Root commit ownership. Consolidate this one repair
round under the current Work Order; preserve the failed/current evidence and
the normal hook. Material commit, terminal review, dedicated actual-SHA
continuity and clean committed-range closure remain blocked until independent
rereview passes.

## Return-Time Closeability Recheck

closeabilityDisposition: CLOSEABLE
outsideAuthorityBlockers: NONE
nextRepairRoute: NONE
workerRedispatchAllowed: YES

## Independent repair rereview and completion disposition

`REVIEW_PASS_BOUNDED`; CORE-BUILD-F1 and CORE-BUILD-F2 `RESOLVED`, open
findings `NONE`, waivers `NONE`. This supersedes the earlier changes-required
disposition while retaining its evidence. The exact worker return SHA-256 is
`2feecf066cd4e622b4a636ed079e9c50f2a0dc809c9ae99270fe4a88e5c6266d`;
all five returned source/test hashes match current bytes. Root-owned config,
instructions, knowledge and continuity remain inside the admitted families;
neither CVF repository changed.

- F1: the initializer now verifies the origin and clean state, and stops on a
  preexisting Core HEAD mismatch before config, checkout or project binding
  writes. Config and pin checkout occur only for a Core cloned by that
  initializer invocation. I inspected the disposable two-commit PowerShell/Git
  regression and consumed its PASS: mismatched existing Core HEAD, `.git/config`
  bytes and status were unchanged; no network was used. The real initializer
  was not run.
- F2: the worker return has the exact standalone self-declared marker. I
  applied pinned native `check_recheck` directly to this `docs/decisions/`
  return and this completion review: each returned zero issues; removing each
  recheck heading in memory produces `return_recheck_missing`, confirming
  applicability. The native CLI malformed `docs/reviews/` return fixture exits
  2, as does malformed active Work Order. Distinct missing-Core,
  malformed-pin and valid-format wrong-digest negatives are present in the
  focused suite. Current `docs/decisions/` returns/reviews remain outside
  native CLI automatic path selection and require this explicit independent
  check; no broader automatic coverage is claimed.
- Focused repair proof: 21 passed, consumed without a duplicate full suite.
  The corrected normal adapter and direct pinned-Core CLI return `COMPLIANT`
  with zero violations. Session and project knowledge checks PASS; worker
  reports size, invariant and catalog gates PASS; diff whitespace check has
  no errors. Installed Core HEAD `aa672d11910ae1982557e4810a2a8002a611e9e6`
  is clean and its two selected hashes match the manifest. SQL source/oracle
  and carried receipt remain at `43e7cfde`/`12ad36cb`/`1c2eefad`; no SQL or
  provider effect was repeated.

This completion pass permits Root to run the unmodified normal material hook
and commit the bounded correction with the carried SQL result. It does not
assert a passed full hook or commit yet. Terminal actual-material review,
dedicated actual-SHA continuity and clean committed-range closure are still
required. The support repair unblocks accepted synthetic G04/G05/G13 SQL
evidence only; G01/A7/G02 remain blocked, G06 and operational coverage remain
open/unknown, G07/G11/G12 and operational G03/G08–G10/G13 remain open, G14
held. P5-A/P5-A2 and Phase 5 remain open at 0/5. Root owns the next commit
and G04–G06 product SPEC return; this review grants no dependent BUILD.

## Independent AM1 authorization after retained full-hook failure

`AM1_AUTHORIZATION_PASS_BOUNDED`; blocking authorization findings `NONE`,
waivers `NONE`. The previous completion pass remains source/config acceptance,
but the unmodified normal material hook stopped before commit with 1 failed,
3,244 passed, 147 skipped, 4 warnings and 8 errors in 206.99 seconds. The
retained log is `.venv/p5a2-core-only-material-20261026.log`. Its eight setup
errors and one cleanup-test failure share `_pinned_helper()` in
`tests/integration/test_project_knowledge_ingest_rehearsal.py`: it asserts
installed HEAD equals `origin/main` equals the project pin. The cleanup case
gets `KeyError: 'path'` only because that helper fails before its callback
records the temporary path. This is the remaining test-level latest-remote
coupling, contrary to accepted R1. No commit was created.

The candidate Work Order adds exactly that integration test path to the
worker's test family and active closeability graph. The repair replaces the
remote-main equality with the corrected local installed-pin binding while
retaining exact helper SHA-256
`856b99d9273b0384c40c05bc2132eae66e9dce20b9a9c8b75c3d91ae7016d2c6`,
helper working/Git integrity, network-token guard, actual native PowerShell
ingestion, index assertions, all negative cases and cleanup. I verified the
installed helper hash and Core pin; the active pinned-Core graph CLI returns
zero violations, and session/knowledge checks PASS. The source fix, focused
results and full-hook retry have not happened yet.

This is one finite same-objective test repair with the same R2 ceiling, test
artifact class, no new external effect and Root commit owner. Root may release
the worker for this path and own return after this review. No skip, deselection,
xfail, helper/Core rewrite, provider or SQL rerun is authorized. Run the nine
implicated integration cases plus 21 Core focused cases once, independently
review the changed test and preserved negative evidence, then retry the
unmodified normal hook. On another independent cause, stop for review before
expanding paths. Material, terminal, actual-SHA continuity and clean-range
gates remain open.

The complete P5-A2 G01–G14 reconciliation and owners in the accepted SPEC
remain current. This correction only unblocks accepted G04/G05/G13 synthetic
SQL result closure. G01/A7/G02 stay blocked; G06 query/auth/caps/cohort/
retention unknown/open; operational G03/G08–G10/G13 and G07/G11/G12 open;
G14 held. Root is accountable and owns config/commit; the backend worker,
independent reviewer/UI owner and operator retain the P5-A2/P5-B/C/D
destinations and business acceptance. Phase 5 remains 0/5. Return to
G04–G06 product SPEC after the finite material closure.

## Independent AM1 repair rereview

`REVIEW_PASS_BOUNDED`; AM1 repair findings `NONE`, waivers `NONE`. This follows
the retained failed full hook and independently authorized single test-path
repair above. I verified the settled integration file SHA-256
`904d149bda37717f30c332c3f06095180132d0bf6c4302d2de4ea31ab9bd0176`
and worker return SHA-256
`f1a713720755c12f041ceca23549caba5737d9d2bc91b47748a691ffa2f0b695`;
the five earlier worker source/test hashes are unchanged. The current project
HEAD is still `7fd67f5e9365c21e7c8a367f6e799ba8e224c5ca`; no material
commit followed the failed hook.

The changed helper calls the corrected local installed-Core binding, compares
HEAD to the project pin and origin URL to the approved public repository, and
requires its unchanged PowerShell helper working bytes to match the pinned Git
blob after LF normalization. Raw helper SHA-256 still matches `856b99d9`.
It no longer reads or compares `origin/main`. The network-token scan, actual
PowerShell ingestion, index contract, negative source/secret cases, and both
normal and induced-failure cleanup remain in the test unchanged. I consumed
the authorized focused run of all nine implicated integration cases and 21
Core cases: `30 passed` in 19.74 seconds. I did not duplicate that run or the
full suite.

The ordinary adapter and pinned native CLI return zero violations; session
and project knowledge checks PASS. The worker reports size, invariant-family
and catalog checks PASS; changed test/return whitespace check is clean. The
worker return's exact standalone marker is applicable to pinned native
`check_recheck`: current bytes return zero issues, and removing its recheck
heading in memory yields `return_recheck_missing`. The retained original full
hook remains `1 failed, 3244 passed, 147 skipped, 4 warnings, 8 errors` in
206.99 seconds, with no commit, skip, xfail or waiver. The Core and physical
SQL source/oracle/receipt remain unchanged; no provider or SQL effect occurred.

Root may retry the unmodified normal material hook once with the reviewed
29-path material set. This rereview does not claim that retry passed. Terminal
actual-material review, dedicated actual-SHA continuity and clean committed
range remain gates. G01–G14 ownership and open/unknown states, P5-A/P5-A2
OPEN and Phase 5 0/5 are unchanged; after bounded SQL result closure, return
to G04–G06 product SPEC.
