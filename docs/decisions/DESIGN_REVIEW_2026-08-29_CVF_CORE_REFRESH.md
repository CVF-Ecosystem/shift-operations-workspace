# Independent DESIGN Review — CVF Public-Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-29`
- Review date: `2026-08-29`
- Role: `INDEPENDENT_DESIGN_REVIEWER`
- Risk: `R2`
- Reviewed DESIGN raw SHA-256:
  `c4ee5d1bd316d4c1b455fa84b95f2ada0fe84e5395656c8806fc64cf0ab2e543`
- Parent INTAKE raw SHA-256:
  `a86b2d2d4a93e003fe3a2c5a6bebba7e7ef723a6e4352f42aa77c3dbba87cf76`
- Parent INTAKE review raw SHA-256:
  `fa58f4a9f04f01d9e8986f2706b52be778e7cad75239be766825e68c424e630f`
- Disposition: `DESIGN_REVIEW_CHANGES_REQUIRED`

## Review boundary

This was a local, read-only source/evidence review except for creation of this
reviewer-owned artifact. It performed no fetch, doctor, reconciler,
initializer, hidden-Core/workspace-root/product/continuity mutation, provider
call, credential use, installation, database action, deployment, commit or
push. The protected operator assessment was excluded completely, and no broad
untracked inventory was performed.

## Independently verified architecture

1. The accepted fresh INTAKE and its independent review bind the old Core
   `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`, frozen target
   `06c3d040a3dc8fa22fa27f2f9c3e40739def075e`, R2 boundary, P4-E parking and
   narrow deterministic reconciliation claim. Local no-fetch Git checks still
   show clean old Core `HEAD`, locally available `origin/main` at the frozen
   target, and downstream `HEAD == origin/main == a8e2ad8...` with staged zero.
2. The selected two-script sequence is feasible. The sanctioned reconciler,
   root-wrapper installer and doctor are byte-identical at old and target Core;
   their Git blob identities are respectively `4b705c6b...`, `234e1ea7...` and
   `2ad83efe...`. The downstream initializer consumes the patched full pin,
   fetches once, safely advances only to that pin, regenerates the ignored
   binding and invokes the doctor.
3. Direct source inspection confirms the closed 17-entry root set: one
   reconciler-owned `WORKSPACE_RULES.md` write, thirteen installer write or
   create-if-missing sites, and the three explicit overlay-artifact deletion
   sites. The `operator-local` active profile does not enter the reconciler's
   public-profile synchronization branch. Per-path `CREATE`/`UPDATE`/`DELETE`/
   `NO_CHANGE` classification and `17/17` success/rollback accounting are
   therefore well founded.
4. The successful public-network graph is exactly three ordered top-level Git
   operations: reconciler clone, initializer fetch, then initializer-owned
   doctor fetch. Post-clone equality before pin edits and subsequent doctor
   equality correctly make target movement a rollback condition. Failure owns
   only its reached `0..3` prefix plus at most one rollback-verifier doctor.
5. Pin sequencing is sound: reconciler first; then exactly-one full-hash edits
   to manifest and the generated AGENTS header; then initializer regeneration
   and five-way target equality across Core `HEAD`, local `origin/main`,
   manifest, AGENTS and ignored binding.
6. The 13 tracked worker paths, additional ignored binding and separately
   reviewer-owned completion artifact are explicitly separated. Dedicated P4-E
   decision/handoff artifacts remain byte-protected, while shared continuity
   carriers may change only to preserve the semantic P4-E
   `DESIGN_REVIEW_PASS` checkpoint. Product/runtime/database/catalog paths are
   excluded.
7. Reviewer-time target movement correctly routes to a distinct preauthorized
   `REPAIR_WORKER` for rollback only from frozen BUILD preimages. It does not
   allow the reviewer to repair, retry reconciliation or silently rebase the
   target.
8. The invariant-family trigger is correctly `APPLICABLE`: three terminal
   outcomes, conditional fields/counters and worker/reviewer validator
   surfaces require one new matrix registered and digest-pinned before SPEC
   review.
9. The claim boundary is appropriately narrow. Pin/freshness reconciliation
   does not adopt Core runtime into the product, prove AI-agent governance, or
   establish deployment/production readiness; no provider call belongs in
   this DESIGN review.

## Numbered finding

