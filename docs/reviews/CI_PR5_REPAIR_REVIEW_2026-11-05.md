# Independent PR #5 CI repair review

Status: HOST_COMPATIBILITY_RESULT_TIMEOUT_REVIEW

Independent reviewer: delegated reviewer, separate from implementation worker.
Product Milestone Binding: P5-A2 G04/G05 CI support only; all G01–G14 gaps,
owners and destinations are in
`docs/work_orders/CI_PR5_REPAIR_2026-11-05.md`.

## Pre-material source review

The reviewer accepted the bounded diff with no blocking finding or waiver.
`pyproject.toml` sets an explicit setuptools backend and `packages = []`,
so the root editable distribution carries dependency metadata without
auto-discovering unrelated workspace packages. Both catalog renderer joins
emit LF in accordance with `.gitattributes`. The generated views have LF
working-tree bytes and no semantic tracked diff. Project validation,
detailed catalog check, kit projection, Windows PowerShell catalog check,
session check, Core preflight and `git diff --check` pass locally.

The first dispatch hook attempt failed 9 demo-test setups solely because an
ambient `DASHSCOPE_API_KEY` name existed in the operator process. Its value
was neither read nor used. The unchanged hook reran in a child process with
that environment variable removed and passed 3549 tests, 148 skipped and
4 warnings, creating dispatch commit `8f4ecfb`. This is not provider
governance proof. No provider call or product runtime action was made.

## Pending return gates

Material hook, material commit/range review, hosted PR `validate`,
`catalog-kit` and `web` checks, and final merge verification remain pending.
Until then, no CI-green or merge claim is made. P5-A2 and UI acceptance remain
OPEN/UNMET; AM4 attempt remains SPENT.

## Hosted rerun after material `9f93aa4`

Independent post-material review PASS, no finding/waiver; the exact 12-path
dispatch plus material range is authorized, worktree clean, no added-line
credential pattern, and Core/session checks pass. PR branch push was a
fast-forward. GitHub Actions run `41900249175`: `catalog-kit` PASS, `web`
PASS, `validate` FAIL at kit projection after editable install and detailed
catalog PASS. This exposes a new platform-dependent evidence sort in
`scripts/sync_cvf_catalog_kit.py`; amendment 1 independent authorization
review PASS. The reviewer reproduced four stub-module evidence divergences
between Windows and POSIX sorting, confirmed normalized casefold sorting
matches the committed registry, and found Core/continuity/closeability
checks PASS. Amended dispatch commit and repair BUILD remain. No merge or
closure claim yet.

## Amendment 1 pre-material source review

Independent reviewer PASS, no blocker or waiver. The only added source path
is `scripts/sync_cvf_catalog_kit.py` as amended. It sorts normalized
relative POSIX paths by `(casefold(), original)` before evidence filtering,
so Windows and Linux choose the same files and casefold ties are stable.
All four affected stub modules match the committed registry. Local projection,
detailed catalog, repository validation, session, Core and diff checks PASS.
Material hook, hosted rerun and merge remain pending.

## Hosted full-test result after `a185e04`

Independent post-material review PASS and fast-forward push completed.
GitHub Actions run `41903721108` passed `catalog-kit` and `web`; `validate`
passed install, detailed catalog, kit projection and repository validation,
then full pytest reported 20 failures and 8 setup errors. Failure families
are missing pinned public Core/workspace rules, Windows PowerShell and exact
local demo environment, public skill validator, and four CRLF-derived
knowledge source hashes. Operator authorized a reviewed clean-runner CI
repair; amendment 2 admission and source review independently PASS. No merge claim.

## Amendment 2 admission and source review

Independent reviewer PASS, findings/waivers NONE/NONE. The operator expressly
authorized clean-runner public dependency installation and merge when green.
Existing dispatch anchors remain; amended admission and aligned continuity
were acknowledged before BUILD and land with the material commit. The exact
native dispatch-continuity row is preserved. Dedicated actual-SHA continuity
and independent clean-range closure remain after terminal material review.

