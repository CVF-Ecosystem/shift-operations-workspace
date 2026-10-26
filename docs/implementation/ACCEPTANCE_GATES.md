# Acceptance Gates

Mỗi phase có evidence pass/fail; phase sau không trở thành authoritative khi gate trước chưa đạt.

## Bắt buộc gắn giao việc với mốc sản phẩm

Áp dụng từ 2026-10-23 theo yêu cầu operator, cho mọi giao việc mới/giao lại,
kể cả giao inline, repair, governance, nghiên cứu và tiếp thu repository.
Đây là hợp đồng bắt buộc khi author/review; chưa phải một checker tự động.
Không thay thế chuỗi phase, thẩm quyền, invariant-family hay live-evidence rule.

Trước dispatch, dùng roadmap, implementation status, source và evidence review
để đối chiếu toàn bộ tiêu chí của mốc. Không suy ra đủ coverage từ số test,
số tranche đã đóng hay scaffold. Nếu mốc đang quá rộng, làm rõ acceptance của
mốc trước; không thu nhỏ mốc chỉ để đóng tranche. Không nhập scope làm hết mốc
vào một lần giao: toàn bộ khoảng thiếu phải được nhìn thấy, thực thi vẫn bounded.

## Product Milestone Binding

Mỗi assignment MUST điền đầy đủ block sau, hoặc dẫn tới một bản canonical đã
đối chiếu lại tại revision hiện hành; dẫn link trống hoặc bản stale không đủ:

- **Milestone:** ID, đường dẫn/section roadmap, revision nguồn được đánh giá.
- **User outcome:** người dùng nào làm được việc gì, qua luồng tích hợp nào;
  nêu rõ mức package, application, end-to-end hoặc production được yêu cầu.
- **Acceptance:** toàn bộ tiêu chí hoàn thành mốc, bằng chứng pass/fail cần có,
  người có quyền nghiệm thu, yêu cầu provider thật khi claim áp dụng.
- **Current truth:** phần đã được chấp nhận, evidence và giới hạn còn hiệu lực.
- **Complete gap reconciliation:** bảng dưới phải phủ mọi acceptance criterion,
  dependency tích hợp, limitation đã ghi và finding còn mở. Mỗi tiêu chí được
  đối chiếu với evidence đã đạt hoặc gap có ID. UNKNOWN là blocker cần xác minh;
  không được coi là không có việc còn thiếu.
- **This assignment:** gap ID nhận xử lý, deliverables, allowed paths, acceptance,
  owner, evidence, điều kiện dừng và phần ngoài scope.
- **Remainder:** toàn bộ gap chưa nhận, owner chịu trách nhiệm và đích đến cụ thể
  trong roadmap/backlog có thể tra cứu; pending decision phải nêu decision owner
  và điều kiện giải quyết. Không dùng “để sau” hoặc tự cấp BUILD cho successor.
- **Product return:** kết quả quan sát được sau tranche và next governed move
  hướng về mốc; việc hỗ trợ phải nêu gap bị chặn, lý do bắt buộc, giới hạn phạm vi
  và điều kiện quay về việc sản phẩm. Không đuổi nguồn thay đổi vô hạn.

| Criterion / dependency | Current evidence / limitation | Gap ID / status | In this assignment? | Owner | Concrete destination / decision |
|---|---|---|---|---|---|
| Điền mọi tiêu chí; không bỏ phần chưa biết | Artifact + revision hoặc UNKNOWN | OPEN / BLOCKED / ACCEPTED với evidence | YES / NO | Vai trò/chủ sở hữu | Roadmap ID/path hoặc quyết định cần giải quyết |

Không có gap chỉ được ghi NONE khi đã reconcile đủ tiêu chí và có evidence.
ORCHESTRATOR không dispatch/redispatch nếu thiếu block, thiếu coverage hoặc có
UNKNOWN chưa được chặn bằng một assignment xác minh hữu hạn gắn với cùng mốc.
UNKNOWN chỉ cho phép assignment xác minh hữu hạn; cấm BUILD triển khai phụ thuộc
vào coverage chưa xác minh. WORK_ORDER_AUTHOR không tự gộp hoặc nới scope để
hấp thụ toàn bộ gap.

## Nghiệm thu tranche và nghiệm thu mốc

Worker return và review phải cập nhật cùng bảng đối chiếu: gap nào thực sự đóng,
gap mới phát hiện, gap còn lại, owner/đích đến và mức đạt của user outcome.
REVIEWER độc lập theo risk contract kiểm tra coverage; không chỉ kiểm tra diff
hoặc số lượng test. Thiếu evidence, thiếu owner hoặc mất gap phải trả CHANGES_REQUIRED.

Tranche hoàn thành khi deliverables/acceptance trong scope đạt, findings đã được
xử lý theo thẩm quyền, review/gate áp dụng đạt, evidence đầy đủ, continuity và
commit hoàn tất theo AGENTS.md. Mốc chỉ hoàn thành khi toàn bộ acceptance đạt,
không còn gap bắt buộc hoặc UNKNOWN; mọi loại trừ phải thuộc boundary mốc đã
được chấp nhận, không phải âm thầm bỏ tiêu chí. CLOSED_BOUNDED của một tranche
không được dùng để tự tick DONE cho mốc hoặc phase cha.

Trước FREEZE, báo rõ hai kết luận riêng: tranche disposition và milestone
coverage/remainder. Không tuyên bố closure khi test bắt buộc đang fail.
