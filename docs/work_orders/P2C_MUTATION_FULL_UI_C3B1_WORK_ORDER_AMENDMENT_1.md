# Work Order Amendment 1 — P2-C C3b1 Frontend Test Command

- Parent: `P2C-MUTATION-FULL-UI-C3B1-WO-001`
- Finding: `C3B1-G6-F1 INVALID_FRONTEND_TEST_COMMAND`
- Risk: `R2`
- Status: `REVIEW_PASS / APPROVED — RESUME ONLY AFTER PUSHED CHECKPOINT AND G6`

## Finding

The pushed Work Order's minimum-command block uses:

```powershell
pnpm --dir apps/workspace-web test -- --run
```

With the locked pnpm 9.15.0 toolchain this is parsed as a pnpm command and
fails with `Unknown option: 'run'`. Because PowerShell continued to the next
command, the later production build passed, but that success does not prove
the omitted frontend test gate. G6 stopped without source edit or provider
call. The package script is already `"test": "vitest run"`; the canonical
non-watch command was run separately and proved the baseline at 2 files / 22
tests passing.

## Amendment

Replace only that minimum command with:

```powershell
pnpm --dir apps/workspace-web run test
```

No other Work Order text changes. The exact C3b1 BUILD ceiling remains 34
numbered/34 unique paths. DESIGN, SPEC R11/R15-R17/R34-R37, acceptance
allocation, evidence classes, stop conditions, role separation and claim
boundary remain unchanged.

## Resume boundary

This amendment authorizes no BUILD, provider call, staging, commit, push,
self-review or FREEZE. After independent `REVIEW_PASS` and push, a separate
four-surface resume checkpoint becomes the new exact pre-BUILD parent. G6
must be rerun from the beginning; prior passing portions are evidence of the
failed attempt only and cannot be spliced into the resumed gate.
