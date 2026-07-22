# Alibaba Live Provider Configuration Specification

Tranche: `PROVIDER-ALIBABA-LIVE-CONFIG`  
Risk: R2

## Intended behavior

1. The credential from the operator-supplied CSV is stored outside Git in the
   Windows current-user environment as `ALIBABA_API_KEY`.
2. Provider tooling can discover the key without printing its value.
3. A versioned JSON catalog records each supplied model code, remaining and
   total free quota, expiration date, enabled status, and priority.
4. A selector returns an eligible model for a supplied date.
5. Expired, disabled, or exhausted models are never selected.
6. Selection prefers lower numeric priority and then the nearest expiration
   date, avoiding unnecessary loss of soon-expiring quota.
7. Live calls use the selected model explicitly instead of relying on the
   CVF core's `qwen-turbo` default.

## Catalog snapshot supplied by operator

| Model | Remaining / total | Expiration |
|---|---:|---|
| `qwen3.7-plus` | 989246 / 1000000 | 2026-08-31 |
| `deepseek-v4-flash` | 987097 / 1000000 | 2026-07-23 |
| `qwen3.7-max-2026-05-17` | 1000000 / 1000000 | 2026-08-23 |
| `qwen3.7-max-2026-06-08` | 1000000 / 1000000 | 2026-09-07 |
| `glm-5.1` | 1000000 / 1000000 | 2026-08-25 |
| `qwen3.7-max-preview` | 1000000 / 1000000 | 2026-08-23 |
| `qwen3.5-plus-2026-04-20` | 1000000 / 1000000 | 2026-07-22 |
| `qwen3.7-max` | 1000000 / 1000000 | 2026-08-19 |
| `glm-5.2` | 1000000 / 1000000 | 2026-09-23 |
| `kimi-k2.7-code` | 1000000 / 1000000 | 2026-09-23 |

## Acceptance criteria

- No API key or credential CSV is tracked by Git.
- A secret-safe readiness check reports `key_present=true` without revealing
  the key.
- Catalog parsing and selection tests cover eligible, expired, disabled,
  exhausted, malformed-date, and deterministic-priority cases.
- On 2026-07-22 the primary selected model is `deepseek-v4-flash`, because its
  free quota expires first on 2026-07-23; the model expiring on the current
  date is held as fallback to avoid ambiguous end-of-day expiry.
- A live Alibaba call succeeds with the explicitly selected model, or the
  tranche records the exact redacted failure and remains open.
- Repository validation and session-state checks pass.

## Non-goals

- No automatic scraping of the Alibaba console.
- No application AI-gateway integration.
- No secret committed to `.env` or another project file.
- No claim that P2-B authentication or other CVF findings are repaired by this
  provider configuration.
