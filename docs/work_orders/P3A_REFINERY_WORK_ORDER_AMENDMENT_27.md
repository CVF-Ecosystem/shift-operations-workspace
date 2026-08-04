# Work Order Amendment 27 — Exact35 Status-Truth Repair

- Repair id: `P3-A-REFINERY-BUILD-REPAIR-AMENDMENT-27-2026-08-04`
- Trigger review: `docs/decisions/P3A_REFINERY_BUILD_EXACT35_INDEPENDENT_REVIEW.md`
- Trigger review SHA-256: `de226b3d74e038ba239b19afeafeb39dad98197cd08f6d6150589b3e677f3ce6`
- Risk / phase: `R2 / WORK_ORDER`
- Status: `PENDING_INDEPENDENT_AUTHORIZATION_REVIEW`
- Calls: `0 provider / 0 network / 0 remote-ingest`

## Trigger and retained truth

Independent exact35 BUILD review reproduced stable33
`4d0ba0a8b901d5cd097f59111f959b667725df651ddcbd0bbb530c0953f6661a`,
focused Refinery `57`, full non-live `1597 / 128 skipped`, doctor `24/1`,
session/file-size/repository/catalog/JSON-YAML/contract-import-I/O/diff gates
PASS, and functional findings F1-F3 closed without waiver.

The review returned `REVIEW_CHANGES_REQUIRED` for one MEDIUM finding only:
`IMPLEMENTATION_STATUS.json` still states exact32/A18 repair-pending truth and
the repository status still ends at P3-A INTAKE. The current governed candidate
is exact35; A26 passed every remaining gate and final audit. No BUILD commit or
FREEZE is permitted until this source-truth defect is repaired and independently
re-reviewed.

## Exact scope and bindings

Amendment 27 authorizes exactly two already-dirty repair paths while the final
candidate remains exactly the same 35 BUILD/continuity paths:

1. `IMPLEMENTATION_STATUS.json`;
2. `knowledge/manifest.json`.

All other exact35 paths are byte-protected. Excluding canonical memory, active
handoff and the two repair paths leaves exact31 protected paths with ordinal
manifest SHA-256:

`00bb194572d0c1dcca5342feca0f5afa43ee4cb594eb6b5ca317da0c3090557a`

The manifest algorithm is SHA-256 over ordinal-path-sorted records
`path UTF-8 + NUL + lowercase file SHA-256 ASCII + LF`.

| Path | Required pre SHA-256 | Required post SHA-256 |
|---|---|---|
| `IMPLEMENTATION_STATUS.json` | `9d9d7d2ff387365ce018cc51de07a24d1eb3a21c08cb723feb3d74e114ae5eb6` | `18b21d8d263ff0518389ab413550b006661d9fabee83cb373320235a6d9ab404` |
| `knowledge/manifest.json` | `cbf115da32e5ad9418f1d91678d2ec2f875e174ee434f5762648325f63da4f80` | `251ca93f47a6527a0d941b7cbd371130a041fb21154ab269a05153b7751844a4` |

After the exact repair, stable33 must be:

`f6ed2c05f7db2737d5d668568eaaf0ea93e22dd66ba19120b10330aab27ee5ff`

## Exact repair contract

Use one atomic `apply_patch`. In `IMPLEMENTATION_STATUS.json` replace exactly
the repository `status` string and exactly five strings inside `p3a_refinery`
with the following complete literal post-image:

