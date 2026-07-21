# Database

PostgreSQL là target source of truth cho Operations Ledger.

## Rules

Migrations append-only; không sửa migration đã áp dụng. Frozen records chỉ thay đổi qua correction records và version links.
