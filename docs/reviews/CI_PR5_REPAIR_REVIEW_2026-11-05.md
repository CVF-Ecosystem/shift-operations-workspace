# Independent PR #5 CI repair review

Status: AMENDMENT_2_SOURCE_REVIEW_PASS_HOSTED_PENDING

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
