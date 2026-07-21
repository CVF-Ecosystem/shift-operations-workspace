# Trust Boundaries

Không dữ liệu nào được tin cho tới khi qua verify/validate. Đây là lý do
governance phải ở backend, không ở frontend.

## Nguồn untrusted (cho tới khi được xử lý)

- **External channel input** (Zalo/WhatsApp/webhook): untrusted → qua
  Integration Edge (signature verify, dedupe, raw payload preserved) trước khi
  vào hệ thống.
- **Attachments**: untrusted → scan trước khi dùng.
- **Customer text**: untrusted → không tự thành confirmed fact.
- **Model output (LLM)**: untrusted → validate schema + operational truth trước
  khi ghi ledger.

## Internal UI cũng không được tin ngầm

**Frontend không phải trust boundary.** Web UI phải gọi backend và mọi request
đi qua identity + authorization ở backend (`workspace-api` +
`cvf-runtime`). UI ẩn một nút **không** thay cho việc backend từ chối hành động
đó — một client khác (mobile, curl) bỏ qua UI vẫn phải bị chặn.

→ Xem [`FRONTEND_BACKEND_BOUNDARY.md`](FRONTEND_BACKEND_BOUNDARY.md) luật #2 và
[`../cvf/CVF_CONTROL_MAPPING.md`](../cvf/CVF_CONTROL_MAPPING.md) (identity,
permission, refusal).

## Contamination guard

Nội dung từ kênh ngoài luôn được xem là dữ liệu không tin cậy và không được điều
khiển system instruction (không cho channel payload chi phối prompt/logic).
