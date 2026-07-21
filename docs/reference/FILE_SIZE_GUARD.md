# File Size Guard

Áp quy tắc kiểm soát kích thước file của CVF (tương đương GC-023) cho workspace
này, để file không phình to âm thầm thành nợ kỹ thuật. Đây là guard **cứng**,
enforce qua `make validate` + pre-commit + CI.

## Ngưỡng (line count)

| Loại file | warn | hard | Ghi chú |
|-----------|-----:|-----:|---------|
| `.py` | 300 | 400 | Vượt hard = build fail; tách module. |
| `.ts` / `.tsx` | 200 | 300 | Frontend giữ nhỏ, dễ đọc/test. |
| `.md` | 400 | 600 | Doc dài hơn được; front door/handoff phình thì rotate. |

- **warn**: cảnh báo, không fail — tín hiệu nên tách sớm.
- **hard**: fail cổng. Không được vượt trừ khi có mục trong exception registry.

Không tính: file rỗng, `__init__.py`, và mọi thứ trong `.venv/`,
`node_modules/`, `.pytest_cache/`, `dist/`, `build/`, `.git/`.

## Khi một file chạm ngưỡng

Trước khi thêm code/test/prose vào một file gần ngưỡng:

1. Kiểm line count hiện tại và ngưỡng của loại đó.
2. Nếu thêm sẽ vượt **hard**: tách module / tạo file mới chuyên trách, **không**
   nén prose chỉ để lọt guard.
3. File sinh tự động (vd `MODULE_CATALOG.md`) hoặc file có lý do chính đáng vượt
   ngưỡng: thêm mục vào exception registry với `approvedMaxLines` + `reason` +
   `requiredFollowup`.
4. Front door / handoff khi gần ngưỡng: mở pointer/successor/archive gọn (giống
   GC-023 CVF root), không để một file phình vô hạn.

## Exception registry

`docs/reference/FILE_SIZE_EXCEPTION_REGISTRY.json`. Mỗi mục:
`{ "path", "approvedMaxLines", "reason", "requiredFollowup" }`. Checker cho phép
file vượt hard tới `approvedMaxLines`; vượt cả mức đó vẫn fail.

## Enforce

- Checker: `scripts/check_file_size.py` (fail-closed, đọc registry).
- Cổng: gài trong `scripts/testing/validate_repository.py`,
  `.githooks/pre-commit`, `.github/workflows/ci.yml`.
- Chạy thủ công: `python scripts/check_file_size.py` (hoặc `make size-check`).
