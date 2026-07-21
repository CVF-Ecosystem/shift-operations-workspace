# CVF Application Profile

Profile áp dụng CVF cho Shift Operations Workspace. Nó **không sao chép CVF
core**; nó khai báo cách ứng dụng này dùng CVF: application id, domain cho phép,
risk classes, và các policy về evidence, approval, provider, data, cost,
refusal, termination, freeze.

Nguồn khai báo: `packages/cvf-application-profile/*.yaml`
(`profile.yaml` là điểm vào).

## required_controls (12)

```text
identity · permission · domain_lock · data_scope · risk · approval
evidence · audit · cost · refusal · termination · freeze
```

## Trạng thái enforce (tóm tắt)

| Nhóm | Control | Trạng thái |
|------|---------|-----------|
| Đã enforce + test | identity, permission, risk, approval, evidence, audit, refusal, freeze, domain_lock, data_scope | enforced |
| Enforce, active khi AI mode bật | cost, termination | enforced (AI-gated) |

Chi tiết từng control → file/gate/test: [CVF_CONTROL_MAPPING.md](CVF_CONTROL_MAPPING.md).

## Cách profile được đọc tại runtime

`cvf_runtime/policy_loader.py · load_profile` load và cache toàn bộ YAML,
**fail-closed** nếu thiếu file. Mọi gate trong `cvf_runtime` resolve rule qua
profile này, nên policy sống ở một nơi thay vì hard-code rải rác.
