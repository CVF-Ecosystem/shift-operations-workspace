# P5-A2 — Audit G04–G06 và đề xuất dùng dữ liệu giả lập

Ngày: 2026-10-25. Trạng thái: DESIGN REVIEW_PASS_BOUNDED; không cấp BUILD.
Nguồn dự án: `552612603bb35fd97a9f688787948542dc59e86e`.
Risk R2; Root ORCHESTRATOR/SPEC_AUTHOR; operator nghiệm thu giá trị nghiệp vụ.

## Kết luận để quyết định

**Có thể tiếp tục phát triển bằng synthetic data. Chưa cần yêu cầu dữ liệu vận hành thật ở bước này.**
Project đã dùng Report/Incident giả lập có schema, version và digest thật trong
`tests/unit/proactive_helpers.py`; phần history/numeric đã được review và commit.
Điểm còn thiếu là nối phần đó với repository/query thật và xác định rõ cohort,
snapshot và completeness. Một database chứa dữ liệu giả lập có thể giúp kiểm tra
các cơ chế này; thay toàn bộ repository bằng kết quả hardcode thì không đủ.

Synthetic data là dữ liệu kiểm thử. Mock provider là thay lời gọi AI bằng kết quả
giả. Bằng chứng về thuật toán/query trên fixture không phải bằng chứng CVF đã
kiểm soát AI. AGENTS.md vẫn yêu cầu real provider request/response cho claim CVF
governance; mọi live/key/model/CSV action hiện tiếp tục được hoãn.

## Product Milestone Binding

Milestone: P5-A2, Phase 5 của `docs/implementation/EXECUTION_ROADMAP.md` tại nguồn
trên. User outcome vẫn là ứng dụng scoped có scheduled signals/forecast, lineage,
freshness/history và human approval cho đúng run/version/source trước durable
recommendation. Full acceptance, 14 gap và owner/destination chuẩn nằm trong
`P5A2_PROACTIVE_REPORTING_INTAKE_DESIGN_2026-10-24.md` và SPEC đã được chấp nhận.

Đối chiếu hiện tại: G01/A7 và G02 operational RAG BLOCKED; G03–G05/G08–G10/G13
chỉ có pure portions được chấp nhận tại `9c72de4`/`5526126`; phần operational
của các gap đó còn OPEN/UNKNOWN. G06 query/auth/completeness, G07 scheduler,
G11 API/UI và G12 approval OPEN; G14 live PARKED. Bảng đủ G01–G14 cùng evidence,
owner và concrete destination đã được reconcile tại
`P5A2_SCOPED_HISTORY_SOURCE_VERIFICATION_2026-10-25.md#product-milestone-binding`.
Các trạng thái này không thay đổi vì đề xuất được review.

Assignment này chỉ audit nguồn và đề xuất cách kiểm chứng G04–G06 bằng fixture;
output là hai decision records và review, cộng các projection continuity/status.
Không sửa source/test/matrix/policy/provider; không tạo database hay chạy thử
forecast mới. Root accountable; Sol backend/contracts, Luna UI, independent
reviewer đánh giá packet; operator final business acceptance. P5-B/C/D giữ owner
và đích đến tại các mục roadmap tương ứng. Phase 5 vẫn 0/5.

## Audit: đã có gì, thiếu gì

Chi tiết 20 source path, SHA-256 và line evidence được ghi trong source-verification
record. Đây là audit có giới hạn, không phải kết luận đã đọc toàn repository.

| Finding | Bằng chứng nguồn | Hệ quả / việc cần làm |
|---|---|---|
| Đã có nền tảng dùng lại | Report versions, immutable snapshot/digest, assignment, JWT và pure history validator đã tồn tại | Dùng các owner này; không viết engine hoặc kho truth thứ hai |
| F01: cohort chưa được định nghĩa đủ | Window theo Report cutoff nhưng reportless shift không có cutoff | SPEC mới phải định nghĩa eligible shifts độc lập với việc đã có Report, rồi kiểm tra thiếu Report |
| F02: limit áp quá muộn | SQL shift/report listing dùng `.all()`; API kiểm tra limit sau khi lấy dữ liệu | Count/bound ở query trước khi dựng Report/body; không lấy 500 dòng đầu rồi nói đầy đủ |
| F03: snapshot chưa thống nhất | Shift listing không nhận `unit`; mở connection riêng; assignment được đọc từng lần | Cần cùng một read snapshot và contract kiểm tra lại access lúc sử dụng |
| F04: timestamp SQLite | `DateTime(timezone=True)` không tự chứng minh timestamp trả về có offset | Giữ refusal với naive time; không tự gắn UTC hoặc Asia/Saigon |
| F05: retention chưa có authority | `complete`/`retention_complete` trong pure input là caller assertions | Fixture có thể chứng minh chính dataset của nó đầy đủ; chưa có quyền suy ra coverage dữ liệu thật |
| F06: integration chưa có proof | Pure tests chưa gọi source adapter/query scoped xuyên backend | Cần tranche query/adapter riêng với actual backend và ground truth độc lập |

Root cũng kiểm tra các excerpt của bốn test surfaces: proactive helper,
supplied-contract integration, Report ledger parity và assignment route tests.
Chúng là điểm tái sử dụng harness; không được coi là P5-A2 adapter đã tồn tại.
Không chạy lại tests để tạo thêm số lượng bằng chứng cho audit này.

