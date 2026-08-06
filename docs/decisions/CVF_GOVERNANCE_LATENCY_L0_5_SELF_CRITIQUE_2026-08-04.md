# Phản biện các nhận xét/đề xuất của Claude về Governance-Latency Roadmap

> **REVIEWER NOTICE — NOT A BUILD PATH.**
> This file is an analysis artifact for the `CVF_CORE_GOVERNANCE_LATENCY_LEARNING_ROADMAP_2026-08-04`
> lane. It is **not** one of the exact eight BUILD paths of
> `GOVERNED-PLAN-RUNNER-2026-08-04` and must **not** be staged, committed or
> counted as part of that BUILD candidate. When auditing the runner BUILD,
> exclude this path and its companion paper replay. It authorizes nothing,
> mutates no governed surface and consumes no approval.

- Date: `2026-08-04`
- Author: Claude (adversarial self-review of own prior analysis)
- Recipient: Codex (independent reviewer, pre-implementation)
- Artifact class: `ANALYSIS / NON-AUTHORITATIVE / ADVERSARIAL SELF-REVIEW`
- Status: `DRAFT_FOR_CODEX_REVIEW`
- Companion: `CVF_GOVERNANCE_LATENCY_L0_5_PAPER_REPLAY_2026-08-04.md`
- Calls: `0 provider / 0 network / 0 remote-ingest`
- Governed paths mutated: `NONE`

## 0. Mục đích và cách đọc

Tài liệu companion kết luận "proceed to L1" với tỷ lệ 14/15 (93%). Tài liệu này
**tấn công chính kết luận đó**.

Codex không nên đọc đây như một bản rút lui. Nhiều đề xuất vẫn đứng vững. Mục
đích là tách rõ:

- phần nào có **bằng chứng repository** đứng sau (đáng tin),
- phần nào là **suy luận của Claude** (cần Codex kiểm chứng độc lập),
- phần nào Claude **có xung đột lợi ích cấu trúc** (cần bên thứ ba phán xét).

Quy ước độ tin cậy dùng xuyên suốt:

| Mức | Nghĩa |
|---|---|
| `EVIDENCED` | có artifact committed trong repo chứng minh trực tiếp |
| `INFERRED` | suy luận hợp lý từ bằng chứng, chưa được kiểm chứng độc lập |
| `SPECULATIVE` | phán đoán thiết kế, không có bằng chứng trong repo |
| `CONFLICTED` | Claude không phải bên trung lập để đánh giá |

---

## 1. Lỗ hổng phương pháp nghiêm trọng nhất: Claude tự chấm bài của chính mình

**Mức: `CONFLICTED` — đây là phản biện quan trọng nhất trong tài liệu này.**

Bảng replay 14/15 được lập bởi cùng tác nhân (Claude) vừa mới:

1. viết implementation của governed plan runner (8 file, WS-3 prototype);
2. đánh giá roadmap đề xuất WS-3;
3. chấm điểm xem WS-3 sẽ ngăn được bao nhiêu incident.

Đây là xung đột cấu trúc, không phải cáo buộc thiên vị chủ quan. Cột "Where it
fails in new model" phần lớn trỏ tới WS-3 — chính thứ Claude vừa xây. Một tác
nhân vừa đầu tư công sức vào một giải pháp sẽ có xu hướng thấy giải pháp đó
hiệu quả.

**Kiểm chứng cụ thể Codex nên chạy:** lấy 15 incident, tự phân loại **mù**
(không đọc bảng của Claude), rồi so sánh. Nếu Codex ra 11/15 hoặc 12/15, khác
biệt nằm ở đâu — ở bằng chứng hay ở diễn giải? Con số 93% chỉ nên tin sau khi
có hai lần phân loại độc lập khớp nhau.

**Claude không nên là bên chốt con số này.** Đề nghị Codex coi 14/15 là
*giả thuyết cần kiểm chứng*, không phải kết quả.

---

## 2. Bảng replay dùng định nghĩa "R2 survives" quá dễ dãi

**Mức: `INFERRED`, và tôi cho rằng phản biện này đúng.**

Bảng chấm "Yes" cho một incident nếu mô hình mới **phát hiện** được lỗi trước
admission. Nhưng đó không phải câu hỏi đúng. Câu hỏi đúng là: **có phải mọi
phát hiện pre-admission đều không tiêu tốn approval?**

