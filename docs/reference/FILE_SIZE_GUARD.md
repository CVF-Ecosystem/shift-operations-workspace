# File Size Guard

Áp quy tắc kiểm soát kích thước file của CVF (tương đương GC-023) cho workspace
này, để file không phình to âm thầm thành nợ kỹ thuật. Đây là guard **cứng**,
enforce qua `make validate` + pre-commit + CI.

CVF-FILE-SPLIT-GUARD-HARDENING (2026-07-26) siết ngưỡng Python và mở rộng
sang JavaScript/JSX, đồng thời khoá exception registry khỏi mọi suffix
executable — xem `docs/decisions/ADR_2026-07-26_CVF_FILE_SPLIT_GUARD_HARDENING.md`
và `docs/specs/CVF_FILE_SPLIT_GUARD_HARDENING_SPEC.md` cho quyết định đầy đủ.

## Ngưỡng (line count)

| Loại file | warn | hard | Ghi chú |
|-----------|-----:|-----:|---------|
| `.py` | 250 | 300 | Executable. Vượt hard = build fail; tách module. Không được dùng exception registry. |
| `.ts` / `.tsx` / `.js` / `.jsx` | 160 | 200 | Executable. Cùng quy tắc như `.py`. |
| `.md` | 400 | 600 | Doc dài hơn được; front door/handoff phình thì rotate. Có thể dùng exception registry. |

- **warn**: cảnh báo, không fail — tín hiệu nên tách sớm.
- **hard**: fail cổng cho file MỚI/không có trong debt baseline. Executable
  vượt hard chỉ được tồn tại qua debt baseline digest-bound (xem dưới); không
  có exception nào áp dụng cho executable.

Không tính: file rỗng, `__init__.py`, và mọi thứ trong `.venv/`,
`node_modules/`, `.pytest_cache/`, `dist/`, `build/`, `.git/`.

Line count xác định (deterministic): CRLF được universal-newline-normalize về
LF khi đọc; một newline cuối file không cộng thêm dòng ảo; file rỗng đếm là 0
dòng.

## Legacy debt ratchet (executable)

`docs/reference/FILE_SPLIT_DEBT_BASELINE.json`. Một file executable pre-existing
vượt hard limit chỉ được phép tồn tại khi có đúng một mục trong baseline này,
khớp CHÍNH XÁC:

- `path` (repo-relative, normalized, không traversal/absolute);
- `sha256` của nội dung file hiện tại;
- `lineCount` hiện tại (đếm bằng cùng thuật toán deterministic ở trên);
- `hardLimit` đúng bằng chính sách hiện hành cho suffix đó;
- `reason` + `requiredSplit` (bounded, không phải lời xin lỗi chung chung).

Baseline **fail-closed**: thiếu file, JSON hỏng, path trùng, path ngoài repo,
path không phải file tracked, `hardLimit` sai chính sách, `sha256`/`lineCount`
lệch nội dung thật, hoặc file đã compliant (≤ hard limit) mà vẫn còn mục trong
baseline (stale) — tất cả đều FAIL cho tới khi sửa/xoá mục đó. Sửa nội dung
file trong baseline bắt buộc phải tách xuống dưới hard limit trong cùng
changed set — không có "sửa cùng số dòng" nào bypass được vì digest phải khớp.

Baseline **không phải cơ chế exception chung** — thêm/sửa một mục là một thay
đổi chính sách có kiểm soát (governed policy change), luôn hiện trong Git
review.

## Khi một file executable chạm ngưỡng

1. Kiểm line count hiện tại và ngưỡng của loại đó.
2. Nếu thêm sẽ vượt **hard**: tách module / tạo file mới chuyên trách, **không**
   nén statement hay xoá assertion chỉ để lọt guard.
3. Không được thêm executable vào exception registry — registry chỉ áp dụng
   cho suffix non-executable (hiện tại chỉ `.md`).
4. Front door / handoff Markdown khi gần ngưỡng: mở pointer/successor/archive
   gọn (giống GC-023 CVF root), không để một file phình vô hạn.

## Exception registry (chỉ non-executable)

`docs/reference/FILE_SIZE_EXCEPTION_REGISTRY.json`. Mỗi mục:
`{ "path", "approvedMaxLines", "reason", "requiredFollowup" }`. Checker cho
phép file vượt hard tới `approvedMaxLines`; vượt cả mức đó vẫn fail. Bất kỳ
mục nào trỏ tới suffix executable đều FAIL ngay khi parse (R6/R11). Path
thiếu, JSON hỏng, path trùng, path ngoài repo, `approvedMaxLines` không phải
số nguyên dương, hoặc target không tồn tại — tất cả FAIL.

## Enforce

- Checker: `scripts/check_file_size.py` (fail-closed, đọc cả hai registry).
- Cổng: gài trong `scripts/testing/validate_repository.py`,
  `.githooks/pre-commit`, `.github/workflows/ci.yml`.
- Chạy thủ công: `python scripts/check_file_size.py` (hoặc
  `python scripts/check_file_size.py --warn` để thấy thêm cảnh báo — `--warn`
  không bao giờ làm yếu failure). CLI argument không xác định luôn FAIL.
