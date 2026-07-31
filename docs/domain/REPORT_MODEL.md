# Report Model

Fixed `END_SHIFT` report type. Mỗi version là snapshot bất biến (content/cutoff/shift_id/version/created_at không đổi sau khi tạo); chỉ `status` và `is_current` được phép đổi. Lifecycle DRAFT → IN_REVIEW → APPROVED → FROZEN, chỉ chiều tiến, FROZEN là terminal. Snapshot gồm đúng sáu section (operational_events, corrections, tasks, customer_requests, incidents, handovers) cộng source_manifest và snapshot_digest SHA-256 canonical. Chỉ report P5-A rendering/export không thuộc phạm vi này.
