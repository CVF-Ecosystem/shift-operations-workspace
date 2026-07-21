# CVF Control Mapping

Ánh xạ từng CVF `required_control` (khai báo trong
`packages/cvf-application-profile/profile.yaml`) tới **điểm thực thi bằng code**,
kèm trạng thái thật.

Trạng thái:

- **enforced** — có code chạy tại runtime + có test chặn khi vi phạm.
- **profile-only** — policy đã có trong YAML nhưng chưa có code đọc/enforce.
- **planned** — chưa có cả policy lẫn code.

Golden verticals hiện có (đều dùng chung các gate `cvf-runtime`, không fork):

1. **Operational Event → confirm** — `EventService.confirm`
2. **Operational Event → correct** (post-freeze correction record) — `CorrectionService.correct_event`

Các domain khác (Message, Task, Customer Request, Incident, Report) sẽ nhân bản
đúng chuỗi này.

## Bảng ánh xạ

| CVF control | Trạng thái | Enforce ở đâu (file · symbol) | Policy nguồn | Test |
|---|---|---|---|---|
| identity | enforced | `dependencies.py · get_principal` → `cvf_runtime/identity.py · Principal` | — (header `X-User-Id`/`X-User-Role`) | `tests/cvf/test_gates_unit.py` (identity) |
| permission | enforced | `cvf_runtime/permission.py · require_action`; gọi tại `events/router.py` và `application/services.py` | `_ACTION_MIN_ROLE` (code) | `test_permission_*`, `test_operator_confirm_denied_by_permission` |
| domain_lock | enforced | `cvf_runtime/domain_lock.py · assert_event_type_in_scope`; gọi tại `events/router.py · create_event` | `cvf-application-profile/domain-lock.yaml` | `test_domain_lock_*` |
| data_scope | enforced | `cvf_runtime/data_scope.py · assert_placement_allowed` (external_ai rule) | `cvf-application-profile/data-policy.yaml` | `test_restricted_local_only`, `test_confidential_blocks_external` |
| risk | enforced | `cvf_runtime/risk.py · requirement_for` | `risk-classes.yaml`, `approval-policy.yaml`, `evidence-policy.yaml` | `test_requirement_reads_profile` |
| approval | enforced | `cvf_runtime/approval.py · assert_approval_satisfied` | `approval-policy.yaml` | `test_r3_*`, `test_r4_escalation_board_roles` |
| evidence | enforced | `cvf_runtime/evidence.py · assert_evidence_sufficient` | `evidence-policy.yaml` | `test_evidence_*`, `test_r2_denied_when_evidence_missing` |
| audit | enforced | `cvf_runtime/audit.py · AuditLog.record`; ghi tại `EventService.confirm` và `CorrectionService.correct_event` | — (append-only) | `test_r3_full_chain_confirms_and_audits`, `test_confirmed_event_corrected_with_record_and_audit` |
| cost | enforced (AI-gated) | `cvf_runtime/budget.py · assert_within_budget` (token limit + daily/monthly cap) | `cvf-application-profile/cost-policy.yaml` | `test_token_overflow_denied`, `test_daily_cap_falls_back_to_rules` |
| refusal | enforced | `cvf_runtime/errors.py · CvfDenied` → HTTP map tại `events/router.py` | `cvf-application-profile/refusal-policy.yaml` | mọi test `CvfDenied` |
| termination | enforced (AI-gated) | `cvf_runtime/termination.py · should_terminate` / `assert_not_terminated` (timeout, token limit, repeated failures, kill switch) | `cvf-application-profile/termination-policy.yaml` | `test_timeout_terminates`, `test_kill_switch_terminates` |
| freeze | enforced | `domain/lifecycle.py · assert_transition` (FROZEN không có transition ra); `repository.py` chặn ghi vào shift FROZEN; `CorrectionService` chỉ cho correct record CONFIRMED/CORRECTED/FROZEN và không silent-overwrite record FROZEN | `cvf-application-profile/freeze-policy.yaml` | `test_confirm_blocked_on_frozen_shift`, `test_frozen_event_not_silently_overwritten`, `tests/integration/test_freeze.py` |

## Thứ tự chain trong `EventService.confirm`

```text
identity        (dependency: get_principal)
   ↓
permission      (require_action "event.confirm")
   ↓
freeze/state    (assert_transition: PROPOSED → CONFIRMED)
   ↓
evidence        (assert_evidence_sufficient)
   ↓
approval        (assert_approval_satisfied: quorum + distinct principals)
   ↓
[mutation]      (state = CONFIRMED, version += 1)
   ↓
audit           (append-only AuditRecord: who/action/before→after/chain)
```

## Trạng thái: 12/12 control đã có gate + test

Tất cả `required_controls` giờ có code enforce trong `cvf_runtime` và test chặn
khi vi phạm. `cost` và `termination` được đánh dấu **AI-gated**: logic chạy và
test được ngay, nhưng chỉ thành load-bearing khi một AI mode ngoài `NO_AI` được
bật (ở `NO_AI` không có provider call nào để giới hạn/ngắt).

## Khoảng trống còn lại (chiều sâu / vận hành thật)

- **Persistence**: audit + correction ghi qua `Ledger.append_audit` /
  `add_correction`. `SqlLedger` (Postgres append-only) đã có nhưng mới test
  structural conformance, **chưa** test round-trip trên DB thật (cần
  `docker compose up postgres`).
- **AI wiring**: `data_scope`, `budget`, `termination` gate đã sẵn nhưng chưa có
  `ai-gateway`/`ai-providers` gọi chúng (còn contract-only/stub).
- **Identity**: header-based principal, chưa phải xác thực JWT/session. Nâng cấp
  nguồn identity không đổi các gate phía sau `Principal`.
