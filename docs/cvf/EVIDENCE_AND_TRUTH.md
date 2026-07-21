# Evidence and Truth

Nguyên tắc lõi: **tin nhắn gốc là evidence, không mặc nhiên là sự thật đã xác
nhận**. Một sự kiện chỉ trở thành official operational fact khi đã qua approval
và mang đủ evidence.

## Data states

```text
RAW → NORMALIZED → PROPOSED → CONFIRMED
                      ├→ REJECTED
                      └→ CORRECTED → FROZEN
```

Chỉ `CONFIRMED`, `CORRECTED` hợp lệ, hoặc `FROZEN` mới được dùng làm official
fact trên báo cáo lãnh đạo. `RAW`/`PROPOSED` thì không. Transition hợp lệ được
enforce ở `domain/lifecycle.py · assert_transition`.

## Evidence requirement

- `evidence-policy.yaml`: minimum theo risk (R2≥1, R3≥1, R4≥2) và
  `prohibit_unlinked_official_fact: true`.
- Enforce: `cvf_runtime/evidence.py · assert_evidence_sufficient`, gọi trước khi
  `CONFIRMED` trong `EventService.confirm`.

## Truy vết (traceability)

Mọi mutation quan trọng ghi một audit record append-only
(`cvf_runtime/audit.py`), lưu qua ledger (`Ledger.append_audit`) nên tồn tại qua
restart khi dùng `SqlLedger`. Mỗi correction giữ before/after version
(`CorrectionService`). Nhờ đó mọi dòng kết luận truy ngược được về evidence và
lịch sử phê duyệt.
