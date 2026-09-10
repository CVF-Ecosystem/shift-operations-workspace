# P4-E SPEC Rework Response - Generation 1

- Tranche: `P4E-IDENTITY-CONVERSATION-ROUTING-2026-09-09`
- Role: `SPEC_AUTHOR`
- Source review:
  `docs/decisions/SPEC_REVIEW_2026-09-09_P4E_IDENTITY_CONVERSATION_ROUTING.md`
- Source review SHA-256:
  `a4ee2f643186ca11be7d08c8e555aa55372c63b20d58bb3ab81b24e5b83d17f8`
- Source disposition: `SPEC_REVIEW_CHANGES_REQUIRED`
- Rework disposition: `REPAIRED_PENDING_INDEPENDENT_SPEC_REREVIEW`
- Waivers requested: `NONE`
- Work Order authority: `NOT_GRANTED`

## Review acceptance and qualified disagreement

The Generation 1 review is retained unchanged as independent evidence. This
response accepts its blocking disposition and all seven repair obligations.
Acceptance of a repair obligation does not require adopting every phrase in
the review's diagnosis:

| Finding | Author position |
|---|---|
| `P4E-SPEC-REV-F1` | **Accepted.** The handoff omitted the exact command and conflated declared-family evidence with the extended repository regression. The phrase "contradicts handoff" is too strong: `72 passed, 2 skipped` is reproducible from the four-path command recorded below and was not fabricated. Its provenance was insufficient, so the MAJOR evidence disposition remains accepted. |
| `P4E-SPEC-REV-F2` | **Accepted without qualification.** R12 contradicted the terminal `REFUSED` matrix shape. |
| `P4E-SPEC-REV-F3` | **Accepted without qualification.** The SPEC failed to distinguish command/audit reason from sanitized receipt fields. |
| `P4E-SPEC-REV-F4` | **Accepted with wording qualification.** "Unreachable" is too categorical because privacy deletion also removes lookup material, but no normative action-to-reason binding existed. The ambiguity was real and has been removed by separating secret-authority rotation evidence from mapping-action receipts. |
| `P4E-SPEC-REV-F5` | **Accepted without qualification.** AC-15 required a mapping that the SPEC did not provide, and R10 retirement lacked a direct negative composition criterion. |
| `P4E-SPEC-REV-F6` | **Accepted as scope hardening.** Documentation-only empty scaffolds do not themselves contradict the canonical target set or implement forbidden behavior. The stale identity README and unqualified scaffold wording could nevertheless mislead a future worker, so all three are now explicitly bounded. |
| `P4E-SPEC-REV-F7` | **Accepted.** It was not a schema/guard failure because trigger strings are free-form. The numeric vocabulary still obscured the canonical applicability concepts; the repair normalizes all three new families. The author considers this semantic hygiene closer to MINOR than purely COSMETIC, without changing the review's retained severity. |

## Repair ledger

| Finding | Repair |
|---|---|
| F1 | Handoff now records the exact two-path declared-evidence command/result (`35 passed, 2 skipped`) and the distinct four-path extended-regression command/result (`72 passed, 2 skipped`). |
| F2 | R12 now makes unknown claim state and lineage-digest mismatch terminal persisted refusals. The placement matrix adds `UNKNOWN_CLAIM_STATE` and `LINEAGE_DIGEST_MISMATCH`; its required decision fields remain authoritative. |
| F3 | R19 now states that privacy-delete reason is restricted command/audit input and is deliberately absent from sanitized success/replay receipts. No conditional receipt field was added. |
| F4 | `SECRET_ERASURE_FAILED` was removed from mapping-action reasons. Rotation failure now produces a sanitized `TOKEN_KEY_RETIREMENT_BLOCKED` secret-authority audit/readiness record outside the mapping-action family and blocks retirement. |
| F5 | AC-16 directly proves sole production persistence composition, and a complete R1-R21 to AC traceability table was added. |
| F6 | SPEC and Work Order constraints exclude the customer/vessel scaffold directories. Their READMEs and the identity-mapping README now state the P4-E v1 boundary explicitly. |
| F7 | All three matrices now use common names for the five applicable canonical trigger concepts; unsupported adjacent-finding/lifecycle/retry aliases were removed. |

## Re-pinned matrices

- `P4E-MAPPING-ACTION-OUTCOMES`:
  `ea2af8122016a7b8ee10d9a8aa097f1b692a168a4914425172c555cd4d003e1a`
- `P4E-IDENTITY-RESOLUTION-OUTCOMES`:
  `4ef64cf1f53633974b0e585018148a8f6bbe7a16ce4683329aa29d51c0000bdc`
- `P4E-CONVERSATION-PLACEMENT-OUTCOMES`:
  `fd351b6670292e82835b4ec34c270768174758a6d8a3f1558e4e4b3a8ec8cc56`

## Verification status

- Generation 1 review byte SHA-256 remained
  `a4ee2f643186ca11be7d08c8e555aa55372c63b20d58bb3ab81b24e5b83d17f8`.
- Repaired SPEC byte SHA-256 is
  `de3af4a90425ee70f8e285fc31e12774497f7a190b776beab3ed3d32fdc90618`.
- invariant-family guard: `PASS`
- declared two-path matrix evidence: `35 passed, 2 skipped`
- extended four-path repository invariant regression: `72 passed, 2 skipped`
- session, Project Knowledge, catalog, file-size, and repository guards: `PASS`
- `git diff --check`: `PASS`

The exact test commands are recorded in the active handoff. This author does
not close the findings. An independent `SPEC_REVIEWER` must recompute the
review hash, SPEC/matrix digests, test commands, and every repair row before
changing the disposition.

## Claim boundary

Documentation, matrices, pins, and continuity only. No product source,
application schema, database migration, dependency, provider/live call,
credential, deployment, Work Order, or BUILD authority.
