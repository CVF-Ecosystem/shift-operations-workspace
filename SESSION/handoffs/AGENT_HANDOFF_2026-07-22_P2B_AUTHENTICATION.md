# Agent Handoff — 2026-07-22 (P2-B: real authentication)

Provider-neutral handoff. Continues from
[`AGENT_HANDOFF_2026-07-22_P2A_CUSTOMER_REQUEST.md`](AGENT_HANDOFF_2026-07-22_P2A_CUSTOMER_REQUEST.md)
(via [`AGENT_HANDOFF_2026-07-22_POST_BOOTSTRAP.md`](AGENT_HANDOFF_2026-07-22_POST_BOOTSTRAP.md)
and [`AGENT_HANDOFF_2026-07-22_PORTABLE_CLONE.md`](AGENT_HANDOFF_2026-07-22_PORTABLE_CLONE.md),
which reconciled two pending batches after this P2-A tranche).

- **Mode:** cvf_enforcement_buildout
- **Tranche:** P2-B — Execution Roadmap Phase 2, real authentication
  replacing header-trusting identity
- **Startup ack:** mode=cvf_enforcement_buildout; active handoff=this file;
  next allowed move=P2-A (còn lại: incidents/handovers, cần migration mới
  trước), reconcile known-principals.yaml with the new users table, or P2-C;
  parked checkpoint=none.

## Bối cảnh

Sau khi hai batch treo (customer_request repair, bootstrap-continuity) được
review và commit riêng, operator chọn P2-B (authentication thật) trong số ba
lane hợp lệ (`next_allowed_move`). `identity` là CVF control cuối cùng còn ở
trạng thái "not verified server-side" — mọi 5 domain đã build (Event/
Correction/Task/Shift/CustomerRequest) đều thừa hưởng giới hạn này qua cùng
một `get_principal` dependency.

## Việc đã làm — JWT bearer token thay header-trusting identity

Thiết kế đầy đủ ở
[`docs/decisions/ADR_2026-07-22_P2B_JWT_AUTHENTICATION.md`](../../docs/decisions/ADR_2026-07-22_P2B_JWT_AUTHENTICATION.md).
Tóm tắt:

1. **`database/migrations/003_users.sql`** (mới): bảng `users` — `user_id`
   text PRIMARY KEY (tái dùng id kiểu `known-principals.yaml`, vd `op1`),
   `username` UNIQUE, `password_hash`, `role` CHECK khớp
   `cvf_runtime.identity.KNOWN_ROLES`, `is_active`.
2. **`operations-ledger`**: `users` Table trong `tables.py` (mirror migration
   003); `add_user`/`get_user_by_username` thêm vào `Ledger` Protocol,
   `SqlLedger`, `InMemoryLedger` (bao gồm trong snapshot của
   `InMemoryLedger.transaction()` cho nhất quán, dù chưa domain nào mutate
   user qua transaction thật). `User` model mới trong `domain/models.py`.
3. **`workspace_api/auth/`** (mới):
   - `passwords.py` — `hash_password`/`verify_password` qua `bcrypt`.
   - `tokens.py` — `create_access_token(principal) -> str` /
     `decode_access_token(token) -> Principal`, JWT HS256 ký bằng
     `settings.jwt_secret_key`, `algorithms=["HS256"]` cố định tường minh
     (chặn tấn công `alg: none`); role ngoài `KNOWN_ROLES` bị từ chối vì
     `Principal`'s validator chạy khi decode.
   - `router.py` — `POST /auth/login` (`{username, password}` →
     `{access_token, token_type, expires_in}`), lỗi 401 chung cho username
     lạ/sai mật khẩu/tài khoản inactive (chặn username enumeration).
4. **`config.py`**: `jwt_secret_key: str` KHÔNG default (fail-closed lúc
   khởi động); `jwt_access_token_ttl_minutes: int = 60`.
5. **`dependencies.py::get_principal`**: viết lại dùng `HTTPBearer`, decode
   qua `auth/tokens.py`, 401 khi thiếu/hỏng/hết hạn/sai chữ ký. **Không sửa
   router nào khác** — mọi router vẫn `Depends(get_principal)` y nguyên.
6. **`scripts/seed_dev_users.py`** (mới): script dev/test độc lập, seed 8 user
   tái dùng id/role của `known-principals.yaml` (mật khẩu cố định
   `<user_id>-devpass`, ghi rõ KHÔNG dùng cho production). Verified round-trip
   thật qua SqlLedger/SQLite (idempotent — chạy lần 2 skip user đã có).
7. **`root conftest.py`** (mới): set `JWT_SECRET_KEY` test-only trước khi
   pytest import bất kỳ module nào, để test suite không phụ thuộc `.env` cục
   bộ.
