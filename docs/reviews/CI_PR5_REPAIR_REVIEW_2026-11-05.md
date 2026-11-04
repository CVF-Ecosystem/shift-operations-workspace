# Independent PR #5 CI repair review

Status: SOURCE_REVIEW_PASS_AMENDMENT_1_PENDING

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