Xét incident #9 (outer timeout 120s < budget, A22→A23). Runner sẽ fail-fast ở
`requiredOuterTimeoutSeconds`. Nhưng:

- Ai sửa timeout? Nếu cần sửa Work Order (nơi ghi budget), thì phải có amendment
  → vẫn tốn một chu trình, chỉ là rẻ hơn.
- Nếu agent tự sửa được trong repair envelope (WS-5), thì WS-5 đang gánh nhiều
  hơn những gì §WS-5 mô tả.

Tương tự #1, #4, #5: phát hiện được selector/path sai, nhưng **plan vẫn sai** và
phải được sửa lại. Nếu plan là artifact đã-review, sửa nó cần review lại.

**Hệ quả:** 14/15 đo "defect caught pre-admission", không đo "governance cycle
avoided". Hai con số này khác nhau, và con số thứ hai mới là thứ WS-7 cần.

**Đề nghị:** Codex tách bảng thành hai cột:
- `R2 unconsumed?` (approval sống sót)
- `Cycle avoided?` (không cần amendment mới)

Tôi dự đoán cột thứ hai sẽ thấp hơn đáng kể — có thể 8-10/15. Đó vẫn là cải
thiện lớn, nhưng là con số trung thực hơn để đặt SLO.

---

## 3. Phát hiện cascade: đúng về hiện tượng, nhưng suy luận nhân quả yếu

**Mức: `EVIDENCED` cho dữ liệu, `INFERRED` cho kết luận.**

Dữ liệu vững: A19→A20→A22→A23→A24→A26 đều có LF/CRLF trong trigger section.
Đây là fact đọc được từ repository.

Nhưng kết luận "một root cause đốt 6 R2" có ba điểm yếu:

**3.1. Gán nhân quả hồi cứu.** Tôi đọc 6 amendment, thấy LF/CRLF, rồi gán chung
một root cause. Nhưng A24 là lỗi trong test code (`read_text`/`write_text`),
A26 là lỗi trong patch engine, A20 là lỗi generator output. Ba cơ chế khác nhau
cùng biểu hiện qua newline. Gộp thành "một root cause" có thể là đơn giản hóa
quá mức — và nếu đúng là ba nguyên nhân riêng, thì "sửa một chỗ tiết kiệm 6 chu
trình" là sai.

**3.2. Giả định phản thực chưa kiểm chứng.** Tôi ngầm giả định: nếu chặn được
A19 thì A20-A26 không xảy ra. Nhưng có thể mỗi amendment lại bộc lộ một lỗi
*mới* độc lập, vốn bị che khuất bởi lỗi trước. Trong trường hợp đó, chặn A19
chỉ khiến A20 xảy ra sớm hơn, không loại bỏ nó.

**3.3. Đây có thể là learning curve bình thường.** P3-A là tranche đầu tiên
chạy ở quy mô này trên Windows. Một phần trong 28 amendment có thể là chi phí
một lần của việc khám phá môi trường, không phải lỗi hệ thống lặp lại. Tranche
thứ hai có thể tự nhiên rẻ hơn mà không cần bất kỳ thay đổi core nào.

**Đây là phản biện mạnh nhất về mặt định lượng:** nếu (3.3) đúng, roadmap đang
xây một chương trình 9-tranche để giải quyết một chi phí đang tự giảm.

**Kiểm chứng Codex nên làm:** so sánh mật độ amendment giữa P2C/P2D (tranche
trước) và P3-A. Nếu P3-A không cao bất thường, giả thuyết "governance
amplification hệ thống" yếu đi đáng kể. Repository có đủ dữ liệu để trả lời:
`ls docs/work_orders/ | grep AMENDMENT` theo từng phase.

---

## 4. Đề xuất "byte-discipline cho test code" — có thể sai địa chỉ

**Mức: `SPECULATIVE`. Tôi rút lại một phần đề xuất này.**

Tôi đề xuất thêm static check bắt test code dùng byte-mode I/O. Ba vấn đề:

**4.1. Phạm vi quá rộng.** Rất nhiều test dùng `read_text()` hợp pháp. Một
static check phân biệt "snapshot/restore" với "đọc thường" sẽ hoặc quá nhiễu
(false positive cao — chính thứ WS-7 muốn giảm), hoặc quá hẹp (dễ né).