1. **`CORE-REFRESH-DESIGN-REV-F1` — absent worker evidence paths have no
   unambiguous preimage/rollback rule.** Section 3 requires a raw preimage for
   every mutable downstream carrier in section 7, although the root-effects
   receipt and worker-return paths may be absent before BUILD. Section 6 then
   says to restore downstream carriers to their observed preimages, while
   sections 6 and 8 also require failure evidence to be retained at those two
   canonical paths. For an absent-before-BUILD evidence path, there is neither
   a raw byte preimage to restore nor a stated precedence between restoring
   absence and retaining terminal failure evidence. This makes the otherwise
   bounded 13-path rollback contract non-executable without interpretation.

   Repair DESIGN by classifying each of the 13 paths as a pin carrier, shared
   continuity carrier or evidence carrier; record `PRESENT` plus raw preimage
   or explicit `ABSENT` for every path; and state exact terminal behavior for
   newly created evidence paths. A sound rule may retain the two canonical
   evidence artifacts as the explicit exception after restoring all pin and
   shared-carrier preimages, provided their absence/post-state and hashes are
   accounted for and no other newly created downstream path survives.

## Waivers

`NONE`.

## Deterministic checks

- Session-state/mirror guard: `PASS`.
- Project Knowledge guard: `PASS`.
- Invariant-family guard: `PASS`.
- Catalog drift guard: `PASS`.
- File-size guard: `PASS`.
- Scoped diff check: `PASS`.
- Staged set: empty.

## Final disposition

`DESIGN_REVIEW_CHANGES_REQUIRED` — one blocking finding, waivers `NONE`.

Return F1 to a declared `REPAIR_WORKER`. SPEC, Work Order, reconciliation,
network/root effects, P4-E SPEC, commit and push remain unauthorized. After a
bounded DESIGN repair, a fresh independent rereview must recompute the DESIGN
hash and close or retain F1 explicitly.

---

## Independent DESIGN rereview — 2026-08-29

- Role: `INDEPENDENT_DESIGN_REREVIEWER`
- Recomputed repaired DESIGN raw SHA-256:
  `4d6f0757ebf0138d92b1af85903c5822b1265134ba18d7f8bf6457ef6f2877c2`
- Prior finding `CORE-REFRESH-DESIGN-REV-F1`: `CLOSED`
- Disposition: `DESIGN_REVIEW_CHANGES_REQUIRED`

### Rereview boundary

This rereview independently inspected the repaired DESIGN and the prior review
artifact using local, allowlisted, read-only checks. It appended only this
reviewer-owned section. It performed no network, doctor, reconciler,
initializer, Core/workspace-root/product/continuity mutation, provider call,
credential use, installation, database action, deployment, commit or push. It
did not observe or inventory the protected operator assessment and performed no
broad untracked inventory.

### Closure of `CORE-REFRESH-DESIGN-REV-F1`

`CLOSED`. The repaired DESIGN now provides an executable and internally
consistent absence/restoration rule:

1. Section 7 classifies all 13 tracked worker paths exactly as two pin
   carriers, nine shared continuity carriers and two evidence carriers.
2. Section 3 requires `PRESENT` plus raw preimage or explicit `ABSENT` for each
   of those 13 paths and the ignored local binding. Both canonical evidence
   paths must be `ABSENT` before a first BUILD.
3. Section 6 first restores the two pins, nine shared carriers and binding to
   their observed preimages. Only after that checkpoint may shared continuity
   carriers record terminal failure; pins and binding remain restored.
4. The two canonical evidence artifacts are the sole explicit exception to
   restoring their recorded absence. Each must be accounted as `CREATE` plus
   post-hash, and no other absent-before-BUILD downstream path may survive.
5. Section 8 forbids overwriting those paths on retry and requires a separately
   reviewed attempt-path change.

### New adjacent finding

1. **`CORE-REFRESH-DESIGN-REV-F2` — terminal evidence post-hash ownership is
   self-referential or unspecified.** Sections 6 and 8 require both newly
   created evidence artifacts to be recorded as `CREATE` plus raw post-hash,
   while section 8 makes the JSON root-effects receipt the canonical semantic
   owner and the Markdown worker return only its summary. With exactly those
   two permitted evidence carriers, neither artifact can contain its own final
   raw SHA-256; having them contain one another's final raw hashes is circular.
   The completion-review artifact is reviewer-owned and may not exist on a
   terminal failure, so it cannot silently satisfy the worker's rollback
   evidence obligation.

   Repair DESIGN by assigning every required raw evidence-artifact post-hash
   to an explicit, non-self-referential terminal record whose path, owner,
   creation order, success/failure availability and path-ceiling treatment are
   declared. Alternatively, narrow the worker receipt contract so self-hash is
   explicitly not required and state exactly which later independent artifact
   records each final raw hash. The repair must preserve the two-evidence-path
   absence exception and must not introduce an undeclared surviving path.

