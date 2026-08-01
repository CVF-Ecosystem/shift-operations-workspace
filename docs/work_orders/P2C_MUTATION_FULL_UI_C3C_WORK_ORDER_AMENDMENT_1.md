# Work Order Amendment 1 — P2-C C3c Browser Toolchain Pin

- Parent: `docs/work_orders/P2C_MUTATION_FULL_UI_C3C_WORK_ORDER.md`
- Trigger: `C3C-G6-REV-F1 PLAYWRIGHT_PIN_NOT_AVAILABLE_PREBUILD`
- Risk: `R2`
- Ceiling effect: none; exact BUILD ceiling remains 38 paths
- Status: `APPROVED — SUPERSEDES ONLY THE CONFLICTING G6/PIN WORDING`

## Finding

The parent correctly requires a pinned Playwright dependency during BUILD and
a usable Chromium prerequisite at G6, but does not name the version. Because
`@playwright/test` is not yet in the pre-BUILD manifest, “check the pinned
Playwright Chromium prerequisite” is not reproducible: there is no existing
pin to resolve, and leaving selection to the worker would make the lockfile and
browser revision unreviewed.

## Exact repair

- BUILD MUST add dev dependency `@playwright/test` at exact version `1.62.1`
  (no caret, tilde, tag or range) in the already-authorized `package.json` and
  resolve that exact version in the already-authorized `pnpm-lock.yaml`.
- Pre-BUILD G6 MUST run the isolated, version-qualified command
  `pnpm dlx @playwright/test@1.62.1 install chromium`, then
  `pnpm dlx @playwright/test@1.62.1 --version`. The command may populate the
  external pnpm/browser cache but MUST leave zero tracked or untracked
  repository paths and no owned process after completion.
- BUILD and independent review MUST use the manifest-installed command
  `pnpm --dir apps/workspace-web exec playwright --version` and confirm it is
  `1.62.1`; the evidence runner uses that installed tool, not `dlx`.
- Browser download failure, version mismatch, repository residue or a skipped
  browser remains `BLOCKED_G6`/review failure. No fallback browser, ambient
  global Playwright or silent download during evidence execution is allowed.

All route, state, accessibility, runner, cleanup, exact-path and claim
boundaries in the parent remain unchanged. No BUILD/provider/Claude CLI/MCP,
stage/commit/self-review/FREEZE is authorized by this amendment alone.
