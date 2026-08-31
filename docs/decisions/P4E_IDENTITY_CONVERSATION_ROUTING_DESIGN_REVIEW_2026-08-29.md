# Independent DESIGN Review — P4-E Identity Mapping and Conversation Routing

- Tranche: `P4E-IDENTITY-CONVERSATION-ROUTING-2026-08-29`
- Review role: `INDEPENDENT_DESIGN_REVIEWER`
- Phase reviewed: `DESIGN`
- Risk: `R2`
- Date: `2026-08-29`
- Reviewed artifact:
  `docs/decisions/DESIGN_2026-08-29_P4E_IDENTITY_CONVERSATION_ROUTING.md`
- Reviewed artifact SHA-256:
  `210e31d04d042d6467479cfd412c192bdf99dca74d9433fcb4d14b5621673180`
- Disposition: `DESIGN_REVIEW_CHANGES_REQUIRED`

## CVF Agent Declaration

```text
CVF Agent Declaration
Project: shift-operations-workspace
CVF Core: D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\.Controlled-Vibe-Framework-CVF @ a7a797d7111be472ef2cbd928cbeffc70ccb6bc6
Phase: p4e_identity_conversation_routing_design (DESIGN)
Risk ceiling: R2
Live evidence required: YES
Active handoff: SESSION/handoffs/P4E_IDENTITY_CONVERSATION_ROUTING_2026-08-29.md
Next allowed move: independent DESIGN review; SPEC/WORK_ORDER/BUILD and external effects remain unauthorized until DESIGN_REVIEW_PASS and explicit transition
Parked checkpoint: XR1 sibling historical-object debt remains unresolved and outside P4-C closure
Active role: INDEPENDENT_DESIGN_REVIEWER
```

Canonical bootstrap, session memory, active state and active handoff agree on
the active tranche, DESIGN phase, R2 ceiling and next move. The workspace
doctor returned `PASS WITH NOTE`: 24 checks passed and the bounded legacy-
catalog warning remained. The resolved hidden Core is clean; its HEAD,
`origin/main` and manifest pin equal the declared commit.

## Independence and review boundary

This reviewer did not author or repair the DESIGN. Review was read-only except
for this reviewer-owned artifact. No SPEC, WORK_ORDER, BUILD, product,
continuity, database, dependency, credential, installation, deployment,
commit or push action was performed. No provider call or product-network call
was made, and this review makes no claim that CVF governs AI/agent behavior.

The excluded
`docs/decisions/ASSESSMENT_2026-07-23_OPERATIONS_WORKSPACE_REPOSITIONING.md`
was not opened, read, hashed or inventoried. No broad untracked-file inventory
was used.

## Objective evidence

1. The accepted INTAKE requires a stable identity key bound to all relevant
   provider/channel/endpoint/workspace dimensions, current user and assignment
   authority, deterministic fail-closed placement, explicit privacy lifecycle,
   and invariant-family registration before implementation.
2. Current P4-C source authenticates the exact v1 metadata/body preimage but
   has no sender field. `RoutingService` generates a new proposal id, maps
   `external_message_id` to `external_id`, persists an Edge proposal, and signs
   an actor-neutral handoff with null actor/assignment/approval/conversation
   and `confirmed=False`.
3. Workspace API currently accepts a smaller closed proposal shape, generates
   another proposal id, and stores it only in
   `InMemoryExternalIngressRepository`. `ExternalIngressService` deliberately
   has no Ledger dependency. These facts support the DESIGN's need for a
   minimal P4-C seam and durable Workspace proposal persistence, but also make
   the transaction owner a required architecture decision.
4. Workspace API `get_principal` builds `Principal.role` from the verified JWT.
   `cvf_runtime.permission.require_action` authorizes directly from that role.
   The authoritative `users` row is separately readable through
   `Ledger.get_user_by_id`; therefore a permission check before the fresh user
   read remains dependent on potentially stale token role unless the DESIGN
   explicitly rebinds or compares that authority.
