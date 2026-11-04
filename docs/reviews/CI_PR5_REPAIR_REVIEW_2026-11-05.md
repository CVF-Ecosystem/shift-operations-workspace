# Independent PR #5 CI repair review

Status: ACL_FIXTURE_REFINEMENT_SOURCE_REVIEW

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
