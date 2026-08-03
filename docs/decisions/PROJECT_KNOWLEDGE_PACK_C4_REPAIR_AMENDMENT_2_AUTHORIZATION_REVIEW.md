# Project Knowledge Pack C4 Repair Amendment 2 — Authorization Review

- Tranche: `PROJECT-KNOWLEDGE-PACK-C4-REPAIR-AMENDMENT-2-2026-08-03`
- Parent amendment authority: `c32b5c51d51847dbd0fbf3bb582e9f7dd3fa1734`
- Parent C4 authority: `8dd99c02ad27901f416b935a1dcf78ab6ccd4eaa`
- Parent BUILD: `bb3e33668a6d60585455bf0301ba059918a15890`
- Risk: `R2`
- Review role: `INDEPENDENT_AUTHORIZATION_REVIEWER`
- Disposition: `AUTHORIZATION_REVIEW_PASS`
- Waiver: `NONE`
- Review date: `2026-08-03`

## Reviewed immutable Amendment 2 drafts

| Artifact | SHA-256 |
|---|---|
| `docs/decisions/INTAKE_2026-08-03_PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_2.md` | `9980d3740e1145fce3869229f77f16dc5b0fbf1e57527d543ef65084d9190402` |
| `docs/decisions/ADR_2026-08-03_PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_2.md` | `1c265ec54677ce014d4792e40309a5d0f91e4b08ce2b28ebf41795ac13b77ddf` |
| `docs/specs/PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_2_SPEC.md` | `93b55e81d8f92af2a12cc4b7a7213b6649d532bb70c1466d559173dddd5c80a2` |
| `docs/work_orders/PROJECT_KNOWLEDGE_PACK_C4_REPAIR_AMENDMENT_2_WORK_ORDER.md` | `17998426746c7d0532f940c941f89966e99efd275e5f715e76083aada40698cc` |

The Amendment 1 authority is a pushed, separate five-path commit at
`c32b5c5`; its four draft hashes and independent review hash remain
`a2b2c3e4...`, `c4c07337...`, `009f1b78...`, `b552594b...`, and
`f5db6863...`, respectively. The parent C4 authority remains pushed separately
at `8dd99c0`.

## Independent findings

- **Retained fail-stop evidence:** PASS. Amendment 2 retains, rather than
  rewrites, both prior outcomes: the original two-code validator failure and
  Amendment 1's sole fresh sequence. The recorded Amendment 1 sequence passed
  the knowledge validator, focused `77 passed`, session and 22-module catalog
  gates, then stopped at file size. Repository validation and doctor did not
  run, and no retry is recorded. This review did not rerun any gate.
- **604-line condition:** PASS. Independent read-only counting found
  `docs/implementation/EXECUTION_ROADMAP.md` at exactly 604 physical lines.
  The guard's deterministic algorithm applies a 600-line Markdown hard limit;
  the roadmap has no exception-registry entry. The retained file-size failure
  therefore follows directly from current bytes and policy.
- **Exact candidate and minimal repair:** PASS. Relative to pushed Amendment 1
  authority, the current unstaged candidate changes exactly the same ten paths
  authorized by Amendment 1, with no staged path. Amendment 2 adds no candidate
  path. The only repair edits are inside two already admitted paths:
  `docs/implementation/EXECUTION_ROADMAP.md` is condensed by at least four
  physical lines using only existing Project Knowledge Pack closure prose,
  and only that source's SHA-256 value is then replaced in
  `knowledge/manifest.json` after final roadmap bytes settle. Splitting the
  roadmap, adding an exception, changing the guard, or adding a document is
  neither necessary nor authorized.
- **Manifest state and ordering:** PASS. Before Amendment 2 repair, all three
  refreshed `project-context` pins match their current sources. The roadmap
  pin is `18c0912d152b0111b38e73e58b842edea184349e96a761199e5247d2f8023458`.
  The other two repaired pins remain fixed. Roadmap bytes must settle first;
  only its one manifest SHA-256 value may then change. Any later roadmap-byte
  change or other manifest change is a stop condition.
- **Replacement ceiling:** PASS. Amendment 1's failed sequence is immutable
  evidence, not an available retry. Amendment 2 permits exactly one
  replacement fail-stop sequence over the repaired ten-path candidate:
  knowledge validator, focused unit, session, catalog, file-size, repository,
  JSON/diff/residue/protected-hash gates, then one workspace doctor invocation.
  The first failure ends execution. No second replacement sequence, gate
  retry, helper rehearsal, generator write or doctor retry is authorized.
- **Bounded git-network reconciliation:** PASS. After fresh exact human R2
  approval, the successful path has exactly three network-bearing command
  invocations and no others:

  1. one `git push origin main` for the exact five-path Amendment 2 authority;
  2. one direct invocation of the resolved workspace-doctor script, whose
     implementation performs exactly one CVF-core
     `git fetch origin main --quiet`;
  3. one `git push origin main` for the independently approved exact ten-path
     closure commit.

  A failure retains only the prefix already executed and stops; it never
  authorizes continuing merely to reach a count of three. No project fetch,
  pull, second doctor/core fetch, push retry or post-push fetch is allowed.
  Clean `HEAD == origin/main` verification must use the local refs updated by
  the successful pushes.
- **Protected bytes:** PASS. Amendment 2 preserves the other eight candidate
  paths during its repair, the non-roadmap Project Context pins, all Amendment
  1 and parent C4 authority files, the other six BUILD paths, validator and
  both knowledge test hosts, file-size guard and registries, `.cvf/**`,
  provider configuration, application/runtime source, other handoffs and
  later-queue artifacts. The final overall repair/closure candidate remains
  exactly ten paths.
- **Call and claim ceiling:** PASS. Provider, provider-configuration, helper,
  integration rehearsal, POST, remote ingest, retrieval and all other network
  calls remain zero. The closure claim remains only a reviewed repository-owned
  INTERNAL advisory pack, deterministic local validation and previously
  reviewed disposable local transformation. It proves no automatic injection,
  provider/model behavior, DLP/minimization, Refinery, retrieval, RAG,
  learning, production readiness or Phase 3 completion.
- **Independent closure gate:** PASS. Only a fresh independent
  `FREEZE_REVIEW_PASS` over the final exact ten-path candidate and retained/new
  evidence transfers to closer and commit steward. No self-approval or waiver
  is admitted.

At review time `HEAD == origin/main == c32b5c5`, exactly ten candidate paths
are modified and unstaged, the four Amendment 2 drafts are untracked, and no
path is staged. This reviewer performed no candidate/draft edit, validator,
test, generator, doctor, fetch, network, provider, helper, POST, stage, commit
or push action.

## Authorization disposition

`AUTHORIZATION_REVIEW_PASS` is recorded with no waiver. It is not human R2
approval and does not itself authorize an authority push or repair.

**Before any Amendment 2 push or repair edit, a human operator must explicitly
approve R2 for exact Work Order SHA-256
`17998426746c7d0532f940c941f89966e99efd275e5f715e76083aada40698cc`,
including the exact successful-path ceiling of three bounded git-network
command invocations above. The exact five-path Amendment 2 authority package
must then be committed and pushed separately while all ten candidate paths
remain unstaged.** Any draft hash change invalidates this review. Until both
gates are satisfied, stop before repair, replacement verification, doctor,
staging or closure commit.
