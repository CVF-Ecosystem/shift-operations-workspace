# Agent Handoff - P4-A1 Governed Retrieval Work Order

Date: 2026-08-10
Repository: `shift-operations-workspace`
Risk: `R2`
Current mode: `p4a1_governed_retrieval_build_authorized`
Active role: `IMPLEMENTATION_WORKER`
Commit mode: `WORKER_MUST_NOT_COMMIT`
Execution base HEAD: `d878001b6a1a536218b2c66019243510ef3f7aec`

## Startup acknowledgment

Startup acknowledged: current mode=`p4a1_governed_retrieval_build_authorized`;
active handoff=`SESSION/handoffs/AGENT_HANDOFF_2026-08-10_P4A1_GOVERNED_RETRIEVAL_WORK_ORDER.md`;
next allowed move=one separate worker implements the exact31 Work Order and
returns `COMPLETE_PENDING_REVIEW` without commit; parked checkpoint=independent
BUILD review after worker return, with all deeper lanes still parked.

## Authority packet

| Artifact | SHA-256 | Disposition |
|---|---|---|
| `docs/decisions/INTAKE_2026-08-10_P4A1_GOVERNED_RETRIEVAL.md` | `7c32cd312ad4d889aa5039fbc32c032ee4312e0976224411cac106145b1ffde7` | accepted parent |
| `docs/decisions/ADR_2026-08-10_P4A1_GOVERNED_RETRIEVAL.md` | `8dbdfbaded8ed523eb465bc3c657620a323fafae465f5d0d0d66fe8cac6aa4fc` | accepted 12-decision design |
| `docs/specs/P4A1_GOVERNED_RETRIEVAL_SPEC.md` | `f2385689b4ccca2bf669500bc984383f223e62b46fbf5a87f54587ad9530bb09` | normative 12 R / 12 AC |
| `docs/specs/P4A1_GOVERNED_RETRIEVAL_RECEIPT_CONTRACT.md` | `11af01c38a45e1891b752eb65c49c86827a6504c95d35d9ab2e8206a148df619` | inseparable normative R9 appendix |
| `docs/decisions/P4A1_GOVERNED_RETRIEVAL_SPEC_REVIEW.md` | `ae7bf0275504abe650afa3286e5864ec97a902b76fe1520651d653a9d644c394` | `SPEC_REVIEW_PASS`; none/none |
| `docs/work_orders/P4A1_GOVERNED_RETRIEVAL_FOUNDATION_WORK_ORDER.md` | `b9889e4e207f408c705210207bfd1fcb32720ad7258522c2d0446e0d59d837e6` | authorized exact31 |
| `docs/decisions/P4A1_GOVERNED_RETRIEVAL_WORK_ORDER_AUTHORIZATION_REVIEW.md` | `00f9b927ad7206c54c07b4342810c690345cd3e1569174b5c1cc8e14ada6484a` | `WORK_ORDER_AUTHORIZATION_REVIEW_PASS`; none/none |

The Work Order review closed F1-F3 and the roadmap/Knowledge manifest-pin
blocker without waiver. This handoff completes its exact-six pre-BUILD
continuity release. The Work Order and review remain the implementation
authority; this handoff does not widen their paths or claims.

## Exact worker boundary

The Work Order owns exactly 31 BUILD paths: 2 existing clean paths and 29 new
paths. Pre-release inspection returned `count=31`, `dirty=0`. The worker must
recompute this before editing and stop on any drift.

Only `PROJECT_KNOWLEDGE_LOCAL_V1` may produce positive evidence. These remain
disabled and must not be read or enabled:

- `SHIFT_CONFIRMED_OPERATIONS_V1`;
- `SHIFT_ADVISORY_MESSAGES_V1`;
- all six canonical digest owners.

The worker performs no provider, network, product API, external database,
PostgreSQL, Docker, audit write, API route, UI, deployment, vector/index, RAG,
or persistence action. Disposable local SQLite is allowed only for the exact
SqlLedger parity tests named by the Work Order.

## Pre-existing non-BUILD dirty manifest

Canonical manifest algorithm: sort paths with the PowerShell `Sort-Object`
behavior used at release; serialize each row as
`status<TAB>path<TAB>sha256<LF>` in the order below; SHA-256 the UTF-8 bytes.

- Count: `15`
- Manifest SHA-256:
  `98837a163e436c76412177356dd32f3bbcb9346f0c8c19455f3c46cdd18153a0`
- Successor handoff disposition: excluded from this pre-existing manifest and
  pinned separately by its whole-file SHA-256 in the dispatch prompt.

