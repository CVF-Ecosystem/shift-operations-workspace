# P3-A Refinery Work Order Amendment 14 — Independent Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk / phase: `R2 / WORK_ORDER`
- Amendment 14 SHA-256: `a1a76cbfa979855cf64d650ccca5ede807470b12bf5e9930a7cc7a1cb15bbe17`
- Consumed Amendment 13 SHA-256: `332895d89799ec724031057cf265b1c84e6a62a8510b6f86363a4fe309f9da50`
- Amendment 13 review SHA-256: `c9719ab585e33f6b74f9ea0e3e182e681ffa1a5f9fa952e73892294e502d36a7`
- Amendment 13 authority / acknowledgment: `af691d049ca37288d99a09ac0df790018e3fc31c` / `20f3f73c5fdd9d3704823c8191f067f57422be76`
- Provider/network/remote-ingest calls: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_PASS`

Amendment 14 accurately consumes Amendment 13's first-failure stop and
authorizes a zero-repair continuation from the already completed atomic repair.
Its exact-32/stable-30/suffix bindings make the dirty candidate invariant under
the required governance-only partial commits. The explicit five-file focused
suite removes the invalid wildcard seam without rerunning or relabeling the
failed command. Remaining gates stay ordered, one-shot, local and fail-closed.

Open authorization findings: `NONE`. Waivers: `NONE`.

This PASS does not itself authorize continuation. A bounded authority
checkpoint must be committed and pushed with the partial-staging discipline
below, followed by a fresh exact human R2 acknowledgment for Amendment 14
before the one permitted invocation may begin.

## Consumed Amendment 13 truth

Independent Git, artifact and canonical-continuity checks establish:

- `HEAD == origin/main == 20f3f73c5fdd9d3704823c8191f067f57422be76`;
- `af691d049ca37288d99a09ac0df790018e3fc31c` is the pushed Amendment 13
  authority checkpoint and `20f3f73c5fdd9d3704823c8191f067f57422be76`
  is its pushed fresh-R2 acknowledgment checkpoint;
- Amendment 13 preflight passed, its one atomic six-path repair passed, and
  `python scripts/check_file_size.py` passed;
- the next read-only `rg` inventory returned non-zero because Windows treated
  wildcard literals as invalid paths;
- execution stopped at that first failure, the command was not retried, and
  focused, catalog, full-suite and all later gates remained `NOT_RUN`;
- provider/network/remote-ingest calls remained `0/0/0`.

Amendment 13 and its R2 are consumed. Amendment 14 is a fresh, independently
reviewed zero-repair continuation, not a retry or relabeling of the failed
wildcard inventory.

## Independent current-state reproduction

The reviewer excluded only the two authority-state paths and Amendment 14
itself from the 35-path preparation worktree. The result is the exact 32-path
dirty BUILD/continuity candidate. Excluding its two volatile continuity front
doors produces the stable 30-path set.

Using ordinal case-sensitive sorting and UTF-8 records encoded as
`path + NUL + lowercase_file_sha256 + LF`, the reviewer reproduced:

| Binding | Expected | Reproduced | Result |
|---|---:|---:|---|
| Dirty BUILD/continuity paths | exact `32` | exact `32` | `PASS` |
| Stable candidate paths | exact `30` | exact `30` | `PASS` |
| Stable-30 manifest | `a50cebb5f4f4b2e6b6ae79bc56ebc70ac17c1fdd28b7242267a17e96e9c6a436` | same | `PASS` |
| `pipeline.py` | 285 / `69a55e2e7ad3b115176ae853f2756d3115f69aa12d0d1f7a6088ab15bb8371bf` | same | `PASS` |
| `protection.py` | 260 / `d909c740e1a2e93859ca47a596c3dac2afaf740648044523b5d5e9de3e58a3f5` | same | `PASS` |
| Memory archive | 335 / `e218cbc150d03bd9c42f623f972e43ee33ee00b530882195e2c8c145ab918f86` | same | `PASS` |
| Handoff archive | 394 / `c50d4bfd7c7745fa1bb3e5758eddb57c905f5d10fac5da5fda8707f63aee0d44` | same | `PASS` |
| Stable memory suffix | 243 / `6a055880ab97e542fa122ff6cbe3025d993aa521d3b4e9098abf82fa97237ac6` | same | `PASS` |
| Stable handoff suffix | 2 / `46f46615b06dff42a2c44b55321e30c862881146a58a98549fe06f06aaceb357` | same | `PASS` |
| Staged paths | `0` | `0` | `PASS` |

The memory and handoff archive links resolve relative to their canonical front
doors. Current canonical memory/handoff sizes are 302/503 lines after the A14
candidate preamble, while both archives are 335/394; all four remain within the
600-line Markdown hard ceiling. Both changed Python sources remain within the
300-line executable hard ceiling. No repair content changed during review.

## Zero-repair continuation and ordered gates

The repair-touch ceiling is exactly zero. The continuation must first reproduce
the pushed authority/R2 lineage, exact-32 set, stable-30 manifest, source and
archive hashes, suffix hashes, resolving links, line limits and empty index.

The focused command must explicitly list exactly these five tracked hosts once:

1. `tests/unit/test_refinery_models.py`
2. `tests/unit/test_refinery_canonical.py`
3. `tests/unit/test_refinery_pipeline.py`
4. `tests/unit/test_refinery_adversarial.py`
5. `tests/unit/test_refinery_contract.py`

Its required result is exactly `53 passed`. Only then may catalog `--check`,
the full non-live suite, session-state/repository/JSON-YAML/forbidden
import-I/O/secret/diff checks, and the final invariant audit run in that order.
Each command runs once; the first non-zero or invariant mismatch stops all later
steps. The failed wildcard `rg` command is neither rerun nor relabeled.

## Partial-staged authority and R2 checkpoints

The authority checkpoint's staged path set must be exactly these six paths:

- `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_14.md`;
- `docs/decisions/P3A_REFINERY_WORK_ORDER_AMENDMENT_14_AUTHORIZATION_REVIEW.md`;
- `SESSION/ACTIVE_SESSION_STATE.json`;
- `CVF_SESSION/ACTIVE_SESSION_STATE.json`;
- `SESSION/SESSION_MEMORY.md` — only new A14 authority/review preamble hunks;
- `SESSION/handoffs/AGENT_HANDOFF_2026-08-03_P3A_REFINERY.md` — only new A14
  authority/review governance hunks before the stable suffix.

The cached diff must exclude every source, archive, catalog, fixture, knowledge,
contract, package, implementation-status and test hunk. In the two partially
staged front doors it must also exclude every rotation deletion/addition and
must preserve the two reviewed suffixes byte-for-byte. The unstaged diff must
still represent exact 32 BUILD/continuity paths before the commit. After the
checkpoint is pushed, the index must be empty and the worktree must reproduce
exact 32, stable 30 and both suffix bindings unchanged.

The subsequent fresh-R2 checkpoint uses the same rule with exactly four staged
governance paths: canonical state, mirror, and only the new R2 acknowledgment
hunks from the two continuity front doors. After it is pushed, the index must
again be empty and exact-32/stable-30/suffix truth must remain unchanged.

## Claim boundary and next governed move

No repair edit, provider/network/remote-ingest call, retry, unrelated edit,
catalog write, BUILD commit/push, self-review, FREEZE or later lane is
authorized. A successful continuation yields only the still-dirty exact-32
candidate pending independent BUILD review; it proves no caller wiring,
persistence, `data_scope`, retrieval/RAG, learning runtime, production
readiness, P3-A closure or Phase 3 completion.

COMMIT_STEWARD may now prepare and push only the bounded six-path authority
checkpoint above, prove that the exact-32 candidate remains wholly unstaged,
and stop for fresh exact Amendment 14 human R2.