5. Current source has authoritative User, Shift, Incident and active Shift
   Assignment surfaces, but no CustomerContact, Customer, Vessel, Conversation
   or Workspace aggregate. The DESIGN correctly defers unsupported customer/
   vessel targets, preserves internal `POST /messages`, and treats its injected
   workspace digest only as a non-truth queue scope.
6. The DESIGN correctly declares the invariant-family standard applicable and
   separates mapping action, identity resolution and placement families. It
   also preserves the full live-evidence trigger family and does not use mock
   evidence as governance proof.

## Numbered findings

### P4E-DESIGN-REV-F1 — External identity namespace omits admitted identity dimensions

`SenderEvidenceV1` includes configured provider-account digest, subject kind,
extraction-policy identity and verification identity, but both the sender-token
HMAC tuple and `ExternalIdentityKeyV1` omit those dimensions. They cover only
workspace, endpoint, channel, normalized sender, token key id/token. If an
endpoint is rebound to another provider account, or extraction/subject
semantics change while the endpoint/channel id remains stable, an old confirmed
mapping can resolve a newly interpreted subject. That conflicts with the
INTAKE requirement that the complete available provider/channel/endpoint/
workspace scope be identity authority and with the DESIGN's own no-auto-link
rule for key changes.

Minimal repair: either add every identity-semantic dimension (at least
provider-account digest, subject kind, and extraction-policy semantic version)
to the canonical token preimage and external-identity key, or define and prove
an immutable endpoint-configuration binding that makes those values
inseparable and forces stale/refusal plus human-reviewed correction on change.
The signed handoff and stored evidence must bind the same canonical tuple.

### P4E-DESIGN-REV-F2 — Permission precedes fresh authoritative role resolution

The human-action sequence performs action permission at step 2, then reads the
authoritative active User and current role at step 3. Current permission code
uses `Principal.role` from the JWT. The DESIGN does not require equality with
the fresh stored role or rerun permission using a principal reconstructed from
that row. A still-valid elevated token can therefore pass the protected mapping
or binding permission after the user has been demoted, even though the later
lookup observes the demotion.

Minimal repair: after cryptographic JWT identity admission, resolve the active
User first and make the fresh stored role the sole permission input (or fail
closed on any token/stored-role mismatch), then revalidate that authority in
the mutation transaction. Apply the same rule to propose, confirm, reject,
revoke, correct and binding create/replace actions.

### P4E-DESIGN-REV-F3 — Proposal-to-placement transaction ownership is unresolved

Section 2 assigns operations-ledger only P4-E persistence, while section 9
assigns Workspace API a new durable external-proposal repository. Section 6
nevertheless requires proposal existence/version validation in the same
governed Ledger transaction as placement. Current source has two separate
stores: Edge SQL proposal persistence and Workspace API process-local proposal
persistence with no Ledger dependency. The DESIGN does not select a canonical
Workspace proposal store, connection/unit-of-work owner, or cross-store
protocol capable of satisfying its own same-transaction/TOCTOU claim.

Minimal repair: choose one durable Workspace proposal persistence owner and
state the exact atomicity model. Either admit immutable proposals into a table
participating in the same Ledger unit-of-work as placement, while preserving
P4-C contract ownership, or define a version/digest-pinned cross-store protocol
with fail-closed revalidation, idempotent retry/compensation and a bounded claim
that does not assert single-transaction atomicity. Also resolve whether the
post-persist placement invocation is synchronous, queued or retry-driven.

### P4E-DESIGN-REV-F4 — Opaque-only sender evidence has no feasible governed human-selection path

The first observation stores only an opaque token/evidence tuple and may not
choose a target. A human proposer must then select a user for that observation,
and a different confirmer must re-enter the exact raw sender value. The DESIGN
forbids raw sender persistence/logging and provider lookup, but does not define
how either human can identify/select the relevant observation without relying
on candidate content, an undisclosed evidence viewer, or live provider access.
Confirmation re-entry alone does not explain how the proposal was associated
with the intended observed subject.