| Status | Path | SHA-256 |
|---|---|---|
| ` M` | `CVF_SESSION/ACTIVE_SESSION_STATE.json` | `9f588057de52c24eb62ba35be6510e30b3810acf333de95a5ad87ad89ed88408` |
| `??` | `docs/decisions/ADR_2026-08-10_P4A1_GOVERNED_RETRIEVAL.md` | `8dbdfbaded8ed523eb465bc3c657620a323fafae465f5d0d0d66fe8cac6aa4fc` |
| `??` | `docs/decisions/INTAKE_2026-08-10_P4A1_GOVERNED_RETRIEVAL.md` | `7c32cd312ad4d889aa5039fbc32c032ee4312e0976224411cac106145b1ffde7` |
| `??` | `docs/decisions/P4A1_GOVERNED_RETRIEVAL_SPEC_REVIEW.md` | `ae7bf0275504abe650afa3286e5864ec97a902b76fe1520651d653a9d644c394` |
| `??` | `docs/decisions/P4A1_GOVERNED_RETRIEVAL_WORK_ORDER_AUTHORIZATION_REVIEW.md` | `00f9b927ad7206c54c07b4342810c690345cd3e1569174b5c1cc8e14ada6484a` |
| ` M` | `docs/implementation/EXECUTION_ROADMAP.md` | `8daada8f9988798c992c5f4ddc5e8c63c09a8948afecb0d9ea952d07a635cb3a` |
| `??` | `docs/implementation/P4_CROSS_REPOSITORY_REFERENCE_COORDINATION.md` | `ec97f194b1f65f22feba2ca3fccbf8e07f7ed36355d86e5c387fa1ab9060b8ab` |
| `??` | `docs/specs/P4A1_GOVERNED_RETRIEVAL_RECEIPT_CONTRACT.md` | `11af01c38a45e1891b752eb65c49c86827a6504c95d35d9ab2e8206a148df619` |
| `??` | `docs/specs/P4A1_GOVERNED_RETRIEVAL_SPEC.md` | `f2385689b4ccca2bf669500bc984383f223e62b46fbf5a87f54587ad9530bb09` |
| `??` | `docs/work_orders/P4A1_GOVERNED_RETRIEVAL_FOUNDATION_WORK_ORDER.md` | `b9889e4e207f408c705210207bfd1fcb32720ad7258522c2d0446e0d59d837e6` |
| ` M` | `knowledge/manifest.json` | `c21c098c10d6c20e3ee6c71450b6b0a86c099dd7b16f32f8a6c2654622bc8952` |
| ` M` | `knowledge/PROJECT_CONTEXT.md` | `f2318222889f428f1b6951510c79e2889255e3e3594179076efbfdb54c363a34` |
| ` M` | `SESSION/ACTIVE_SESSION_STATE.json` | `ec55174c9a02cca8dd50ac0f345540aa860f4f803a02b758a6e4d3a6038009d7` |
| `??` | `SESSION/handoffs/AGENT_HANDOFF_2026-08-10_P4A1_GOVERNED_RETRIEVAL_INTAKE.md` | `4330ff25ae54321ee589e9393d18de1970b64934e9b19629455cf4e13987093b` |
| ` M` | `SESSION/SESSION_MEMORY.md` | `5d7d82bcb1a7826e1d38707f588a1e66b12e7ea13bd32012715665e53b492c4d` |

The worker must not change any row above. It returns a fresh recomputation
showing all 15 hashes unchanged plus a separate exact31 diff.

## Pre-BUILD release changes

The session-sync steward changed only the six authorized non-BUILD paths:

1. canonical session state;
2. compatibility mirror state;
3. session memory;
4. roadmap next-move sentence only;
5. Project Knowledge manifest's Project Context roadmap SHA-256 pin only; and
6. this successor handoff.

The roadmap P4-A1 checkbox remains open. No catalog/status/source/runtime file
was changed by this release. No BUILD, stage, commit, push, provider, network,
product API, external database, or local SQLite call occurred.

## Required worker return

Return `COMPLETE_PENDING_REVIEW` or `BLOCKED` exactly as the Work Order defines.
Keep HEAD unchanged and all BUILD changes unstaged. Include exact31 diff,
unchanged 15-row manifest evidence, focused/full/gate results, local SQLite
count, external-call/audit counts, file sizes, and the bounded claim.

Stop after return. Only the independent BUILD reviewer/closer may proceed.

## Parked boundary

P4-A, P4-A2, LPCI1 Web answer/provider behavior, API keys, LLM calls, semantic
or vector RAG, full/restricted/confidential documents, durable audit or
persistence, production API/UI, deployment, operational corpus enablement,
digest owners, and deeper project development all require fresh authority.
