# P5-A Live Canary Contract

Status: SPEC draft for independent review; no caller or live evidence is present.

This specification is the independent contract for P5-A criterion A7's single
admitted public-synthetic provider canary. It follows
`docs/cvf/INVARIANT_FAMILY_STANDARD.md`; its registered family is
`P5A-LIVE-CANARY-OUTCOMES` in
`docs/cvf/invariants/p5a-live-canary-outcomes.json`. The matrix is the semantic
owner for terminal receipt fields, outcome relations, and mutation expectations.

## Claim boundary and authority

The authority is the immutable
`docs/decisions/P5A_REPORTING_ENGINE_LIVE_ADMISSION_2026-10-23.json` and the
user's exact recorded grant `Cho phép đúng giới hạn trên`. It permits one
Alibaba Cloud Model Studio `qwen-flash` request to the recorded Singapore
endpoint, using only the Windows CurrentUser `ALIBABA_API_KEY`, a PUBLIC
synthetic prompt, at most 64 output tokens, no retries, redirects, or fallback,
a 60-second timeout, and a USD 0.01 pay-as-you-go ceiling. The admission's
published input/output rates are USD 0.05/0.40 per million tokens. The expired
free-quota record is not authority. This specification grants no second model,
endpoint, credential source, provider request, public release, or deployment.

The canary records one actual invocation bound to a current local gate
observation digest. The provider sees that digest and the fixed synthetic
request. It does not decide, approve, or control report generation, export
authorization, operational truth, or any CVF gate. The provider response is a
digest echo only. No broader AI-governance behavior claim follows from the
canary. A structural fixture or mutation result is contract evidence only and
must never be described as a live provider result.

## Preflight before credential access

The runner is explicit-run only. Importing it or its helpers performs no
credential lookup, environment-file load, provider action, network access, or
automatic execution. Default and preflight-only modes read no credential and
make no provider request. A successful readiness-only run writes neither the
attempt marker nor the live-evidence receipt; its readiness output is not a
terminal outcome and must not be represented as `PRECALL_BLOCKED_ZERO_CALL`.
Only an explicit run that terminates on failure or reaches the reserved
provider attempt may write the live-evidence receipt. A successful default or
preflight-only readiness result is ignored as evidence and creates no
`LIVE_ATTEMPT` or `LIVE_EVIDENCE` artifact.

At the start of an explicit run, inspect the fixed attempt-marker path before
checking worktree cleanliness. If a marker already exists, is partial, or its
absence cannot be established, terminate as `RESERVED_NOT_ACCEPTED_OR_UNKNOWN`
with marker count 1, key-read count 0, transport count 0, and no credential or
network access. Do not overwrite the marker or any existing evidence file. This
marker-first refusal ensures a prior untracked marker cannot be misreported as
a zero-reservation `WORKTREE_DIRTY` preflight result. If the marker is absent,
continue with the gates below; a concurrent marker created before the later
exclusive reservation step has the same reserved terminal accounting.

Before any provider-key lookup, the explicit run must:

1. Read and validate the immutable admission and local evidence receipt. The
   canonical SHA-256 of the local evidence file must equal the admission's
   `localEvidenceCanonicalSha256`; its original committed source hashes must
   still match the current committed source bytes using the recorded text EOL
   normalization (assets remain byte-exact). Also hash the exact A7 runner and
   helpers, plus the current API-probe composition and dependencies used:
   `apps/workspace-api/src/workspace_api/main.py`,
   `apps/workspace-api/src/workspace_api/dependencies.py`,
   `apps/workspace-api/src/workspace_api/auth/tokens.py`,
   `apps/workspace-api/src/workspace_api/api/reports/router.py`,
   `apps/workspace-api/src/workspace_api/application/report_export.py`,
   `apps/workspace-api/src/workspace_api/application/report_service.py`,
   `apps/workspace-api/src/workspace_api/application/assignment_scope.py`,
   and `apps/workspace-api/src/workspace_api/infrastructure/repository.py`.
   Record the current reviewed Git commit and require a clean worktree.
2. Run the current read-only Core inheritance and invariant-family checks and
   require zero binding/closeability violations and a passing family check.
   The reviewed source commit and its normal full-gate result must be recorded.
