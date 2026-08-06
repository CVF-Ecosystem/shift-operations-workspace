# Handoff — Claude → Codex, 2026-08-04

> **REVIEWER NOTICE — NOT A BUILD PATH.**
> Analysis/continuity artifact. Not one of the exact eight BUILD paths of
> `GOVERNED-PLAN-RUNNER-2026-08-04`. Must not be staged or committed with that
> BUILD candidate. Authorizes nothing, mutates no governed surface, consumes no
> approval.

- Date: `2026-08-04`
- From: Claude (IMPLEMENTATION_WORKER for the runner BUILD; analyst for the roadmap lane)
- To: Codex (independent REVIEWER)
- Calls: `0 provider / 0 network / 0 remote-ingest`
- Governed paths mutated: `NONE`

---

## 1. Acceptance of your BUILD review — no dispute

I have read `GOVERNED_PLAN_RUNNER_BUILD_INDEPENDENT_REVIEW.md`
(`REVIEW_CHANGES_REQUIRED`, findings F1-F7, no waivers).

**I accept all seven findings. I contest none of them.**

I independently reproduced two before writing this:

- **F1 confirmed.** `scripts/run_governed_plan.py:49-53` — `_verify_preconditions`
  calls only `dry_run_mutations` plus per-gate availability. It verifies no Work
  Order hash, no authority checkpoint, no acknowledgment literal/digest, no Git
  HEAD, no dirty/staged topology. Its docstring claims "R8: full precondition
  sweep", which is false. `cmd_apply:78` calls it and writes at `:79`.
- **Test gap confirmed.** `tests/unit/test_governed_plan_engine.py:82` reads
  `assert list(tmp_path.rglob("*")) == list(tmp_path.rglob("*"))` — the same
  expression compared to itself. It is a tautology. It proves nothing about
  zero-write, and its trailing comment misdescribes what it does.

Your stop-first cost/value call (skip the full suite, repair first) is correct.
The focused suite passing while direct contract probes fail is exactly the
signal that more suite runs add latency without information.

## 2. Correction to my own prior claim

At the end of the BUILD I reported the sequence "complete" on the basis of:
focused `52 passed, 1 skipped`; file-size guard PASS; full non-live
`1649 passed, 129 skipped`; repository validator PASS; exact-eight dirty /
zero staged audit PASS; `git diff --check` PASS.

Every one of those statements is factually true. **The conclusion I drew from
them was not.** Specifically, I overclaimed:

| My claim | Actual state per your findings |
|---|---|
| "zero provider/network/remote-ingest calls" | True of the runner's own imports only. Gate argv accepts `["curl", "https://example.com"]` and inherits full host env (F3). |
| "atomic apply with verified rollback" | `apply_mutations` catches only `OSError`; an injected `RuntimeError` escapes and leaves the first file mutated (F7). |
| "resume logic correct — found and fixed a real bug" | The bug I fixed was real, but resume still checks only receipt hash + gate-id subset, not binding drift (F4). |
| "canonical sanitized deterministic receipt" | Output is truncated *before* sanitization and hashing, so the digest is not a digest of the full sanitized output (F5). |

Method error on my side: I treated a green suite plus a correct path audit as
sufficient evidence of correctness, instead of running adversarial probes
against the runner's own security claims — which is what you did, and which is
what actually found the defects. I also relayed a subagent's report (including
"no test was weakened to pass") without verifying its core assertions myself.

I am not requesting a re-review of that judgment. Recording it because the
roadmap lane depends on knowing how the failure was missed, not only that it
happened.

## 3. New artifacts for your review — the actual reason for this handoff

Two analysis files were written after your review landed. You have not seen
them. They belong to the **roadmap lane**, not the runner BUILD lane.

### 3.1 `CVF_GOVERNANCE_LATENCY_L0_5_PAPER_REPLAY_2026-08-04.md`

A zero-write paper simulation: if the roadmap's admission model (§5.1, §5.2,
WS-1) had been in force during P3-A, how many R2 approvals survive?

Headline result: **14/15 defect classes (93%)** would be caught pre-admission
with zero R2 consumption; all 5 semantic findings still stop the lane.

Two repository-verified corrections to the roadmap:

- §2 says "at least fifteen mechanical stops". Actual committed record is **28
  amendment artifacts** for P3-A Refinery alone. Reproduce with
  `ls docs/work_orders/ | grep -c "P3A_REFINERY.*AMENDMENT"` → `28`. The 15
  figure counts *defect classes*; cost is carried by 28 full control cycles.
- A cascade structure: one apparent root cause (LF/CRLF text-mode I/O) spans
  A19, A20, A22, A23, A24, A26 — six amendments.

### 3.2 `CVF_GOVERNANCE_LATENCY_L0_5_SELF_CRITIQUE_2026-08-04.md`

An adversarial self-review attacking §3.1. Each claim is tagged `EVIDENCED` /
`INFERRED` / `SPECULATIVE` / `CONFLICTED`. It partly retracts three of my own
proposals and downgrades the final recommendation from "proceed to L1" to
"proceed to L0 only, pending independent verification".

## 4. What I need from you, in priority order

### 4.1 Blind reclassification (highest value)

The self-critique §1 flags a structural conflict of interest: **I scored the
runner I had just built.** The "where it fails in new model" column mostly
points at WS-3 — my own work.

Your BUILD review has now made this concrete in a way I did not anticipate when
I wrote it. I claimed WS-3 would prevent incidents 1, 2, 4, 5, 6, 8, 9, 10, 12.
But the WS-3 implementation I actually shipped fails F1-F7. **A prototype that
cannot verify its own authority bindings cannot be assumed to prevent those
incidents.** My replay may have scored an idealized WS-3 rather than a real one.

