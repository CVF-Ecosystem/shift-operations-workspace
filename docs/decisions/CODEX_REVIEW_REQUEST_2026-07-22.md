# Independent Review Request — shift-operations-workspace

Repo: this repository (`shift-operations-workspace`)
GitHub: `https://github.com/CVF-Ecosystem/shift-operations-workspace`
Current HEAD at time of request: `7a3bb29` ("P2-A (Task): replicate CVF chain to Task domain")

## Who you are for this task

You are an **independent reviewer**, not a continuation agent. Do not pick up
the roadmap and keep building. Your job is to verify claims against the actual
repository state — the same role a previous independent review already played
once at `docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-21.md`. Read that file
first: it is the baseline this repo was measured against, and several
buildout sessions since then claim to have closed its findings. Your job is to
check whether those claims hold up, not to accept them.

## Ground rules

- **Evidence over narrative.** Run the tests yourself (`python -m pytest -q`
  from repo root). Read the actual code at the paths named below — do not
  infer behavior from docstrings, commit messages, or file/folder names.
- **No credit for claims you did not verify.** If a doc says "enforced" or
  "verified," open the file and the test that supposedly proves it. If the
  test doesn't actually exercise the claim, say so.
- **Distinguish blueprint from running code**, the way the first EA review
  did (it scored "integrity of claims" separately from "coverage vs.
  architecture"). This repo mixes a large frozen architecture blueprint
  (`ARCHITECTURE.md`, `docs/`) with a much smaller amount of real, tested code.
  Report both the doc-to-code ratio and what fraction of the *architecture's*
  claimed scope actually has running code.
- **Do not accept self-reported counts.** `docs/catalog/MODULE_REGISTRY.json`
  claims to auto-generate its metrics via `python scripts/generate_catalog.py
  --check`. Run that command yourself; don't just read the JSON.

## What to read first (in this order)

1. `docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-21.md` — the baseline review
   and its findings (numbered 1-5, severity-ranked).
2. `CONTRIBUTING.md` — the provider-neutral front door; it names the required
   reading order for any agent.
3. `SESSION/ACTIVE_SESSION_STATE.json` and the handoff it points to
   (`active_handoff` field) — claims about what was done and verified in each
   session.
4. `docs/implementation/EXECUTION_ROADMAP.md` — the phase/tranche structure
   everything since the baseline review claims to follow.
5. `docs/catalog/MODULE_CATALOG.md` (generated) and
   `docs/catalog/MODULE_REGISTRY.json` (source) — claimed status per module.
6. `docs/cvf/CVF_CONTROL_MAPPING.md` — claims that all 12 CVF
   `required_controls` now have code-level gates + tests.

## Specific claims to verify (do not take these at face value)

1. **"12/12 CVF controls enforced."** `packages/cvf-runtime/` claims to gate
   identity, permission, domain_lock, data_scope, risk, approval, evidence,
   audit, cost, refusal, termination, freeze. Open each gate module and its
   test file. For `cost` and `termination`, the repo itself claims these are
   "AI-gated" (logic runs and is tested, but not load-bearing because no AI
   mode beyond NO_AI is wired). Confirm that framing is honest, not spin.

2. **"Three golden verticals reusing the same gates, not forked."** Compare
   `apps/workspace-api/src/workspace_api/application/services.py`,
   `correction_service.py`, and `task_service.py`. Do they actually call the
   same `cvf_runtime` functions, or did later ones drift/duplicate logic?

3. **"Dual-backend SqlLedger, SQLite-verified, PostgreSQL not yet run live."**
   `packages/operations-ledger/src/operations_ledger/`. Read `tables.py`
   (generic `Uuid`/`JSON.with_variant` types) and `sql_ledger.py`. Run
   `tests/integration/test_sql_ledger_sqlite.py`,
   `test_sql_ledger_integrity.py`, and `test_schema_parity.py` yourself. Then
   independently judge: is the claim "PostgreSQL round-trip not yet verified,
   same code path" an honest limitation, or is there a reason to suspect the
   PostgreSQL path would actually break (e.g., a SQLite-only assumption baked
   in somewhere)?

4. **"Schema parity test prevents tables.py from drifting from the SQL
   migration."** Read `tests/integration/test_schema_parity.py` and
   `database/migrations/*.sql`. Is the parity check actually strict (would it
   catch a real drift), or does it only check surface-level things (e.g.
   table names exist) while missing column-level or type-level drift?

5. **"File-size guard, module catalog, and session-state checks are real
   gates, not decoration."** Read `scripts/check_file_size.py`,
   `scripts/generate_catalog.py`, `scripts/check_session_state.py`, and
   `scripts/testing/validate_repository.py`. Then actually try to break one
   (e.g., edit a threshold, or point `active_handoff` at a nonexistent file)
   and confirm the script fails. Revert your test change afterward - do not
   leave the repo modified.

6. **"Frontend/backend boundary is enforced, not just documented."**
   `docs/architecture/FRONTEND_BACKEND_BOUNDARY.md` claims CVF governance
   gates live only in the backend and the frontend never self-enforces. Check
   `apps/workspace-web/src/` - is there actually a frontend UI to check yet,
   or is this still purely aspirational because the frontend is stub/partial?

## What NOT to do

- Do not implement fixes, refactors, or the next roadmap tranche (P2-A
  remaining domains, P2-B auth, P2-C frontend, etc.). This is a review-only
  pass.
- Do not modify files except transient ones you create and delete yourself to
  test a guard script (see item 5 above) - leave the working tree clean
  (`git status --short` should show nothing at the end).
- Do not soften findings to be agreeable. The first EA review's value came
  from being blunt (e.g., "governed architecture lives in .md and .yaml, not
  yet in code" for the pre-buildout state). Match that bar.

## Deliverable

A markdown report, structured like the original EA review:

1. **Overall verdict** - one paragraph, blunt.
2. **Scorecard** - same dimensions as the original review if useful (claim
   integrity, real code quality, coverage vs. architecture, CVF control
   enforcement in code, production readiness), 0-10 each, with the reasoning
   visible.
3. **Measured evidence** - actual numbers you obtained by running commands
   (test count/pass-fail, LOC, module status breakdown from
   `generate_catalog.py --check` output, etc.), not numbers copied from docs.
4. **Findings**, severity-ranked, each with: what's wrong, where (file:line),
   and how you confirmed it (which command/test you ran or which lines you
   read).
5. **What's actually solid** - genuine strengths you verified, not assumed.
6. **Recommendations**, priority-ordered.
7. **One-line conclusion.**

Save the report as
`docs/decisions/EA_INDEPENDENT_REVIEW_2026-07-22_CODEX.md` (do not overwrite
the 2026-07-21 review - this is a second, dated, independent pass).
