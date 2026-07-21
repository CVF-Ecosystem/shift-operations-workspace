# Security Policy

Mô hình security của Shift Operations Workspace.

## Report vulnerabilities

Không công bố public trước khi owner xác nhận. Ghi rõ component, impact, reproduction steps và evidence.

## Credential handling

API keys, webhook secrets và tokens chỉ nằm ở backend credential vault hoặc environment secret store; không commit vào repository và không đưa xuống frontend.

## External input

Mọi payload từ channel ngoài là untrusted data, phải qua signature verification, rate limit, deduplication, attachment validation, quarantine và contamination guard.

## AI boundary

Không gửi raw history toàn ca vào model. Context phải được tối thiểu hóa, redaction và policy-evaluated trước khi gọi provider.