Minimal repair: define a privacy-preserving management flow. For example,
propose and confirm can each accept the sender value only as a transient no-log
input, recompute the complete scoped token, locate the stored observation and
discard the value; alternatively specify a separately authorized minimized
display/evidence port and its disclosure/audit rules. State how separation of
duty, idempotency and correction work without adding a hidden UI/provider
dependency or reading candidate content as identity authority.

### P4E-DESIGN-REV-F5 — `WORKSPACE` and `FALLBACK` collapse into one queue without distinct semantics

The supported binding targets list both `WORKSPACE` and `FALLBACK`, but each is
described as the non-truth manual-triage queue. Section 8 also routes no-mapping,
legacy-evidence and unsupported-target cases to `FALLBACK` without actor
authority. It is therefore unclear whether `FALLBACK` is a human-created
`RouteBindingV1` target, a system terminal disposition, or merely the same
physical queue used by an explicit `WORKSPACE` binding. That ambiguity affects
authorization, conversation-key fields, outcome matrices and the meaning of a
successful placement.

Minimal repair: define distinct semantics. A narrow resolution is to reserve
`WORKSPACE` for an explicit human-authorized binding to the configured triage
scope and make `FALLBACK` only a system disposition with no active binding,
actor or privileged target. If both can be bindings, define non-overlapping
authority, fields and outcomes for each.

## Waivers

`NONE`.

## Disposition

`DESIGN_REVIEW_CHANGES_REQUIRED` — findings
`P4E-DESIGN-REV-F1..F5` are open; waivers `NONE`.

Repair is bounded to the reviewed DESIGN and any DESIGN-owned digest/reference
updates needed to close these five findings. This reviewer does not authorize
SPEC, WORK_ORDER, BUILD, product/database edits, provider/network calls,
credentials, installation, deployment, commit or push. After repair, a
different independent DESIGN rereview must verify the complete artifact and
recompute its SHA-256 before any phase transition.

---

## Independent DESIGN Rereview — repaired artifact

- Rereview role: `INDEPENDENT_DESIGN_REREVIEWER`
- Date: `2026-08-29`
- Independence: this rereviewer did not author, repair or perform the first
  review of the DESIGN
- Repaired artifact SHA-256:
  `2d0975a301a15c7b8a85eba121410391ddca2f067b16d9c5089d79edb9c397b9`
- Final disposition: `DESIGN_REVIEW_PASS`

### Rereviewer CVF Agent Declaration

```text
CVF Agent Declaration
Project: shift-operations-workspace
CVF Core: D:\UNG DUNG AI\TOOL AI 2026\CVF-Workspace\.Controlled-Vibe-Framework-CVF @ a7a797d7111be472ef2cbd928cbeffc70ccb6bc6
Phase: p4e_identity_conversation_routing_design (DESIGN)
Risk ceiling: R2
Live evidence required: YES
Active handoff: SESSION/handoffs/P4E_IDENTITY_CONVERSATION_ROUTING_2026-08-29.md
Next allowed move: independent rereview of the repaired P4-E DESIGN; SPEC, WORK_ORDER, BUILD and external effects remain unauthorized pending a pass and explicit transition
Parked checkpoint: XR1 sibling historical-object debt remains unresolved and outside P4-E
Active role: INDEPENDENT_DESIGN_REREVIEWER
```

The canonical bootstrap projection, session memory, active state and active
handoff agree on the tranche, DESIGN phase, R2 ceiling and review boundary.
The workspace doctor returned `PASS WITH NOTE` with 24 passes and the bounded
legacy-catalog warning. The hidden Core was clean and its HEAD, `origin/main`
and manifest pin all equalled the declared commit.

### Rereview boundary

This rereview was read-only except for this append to the existing reviewer-
owned review artifact. The protected ASSESSMENT file was not opened, read,
hashed or inventoried, and no broad untracked inventory was used. No SPEC,
WORK_ORDER, BUILD, product, continuity, database, dependency, credential,
installation, deployment, commit or push action was performed. No provider or
product-network call was made. This is deterministic DESIGN review evidence,
not a claim that CVF governs AI or agent behavior.

### Finding closure evidence

