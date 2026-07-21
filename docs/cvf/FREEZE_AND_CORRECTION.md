# Freeze and Correction

Freeze ngăn silent overwrite. Sau khi record/ca được freeze, mọi thay đổi phải
đi qua một **correction record** có before/after, reason, actor, version và
approval.

## Freeze policy

`freeze-policy.yaml`:

```text
freeze_requires: [shift_closed, report_approved, open_handover_items_linked]
post_freeze_mutation: correction_record_only
silent_overwrite: prohibited
```

## Correction — golden vertical thứ hai

`CorrectionService.correct_event` (`apps/workspace-api/.../application/correction_service.py`):

- Chỉ record đã là official fact (`CONFIRMED`/`CORRECTED`/`FROZEN`) mới được
  correct; `PROPOSED` phải đi qua confirm bình thường.
- Reason bắt buộc (không rỗng).
- Áp cùng approval quorum theo risk của record (tái dùng
  `assert_approval_satisfied`).
- Record `FROZEN` **không bị silent-overwrite**: giữ nguyên `FROZEN`, tạo
  correction record + bump version. Record `CONFIRMED` chuyển sang `CORRECTED`.
- Correction là append-only trong ledger (`add_correction`); audit ghi
  before/after.

Enforce state: `domain/lifecycle.py · assert_transition` (FROZEN là terminal).
Xem [CVF_CONTROL_MAPPING.md](CVF_CONTROL_MAPPING.md).
