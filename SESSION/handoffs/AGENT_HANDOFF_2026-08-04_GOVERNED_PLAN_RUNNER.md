# Agent Handoff — Governed Plan Runner

## Disposition

- Tranche: `GOVERNED-PLAN-RUNNER-2026-08-04`
- Parent: P3-A Refinery `CLOSED_BOUNDED` at FREEZE `3c53882`
- Risk: `R2`
- Control-chain phase: `REVIEW` (parked; findings open)
- Active role: `SESSION_SYNC_STEWARD`
- Status: `PARKED_REVIEW_CHANGES_REQUIRED_LOCAL_EVIDENCE_ONLY`

## Intent and boundary

The operator requested an immediate project-local fix for mechanical workflow
failures whose latency and quota cost exceeded their product value. The runner
validates and simulates argv/byte plans before R2, then provides atomic local
execution and deterministic receipts. It changes no CVF core or policy
semantics and grants no retry of consumed approvals.

## Authority candidate

- ADR: `docs/decisions/ADR_2026-08-04_GOVERNED_PLAN_RUNNER.md`
  (`4c273fc8f0fb984ffa4b2ce0061b981ccb89efd6097ddb873780f82aefa9ed97`)
- SPEC: `docs/specs/GOVERNED_PLAN_RUNNER_SPEC.md`
  (`b26b90388e5b41c58aa11d2f245a3ee590fb82fafd347c496c6b7187f1611260`)
- Work Order: `docs/work_orders/GOVERNED_PLAN_RUNNER_WORK_ORDER.md`
  (`352a75fb837efa179c604eb2f52a0ff9fcb6693295f549bc2a7443f87a169327`)
- BUILD ceiling: exact eight paths; zero provider/network/remote-ingest calls.

## Superseded authorization route

Initial review `57e1ead6…fe63` is FAIL/GPR-AUTH-F1: reviewer invoked `uv`,
created `.venv`/`uv.lock`, downloaded `pydantic-core` and installed 26 packages
despite zero-network scope. Generated residues were removed, no waiver. Fresh
local-only review `7357cd56…d409` closed F1 but found F2: dependency-complete
Python is 3.11.9 while ADR required >=3.12. ADR now uses compatible >=3.11;
that review granted no BUILD/stage/commit/push authority.

Final local-only review `f7408e2d…ee5f` PASS; F1/F2 closed without waiver,
findings NONE. Its proposed exact10/fresh-R2 route was not completed in
canonical continuity and does not retroactively authorize the later candidate.

## Independent BUILD review and park disposition

Independent BUILD review
`docs/decisions/GOVERNED_PLAN_RUNNER_BUILD_INDEPENDENT_REVIEW.md`
(`5a8b9154dcb182689bac5575fed2241863b11343ee43b0540b5fecd624822f76`)
returned `REVIEW_CHANGES_REQUIRED`, no waiver. Focused tests were
`52 passed, 1 skipped`, but direct probes reproduced material authority/R2/HEAD,
zero-network, resume/receipt and rollback failures (`GPR-BUILD-F1..F7`).

The operator chose retention rather than repair or deletion:

- preserve all exact-eight BUILD files unchanged and unstaged;
- preserve the independent review and
  `docs/decisions/CVF_CORE_GOVERNANCE_LATENCY_LEARNING_ROADMAP_2026-08-04.md`
  as the upstream-learning use case;
- do not delete, repair, stage, commit or push any of these local artifacts;
- do not claim BUILD authorization, REVIEW_PASS, FREEZE or runtime readiness.

Frozen local evidence checksums at park time:

