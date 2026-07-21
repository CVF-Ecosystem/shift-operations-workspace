# Risk and Approval

Mỗi record nghiệp vụ mang một **risk class** (R0–R4). Risk class quyết định
capability được dùng, evidence bắt buộc, và ai phải phê duyệt.

## Risk classes

| Risk | Nội dung | Approval | Evidence tối thiểu |
|------|----------|----------|--------------------|
| R0 | Tin nhắn thông thường | none | 0 |
| R1 | Cập nhật tiến độ | sender/role khi cần | 0 |
| R2 | Downtime, thay đổi kế hoạch | shift_supervisor | 1 |
| R3 | Khiếu nại, thiệt hại, hàng nguy hiểm | dual (supervisor + manager) | 1 |
| R4 | Tai nạn, pháp lý, công bố ra ngoài | escalation (manager + executive) | 2 |

Nguồn policy: `packages/cvf-application-profile/risk-classes.yaml`,
`approval-policy.yaml`, `evidence-policy.yaml`.

## Enforce ở đâu

- Risk → yêu cầu: `cvf_runtime/risk.py · requirement_for`.
- Approval quorum: `cvf_runtime/approval.py · assert_approval_satisfied` — kiểm
  đúng role, đúng số người, **không** cho một người điền hai ghế, không tự phê
  duyệt.
- Evidence tối thiểu: `cvf_runtime/evidence.py · assert_evidence_sufficient`.

Gọi trong chuỗi: `EventService.confirm` và `CorrectionService.correct_event`.
Xem bảng đầy đủ tại [CVF_CONTROL_MAPPING.md](CVF_CONTROL_MAPPING.md).