## Mock data giúp chứng minh đến đâu?

| Mục tiêu | Cách dùng dữ liệu giả lập | Claim được phép sau evidence phù hợp |
|---|---|---|
| Numeric và as-of selection | Report/Incident hợp lệ, clock/IDs/version cố định, expected values độc lập | Đúng các tình huống số học/chronology đã dựng; phần này đã có accepted evidence |
| Query, version và boundedness | Seed fixture vào InMemoryLedger/SqlLedger thật, chạy adapter/query thật | Đúng manifest/count/window/version/cap trên dataset được pin |
| SQL time handling | Round-trip timestamp thật qua backend đang kiểm tra | Backend giữ offset đúng hoặc từ chối ambiguity đúng; không giả định kết quả |
| Application access mechanics | Fixture actors/assignments và auth harness thật; kiểm tra missing/revoked/foreign scope | Bằng chứng cơ chế application trong boundary kiểm thử; chưa là live AI-governance proof |
| CVF kiểm soát AI | Dữ liệu PUBLIC synthetic có thể là payload, nhưng phải qua provider API thật | Chỉ claim hẹp được admitted/reviewed từ request/response thật; hiện chưa thực thi |
| Forecast dùng cho vận hành | Cần lịch sử vận hành có owner, coverage/retention và evaluation phù hợp | Synthetic data chưa chứng minh độ chính xác hoặc ích lợi nghiệp vụ thực tế |

## Đề xuất: synthetic trước, source contract rõ trước BUILD

**Ưu tiên 1 — scoped-history SPEC/Work Order.** Giữ numeric policy đã chấp nhận.
Định nghĩa query/cohort policy riêng có version, linked invariant family và
native Ledger/Report/auth ownership. Default để review: cohort fixture gồm các
shift đang được actor ACTIVE-assigned có `ends_at` trong `[start,end)`, không
lọc theo trạng thái mutable hoặc việc có Report; Report cutoff vẫn tuân SPEC.
Đây là đề xuất cho SPEC tiếp theo, chưa là thay đổi cohort vận hành được nhận.

Phải tách hai authority: manifest fixture do harness sở hữu cho phép chứng minh
coverage **của fixture**; runtime production chỉ được nhận coverage/retention từ
owner có thẩm quyền được định nghĩa và kiểm chứng. Không có owner/proof phù hợp
thì trả incomplete. Dữ liệu thật chưa xác nhận không chặn thiết kế/test fixture,
nhưng vẫn chặn claim operational completeness và acceptance phụ thuộc vào nó.

**Ưu tiên 2 — tranche adapter/query trên synthetic data.** Sau SPEC/WO được review,
reuse backend thật thay vì mock query trả sẵn. Dùng fixed clock, deterministic IDs,
manifest ground truth tách khỏi query đang test; không đọc production/.env.

Dataset đề xuất: 36 ca, ít nhất 18 observations hợp lệ, hai actor có assignment
khác nhau; versions đến muộn, duplicate/conflicting bytes, ca thiếu Report,
revocation, timestamps lệch offset/naive, cuối window loại trừ, nguồn quá 24h,
và các case 501 shift/report-version/incident-ref trong **các fixture riêng**,
không trộn với happy path 36 ca. Counts/lineage/expected
predictions phải có oracle độc lập. Fixture labels và evidence không được
đi vào canonical operational truth hoặc làm readiness badge cho dữ liệu thật.

Acceptance của tranche: query thật khớp manifest, scope/window/version đúng,
cap trước materialization, transaction/snapshot được chứng minh hoặc từ chối,
revocation không leak, input/data không bị sửa, incomplete/time ambiguity có
outcome rõ. Với SQLite, refusal do mất timezone là kết quả hợp lệ của negative
case, **không phải positive SQL readiness**. Positive PostgreSQL proof cần
backend giữ timezone đúng và phạm vi disposable/local được WORK_ORDER cho phép;
packet audit này chưa chạy database nào.

**Ưu tiên 3 — application wiring và evidence còn lại.** Sau source boundary được
review, mới nối API/UI/scheduler theo G07/G11/G12; UI hiển thị rõ synthetic,
abstained/stale và không tự ghi khuyến nghị thành fact/action. Operational RAG,
real-provider governance và business-quality proof vẫn giữ các gate gốc.

## Quyết định đề xuất và điểm dừng

Khuyến nghị tiếp tục bằng **synthetic fixture + backend thật** cho source adapter
G04–G06, theo SPEC/WO được review. Không cần chờ import dữ liệu thật để bắt đầu
bước contract. Không thay frozen SPEC/matrix trong packet audit này.

Source-verification tranche dừng ở audited facts và đề xuất được review, không
cấp BUILD hay tạo successor support survey. Next product action là một packet
SPEC/WO scoped-history gắn G04–G06 và các acceptance trên. Tranche outcome và
product milestone position được kết luận riêng trong independent review;
P5-A/P5-A2 cùng toàn bộ operational remainder vẫn OPEN.

Review độc lập: `P5A2_SCOPED_HISTORY_AUDIT_PROPOSAL_REVIEW_2026-10-25.md` —
REVIEW_PASS_BOUNDED, không còn finding chặn. Root chấp nhận hướng DESIGN này;
SPEC/WO và BUILD vẫn là các gate tiếp theo. Actual material/continuity receipt
được ghi trong handoff scoped-history hiện hành sau normal commit hooks.