3. Build a disposable app using the production API composition, production JWT
   signer, and `InMemoryLedger`; do not import pytest test modules. Through the
   actual `GET /reports/{report_id}/export` route, observe these four API
   results using only a PUBLIC synthetic report and no provider: missing bearer
   `401`; authenticated unknown report `404`; authenticated known synthetic
   report with an invalid export option `422`; valid authenticated synthetic
   PDF export `200`. For the 200 result retain only status, MIME type, byte
   count, and SHA-256 of response bytes; do not retain its body, report
   identifier, or operational content. Record the other response status and
   stable error code only. Stop if any expected result is absent.
4. Start a deterministic, UTF-8 JSON gate-observation envelope with a fixed
   ordered check list whose states are `NOT_RUN`; update each reached check to
   `PASS` or `FAIL` with a fixed safe reason code. Include exact source hashes,
   commit/clean state, named gate results, and the four sanitized API
   observations. Hash its canonical serialization with SHA-256. Mark the
   envelope `COMPLETE` only when every required check passes; otherwise mark it
   `PARTIAL_PREFLIGHT` and retain `NOT_RUN` for checks not reached. The envelope
   and digest contain no credential, request header, report body, or actual
   report identifier. Only the digest of a `COMPLETE` envelope is supplied to
   the provider; a partial digest is receipt metadata and cannot be described
   as a complete gate result.

A failed preflight ends as `PRECALL_BLOCKED_ZERO_CALL`: no attempt marker,
credential read, provider transport, or accepted response. It is not A7 live
proof. Do not continue to credential lookup after a failed check. If exclusive
marker creation fails before any marker bytes exist, this is also a zero-call
pre-reservation block; if any marker bytes may exist, classify it as reserved
unknown below and never try to replace them.

## One-use reservation and provider request

After successful preflight, reserve the exact admission once by creating
`docs/decisions/P5A_REPORTING_ENGINE_LIVE_ATTEMPT_2026-10-23.json` exclusively
(`O_CREAT|O_EXCL` semantics). On Windows, use exclusive `CREATE_NEW` with
write-through semantics (for example, `CreateFileW` with
`FILE_FLAG_WRITE_THROUGH`), write the minimal marker, and call
`FlushFileBuffers` on the marker file handle before continuing. Flush the
parent directory entry where the filesystem/platform supports it; do not use
ordinary Python `os.fsync` on a directory. Fail closed if file flush or durable
marker creation cannot be established. Preserve any partial marker. The marker
contains only the admission id, reviewed commit, gate digest, reservation time,
and a fixed marker version; never a key or header. An existing, partial, or
ambiguous marker is terminal: do not overwrite, remove, repair, reset, or
resume it, and do not read the credential or send a request. A present or
possibly-created marker counts as the single reservation and is recorded as
`RESERVED_NOT_ACCEPTED_OR_UNKNOWN`, even if no transport began. The marker is
the durable one-use boundary even if later work fails.

Only after successful reservation may the runner query the exact Windows
CurrentUser environment registry value `HKCU\\Environment\\ALIBABA_API_KEY`
directly. Do not use `os.environ`, inherited provider variables, `.env` files,
dotenv, shell expansion, a credential store fallback, or another key name. Do
not print, hash, persist, or include the key in an exception, receipt, request
body, or log. Missing/unreadable key after reservation is a terminal reserved
outcome; no transport follows.

Construct one UTF-8 JSON chat-completion body with exactly one user message and
the fixed ASCII template below, substituting the gate digest literally:

```text
Return only the JSON object below and no other text:
{"gate_observation_digest":"<DIGEST>","result":"echoed"}
```

Replace the single `<DIGEST>` placeholder with the lowercase 64-character
gate-observation digest before serialization.

The request body uses model `qwen-flash`, `max_tokens: 64`, `n: 1`,
`stream: false`, and top-level `enable_thinking: false`. It contains no report
data. Before transport, compute and retain the SHA-256 of the complete request
body; never include the Authorization header in receipts. Use TLS certificate
verification, the exact admitted HTTPS endpoint, a 60-second timeout,
`follow_redirects=false`, no retry transport, no proxy/environment credential
inheritance, and exactly one direct POST. Do not perform model discovery, batch
submission, extra health calls, fallback, or a second request. Increment the
transport-attempt counter immediately before invoking that POST. A timeout,
connection error, redirect response, or any later validation failure remains
one consumed reservation and must not trigger another request.

## Response validation, accounting, and receipt