**4.2. Có giải pháp rẻ hơn nhiều.** `.gitattributes` với `* text=auto eol=lf`
hoặc `core.autocrlf=false` giải quyết phần lớn lớp lỗi này ở tầng repo, không
cần bất kỳ control governance nào. Tôi đã đề xuất giải pháp phức tạp trước khi
kiểm tra giải pháp đơn giản.

**4.3. Tôi chưa kiểm tra cấu hình hiện tại.** Không rõ repo đã có
`.gitattributes` chưa. Đề xuất một control mới mà chưa kiểm tra control sẵn có
là lỗi phương pháp.

**Đề nghị Codex:** kiểm tra `.gitattributes` và `git config core.autocrlf`
trước. Nếu chưa cấu hình, đó là fix một dòng thay cho một workstream.

---

## 5. Đề xuất "fail-safe: unknown state ⇒ CONSUMED" — có tác dụng phụ nguy hiểm

**Mức: `SPECULATIVE`. Tôi giữ đề xuất nhưng phải nêu mặt trái.**

Tôi đề xuất: khi trạng thái admission không xác định, mặc định coi là đã
consumed (an toàn hơn double-use).

Mặt trái chưa nêu ở lần trước: điều này tạo **incentive ngược**. Nếu mọi trạng
thái mơ hồ đều đốt approval, thì:

- áp lực dồn vào việc làm cho trạng thái *luôn* xác định — tốt;
- nhưng cũng tạo động cơ phân loại rộng "chắc là chưa admitted" để cứu
  approval — xấu, và khó phát hiện.

Nghiêm trọng hơn: nó **mâu thuẫn với chính mục tiêu roadmap**. Roadmap tồn tại
để giảm việc đốt approval oan. Một fail-safe đốt approval mỗi khi mơ hồ sẽ tái
tạo đúng vấn đề cũ ở một chỗ khác, nếu vùng mơ hồ không nhỏ.

**Đề nghị:** giữ fail-safe, nhưng bắt buộc kèm metric "unknown-state rate".
Nếu tỷ lệ này >5%, đó là lỗi thiết kế state machine chứ không phải chuyện vận
hành bình thường.

---

## 6. Đề xuất WS-11 (machine-readable authority state) — chưa kiểm tra trùng lặp

**Mức: `SPECULATIVE`, và có thể đã tồn tại.**

Tôi đề xuất một file trạng thái authority sinh tự động. Nhưng repo **đã có**:

- `SESSION/ACTIVE_SESSION_STATE.json`
- `CVF_SESSION/ACTIVE_SESSION_STATE.json`
- `scripts/check_session_state.py`

Tôi chưa đọc kỹ nội dung hai file này trước khi đề xuất. Nếu chúng đã chứa
phần lớn các trường tôi liệt kê (`current_lane`, `allowed_paths`,
`approval_state`), thì WS-11 nên là **mở rộng cái đang có**, không phải
workstream mới.

**Đề nghị Codex:** đọc `SESSION/ACTIVE_SESSION_STATE.json` và đối chiếu với
danh sách trường tôi đề xuất. Có khả năng cao đây là gap nhỏ, không phải
workstream.

---

## 7. Những đề xuất tôi vẫn giữ nguyên (và lý do)

Không phải mọi thứ đều nên rút lại. Ba đề xuất sau có bằng chứng vững:

**7.1. `EVIDENCED` — Restate §2 thành "15 classes / 28 cycles".**
Đếm được trực tiếp: `ls docs/work_orders/ | grep -c "P3A_REFINERY.*AMENDMENT"`
trả về 28. Đây là fact, không phải diễn giải. §2 hiện đang *dưới*-báo cáo chi
phí thực.

**7.2. `EVIDENCED` — Incident #15 (`uv`) chứng minh capability > prompt.**
Bằng chứng nằm trong `GOVERNED_PLAN_RUNNER_AUTHORIZATION_REVIEW.md` dòng 23-27
và 41-46: reviewer đọc ranh giới zero-network, vẫn chạy `uv run`, tạo `.venv`,
tải `pydantic-core`, cài 26 package. Lệnh cấm bằng prompt đã thất bại đúng một
lần có ghi nhận. WS-2 có nền tảng thực nghiệm vững nhất trong toàn roadmap.

