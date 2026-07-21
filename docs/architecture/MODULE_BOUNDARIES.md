# Module Boundaries

Hướng phụ thuộc (dependency direction) được khóa để tránh coupling sai. Bản đồ
module đầy đủ + trạng thái: [`../catalog/MODULE_CATALOG.md`](../catalog/MODULE_CATALOG.md).

## Luật ranh giới

1. **Domain modules không import provider implementations.** Business logic phụ
   thuộc contract/interface, không phụ thuộc LLM/channel/storage cụ thể.
2. **Ứng dụng phụ thuộc một chiều xuống ledger**, không ngược lại:
   `workspace-api` → `operations-ledger` (Protocol). `operations-ledger` không
   import `workspace-api`.
3. **Integration Edge không ghi confirmed truth.** Nó chỉ nhận, verify, dedupe,
   giữ raw payload; việc xác nhận sự thật thuộc về core qua CVF chain.
4. **Report engine chỉ đọc** confirmed/corrected/frozen records, không tạo fact.
5. **CVF gate ở backend, không ở frontend** (xem
   [`FRONTEND_BACKEND_BOUNDARY.md`](FRONTEND_BACKEND_BOUNDARY.md) luật #2).
6. **Provider chỉ cung cấp capability** qua adapter contract; không sở hữu
   workflow.

## Enforce

Hướng phụ thuộc giữa module được liệt kê trong `depends_on` của
`docs/catalog/MODULE_REGISTRY.json`; `scripts/generate_catalog.py --check` xác
minh mọi `depends_on` trỏ tới module tồn tại.
