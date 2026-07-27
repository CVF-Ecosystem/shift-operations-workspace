# ADR Addendum — P2-A Canonical Debt Digest Correction

ID: `ADR-2026-07-27-P2A-CANONICAL-DEBT-DIGEST-CORRECTION`
Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
Risk: R2
Phase: DESIGN amendment after independent BUILD re-review
Status: REVIEW_PASS
Amends: `ADR_2026-07-27_P2A_HANDOVER_ROLLBACK_PORTABILITY_ADDENDUM.md`

## Finding

Amendment 3 correctly made debt SHA-256 newline-representation-neutral. The
corrected gate then exposed one pre-existing baseline value that had been
recorded from CRLF-materialized worktree bytes:

```text
scripts/generate_catalog.py
recorded/raw CRLF: a46bd98d675af51d75d313b0913721c77af8d72f5fad97ded6908090703c4578
canonical/Git blob: fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b
```

The file's logical content and line count are unchanged. The other debt entry
already matches its canonical digest.

Finding: `HOV-REV-F14 PREEXISTING_CANONICAL_DEBT_DIGEST_DRIFT`.

## Decision

Correct exactly the `sha256` value for the existing
`scripts/generate_catalog.py` debt entry to:

`fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b`

This is a one-time migration of an existing baseline value to the canonical
digest rule approved by Amendment 3. It is not a waiver, a new debt entry, a
general rehash authorization or permission to change the governed file.

## Boundary

`docs/reference/FILE_SPLIT_DEBT_BASELINE.json` is already in the original
44-path BUILD authorization. This correction adds no BUILD path: the final
ceiling remains exactly 47 paths and no 48th path is conditional.

No other field, debt entry, digest, source file, test, Git setting or
`.gitattributes` path may change under this amendment.

## Independent disposition

Codex independently reproduced the red gate and compared the recorded value,
raw CRLF worktree bytes, universal-newline canonical text and committed Git
blob. F14 is accepted without waiver. Under the operator-delegated
reviewer/work-order authority, this bounded correction is approved.
