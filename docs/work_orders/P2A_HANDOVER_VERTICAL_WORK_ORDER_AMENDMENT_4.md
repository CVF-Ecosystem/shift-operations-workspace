# Work Order Amendment 4 — P2-A Canonical Debt Digest Correction

ID: `P2A-HANDOVER-WO-AMENDMENT-4`
Tranche: `P2A-HANDOVER-VERTICAL-2026-07-26`
Risk: R2
Status: APPROVED — REPAIR PROHIBITED UNTIL C2h AND C2i ARE PUSHED
Amends: parent Work Order and Amendments 1-3

## 1. Accepted finding

`HOV-REV-F14 PREEXISTING_CANONICAL_DEBT_DIGEST_DRIFT` is accepted without
waiver. Amendment 3 exposed a baseline SHA that represents CRLF worktree bytes
rather than the unchanged Git blob's canonical logical content.

## 2. Exact unchanged C3 boundary

The authorized BUILD set remains exactly the existing 47 paths.
`docs/reference/FILE_SPLIT_DEBT_BASELINE.json` is already within the original
44 paths. No 48th path is authorized or conditional.

## 3. Repair scope

After C2h/C2i are pushed, Claude may declare `REPAIR_WORKER` and:

1. change only the `sha256` scalar of the existing
   `scripts/generate_catalog.py` debt entry from
   `a46bd98d675af51d75d313b0913721c77af8d72f5fad97ded6908090703c4578`
   to
   `fff6229dde57a174935b87eb8319ef7e6d1bdd882580f74e672c81054739c93b`;
2. update the existing BUILD receipt to record F14 and the successful reruns;
3. rerun all parent/amended focused, full, repository, PostgreSQL and provider
   gates, then stop for independent review.

No other baseline field or entry may change. Do not modify
`scripts/generate_catalog.py`, add debt, perform a bulk rehash, change line
limits, use `.gitattributes`, or alter Git configuration.

## 4. Mandatory evidence

- a zero-context JSON diff proving exactly one baseline scalar changed;
- canonical digest comparison against the committed Git blob;
- focused file-size guard suite and direct file-size gate;
- full root and tests-only non-live suites;
- catalog, session-state, validator, diff and doctor gates;
- disposable PostgreSQL 16 round trip and exact cleanup;
- exactly one successful real-provider evidence run;
- corrected BUILD receipt with no secret-bearing output.

## 5. Stop conditions

STOP on:

- any BUILD path beyond the existing 47;
- any baseline change other than the one authorized scalar;
- any source-content or line-count drift;
- any debt add/remove, bulk rehash or policy relaxation;
- red gate, receipt drift, leaked secret, stage, commit or push.

## 6. Commit graph and role

- C2h: exactly this Amendment 4 ADR/SPEC/Work Order set.
- C2i: reviewer-owned continuity acknowledgment and repair route.
- C3: exactly 47 BUILD paths after independent REVIEW_PASS.
- C4: closure remains separate.

Claude performs no stage, commit, push or self-approval and stops at:

`READY_FOR_INDEPENDENT_HANDOVER_BUILD_RE_RE_RE_RE_RE_RE_REVIEW`

## 7. Independent approval

Codex independently reproduced F14 and approves this exact one-scalar repair
inside the unchanged 47-path BUILD boundary under the operator-delegated
reviewer/work-order authority.