1. `P4E-DESIGN-REV-F1 — CLOSED`. Sections 3 and 4 now bind the HMAC token
   preimage and `ExternalIdentityKeyV1` to the complete identity-semantic
   namespace: workspace digest, endpoint, channel, configured provider-account
   digest, subject kind, extraction-policy id and semantic version,
   verification scheme/version, normalized sender bytes/token and token key
   id/version. The signed handoff carries the same semantic selectors plus
   provenance digests. Any account, subject, extraction, verification or key
   change creates a new key and requires a human-reviewed correction; it
   cannot inherit an old confirmation.
2. `P4E-DESIGN-REV-F2 — CLOSED`. Section 5 admits only the verified JWT subject,
   then reads the authoritative active User and reconstructs permission
   authority from the fresh stored role. It explicitly excludes the JWT role
   claim from permission input and requires an actor reread plus fresh-role
   permission rerun inside the mutation transaction for every mapping and
   binding management action. Demotion, inactivity or subject mismatch refuses
   before mutation.
3. `P4E-DESIGN-REV-F3 — CLOSED`. Sections 2, 6 and 9 select operations-ledger
   as the Workspace-side physical persistence and unit-of-work owner for the
   immutable admitted proposal, exactly one pending placement-work item and
   P4-E records, while P4-C retains semantic proposal ownership and Workspace
   API owns composition. Transaction A durably admits proposal plus work;
   transaction B locks work, rereads digest-pinned lineage and current
   authority, then atomically writes one terminal placement decision and
   completes work. Transient failure rolls back B and leaves pending work for
   bounded idempotent retry. The design expressly limits `ROUTED` to durable
   actor-neutral Workspace admission and makes no cross-step atomicity or
   exactly-once claim.
4. `P4E-DESIGN-REV-F4 — CLOSED`. Sections 4 and 5 define a privacy-safe
   management flow. The authorized list exposes only opaque observation id and
   minimized selector/time metadata. Propose supplies the exact sender value
   transiently, recomputes the complete scoped token against the selected
   immutable observation and discards the value. A different confirmer must
   re-enter the value and obtain the identical key before target lookup or
   mutation. Correction repeats the two-human successor flow. Raw sender,
   sender token and candidate content are excluded from persistence, audit,
   receipts and logs; no hidden provider lookup, candidate-content authority
   or undisclosed evidence viewer is required.
5. `P4E-DESIGN-REV-F5 — CLOSED`. Sections 7 and 8 now make `WORKSPACE` a
   positive, explicit human-authorized binding to the configured single-
   workspace triage scope. `FALLBACK` is not a binding target; it is a system
   terminal non-privileged disposition with no actor, target binding or
   conversation key, even if it shares a physical triage queue. Their
   authorization, fields and outcome meanings are therefore non-overlapping.

### Adjacent-risk review

The repaired DESIGN also remains closed on adjacent R2 risks: identity linkage
never supplies authentication or frozen role/assignment authority; target and
assignment eligibility are revalidated at bind and route time; unsupported
customer/contact/vessel kinds remain unactivatable; multiple current mappings
or bindings fail as corruption rather than priority routing; fallback/refusal
forbid conversation keys; durable proposal replay/collision and pending-work
recovery are digest-pinned; privacy retention, deletion/tombstone, key rotation
and allowlisted telemetry remain bounded for SPEC; internal `POST /messages`,
P4-C lineage ownership and P4-D delivery ownership remain unchanged. The three
triggered invariant families are separately owned and required for registry/
digest binding before implementation. No additional DESIGN-level finding was
identified.

### Rereview findings

`NONE`.

### Rereview waivers

`NONE`.

### Final disposition

`DESIGN_REVIEW_PASS` — original findings `P4E-DESIGN-REV-F1..F5` are closed;
final findings/waivers `NONE/NONE`.

This pass accepts only the repaired architecture at DESIGN. It does not open
SPEC automatically and grants no WORK_ORDER, BUILD, product/database change,
provider/network call, credential, installation, deployment, commit or push.
The ORCHESTRATOR may open SPEC only through an explicit phase transition.
