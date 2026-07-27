# ADR Addendum — P2-A Handover Rollback Portability

ID: `ADR-2026-07-27-P2A-HANDOVER-ROLLBACK-PORTABILITY`
Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
Risk: R2
Phase: DESIGN amendment after independent BUILD re-review
Status: REVIEW_PASS
Amends: `ADR_2026-07-26_P2A_HANDOVER_VERTICAL.md`

## Finding

Independent AC-21 rehearsal at committed parent `6850e6e` restored the
expected tests-only baseline (`507 passed, 44 skipped, 1 warning`) but the
file-size gate failed:

```text
debt entry sha256 is stale:
scripts/run_identity_live_governance_evidence.py
```

The tracked blob and primary worktree use LF and match the authorized digest
`59288b5c...`. A fresh Windows worktree under the repository's effective
`core.autocrlf=true` checks out the same blob as CRLF, producing
`04e4039e...`. Line count and logical text are unchanged.

Finding: `HOV-REV-F13 ROLLBACK_REHEARSAL_EOL_NONPORTABILITY`.

## Decision

Debt digests become content-sensitive but newline-representation-neutral:

- decode governed executable text as UTF-8 using universal-newline handling;
- canonicalize CRLF and lone CR to LF;
- compute SHA-256 over the canonical UTF-8 bytes;
- preserve every other byte/content distinction.

This keeps the debt ratchet fail-closed for real edits while allowing the same
Git blob to verify after LF or CRLF checkout. Existing LF baseline digests
remain valid and are not rehashed.

The guard documentation must state the canonical digest rule. Tests must prove
LF-authored debt still passes after CRLF checkout representation and that a
same-line-count content mutation still fails.

## Boundary

Authorize exactly three additional BUILD paths:

1. `scripts/check_file_size.py`;
2. `tests/integration/test_file_size_guard.py`;
3. `docs/reference/FILE_SIZE_GUARD.md`.

The final BUILD ceiling becomes exactly 47 paths. No 48th path is conditional.
No debt entry may be added, rehashed or restored. The hard limits and closed
legacy allowlist remain unchanged.

No provider call is needed to authorize this amendment. All parent PostgreSQL,
provider, repository and reviewer rollback gates remain mandatory after repair.

## Independent disposition

Codex reproduced the failure in two fresh worktrees, distinguished LF
`59288b5c...` from CRLF `04e4039e...`, and verified complete cleanup.
F13 is accepted without waiver. Under the operator-delegated reviewer/work-order
authority, this bounded design amendment is approved.
