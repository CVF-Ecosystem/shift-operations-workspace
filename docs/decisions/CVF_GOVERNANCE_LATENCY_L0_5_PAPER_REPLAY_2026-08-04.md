# L0.5 — Paper Replay of P3-A Incidents Against the Proposed Admission Model

> **REVIEWER NOTICE — NOT A BUILD PATH.**
> This file is an analysis artifact for the `CVF_CORE_GOVERNANCE_LATENCY_LEARNING_ROADMAP_2026-08-04`
> lane. It is **not** one of the exact eight BUILD paths of
> `GOVERNED-PLAN-RUNNER-2026-08-04` and must **not** be staged, committed or
> counted as part of that BUILD candidate. When auditing the runner BUILD,
> exclude this path and its companion self-critique. It authorizes nothing,
> mutates no governed surface and consumes no approval.

- Date: `2026-08-04`
- Artifact class: `ANALYSIS / NON-AUTHORITATIVE`
- Status: `DRAFT_FOR_REVIEW`
- Author: Claude
- Companion: `CVF_GOVERNANCE_LATENCY_L0_5_SELF_CRITIQUE_2026-08-04.md`
  (adversarial self-review — **read both together**; several conclusions below
  are qualified or partly retracted there)
- Calls: `0 provider / 0 network / 0 remote-ingest`
- Method: read-only inspection of committed authority artifacts in
  `docs/work_orders/` and `docs/decisions/`

## 0. What this is and is not

This is a zero-write, on-paper simulation answering one question:

> If the roadmap's admission model (§5.1, §5.2, WS-1) had been in force during
> P3-A, how many R2 approvals would have survived the recorded incidents?

It authorizes nothing. It does not edit CVF core, policy, or any governed path.
It is the cheap falsification step recommended before committing to tranches
L1-L8, and it applies the roadmap's own WS-3 principle — simulate before apply —
to the roadmap itself.

## 1. Correction to the roadmap's baseline

The roadmap §2 states "at least fifteen mechanical stops". The committed record
is materially larger and should be restated before any SLO is fixed:

| Measure | Roadmap §2 | Observed in repository |
|---|---|---|
| Mechanical stop classes | 15 | 15 (classes, correct) |
| Actual amendment artifacts | not stated | **28** for P3-A Refinery alone |
| Independent review artifacts | not stated | 20+ in `docs/decisions/` |
| R2 approvals consumed | not stated | **>=28**, one per amendment minimum |

Each amendment is a full control-chain cycle: authoring, independent
authorization review, pushed authority checkpoint, fresh exact human R2,
one no-retry invocation, then a re-review. The 15 figure counts *defect classes*;
the governance cost is carried by the **28 amendment cycles**.

Recommendation: restate §2 as "15 recurring defect classes across 28 recorded
amendment cycles". This strengthens the case and removes the §2-vs-WS-0
ordering problem noted in review (conclusion currently precedes its evidence).

Reproduction: `ls docs/work_orders/ | grep -c "P3A_REFINERY.*AMENDMENT"` → `28`.

## 2. Replay table

Classification uses the roadmap's WS-0 schema. The decisive column is
**"R2 survives?"** — whether the proposed model would leave the approval
unconsumed and reusable.

> Caveat added after self-critique: "R2 survives" measures *defect caught
> pre-admission*, which is **not** the same as *governance cycle avoided*. See
> the companion self-critique §2. The stricter count is likely 8-10/15.

| # | Incident (source) | Primary class | Where it fails in new model | R2 survives? |
|---|---|---|---|---|
| 1 | Windows-invalid literal wildcard to `rg` | `PRE_ADMISSION_MECHANICAL_FAILURE` | Contract validation: glob metacharacter rejected (WS-3) | **Yes** |
| 2 | Missing package path, stdin Python probe | `PRE_ADMISSION_MECHANICAL_FAILURE` | Executable/path resolution in validate (WS-3) | **Yes** |
| 3 | Mistyped checkpoint SHA (A21, `d5e4a7b7…` vs `d5e4a7bb…`) | `CONTINUITY_FEEDBACK_LOOP` | Dry-run HEAD binding check, zero-write (WS-3/WS-6) | **Yes** |
| 4 | Guessed pytest selector that did not exist | `PRE_ADMISSION_MECHANICAL_FAILURE` | `--collect-only` proof in dry-run (WS-3, SPEC R6) | **Yes** |
| 5 | Wrong file-size script name | `PRE_ADMISSION_MECHANICAL_FAILURE` | Script-path regular-file check in dry-run (WS-3) | **Yes** |
| 6 | PowerShell `foreach($p in$a)` parse failure (A16→A17) | `PRE_ADMISSION_MECHANICAL_FAILURE` | Eliminated: argv arrays, `shell=False`, no shell (WS-3) | **Yes** |
| 7 | JS decoding primitive unavailable in executor | `ENVIRONMENT_MISMATCH` | Capability profile declares available interpreters (WS-2) | **Yes** |
| 8 | UTF-8 stdin transport mismatch (A21 Vietnamese ack) | `ENVIRONMENT_MISMATCH` | No stdin transport; literals read from file as bytes (WS-3) | **Yes** |
| 9 | Outer timeout 120s < reviewed budget (A22→A23) | `PRE_ADMISSION_MECHANICAL_FAILURE` | `requiredOuterTimeoutSeconds` fail-fast check (WS-3, SPEC R7) | **Yes** |
| 10 | Windows text-mode LF→CRLF translation (A19→A20) | `ENVIRONMENT_MISMATCH` | Byte-mode I/O only; newline metrics surfaced in dry-run | **Yes** |
| 11 | Fixture restoration changed newline bytes (A24) | `CONTROL_FALSE_POSITIVE` | Byte-mode restore; **but see §4 — test-side defect, partly outside runner** | **Partial** |
| 12 | Mixed-line-ending patch output (A26) | `ENVIRONMENT_MISMATCH` | Precomputed bytes + atomic replace, no text-mode write | **Yes** |
| 13 | Two-space JSON indent / post-hash mismatch (A27→A28) | `CONTROL_FALSE_POSITIVE` | `SEMANTIC_CANONICAL` mode: whitespace-only JSON drift not byte-escalated (WS-4) | **Yes** |
| 14 | Self-referential future commit-hash assumption | `CONTINUITY_FEEDBACK_LOOP` | Receipts carry identifiers; no pre-commit hash embedding (WS-6) | **Yes** |
| 15 | Reviewer `uv` created `.venv`, downloaded packages | `CAPABILITY_VIOLATION` | Denied at capability layer before `.venv`/download (WS-2) | **Yes** |

