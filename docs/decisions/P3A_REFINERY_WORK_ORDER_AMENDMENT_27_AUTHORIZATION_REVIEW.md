# P3-A Refinery Work Order Amendment 27 — Authorization Review

- Review date: `2026-08-04`
- Role: `REVIEWER` (independent authorization review)
- Risk / phase: `R2 / WORK_ORDER`
- Amendment reviewed:
  `docs/work_orders/P3A_REFINERY_WORK_ORDER_AMENDMENT_27.md`
- Reviewed SHA-256:
  `94a38f86607bd87ddfe7365eae0e38203659e147a8f5246efb2f6d8fd79234b5`
- Trigger review SHA-256:
  `de226b3d74e038ba239b19afeafeb39dad98197cd08f6d6150589b3e677f3ce6`
- Provider/network/remote-ingest calls during review: `0/0/0`
- Waivers: `NONE`

## Disposition

`WORK_ORDER_AMENDMENT_AUTHORIZATION_REVIEW_FAIL`

Amendment 27 selects the correct minimum two-path repair and preserves the
exact35 candidate boundary, but its proposed output is not independently
constructible from the reviewed artifact. The asserted post-hashes and
post-stable33 manifest therefore cannot be reproduced without inventing
unreviewed status strings. Authorization must fail before checkpoint, R2 or
repair.

## Reproduced pre-state and scope

The current candidate and trigger finding reproduce:

| Binding | Expected | Reproduced | Result |
|---|---:|---:|---|
| Final candidate paths | `35` | `35` | PASS |
| Staged paths | `0` | `0` | PASS |
| Stable paths | `33` | `33` | PASS |
| Stable33 manifest | `4d0ba0a8b901d5cd097f59111f959b667725df651ddcbd0bbb530c0953f6661a` | same | PASS |
| Repair paths | exact `2` | status + knowledge manifest | PASS |
| Protected paths | `31` | `31` | PASS |
| Protected31 manifest | `00bb194572d0c1dcca5342feca0f5afa43ee4cb594eb6b5ca317da0c3090557a` | same | PASS |
| Status pre-hash | `9d9d7d2ff387365ce018cc51de07a24d1eb3a21c08cb723feb3d74e114ae5eb6` | same | PASS |
| Knowledge pre-hash | `cbf115da32e5ad9418f1d91678d2ec2f875e174ee434f5762648325f63da4f80` | same | PASS |

The exact2 scope is necessary and non-expansive. Updating
`IMPLEMENTATION_STATUS.json` closes the trigger finding; updating only its
source pin in `knowledge/manifest.json` preserves knowledge-pack integrity.
All other exact35 paths are correctly protected.

## Finding A27-AUTH-F1 — exact repair output is not frozen

The Work Order requires one atomic exact patch and binds these proposed outputs:

- status post-hash
  `18b21d8d263ff0518389ab413550b006661d9fabee83cb373320235a6d9ab404`;
- knowledge-manifest post-hash
  `251ca93f47a6527a0d941b7cbd371130a041fb21154ab269a05153b7751844a4`;
- post-stable33 manifest
  `f6ed2c05f7db2737d5d668568eaaf0ea93e22dd66ba19120b10330aab27ee5ff`.

However, the artifact does not contain the exact patch or exact replacement
strings needed to produce the status post-image:

1. it specifies only the suffix, not the exact full repository `status` value;
2. it provides an exact literal only for `governance_disposition`'s leading
   token, followed by semantic prose rather than the complete string;
3. `authority_commits`, `changed_set`, `evidence_status`, and
   `next_governed_move` are described semantically, with no exact literals;
4. it says to change "six string values inside `p3a_refinery`" but enumerates
   only five changed fields and explicitly preserves the other two strings
   (`spec` and `claim_boundary`). The current object has seven string fields,
   so the count and enumerated contract disagree.

The knowledge-manifest one-line replacement is exact, but its new pin depends
on the unconstructible status post-image. A reviewer cannot derive or simulate
the asserted status post-hash from A27 without choosing wording, punctuation
and spacing that the Work Order never authorized. A post-hash alone proves no
semantic mapping and is not a substitute for a frozen patch or exact output.

This finding has no waiver. Amend A27 to embed a canonical exact patch or a
SHA-bound execution sheet containing every complete replacement string and the
one manifest-pin replacement. Correct the changed-field count. A fresh
independent re-review must then reproduce both post-hashes and the
post-stable33 manifest in memory before any checkpoint or R2.

## Remaining authorization assessment

Subject to F1 repair, the rest of A27 is sufficient and non-expansive:

- ordered preflight binds authority topology, exact35, staged0, both
  pre-hashes, stable33 and protected31;
- one atomic exact2 repair is appropriate;
- immediate post-hash/scope assertions precede all later gates;
- JSON, knowledge validation/focused tests, session, file-size, repository,
  secret, diff and final audits are proportionate for status/pin-only changes;
- omitting full and Refinery suite reruns is acceptable because source, tests,
  contracts, fixtures and catalog bytes remain protected;
- stop-first/no-retry and zero provider/network/remote-ingest/POST boundaries
  are explicit;
- no BUILD commit, self-review, FREEZE, waiver or later-lane authority leaks
  through the amendment.

## Fresh R2 disposition

No fresh R2 literal or UTF-8 digest is approved by this failed review. The
pending value in canonical state is not consumable authority. An exact proposed
one-line R2 and its UTF-8 SHA-256 may be recorded only after the amended repair
output receives independent authorization review PASS.

## Claim boundary

This is authorization-review evidence only. It performs no repair and makes no
claim about provider behavior, remote ingestion, runtime `data_scope`,
retrieval/RAG, production readiness, BUILD completion, P3-A closure or Phase 3
completion.