Capture HTTP status and the complete response body within a 64 KiB bound. The
live-evidence JSON is an evidence wrapper with a nested `terminal_receipt`,
`gate_observation_envelope`, `sanitized_request_body`, and
`sanitized_response_body`/capture metadata. Validate the nested
`terminal_receipt` as the closed object described by the registered matrix;
request/response bodies belong only in the wrapper and never as extra receipt
fields. Preserve the full sanitized request and, if received, full sanitized
response body; do not store request headers. Redact bearer/API-key material
and secret-bearing error strings before writing. Never persist raw exception
text or response headers. If the response cannot be fully captured within the
bound, retain its SHA-256, size, status when available, and a fixed safe reason
code; do not store a truncated body as if it were complete.

An actual response is `ACCEPTED_SINGLE_RESPONSE` only if all checks pass:

- HTTP status is 200; the response is valid JSON with model exactly
  `qwen-flash`, one choice at index 0, assistant role, no tool call/refusal,
  `finish_reason` `stop`, and a complete message string that parses as one JSON
  object with exactly `gate_observation_digest` and `result`.
- The parsed digest equals the current gate-observation digest and `result` is
  exactly `echoed`. No prose, additional key, truncation, or non-empty
  reasoning-content field is accepted. Reject duplicate JSON keys and
  non-standard numeric constants at every response-object level.
- Usage has non-negative integer `prompt_tokens`, `completion_tokens`, and
  `total_tokens`; `total_tokens == prompt_tokens + completion_tokens`;
  `prompt_tokens <= 256`; `completion_tokens <= 64`.
- Compute a conservative usage-based cost estimate in integer nano-USD using
  the admitted published rates: `prompt_tokens * 50 + completion_tokens * 400`.
  It must be at most 10,000,000 nano-USD (USD 0.01). This is an estimate from
  returned token usage, not an account invoice or quota proof. Record all three
  usage counts, the computed amount, formula/rate version, model, HTTP status,
  response digest, and exact request digest.

Any post-reservation path that does not satisfy every acceptance check is
`RESERVED_NOT_ACCEPTED_OR_UNKNOWN`. Record the safe phase/reason, cumulative
reservation/key-lookup/transport/response/acceptance/retry/redirect/fallback
counters, sanitized request and any complete sanitized response, response
digest, available valid usage and cost estimate, and whether the outcome is
unknown. Do not invent usage or cost when missing/invalid. Record a returned
usage object when available; if valid, preserve its counts and calculated cost
even when another response check rejects the call. Do not persist any raw key,
Authorization header, operational report data, raw exception, or unsanitized
provider error. Preserve the one-use marker on every path.

Terminal receipts are closed objects conforming to the three outcomes and
shape variants in the registered matrix. Core counters are admission-wide:
before reservation all are zero; after reservation the marker count is one;
transport attempts are zero or one; responses never exceed transport
attempts; accepted responses never exceed responses; retry, redirect, and
fallback counts are always zero. The only accepted positive has one marker,
one successful CurrentUser key lookup, one POST attempt, one actual response,
and one accepted response. Any inconsistency is a contract failure, not an
extra outcome or retry permission.

The actual admitted request and sanitized response are the only evidence that
can satisfy R12's separate live-canary requirement. Preflight outcomes,
structural/mutation fixtures, a digest echo fixture, or provider-free tests do
not satisfy it. A failed/ambiguous reservation remains terminal; there is no
automatic resume or marker reset. A7 remains open until the independent A7
receipt reviewer assigned by the Work Order (currently Luna/max,
`p5a_readiness`) accepts the actual receipt; root then completes the existing
committed closure gates.

The matrix counters are `marker_reservations`, `key_read_attempts`,
`transport_attempts`, `responses`, `accepted_responses`, `retry_count`,
`redirect_count`, and `fallback_count`. Shape variants enforce
`responses <= transport_attempts` and `accepted_responses <= responses`; the
sole accepted shape fixes each of the first five counters to one. A marker
already present for this admission is one reservation, not a new one.

## API reference

The request fields and response usage names follow Alibaba's current
[OpenAI-compatible chat completion documentation](https://www.alibabacloud.com/help/en/model-studio/qwen-api-via-openai-chat-completions)
and [qwen-flash model page](https://www.alibabacloud.com/help/en/model-studio/qwen-flash),
checked 2026-10-23. The live endpoint, key source, prices, and one-call limits
remain owned by the admission record; documentation does not expand that grant.
