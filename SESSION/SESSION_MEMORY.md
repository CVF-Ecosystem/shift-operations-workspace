# Session Memory — human companion to [`ACTIVE_SESSION_STATE.json`](ACTIVE_SESSION_STATE.json), provider-neutral for every agent and human; full chronological history lives in the archive below. _Last updated: 2026-08-20 (P4-A Work Order authorized)_

**2026-08-20 (P4A-AI-GATEWAY / WORK_ORDER AUTHORIZED):** Operator delegated the P4-A reference decision and assigned this agent ORCHESTRATOR/REVIEWER, with a separate BUILD worker. Project-native P4-A1 + public-Core replaces LPCI1-REF for P4-A only. R2 authority review PASS; worker ceiling is 40 paths plus exactly one post-gate live call, no commit/push. P4-A2/P4-B/app/durability/deployment remain parked; no BUILD/live call yet.

**2026-08-20 (CVF-CORE-REFRESH / CLOSED_BOUNDED):** Reconciled stale Core/pins to public `7d9f360a...`; old Core/root preimages preserved. Independent R1–R12 PASS, findings/waivers NONE/NONE; doctor 24 + one bounded warning. Exact-18 local commit `a1aeb60`; no push or AI-governance claim.

**2026-08-18 (P3B-GATE-WIRING / CLOSED_BOUNDED):** SOPR-CP1's two closure commits pushed to `origin/main`. Operator authorized INTAKE for P3-B (sole open Phase 3 item). Key finding, independently re-verified: **no real AI call site exists anywhere in the codebase** — `ai-gateway` is scaffold-only (12 READMEs + 1 interface), `governed-retrieval`/P4-A1 deliberately provider-free — so P3-B **cannot close inside Phase 3**; it is a Phase 4 dependency. INTAKE framed Option A (open minimal P4-A slice) vs B (correct the claim boundary) without pre-deciding, because A crosses `AGENTS.md:196` escalation triggers. **Operator selected Option B.** BUILD recorded P3-B as `BLOCKED_PENDING_P4A_AUTHORITY` in the roadmap entry, Phase 3 header, status table, exit gate and `blocked_work`; Phase 4 NOT opened. Full chain INTAKE→DESIGN→BUILD→REVIEW→FREEZE, each with independent review; DESIGN finding `P3B-DESIGN-F1` (a proposed `[~]` marker was an over-claim vs the file's own legend) closed without waiver, marker kept `[ ]`. Documentation/continuity only: zero source/test/provider/network/DB change.

**2026-08-11 (SOPR-CP1 + Amendment 1, CLOSED_BOUNDED/REVIEWER_ACCEPTED):** Hidden Core already clean at `2103a38f...`; manifest/AGENTS pin repaired to match. Reviewer recomputation, stress 10/10, two full suites 605 passed, doctor 24 PASS. Superseded by 2026-08-18 above; full entry in archive.

**2026-08-11 (ACRC-T3, CLOSED_BOUNDED):** Compacted continuity, archived pre-T3 carriers. Superseded; see archive.

P4-A1 governed retrieval (2026-08-10) `CLOSED_BOUNDED`/parked at `ffe1c5b5...`, review `d56b835d...`, findings/waivers `NONE`/`NONE`. Full text in archive.

## Không được làm (không có xác nhận mới)

Xem `blocked_work` trong `ACTIVE_SESSION_STATE.json`. Cốt lõi: không dùng lại
nhãn "enforced"/"12/12"/"golden vertical"/"tất cả High Finding đã sửa" không
giới hạn; không tin tuyên bố "CLOSED"/"đã xong" của bất kỳ agent nào mà không
tự chạy lại probe/test; không coi `CVF_SESSION/ACTIVE_SESSION_STATE.json` là
nguồn canonical — nó chỉ là compatibility mirror, `python
scripts/check_session_state.py` xác nhận không lệch trước khi kết thúc phiên
có sửa 1 trong 2 file state; không mở downstream project lane nào khác ngoài
T3 mà không có fresh authority. Chi tiết đầy đủ từng tranche nằm trong archive
bên dưới.

## Full History

The complete chronological entry log through 2026-08-10 (P3-A Refinery
amendment lineage, P3-C retrieval-ready contract, P4-A1 governed retrieval,
the P1-B/P2-A/P2-B/P2-C/P2-D/Phase-2 lineage, the earlier
`archive/SESSION_MEMORY_2026-07-22_TO_2026-07-31.md` reference, and every
Vietnamese-language continuity-drift and "không được làm" record back to
project bootstrap) is preserved byte-exact in the archive below. Read it only
when a current fact above is missing or contradictory.

- [`SESSION/archive/SESSION_MEMORY_PRE_T3_2026-08-11.md`](archive/SESSION_MEMORY_PRE_T3_2026-08-11.md)
