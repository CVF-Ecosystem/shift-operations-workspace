# PR #5 CI repair — active handoff

<!-- CVF-GC020-MATERIAL-SHA:START -->
Material commit recorded for this handoff: `9e8b766e4438af7d715682f0a713db167d8303ce`.
<!-- CVF-GC020-MATERIAL-SHA:END -->

Date: 2026-11-05. Tranche: CI-PR5-REPAIR. Status: MATERIAL_ACCEPTED_MERGE_GATED; phase REVIEW.
Risk R2. ORCHESTRATOR → SPEC_AUTHOR → WORK_ORDER_AUTHOR → independent
authorization REVIEWER → IMPLEMENTATION_WORKER. The operator explicitly
authorized fixing both failing PR checks and merging PR #5 when gates pass.

## CVF Agent Declaration

Project: shift-operations-workspace. Installed read-only public Core:
`../.Controlled-Vibe-Framework-CVF@c4c8767ac8861854f40d466ba338ffd11eb9558e`.
Live provider evidence required YES for any AI-governance behavior claim;
this repair makes none. Active handoff: this file. Next allowed move:
Verify latest hosted PR #5 checks and independent clean-range review, merge
only when all pass; after merge return to separately admitted G04/G05
readiness planning. Parked checkpoint: AM4 attempt SPENT, UI acceptance
UNMET, P5-A2 OPEN; no UI/runtime/SQL/provider attempt is authorized.

## Dispatch acknowledgment

The successor handoff, canonical state, bootstrap projection and compatibility
mirror advance together before BUILD. The catalog initial-handoff pointer
follows this active handoff. This work closes only CI infrastructure defects;
all G01–G14 product gaps remain at their recorded destinations. Do not infer
application readiness or AI-governance behavior from green checks. Return to
separately admitted G04/G05 UI readiness diagnosis/planning after CI closure.

## Evidence and open decisions

At dispatch, `validate` fails during `pip install -e ".[dev]"` because
setuptools discovers multiple top-level monorepo directories; `catalog-kit`
fails because generated CRLF text is compared with an LF checkout. `web`
passes. No source repair or merge has occurred at this checkpoint. Independent
authorization review must clear continuity before BUILD. No other open CI
root cause is accepted yet; hosted rerun can reveal one. Independent
authorization review PASS after aligned continuity and G01–G14 binding;
BUILD began after dispatch commit `8f4ecfb` passed its normal hook
(3549 passed, 148 skipped, 4 warnings). Current role IMPLEMENTATION_WORKER;
initial source scope was `pyproject.toml` and catalog renderer only. Generated views
have LF working-tree bytes; their tracked normalized content is unchanged.

## Hosted result and amendment 1

Material commit `9f93aa4` passed its normal hook (3549/148/4), independent
post-material review PASS and was pushed to the PR branch. Hosted `catalog-kit`
and `web` PASS. `validate` passed editable install and detailed catalog but
failed kit projection on Ubuntu. Investigation isolated `Path` sorting's
platform-dependent casing in `scripts/sync_cvf_catalog_kit.py`: four stub
evidence paths select root README on Linux but nested README on Windows.
Amendment 1 in the work order adds only deterministic projection sorting.
Authorization re-review PASS with no blocking finding. Dispatch commit
`07b4011` passed its normal hook
(3549/148/4). Current role IMPLEMENTATION_WORKER; deterministic projection
sort is implemented and local projection/catalog/repository validation PASS.
Independent source review, material hook and hosted CI remain. No product
acceptance or AI governance claim.

## Hosted full-test result and amendment 2

Material `a185e04` passed normal hook 3549/148/4, independent post-material
review and fast-forward push. GitHub run `41903721108`: catalog-kit/web PASS;
validate passed install, detailed catalog, projection and repository checks,
then full pytest failed (20 failures, 8 setup errors). Consolidated causes:
clean Ubuntu runner lacks installed public pinned Core/workspace rules,
Windows PowerShell and `.venv/Scripts/python.exe` demo environment, exact
Node modules and public skill validator; four knowledge source pins encode
local CRLF instead of tracked LF bytes. Operator explicitly authorized
expanded public CI setup and merge when all checks pass. Current role
IMPLEMENTATION_WORKER; phase BUILD. Amendment 2 independent authorization
PASS: existing dispatch anchors remain, admission and continuity are recorded
before BUILD and included in the material commit through the normal hook.
Post-material independent review, dedicated actual-SHA continuity and clean
range review remain mandatory. This acknowledgment precedes source changes.

Amendment 2 source review PASS, findings/waivers NONE/NONE. Exact CI workflow
and four knowledge LF pins independently verified, including public validator
commit/SHA. Local knowledge/repository/catalog/Core/session checks PASS.
Normal material hook, hosted CI and merge are next. No test exclusion added.

## Accepted material and actual-SHA continuity

Independent terminal material review PASS for exact10paths
`a185e04..9e8b766e4438af7d715682f0a713db167d8303ce`, findings/waivers
NONE/NONE. Normal unchanged hook3549PASS/148skip/4warnings in183.06s with
the pinned public validator. The material is pushed. This dedicated
continuity records its actual SHA after independent terminal review; role
SESSION_SYNC_STEWARD, phase REVIEW. Clean split-range review follows this
commit. Hosted run `41907009464` and latest-head checks gate merge; no
CI-green or merge claim is made here. Operator merge authority remains.