### Incidents that are *not* prevented (correctly)

These appear in the P3-A chain but are **semantic findings**, and the model
must not suppress them. They are the control coverage that has to survive:

| Source | Finding | Class | Must still consume R2? |
|---|---|---|---|
| A15 | Four public-boundary defects, AC-03/05/06/07 gaps | `SEMANTIC_RISK_FINDING` | Yes — real product defects |
| A19 | Catalog LOC drift (`20258`→`20266`) | `SEMANTIC_RISK_FINDING` | Yes — stale generated truth |
| A24 | `KPK_ELIGIBILITY_MISMATCH` / source-pin drift | `SEMANTIC_RISK_FINDING` | Yes — real contract violation |
| A25 | File-size debt entry pinned to pre-A24 SHA | `SEMANTIC_RISK_FINDING` | Yes — stale debt registry |
| A27 | `IMPLEMENTATION_STATUS.json` states stale exact32 truth | `SEMANTIC_RISK_FINDING` | Yes — false status claim |

## 3. Result

| Outcome | Count | Share |
|---|---|---|
| R2 survives (approval unconsumed) | 14 | 93% |
| Partial / needs design decision | 1 | 7% |
| Not prevented — correctly | 5 semantic findings | — |

**The central hypothesis is confirmed on paper**, subject to the conflict-of-
interest caveat in the companion self-critique §1. 14 of 15 mechanical defect
classes would be caught pre-admission with zero R2 consumption, while all five
semantic findings still stop the lane as intended.

Caveat: this is a paper replay of *classes*, not a replay of all 28 amendment
cycles. Several amendments were cascades — a mechanical stop that consumed R2,
whose repair then triggered the next mechanical stop (A19→A20→A21→A22→A23 is a
five-cycle chain triggered by one LF/CRLF root cause). Cascade suppression is
where the real saving sits — but see self-critique §3 for a competing
explanation of that cascade.

## 4. The one case that does not cleanly survive — and why it matters

**Incident 11 (A24)**: `tests/integration/test_catalog_drift_detection.py`
snapshots files with `read_text()` and restores with `write_text()`, converting
LF to CRLF on Windows. The catalog tests run before the Knowledge tests, so
teardown corrupted state for a later, unrelated test.

The runner does not prevent this, because the defect is **inside test code the
plan legitimately invoked**. The plan was valid; the gate was authorized; the
environment mutated underneath.

This exposes a gap: WS-3 governs *the runner's* I/O discipline but says nothing
about **byte-discipline requirements for repository test code**. A gate that
corrupts the working tree through platform-dependent text I/O is a governance
hazard the admission model cannot see.

> Partly retracted in self-critique §4: a `.gitattributes` / `core.autocrlf`
> setting may address this class at the repository layer far more cheaply than
> a new control. Verify existing configuration before adding anything.

## 5. Second-order finding: cascade amplification

Classifying by root cause rather than by amendment:

| Root cause | Amendments consumed | Cascade length |
|---|---|---|
| LF/CRLF text-mode I/O | A19, A20, A22, A23, A24, A26 | **6** |
| PowerShell parse/compression | A16, A17, A18 | 3 |
| Continuity hash binding | A21, A27, A28 | 3 |
| Semantic product defects | A15, A25 | 2 |

One environment defect appears to have consumed **six** R2 approvals across four
separate repair attempts. No individual control failed; each stop was correct in
isolation. The cost came from stop-first + no-retry applied to a defect class
that recurs deterministically until its root cause is fixed.

Recommend adding a cascade column to the WS-0 incident ledger — measuring
*chains*, not events.

> Contested in self-critique §3: the six amendments involve three distinct
> mechanisms (test code, patch engine, generator output) that merely share a
> newline symptom. Retrospective single-root-cause attribution may be
> oversimplified, and a learning-curve explanation is not excluded.

## 6. Recommendations to the roadmap

| Priority | Change | Basis |
|---|---|---|
| High | Restate §2 as "15 defect classes across 28 amendment cycles" | §1 — directly countable |
| High | Add cascade-length metric to WS-0 and WS-7 | §5 — contested, verify first |
| High | Set WS-7 SLO from the L0 baseline, not the pre-set 80% | §3 |
| Medium | Verify `.gitattributes` before adding byte-discipline control | §4 + self-critique §4 |
| Medium | Add conservative fail-safe: unknown admission state ⇒ CONSUMED | prevents double-use; see self-critique §5 for the downside |
| Low | Cite the resume-logic bug found during runner BUILD as positive control | model catches real semantic defects pre-R2 |

## 7. Verdict

Original verdict was "proceed to L1". **Revised after self-critique to: proceed
to L0, and do not commit to L1 until an independent reviewer has verified
self-critique §1, §2 and §3.** All three verification steps are read-only
repository analysis requiring no code and no core edit.

One design gap (§4) should be closed in DESIGN rather than discovered in BUILD.
