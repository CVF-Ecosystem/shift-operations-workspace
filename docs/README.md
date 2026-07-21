# Documentation

Canonical docs được tổ chức theo foundation, architecture, domain, CVF, AI, channels, workflows, security, operations, implementation và decisions.

## Bắt đầu từ đâu

- **Cấu trúc dự án (đọc trước):** [catalog/MODULE_CATALOG.md](catalog/MODULE_CATALOG.md) —
  module nào đã có code / contract / stub, kèm số liệu sinh tự động.
  Machine source-of-truth: [catalog/MODULE_REGISTRY.json](catalog/MODULE_REGISTRY.json).
- **CVF control → điểm enforce:** [cvf/CVF_CONTROL_MAPPING.md](cvf/CVF_CONTROL_MAPPING.md).
- **Cập nhật catalog:** sửa `MODULE_REGISTRY.json` rồi chạy
  `python scripts/generate_catalog.py --write`.
