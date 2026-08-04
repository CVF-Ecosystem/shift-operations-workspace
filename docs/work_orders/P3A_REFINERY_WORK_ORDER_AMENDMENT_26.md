# Work Order Amendment 26 — Retained Debt-Pin Output Gate Continuation

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-26-2026-08-04`
- Consumed A25 SHA-256: `ff2671a05b732bf6b687bcd65daae32f8895dd669ea63a25ae63c885e2e33cf7`
- A25 initial review / re-review SHA-256: `5a222a068ac54f035d303bd32030f41147c918f8dbdf449a573e1757621629f6` / `007c08f69a494159db25492880cc2528521bbe990fa82970db8cb31f24c31b65`
- A25 authority / R2 acknowledgment checkpoints: `f5fdc5a3495f761d1b6778d6efd92bc67dc53ec8` / `81c2c5fe37d32d6bc61c7ee2d80b80f51181e2f3`
- Risk / phase: `R2 / WORK_ORDER`
- Status: `PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Calls: `0 provider / 0 network / 0 remote-ingest`

## Trigger and retained stop truth

A25 preflight passed exact34, staged0, protected32 and the debt registry's raw
29-CRLF pre-state. Its one authorized `apply_patch` replaced the old generator
SHA with the reviewed new SHA. The immediate post-audit stopped at the required
post-hash assertion before file-size or any later gate. There was no retry and
no provider/network/remote-ingest call.

Read-only inspection shows the patch engine preserved 28 CRLF sequences and
emitted LF for the changed line. The retained debt registry therefore has:

- SHA-256 `ae9ed0dfc28f41f2b551a6f02d878e5a0bcc800b2025738ec54704a0031c5132`;
- old generator SHA occurrences `0`, reviewed new generator SHA occurrences `1`;
- `28` CRLF sequences, `29` LF bytes total and one lone LF;
- valid JSON content with no semantic field beyond the authorized pin changed.

A25 and its fresh R2 are consumed. File-size, repository, JSON/YAML, contract,
import/I/O, secret, diff and final gates remain `NOT_RUN`.

## Zero-repair scope and bindings

Current candidate is exact35 and staged0. A26 authorizes exactly zero repair
paths and retains final exact35 byte-for-byte. No `apply_patch`, formatter,
normalization, generator write, source edit, continuity edit or other write is
permitted during its invocation.

The stable exact33 manifest (final exact35 excluding only canonical memory and
active handoff) is:

`4d0ba0a8b901d5cd097f59111f959b667725df651ddcbd0bbb530c0953f6661a`

It uses SHA-256 over ordinal-path-sorted records
`path UTF-8 + NUL + lowercase file SHA-256 ASCII + LF`. The debt registry SHA,
newline counts and old/new occurrence counts above are immutable bindings.

## Retained evidence

A26 retains without rerun or relabeling:

- A24 exact-four/post-audit, focused catalog `5`, Knowledge validator,
  Knowledge `86`, catalog check, full non-live `1597 / 128 skipped`, and
  session-state PASS;
- A25 preflight PASS and the completed one-path literal replacement;
- A25 immediate post-audit failure and all subsequent `NOT_RUN` truth.

## One ordered zero-write invocation

After independent authorization review, pushed authority checkpoint and fresh
exact A26 R2, `REPAIR_WORKER` runs once, stops at the first failure and never
retries:

1. verify dynamic authority/R2 topology, artifact hashes, staged0, exact35,
   stable33, all retained A24 hashes and the immutable debt raw-byte bindings;
2. run `python scripts/check_file_size.py` once;
3. run `python scripts/testing/validate_repository.py` once;
4. run the remaining JSON/YAML/contract/import-I/O/secret/diff gates once;
5. run final exact35/zero-repair/stable33/debt/continuity/staged0 audit once.

No write is authorized. No provider/network/remote-ingest/POST call, test-suite
rerun, alternate fix, BUILD commit, self-review, FREEZE, waiver or later-lane
expansion is authorized. Any first failure consumes the invocation and requires
a new reviewed amendment and fresh R2.