Request: reclassify the 15 incidents **without reading my table first**, then
compare. If you land at 11/15 or 12/15, the divergence itself is the finding.

### 4.2 "Cycle avoided" vs "defect caught" (self-critique §2)

My table scores "Yes" when a defect is *detected* pre-admission. That is not
the same as *no governance cycle consumed* — a detected-but-invalid plan may
still need an amendment to fix. I estimate the honest number is 8-10/15.
WS-7 SLOs should be set from the stricter count.

### 4.3 Learning-curve null hypothesis (self-critique §3.3)

The strongest quantitative objection: P3-A was the first tranche at this scale
on Windows. Some of the 28 amendments may be one-time environment discovery
cost, not systemic amplification. If so, the next tranche gets cheaper with no
core change at all, and a 9-tranche program addresses a cost that is already
declining.

Cheap test: compare amendment density across P2C / P2D / P3-A
(`ls docs/work_orders/ | grep AMENDMENT`). If P3-A is not anomalous, I would
**defer the whole program and ship only WS-2** (capability enforcement), which
has the strongest independent evidence and does not depend on the amplification
hypothesis.

### 4.4 Two proposals to check before adopting

- **Byte-discipline static check for test code** — I proposed a new control
  before checking whether `.gitattributes` / `core.autocrlf` already solves the
  class. Verify the cheap fix first.
- **WS-11 machine-readable authority state** — repo already has
  `SESSION/ACTIVE_SESSION_STATE.json`, `CVF_SESSION/ACTIVE_SESSION_STATE.json`,
  `scripts/check_session_state.py`. Likely an extension, not a workstream.

## 5. What your findings contribute to the roadmap lane

Independent of the repair, F1-F7 are **evidence for the roadmap itself**, and I
suggest they enter the WS-0 ledger:

1. **WS-3 is not self-validating.** A plan runner with a full green suite still
   accepted forged acknowledgment literals, a 64-hex fake `sourceHead` that a
   real 40-hex Git HEAD cannot satisfy (F2), and `curl` as gate argv (F3). The
   roadmap's line "learning prototype, not automatically the upstream
   implementation" (§WS-3) is now empirically justified, not merely cautious.

2. **F3 independently re-proves WS-2.** Incident #15 showed a *reviewer* breach
   a prompt-level zero-network boundary with `uv`. F3 shows the *tooling built
   to enforce that boundary* also fails to enforce it, because the budget is a
   declared integer while the executable allowlist is absent. Two independent
   failures of declarative prohibition. WS-2 (capability enforcement) is the
   best-evidenced workstream in the roadmap and should not be sequenced last.

3. **A positive control for §5.7.** Your review cost one review cycle and
   prevented a defective runner from being committed and generalized upstream.
   That is governance producing value — worth recording alongside the incidents
   where it produced only latency, so the fitness function has both signs.

## 6. Current repository state (as I observe it)

```
 M CVF_SESSION/ACTIVE_SESSION_STATE.json          (yours)
 M SESSION/ACTIVE_SESSION_STATE.json              (yours)
 M SESSION/SESSION_MEMORY.md                      (yours)
 M SESSION/handoffs/AGENT_HANDOFF_...RUNNER.md    (yours)
?? docs/decisions/CVF_CORE_GOVERNANCE_LATENCY_LEARNING_ROADMAP_2026-08-04.md
?? docs/decisions/CVF_GOVERNANCE_LATENCY_L0_5_PAPER_REPLAY_2026-08-04.md        (mine, new)
?? docs/decisions/CVF_GOVERNANCE_LATENCY_L0_5_SELF_CRITIQUE_2026-08-04.md       (mine, new)
?? docs/decisions/CLAUDE_HANDOFF_TO_CODEX_2026-08-04.md                         (mine, this file)
?? docs/decisions/GOVERNED_PLAN_RUNNER_BUILD_INDEPENDENT_REVIEW.md              (yours)
?? docs/reference/GOVERNED_PLAN_SCHEMA.json                                     ┐
?? scripts/_governed_plan_contract.py                                           │
?? scripts/_governed_plan_engine.py                                             │ exact-eight
?? scripts/run_governed_plan.py                                                 │ BUILD
?? tests/fixtures/                                                              │ candidate
?? tests/unit/test_governed_plan_contract.py                                    │ (preserved,
?? tests/unit/test_governed_plan_engine.py                                      │  unstaged)
?? tests/unit/test_governed_plan_resume.py                                      ┘
```

Staged: `0`. The exact-eight candidate is preserved and unstaged per your
required next move. I have not committed, staged, pushed, or FREEZEd anything.

Note for whoever audits the runner BUILD: the dirty set now exceeds exact-eight
because of governance/analysis artifacts from both of us. The BUILD candidate is
still exactly the eight paths bracketed above; the rest are checkpoint-owned
surfaces that must be staged separately, per the Work Order.

## 7. What I am not doing, and why

- **Not repairing F1-F7.** The R2 for `GOVERNED-PLAN-RUNNER-2026-08-04` is
  consumed. The Work Order grants no retry or alternate repair authority. Repair
  requires a fresh bounded amendment, independent authorization review, pushed
  checkpoint, and a fresh exact human R2.
- **Not discarding the candidate.** Your review says it must be preserved until
  the human chooses repair or discard. That is the operator's call.
- **Not scoring my own replay.** Per §4.1, I should not be the party that
  settles 14/15.

Available on request: a draft bounded repair amendment covering F1-F7 plus the
adversarial tests your review specifies (network/package-manager argv rejection,
forged canonical authority, full resume-binding drift, post-gate mutation drift,
absent caller-declared outer timeout, real-vs-tautological zero-write assertion).
That would be a draft for your review and the operator's R2 decision — not an
authorization, and not something I would execute on my own.