| Path | SHA-256 |
|---|---|
| `scripts/run_governed_plan.py` | `ae9158405034ab46b7f2bb080f3eb013407e8abaca1e0ad66d2ec04f302299ca` |
| `scripts/_governed_plan_contract.py` | `e6f0b7a090f063f95cd97dc291393f3903afe9a17d9b6f7cf7a280b134db45a8` |
| `scripts/_governed_plan_engine.py` | `67972ac157692396d99b532796aa3e4fb9b6a0b7b1fc284a90e24a3a6adfc066` |
| `docs/reference/GOVERNED_PLAN_SCHEMA.json` | `ce5261f8e62bcd0ea79fbf4f77b1fc186afdc9cd0ba70092589352f4ce39c0e4` |
| `tests/unit/test_governed_plan_contract.py` | `bb232ca0e03c2d368d2a11667f87c27f41aa13ba8d6aae685737eb0252b65ac7` |
| `tests/unit/test_governed_plan_engine.py` | `60697249b52d0f1a46c46d04d24d0821ebb5c781d93ec42db894042be1298f5e` |
| `tests/unit/test_governed_plan_resume.py` | `16e2f0379df0d7e61c8a6351c311eb4eae2063d0cbc7ba852278ba28a1d790d0` |
| `tests/fixtures/governed_plan/a28_indent_plan.json` | `b4d86eab5211826078079a5a5ac22c7847db19e22205205aeb5a185fddc31b21` |
| `docs/decisions/GOVERNED_PLAN_RUNNER_BUILD_INDEPENDENT_REVIEW.md` | `5a8b9154dcb182689bac5575fed2241863b11343ee43b0540b5fecd624822f76` |
| `docs/decisions/CVF_CORE_GOVERNANCE_LATENCY_LEARNING_ROADMAP_2026-08-04.md` | `9e439901164ca8e3d126398fbc6ec5484771b8a9b0355c8dd70d01533fdcc87e` |
| `docs/decisions/CLAUDE_HANDOFF_TO_CODEX_2026-08-04.md` | `20d915d5d4171fe9971dbde7a2502cf1860cad137523e890042793c3bcb6658d` |
| `docs/decisions/CVF_GOVERNANCE_LATENCY_L0_5_PAPER_REPLAY_2026-08-04.md` | `cb056b06b0b1b9f9800bdd6b636c727bec88f518fe31787cc1df92c1979d48d4` |
| `docs/decisions/CVF_GOVERNANCE_LATENCY_L0_5_SELF_CRITIQUE_2026-08-04.md` | `80a50ca346b8aaf6893b05a45f74c41413dcc442b991899039edc63b11f4defc` |

The final roadmap received an independent narrow closure `PASS` against the
exact SHA above: findings/waivers `NONE/NONE`. Its authority ceiling is a fresh
core-native L0 intake only. L1+ remains blocked until L0 Gate A returns either
`PROCEED_FULL` or the explicitly bounded `PROCEED_WS2_ONLY`; the Claude replay
numbers remain hypotheses, not accepted metrics.

### Operator retention note

The operator confirmed that this original machine and workspace will remain
available. The parked evidence intentionally exists only in this local dirty
worktree; it is not backed by GitHub and must not be cleaned, stashed, reset or
otherwise normalized during unrelated work. When this project is reopened
after the CVF core improvements, first verify every checksum in the table
above and confirm staged paths remain zero. Any mismatch requires an evidence
integrity review before fresh INTAKE; never reconstruct or silently replace a
missing candidate file.

## Next governed move

This downstream project is parked. Improve CVF core governance latency and
control semantics in its own repository and authority chain. When returning,
rehydrate this handoff and review, then begin a fresh downstream INTAKE and new
bounded repair authority. Never reuse or retroactively accept the prior R2.

## 2026-08-06 superseding transition addendum

The operator authorized completion of the workspace refresh and return to the
project roadmap. The CVF workspace carrier is now refreshed to public core
commit `9b039ea6b`, and the project-specific carrier reconciliation is commit
`e868eb4`.

Historical filenames and frozen prose that call provenance `CVF core` retain
the earlier naming mistake for evidence integrity. They do not redefine the
authority boundary: learning entered the provenance repository through its own
governed roadmap, then the released carrier was bootstrapped into this CVF
workspace.

The earlier dirty-worktree retention instruction is superseded only as follows:

- all frozen candidate and evidence SHA-256 values reproduced after CRLF-to-LF
  normalization; the byte-level differences were newline conversion only;
- the exact-eight candidate is preserved unchanged on local evidence-only
  branch `evidence/governed-plan-runner-rejected-20260804`, commit
  `99789c0b73c70d14703f5a5d0f1278b069fa3925`;
- the candidate remains `REVIEW_CHANGES_REQUIRED`; F1-F7 remain open;
- the evidence branch must not be merged, promoted, or treated as BUILD proof;
- capability enforcement/zero-network still has no downstream implementation
  owner, so another repair-amendment loop would recreate governance latency.

The runner lane is therefore value-parked. Its checkable reopen condition is a
fresh bounded INTAKE that identifies a real capability-enforcement owner and
new authority; the prior R2 is permanently non-reusable.

The next project move is one fresh bounded P3-C retrieval-ready data-contract
INTAKE. No BUILD, provider, network, POST, retrieval, or R2 authority carries
forward. Stop at the next risk/authority gate.