Source diff is the CI workflow plus exactly four knowledge source hashes.
The reviewer independently recomputed the four pins from tracked LF blobs
and verified the official fixed OpenAI validator download SHA-256. The full
unfiltered `python -m pytest -q` gate remains. Windows, exact Python/Node,
local venv, frozen pnpm install, pinned public Core initializer/workspace rules
and validator are prepared before tests. Core/session/diff checks PASS.
Knowledge pack and repository/catalog checks PASS on LF source bytes.
Knowledge review dates retain 2026-11-04 UTC, the validator's clock basis
(the operator's local date is 2026-11-05).

The reviewer also explicitly applied pinned `check_recheck` to the applicable
historical AM4 completion review and AM3 return in `docs/decisions/`, with
zero violations; no automatic legacy-path CLI coverage is asserted. This
does not change those historical product dispositions. Normal material hook,
hosted CI and merge verification remain pending.

## Actual material terminal review

Independent terminal review PASS at
`9e8b766e4438af7d715682f0a713db167d8303ce`, exact10paths from `a185e04`.
No blocker or waiver. Normal hook passed3549/148skip/4warnings in183.06s
using the same pinned public validator. Worktree was clean; Core/session and
diff checks PASS, `.githooks` intact. Authorized fast-forward push completed.
Dedicated actual-SHA continuity follows this review, then independent clean
split-range closure review and latest hosted checks gate PR #5 merge.

## Hosted result and dependent test repair

Clean split-range review PASS exact10 material +6 continuity at58948cc,
no blockers/waivers. Hosted41907009464 subsequently passed full environment,
catalog/repository setup and narrowed to3fail/8errors from two fixtures:
Core helper raw CRLF hash and hosted admin ownership for ACL fixture baseline.
Independent repair admission PASS for exact2test paths added to the Work
Order; no further operator approval required. Normalize only helper hash
input to LF and set fixture owner explicitly, keeping expected SHA, runtime
ACL code and all tamper/refusal assertions. Latest continuity run41907853162
cancelled because same known source causes remain. Repair source review,
normal hook and hosted green gate remain pending.

Dependent source review PASS exact2test changes plus7 authorized records,
no blockers/waivers. Expected helper hash, all tamper cases, runtime ACL code
and private/OWNER RIGHTS/Everyone assertions remain intact. Focused two-file
pytest24PASS in15.65s; Core/session/diff checks PASS. Normal hook and latest
hosted green gates remain.

Portability terminal material review PASS `58948cc..bebe4a1`, exact9paths,
findings/waivers NONE/NONE. Material actual SHA
`bebe4a1ba15cfb60b099da84b7e362c4ab376f56`; focused24PASS and unchanged
normal hook3549PASS148skip4warnings178.92s. Core/session/diff checks PASS,
clean worktree, authorized fast-forward push. Dedicated actual-SHA continuity
follows terminal review; independent clean-range review and all latest-head
hosted checks still gate merge. No current CI-green/merge claim.

Hosted41909216440:3549PASS147skip1failure at the ACL test's initial private
fixture assertion. The owner-only setup was insufficient on the hosted
environment; exact remaining host ACL difference is not asserted. The
same admitted test path now constructs the entire intended protected DACL
with current-user owner and one FullControl Allow rule, using the same
sanitized PowerShell environment as the runtime verifier. Runtime guard and
all three original ACL assertions remain. Focused file8PASS9.42s.

The attempted dedicated continuity hook did not commit:3548PASS148skip,
one report-export child startup deadline failure. Isolated export suite
reran25PASS8.86s without source changes. Current records are included with
the corrective material; dedicated latest-SHA continuity follows its review.

Independent same-path refinement/source review PASS, findings/waivers
NONE/NONE. The complete private fixture DACL is deterministic; runtime
verifier and assertions unchanged. The authorized CI workflow additionally
runs the exact ACL test before the unchanged full pytest gate, failing early
without exclusions or continue-on-error. Core/session/diff checks PASS.

Second full-hook attempt retained:3548PASS148skip4warnings, same export
worker test-only3s partial-write marker failure. Independent distinct-cause
admission PASS for exact export test path: product `DEADLINE_SECONDS` is10;
test now uses that constant and bound deadline+3 for cleanup, preserving
partial write/child termination/ExportFailure assertions. Runtime unchanged.
Combined export+ACL focused33PASS14.76s; Core/session PASS. This correction
addresses the timing mismatch rather than dropping/retrying the assertion.

Combined source review PASS exact10paths versusbebe4a1: three admitted source
paths and seven governance records; findings/waivers NONE/NONE. No runtime
source change, skip or guard weakening. Focused33PASS; normal hook and latest
hosted green remain gates.

Latest terminal material review PASS `bebe4a1..a37b815`, exact10paths, no
blocker/waiver; actual material
`a37b81566e97110d5431551f5feae09c94c7d2a1`. Focused33PASS, unchanged
normal hook3549PASS148skip4warnings197.16s. Clean worktree, Core/session/range
diff checks PASS; authorized fast-forward push. Dedicated actual-SHA
continuity follows terminal review, then clean split-range review and all
latest-head hosted checks before merge. Previous failures are retained.

Hosted41911989403 early fixture step failed with actual PowerShell
TimeoutExpired10s during DACL setup before verifier; precise underlying
dependency remains UNKNOWN. Independently admitted bounded setup repair:
CI sanitized-child identity/Security/Get-Acl preparation90s, hard-fail on
timeout/nonzero/unexpected sentinel; fixture-only setup60s. Actual runtime
verifier10s and original assertions/full gate unchanged.

Independent startup source review PASS, no blocker/waiver. Exact YAML run
executed locally PASS; focused8PASS2.70s; Core/session/YAML/diff PASS.
Prior actual-SHA continuity4829c9c passed normal3549/148/4 in196.86s.
This same-scope material still requires normal hook, terminal review,
dedicated latest-SHA continuity and latest hosted green checks before merge.

Bounded startup terminal material review PASS `4829c9c..800d875`, exact9
paths, findings/waivers NONE/NONE. Actual material
`800d8759a001de72adc3da0d94a9f046a7a7649e`; normal3549PASS148skip4warnings
179.26s plus focused8/exact YAML command PASS. Worktree clean, Core/session/
range diff PASS; authorized push. Dedicated actualSHA continuity follows
terminal acceptance; independent clean-range review and all latest-head
hosted green checks still gate merge. No current CI-green/merge claim.

REVIEW_COST_ESCALATION_REQUIRED recorded after repeated hosted ACL baseline
refusals. Hosted41913581429 warmupPASS, fixture setup completed, actual guard
returnedFalse; exact refusal category UNKNOWN. Independent consolidated
review admitted exactly one bounded diagnostic on the same runner. Observe
the real encoded-command child with unchanged args/env/timeout10/flags,
return its actual result and rethrow actual exceptions; log only elapsed,
TIMEOUT/OSERROR, returncode, exactPASS/exactFAIL/OTHER and stderr-presence.
No raw output/ACL/SID/rights/secrets. Original assertions and full gate remain.
Early workflow uses pytest `-s` only to expose sanitized observations.

Local diagnostic testPASS2.53s, three real child results PASS/PASS/FAIL,
each about0.5s, with stderr-presence true (no raw stderr captured in record).
Core/session/diff PASS. Normal hook, one hosted attempt, then independent
result review; no automatic additional diagnostic or speculative repair.

Independent bounded diagnostic source review PASS, no blocker/waiver:
wrapper forwards the real child behavior and sanitized schema exactly as
admitted; pytest teardown restores it, assertions/full gate unchanged.

One hosted diagnostic41915399636 result: actual ACL child elapsed10.015s,
outcomeTIMEOUT; fixtureREADY assertion passed, total42.30s. No raw output or
ACL recorded. This identifies timeout, not ACL-content rejection; underlying
host cause UNKNOWN. Execution stopped for independent result review.
Diagnostic material13b100e normal3549PASS148skip4warnings185.19s and terminal
reviewPASS; no extra hosted attempt or source repair has been made yet.

Independent diagnostic result review accepted exactTIMEOUT10.015s and
admitted ONE supported fixedWindows2022 compatibility candidate. Only
validate runner label changes; runtime10s, warmup/fixture setup, sanitized
diagnostics, assertions and full tests remain. Underlying delay/Windows2025
causation UNKNOWN; no Defender/security-policy change. Admission and current
BUILD acknowledgment recorded before source; source/terminal review, one
hosted attempt then independent result review. No automatic retry/fix.

Independent host-baseline source review PASS exact8paths, no blocker/waiver.
Only one validate runner-label line plus7 governance records; Core/session/
diff PASS. Normal hook and terminal review precede the one hosted candidate.

Host candidate1c41ff2 normal3549PASS148skip4warnings251.43s and independent
terminal reviewPASS. One run41917032275: actual ACL childTIMEOUT10.022s,
fixtureREADY passed, total40.55s. Windows2022 did not resolve the observed
timeout; no2025 causation claim. Stopped for independent result review
before further source or hosted attempt. No merge/current CI-green claim.

Independent staged probe/helper admission PASS before source: exact
`tests/unit/acl_child_diagnostic.py` test-only split under300line cap; first
actual timeout only triggers one90s read-only copied-script stage probe,
filtered tokens/timings only, original exception rethrown. Real10s/assertions
remain. Current IMPLEMENTATION_WORKER/BUILD acknowledgment; source review,
normal hook, ONE hosted run then stop for independent result review.
CoreCOMPLIANT; activation core-only stale/supplemental finding retained,
project prohibits routine supplemental dependency. G01–G14/AM4 unchanged.

Independent STAGED_DIAGNOSTIC_SOURCE_REVIEW_PASS exact9paths; no blocker
or waiver. Actual10s/args/env/flags/assertions retained; strict allowlisted
markers/partial-output filter, first timeout only, original rethrown.
Focused8PASS3.06s/direct readonly probePASS; Core/session/file-size/catalog/
projection/manager/diffPASS. Next normal hook, terminal review, ONE hosted
probe then stop for independent result review. No retry/repair inferred.

ONE staged41919132332 result: actualTIMEOUT10.014s. Readonly probe
EXIT_ZERO19.287s/stdoutPASS: ENTRY108ms, IDENTITY/READ_1=117ms,
OWNER_1=19233ms; subsequent rules/read2/checksEXIT_PASS by19264ms.
First Get-Acl spans19.116s, not process startup/ACL rejection. Automatic
module discovery latency remains hypothesis, not cause proof. Stop
REVIEW/ORCHESTRATOR for independent result/causal repair admission.
Materialf492038 normal3549PASS148skip4warnings186.67s/terminalPASS.
No further source/hosted attempt or merge inferred; escalation retained.

Independent result review PASS. ONE CI-only causal candidate admitted:
existing bounded90s sanitized dependency preparation resolves unqualified
`Get-Command Get-Acl -ErrorAction Stop` BEFORE explicit module import and
Get-Acl. This tests discovery/cache preparation, not proven causation.
Runtime10s/script/all assertions/full tests unchanged. Source/terminal
review and normal hook precede ONE hosted run then independent result
review; no automatic successor. Current IMPLEMENTATION_WORKER/BUILD
acknowledgment precedes source. Existing G01–G14 binding/stop apply.

Independent DISCOVERY_PREPARATION_SOURCE_REVIEW_PASS exact8paths, no
blocker/waiver. Sole source GetCommand before import; sanitized90s/hardfail/
sentinel retained, actual runtime/test10s unchanged. Exact YAML preparation
localPASS, Core/session/diffPASS. Normal hook/terminal then ONE hosted
candidate, stop for independent result review.

ONE CI discovery41920745392 failed: actualTIMEOUT10.021s; staged
probeEXIT_ZERO25.182s/stdoutPASS, ENTRY147ms READ_1=163ms,
OWNER_1=25108ms, remaining checksEXIT_PASS25139ms. PreparationPASSED
but subsequent child firstGetAcl24.945s; cache preparation insufficient.
Candidatec8c7b36 normal3549PASS148skip4warnings188.81s/terminalPASS.
STOP REVIEW/ORCHESTRATOR; no extra hosted attempt. Prospective exact
scope expansion PENDING_OPERATOR: scripts/p5a2_source_demo_recovery_custody.py,
add one `Import-Module Microsoft.PowerShell.Security -ErrorAction Stop`
inside existing try before identity, preserving real10s/ACL predicates/failure
handling. This explicit dependency initialization is outside current CI/test
scope; no source edit or authority inferred. Independent result/proposal
review requested, operator approval pending. Existing G01–G14 binding and
escalation remain. No product acceptance/merge/AI-governance proof claim.

Independent result review PASS; prospective one-line technical review PASS,
NOT BUILD admission. Import in existing try is failclosed, timeout10s/ACL
predicates unchanged. Operator exact runtime path approval pending; no
fixture change or AM4 budget. Future accepted scope must reconcile live
contract/invariant references without rewriting historical frozen evidence.

Operator exact scope approval received: "Cho phép sửa guard và merge khi xanh".
Independent GUARD_SCOPE_AMENDMENT_ADMISSION_PASS, no blocker/waiver.
IMPLEMENTATION_WORKER/BUILD acknowledgment BEFORE source: add only explicit
Security module import in the existing guard try. Actual10s/predicates/
failure behavior unchanged; no AM4 execution/pin rewrite. G01–G14 unchanged.
CoreCOMPLIANT/sessionPASS, invariant guardPASS; activation core-only retained
stale/supplemental finding at documented project-policy boundary.

Independent GUARD_INITIALIZATION_SOURCE_REVIEW_PASS exact8paths, no
blocker/waiver. One import inside existing try preserves failclosed10s/env/
flags/predicates; no historicalpins/fixture changes. Focused18PASS3.17s,
realPASS/PASS/FAIL0.408/0.329/0.355s, Core/session/invariant/diffPASS.
Next normal fullhook, terminal review, ONE hosted verification/result review.
