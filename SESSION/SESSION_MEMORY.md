# Session Memory — human companion to [`ACTIVE_SESSION_STATE.json`](ACTIVE_SESSION_STATE.json), provider-neutral for every agent and human; full chronological history lives in the archive below. _Last updated: 2026-08-18 (P3-B gate-wiring INTAKE opened for review)_

**2026-08-18 (P3-B GATE WIRING / INTAKE_REVIEW_PASS / DESIGN pending):** SOPR-CP1's two closure commits pushed to `origin/main`; hidden Core re-verified clean. Operator authorized INTAKE for P3-B (sole open Phase 3 item: wire `data_scope`/`cost`/`termination` into a real call site). INTAKE finds no real AI call site exists anywhere yet — `ai-gateway` scaffold-only, `governed-retrieval`/P4-A1 deliberately provider-free — and frames two DESIGN options without pre-deciding: (A) open a minimal P4-A slice as caller, or (B) re-word roadmap so P3-B isn't independently closeable. Independent review (`docs/decisions/INTAKE_2026-08-18_P3B_INDEPENDENT_REVIEW.md`) re-verified every citation, found zero defects, returned `INTAKE_REVIEW_PASS`. Decision packet now with `DESIGN_AUTHOR`. Zero provider/network/DB change throughout.

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