**7.3. `EVIDENCED` — Mâu thuẫn định nghĩa admission (§5.1 vs WS-1).**
Đây là mâu thuẫn nội tại đọc được từ chính văn bản roadmap: §5.1 nói consumption
theo "successful mutation", WS-1 nói "external dispatch consumes before response
handling". Một dispatch gửi đi rồi timeout thì không "successful" — hai điều
khoản không thể cùng đúng. Phải giải quyết trước SPEC.

---

## 8. Câu hỏi tôi không trả lời được — Codex nên quyết

Bốn câu hỏi vượt thẩm quyền và vượt khả năng đánh giá của tôi:

**8.1. Chi phí cơ hội của 9 tranche.** Tôi không biết roadmap này cạnh tranh
với việc gì. Nếu P3-B/P3-C đang chờ, 9 tranche core có thể là lựa chọn sai dù
phân tích kỹ thuật đúng. Đây là quyết định sản phẩm, không phải kỹ thuật.

**8.2. Liệu vấn đề có tự biến mất.** Xem §3.3. Nếu phần lớn 28 amendment là chi
phí học một lần cho môi trường Windows, tranche sau sẽ rẻ hơn tự nhiên. Cần dữ
liệu từ tranche kế tiếp để biết — mà dữ liệu đó chưa tồn tại.

**8.3. Ai chịu chi phí governance của chính roadmap.** Roadmap yêu cầu mọi
tranche core dùng control chain đầy đủ. 9 tranche × chi phí quan sát được ở
P3-A là con số rất lớn. Nếu áp fitness function của §5.7 lên chính chương
trình, nó có qua được không? Tôi nghĩ đây là câu hỏi công bằng và chưa ai trả
lời.

**8.4. `CONFLICTED` — Runner có nên là upstream implementation không.**
Tôi vừa viết nó. Tôi không nên là bên đánh giá liệu nó xứng đáng được
generalize lên core hay nên bị thay thế. Roadmap §WS-3 đã đúng khi nói "learning
prototype, not automatically the upstream implementation" — giữ nguyên câu đó.

---

## 9. Tóm tắt cho Codex

| # | Nội dung | Mức | Hành động đề nghị |
|---|---|---|---|
| 1 | 14/15 do bên có xung đột lợi ích chấm | `CONFLICTED` | Codex phân loại mù, so sánh |
| 2 | "R2 survives" ≠ "cycle avoided" | `INFERRED` | Tách hai cột, dự kiến 8-10/15 |
| 3 | Cascade 6-deep có thể là 3 nguyên nhân riêng | `INFERRED` | So mật độ amendment P2C/P2D vs P3-A |
| 4 | Byte-discipline check có thể thừa | `SPECULATIVE` | Kiểm `.gitattributes` trước |
| 5 | Fail-safe CONSUMED có incentive ngược | `SPECULATIVE` | Giữ, kèm unknown-state metric |
| 6 | WS-11 có thể đã tồn tại | `SPECULATIVE` | Đọc `ACTIVE_SESSION_STATE.json` |
| 7 | 28 cycles / `uv` / mâu thuẫn admission | `EVIDENCED` | Giữ nguyên, đủ căn cứ |
| 8 | Chi phí cơ hội, self-cost, adoption | — | Ngoài thẩm quyền Claude |

## 10. Kết luận

Khuyến nghị trước đó là "proceed to L1". Sau phản biện, tôi điều chỉnh thành:

> **Proceed to L0 (evidence packet) — nhưng không nhảy sang L1 trước khi Codex
> kiểm chứng độc lập §1, §2 và §3.**

Ba điều cần làm rõ trước khi cam kết nguồn lực:

1. phân loại mù độc lập 15 incident (giải xung đột §1);
2. đếm lại theo "cycle avoided" thay vì "defect caught" (§2);
3. đối chiếu mật độ amendment giữa các phase để loại giả thuyết learning-curve (§3.3).

Cả ba đều rẻ — đều là đọc repository, không cần code, không cần core edit.
Nếu cả ba đều xác nhận, cơ sở cho L1 sẽ vững hơn nhiều so với hiện tại.

Nếu (3) cho thấy P3-A không bất thường so với P2C/P2D, tôi cho rằng nên **hoãn**
toàn bộ chương trình và chỉ triển khai WS-2 (capability enforcement) — vốn có
bằng chứng độc lập mạnh nhất và không phụ thuộc vào giả thuyết amplification.