```diff
-  "status": "PHASE_1_DONE_PHASE_2_CLOSED_BOUNDED_PROJECT_OPERATIONS_SKILL_CLOSED_BOUNDED_PROJECT_KNOWLEDGE_PACK_CLOSED_BOUNDED_P3A_REFINERY_INTAKE",
+  "status": "PHASE_1_DONE_PHASE_2_CLOSED_BOUNDED_PROJECT_OPERATIONS_SKILL_CLOSED_BOUNDED_PROJECT_KNOWLEDGE_PACK_CLOSED_BOUNDED_P3A_REFINERY_BUILD_REVIEW_REPAIR_PENDING",
@@
-    "governance_disposition": "BUILD_REPAIR_IN_PROGRESS — final independent review CHANGES_REQUIRED; Amendment 18 authorizes exact9 repairs within final exact32 dirty BUILD/continuity paths.",
-    "authority_commits": "Original SPEC/Work Order authority 72a712d/b93e403; final review 4f5099c5; A18 reviewed authority/R2 lineage is recorded in canonical continuity.",
+    "governance_disposition": "BUILD_REVIEW_REPAIR_APPLIED_PENDING_INDEPENDENT_REREVIEW — exact35 candidate with Amendment 27 exact2 status/source-pin repair; no BUILD commit or FREEZE.",
+    "authority_commits": "Original SPEC/Work Order authority 72a712d/b93e403; prior final review 4f5099c5; A26 gate-pass continuity ac16f07; exact35 independent review de226b3d; A27 authority/R2 lineage is recorded in canonical continuity.",
@@
-    "changed_set": "Exactly 32 dirty BUILD/continuity paths after authorized knowledge additions and continuity/source-size repair; A18 repair touches exactly nine already-dirty paths.",
-    "evidence_status": "Retained A14 evidence: focused 53, catalog, full non-live 1593/128, session/repository/static/final gates PASS. Final review is CHANGES_REQUIRED (F1-F4); A18 repair and all post-repair gates are pending. Calls remain zero.",
+    "changed_set": "Exactly 35 dirty BUILD/continuity paths; Amendment 27 repairs exactly two already-dirty paths: IMPLEMENTATION_STATUS.json and the corresponding knowledge/manifest.json source pin.",
+    "evidence_status": "Retained A24/A26 evidence: focused Refinery 57, full non-live 1597/128, file-size/repository/JSON-YAML/contract/import-I-O/secret/diff/final exact35 gates PASS. Exact35 independent review closed functional F1-F3 and found only stale status truth; fresh independent re-review remains required. Calls remain zero.",
@@
-    "next_governed_move": "After fresh A18 R2, apply only exact9 repair and ordered local gates; then obtain fresh independent BUILD re-review. No later lane activates."
+    "next_governed_move": "Obtain fresh independent BUILD re-review after the reviewed Amendment 27 exact2 repair invocation. No BUILD commit, FREEZE or later lane before REVIEW_PASS."
```

Preserve `spec` and `claim_boundary` byte-for-byte.

In `knowledge/manifest.json`, replace only the `IMPLEMENTATION_STATUS.json`
source pin under the active `project-context` entry:

```diff
-        "sha256": "9d9d7d2ff387365ce018cc51de07a24d1eb3a21c08cb723feb3d74e114ae5eb6"
+        "sha256": "18b21d8d263ff0518389ab413550b006661d9fabee83cb373320235a6d9ab404"
```

No other manifest field, entry, ordering or source pin may change.

## One ordered invocation

After independent authorization review, pushed authority checkpoint and fresh
exact A27 R2, `REPAIR_WORKER` runs once, stops first failure and never retries:

1. verify dynamic authority/R2 topology, artifact hashes, staged0, exact35,
   both pre-hashes, stable33 pre-hash and protected31 manifest;
2. apply the exact two-path atomic patch once;
3. assert both post-hashes, exact35, protected31, post-stable33 and staged0;
4. run `python -m json.tool IMPLEMENTATION_STATUS.json` once;
5. run `python -m json.tool knowledge/manifest.json` once;
6. run `python scripts/check_project_knowledge.py` once;
7. run `python -m pytest tests/unit/test_project_knowledge_pack.py tests/integration/test_project_knowledge_ingest_rehearsal.py -q` once;
8. run `python scripts/check_session_state.py` once;
9. run `python scripts/check_file_size.py` once;
10. run `python scripts/testing/validate_repository.py` once;
11. run the local secret scan and `git diff --check` once;
12. run final exact35/exact2/protected31/post-stable33/source-pin/continuity/
    staged0 audit once.

No provider/network/remote-ingest/POST call, source/test/catalog/fixture edit,
full-suite or Refinery-suite rerun, alternate fix, BUILD commit, self-review,
FREEZE, waiver or later-lane action is authorized. Any first failure consumes
the invocation and requires a new reviewed amendment and fresh R2.
