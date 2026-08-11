# Session Memory — human companion to [`ACTIVE_SESSION_STATE.json`](ACTIVE_SESSION_STATE.json), provider-neutral for every agent and human; full chronological history lives in the archive below. _Last updated: 2026-08-11 (SOPR-CP1 / Amendment 1 closed bounded, reviewer accepted)_

**2026-08-11 (SOPR-CP1 + AMENDMENT 1 / CLOSED_BOUNDED / REVIEWER_ACCEPTED):** The hidden public Core was already clean/current at `2103a38fda01ee827e9fc6c3be38a824fa5d54ad`, equal to local `origin/main`; no reconciler ran. `.cvf/manifest.json` and `AGENTS.md` now pin that exact commit, with exactly three affected Project Knowledge pins refreshed. Independent review rejected the first return because a final-character base64url mutation sometimes preserved decoded JWT signature bytes; Amendment 1 repaired only the deterministic test fixture and evidence. Reviewer recomputation passed authorization stress 10/10, the separately disclosed ordering test 30/30, two consecutive full suites at 605 passed, all required local gates, and doctor 24 PASS plus the one bounded legacy warning. Governance/continuity only; all downstream product/runtime/provider/live/public/deploy lanes remain parked pending fresh authority. Next move is private Core closure/session synchronization after the reviewer-owned target commit.

**2026-08-11 (ACRC-T3 CLOSED_BOUNDED / REVIEWER ACCEPTED):** Compacted continuity to current pointers, archived pre-T3 carriers byte-for-byte, rotated the active handoff, and refreshed three Project Knowledge pins. Independent review reran 17 focused and 605 CVF tests plus all required gates. Governance/continuity only. Superseded by SOPR-CP1 above; see archive for full entry.

P4-A1 governed retrieval (2026-08-10) remains `CLOSED_BOUNDED`/parked at closure `ffe1c5b500f2f27f4166ded97423c4fc76354c67`, independent review `d56b835d9c72ec706fc3b8d293aaf85a147ecd6f62c20cfa1afc29baed52ef22`, findings/waivers `NONE`/`NONE`. Full entry text is in the archive below.

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