8. Tests mới: `tests/cvf/test_auth_tokens.py` (8), `tests/cvf/test_auth_login.py`
   (5, gồm 1 test thêm sau independent review — xem bên dưới),
   `tests/cvf/_auth_test_helpers.py` (helper `auth_headers()` ký token
   thật, dùng lại ở 3 file test HTTP cũ), `tests/integration/test_schema_parity_users.py`
   (role CHECK khớp `KNOWN_ROLES` hai chiều). Cập nhật 3 file test cũ
   (`test_shift_close_governance.py`, `test_customer_request_vertical.py`,
   `test_customer_request_repair.py`) để dùng bearer token thật thay vì header
   `X-User-Id`/`X-User-Role` literal. Thêm probe hồi quy
   `test_old_header_impersonation_no_longer_grants_any_identity` — claim
   `authorized_executive` qua header cũ, không kèm bearer, vẫn 401.

## Kết quả kiểm chứng

- `python -m pytest -q` → **171 passed** (156 trước + 15 test mới: 8 token +
  5 login (gồm 1 thêm sau review) + 1 negative-probe + 1
  test_schema_parity_users; các file cập nhật giữ nguyên số test).
- `python scripts/testing/validate_repository.py` / `generate_catalog.py --check`
  → PASS sau khi chạy `--write` (metrics/Markdown đồng bộ với registry đã cập
  nhật cho `workspace-api`/`operations-ledger`).
- Manual HTTP smoke test: login → bearer token → `POST /shifts/{id}/close`
  trả 200; cùng request chỉ kèm header `X-User-Id`/`X-User-Role` cũ (không
  bearer) → 401; token bị tamper (4 ký tự cuối đổi) → 401 "Signature
  verification failed".
- Independent-agent review (fresh context, no memory of this implementation,
  per `AGENTS.md`'s REVIEWER-independent-from-IMPLEMENTATION_WORKER rule for
  R2+ changes): chạy probe riêng (TestClient độc lập, secret riêng) cho
  header cũ, `alg=none`, sai signing key, token hết hạn, role bịa, cộng round
  -trip login thật — **không tìm thấy bypass nào** trong các vector đó; xác
  nhận `jwt_secret_key` không default; xác nhận mọi router governed vẫn
  `Depends(get_principal)` nguyên vẹn; xác nhận `known-principals.yaml`/
  `approval.py` không bị đụng. **Tìm thấy 1 gap thật:** login endpoint có
  timing side-channel — response body/status giống hệt nhau cho username lạ
  vs sai mật khẩu, nhưng username lạ bỏ qua hoàn toàn bước `verify_password`
  (Python `or` short-circuit), khiến response nhanh hơn ~18 lần — đủ để dò
  username hợp lệ bằng đo thời gian dù response trông giống nhau. **Đã sửa
  trong cùng tranche này** (không phải tranche riêng): `verify_password` giờ
  luôn chạy, so với `DUMMY_PASSWORD_HASH` khi không tìm thấy user
  (`workspace_api/auth/passwords.py`), cân bằng chi phí bcrypt trên mọi
  nhánh. Test mới:
  `test_unknown_username_still_runs_password_verification` (spy-based, không
  dùng wall-clock timing để tránh flaky trong CI).

## Docs đã đồng bộ (front door)

`docs/cvf/CVF_CONTROL_MAPPING.md` (identity row → load-bearing, 5 chỗ
"Còn hạn chế" xóa mention header-based, approval row + confirm-chain diagram
ghi chú), `docs/implementation/EXECUTION_ROADMAP.md` (tick P2-B, viết đoạn
tranche, cập nhật "Bước kế tiếp duy nhất"), `IMPLEMENTATION_STATUS.json`
(block `p2b_authentication` mới, xóa "identity header-based" khỏi
`known_remaining_defects`), `docs/catalog/MODULE_REGISTRY.json` +
`MODULE_CATALOG.md` (regenerated), `.env.example` (`JWT_SECRET_KEY`,
`JWT_ACCESS_TOKEN_TTL_MINUTES`), ADR mới.

## Next allowed move

Theo `EXECUTION_ROADMAP.md`: P2-A (còn lại — incidents, handovers; CHƯA có
bảng migration nào, cần migration mới trước), HOẶC reconcile
`known-principals.yaml` với bảng `users` mới (High Finding #4 vẫn mở), HOẶC
P2-C (frontend UI, giữ boundary backend-only).

## Blocked

Xem `blocked_work` trong `ACTIVE_SESSION_STATE.json`. Mới thêm bởi tranche
này: **không tuyên bố High Finding #4 đã sửa** — P2-B chỉ sửa identity,
KHÔNG đụng known-principals.yaml/approval; không tuyên bố có refresh token/
revocation hay admin user-provisioning thật (chỉ có
`scripts/seed_dev_users.py`, dev/test). Vẫn còn treo như trước: PostgreSQL
round-trip chưa chạy live; data_scope/cost/termination chưa có runtime
caller; refusal routing/recording chưa implement; incidents/handovers (P2-A
còn lại) chưa có migration; không batch nhiều tranche/commit.