### Adjacent-risk result

No other new adjacent architecture finding was identified. The repaired DESIGN
continues to preserve the frozen target, ordered three-operation success graph,
five-way target equality, 17-root ceiling, protected P4-E boundary,
reviewer-time target-movement rollback route, invariant-family trigger and
narrow non-provider claim boundary.

### Rereview findings and waivers

- Findings: `CORE-REFRESH-DESIGN-REV-F2` open; prior F1 closed.
- Waivers: `NONE`.

### Final rereview disposition

`DESIGN_REVIEW_CHANGES_REQUIRED` — F1 is closed, but F2 blocks an executable
terminal evidence contract. Return F2 to a declared `REPAIR_WORKER`; SPEC, Work
Order, reconciliation, network/root effects, P4-E SPEC, commit and push remain
unauthorized. A fresh independent rereview must recompute the repaired DESIGN
hash and close or retain F2 explicitly.

---

## Independent DESIGN rereview — F2 closure — 2026-08-29

- Role: `INDEPENDENT_DESIGN_REREVIEWER`
- Recomputed repaired DESIGN raw SHA-256:
  `2e383c0918a77d3262b9a065e8cbeca5a4e5798dfd7e4771c311f4f0af049443`
- Prior finding `CORE-REFRESH-DESIGN-REV-F1`: `CLOSED`
- Prior finding `CORE-REFRESH-DESIGN-REV-F2`: `CLOSED`
- Disposition: `DESIGN_REVIEW_PASS`

### Rereview boundary

This fresh rereview independently inspected the current repaired DESIGN and
the complete prior review history using only local, allowlisted, read-only
checks. Its sole mutation is this appended reviewer-owned section. It performed
no network, doctor, reconciler, initializer, Core/workspace-root/product/
continuity mutation, provider call, credential use, installation, database
action, deployment, commit or push. It did not touch or inventory the protected
operator assessment and performed no broad untracked inventory.

### Findings closure

1. `CORE-REFRESH-DESIGN-REV-F1` remains `CLOSED`. The DESIGN still classifies
   exactly two pin, nine shared-continuity and two evidence carriers; records
   every carrier as `PRESENT` plus raw preimage or explicit `ABSENT`; requires
   both evidence carriers to be initially `ABSENT`; and makes those two
   canonical evidence paths the sole surviving `CREATE` exception after
   rollback. No other absent-before-BUILD downstream path may survive.
2. `CORE-REFRESH-DESIGN-REV-F2` is `CLOSED`. The two canonical worker evidence
   paths remain available for all three terminal worker outcomes, including
   both rollback outcomes. Neither worker artifact contains its own final raw
   hash or requires the other's final hash, so no self-hash or cross-hash cycle
   exists. For every worker outcome, a later independent terminal reviewer
   recomputes the evidence and records the final raw SHA-256 of both worker
   artifacts in the separately owned
   `docs/decisions/CVF_CORE_REFRESH_COMPLETION_REVIEW_2026-08-29.md`. That
   completion review does not self-hash.

### Adjacent-risk result

No new adjacent DESIGN finding was identified. In particular:

- terminal review is required for `SUCCESS`, `FAILURE_ROLLED_BACK` and
  `FAILURE_ROLLBACK_INCOMPLETE`, so failure review availability is explicit;
- the worker ceiling remains exactly 13 tracked paths plus the ignored local
  binding, while the completion-review path is separately declared and owned
  only by the independent reviewer;
- the canonical JSON worker receipt remains the sole worker semantic owner,
  and the Markdown worker return remains only its non-competing summary;
- the invariant-family trigger remains `APPLICABLE`, with the SPEC_AUTHOR
  required to register `CVF-CORE-REFRESH-OUTCOMES-2026-08-29`, create its sole
  semantic matrix and bind its digest before SPEC review; and
- the frozen target, rollback-only repair route, protected P4-E boundary and
  narrow non-provider claim boundary remain intact.

### Final rereview disposition

`DESIGN_REVIEW_PASS` — prior F1 and F2 are closed; findings `NONE`, waivers
`NONE`.

The ORCHESTRATOR may open SPEC only through an explicit phase transition.
Work Order, reconciliation, network/root effects, P4-E SPEC, commit and push
remain unauthorized.
