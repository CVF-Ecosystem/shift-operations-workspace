# Alibaba DashScope live configuration

`model-quota-catalog.json` is a non-secret operator snapshot of free quota and
expiration dates. Refresh it when the Alibaba console changes. The source
credential is never stored here.

Select the preferred currently eligible model:

```powershell
python packages/ai-providers/alibaba/select_model.py
```

List fallbacks in order:

```powershell
python packages/ai-providers/alibaba/select_model.py --all
```

The selector treats a model as expired on its displayed expiration date, not
after that date, to avoid timezone/end-of-day ambiguity. It excludes disabled
or exhausted entries and then orders candidates by explicit priority, nearest
expiration, remaining quota, and model code.

The credential is expected in the Windows current-user environment as
`ALIBABA_API_KEY`. CVF core tooling recognizes this alias and maps it to its
DashScope live gate. Never paste the value into commands, documentation, or
evidence.

`CurrentUser` environment changes are inherited only by processes started
after the change. Open a new terminal before a live run. If a long-running
terminal must be reused, import the user-scoped value into that process
without printing it:

```powershell
$env:ALIBABA_API_KEY = [Environment]::GetEnvironmentVariable(
  'ALIBABA_API_KEY',
  'User'
)
if ([string]::IsNullOrWhiteSpace($env:ALIBABA_API_KEY)) {
  throw 'ALIBABA_API_KEY is unavailable in the Windows CurrentUser environment'
}
```

The command deliberately emits no secret. A readiness result may report only
the variable name/presence, never its value or an Authorization header.

This package is live-run configuration only. It does not implement the Phase 4
AI gateway or make AI-specific CVF controls load-bearing.
