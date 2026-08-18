# DESIGN — P3-B Option B: Claim-Boundary Correction

- Tranche: `P3B-GATE-WIRING-2026-08-18`
- Control-chain phase: `DESIGN`
- Parent authority: `INTAKE_REVIEW_PASS`
  (`docs/decisions/INTAKE_2026-08-18_P3B_INDEPENDENT_REVIEW.md`, findings NONE)
- Reviewed INTAKE: `docs/decisions/INTAKE_2026-08-18_P3B_DATA_SCOPE_COST_TERMINATION_WIRING.md`
  (SHA-256 `d2b825b9629d63873f218aeddc728b5ba3d10f322a662e67a4a892e5aec59b33`)
- Risk: `R1` (documentation/claim-boundary only; downgraded from INTAKE `R2`
  because Option B touches no runtime, provider, or data path)
- Active role: `DESIGN_AUTHOR`
- Provider/product-API/POST/network calls: `0/0/0/0`
- Runtime, database, package source changes: `NONE`

## Operator decision recorded

The INTAKE deliberately did not pre-decide between Option A and Option B,
because Option A would open Phase 4 provider/network work under a
Phase-3-labeled tranche — a boundary change that `AGENTS.md:196` requires be
escalated rather than absorbed by an agent.

The operator was presented with both options and their consequences on
`2026-08-18` and selected **Option B**.

Recorded decision: **P3-B is not independently closeable. Phase 4 remains
parked. The roadmap and session state are corrected to state this
explicitly.** No minimal P4-A slice is authorized by this tranche.

## Problem this DESIGN corrects

`docs/implementation/EXECUTION_ROADMAP.md:426-427` currently renders P3-B as
an ordinary unchecked Phase 3 checkbox:

```markdown
- [ ] **P3-B:** Wire các gate data_scope/cost/termination vào một điểm gọi thật
      (khi Phase 4 AI bật) — hết trạng thái "AI-gated only".
```

Read alone, this implies a future session can pick up P3-B and close it
inside Phase 3. That is false, and the falseness is load-bearing: the Phase 3
header reads `PARTIAL (5/6)`, inviting a reader to conclude one small
remaining item stands between the project and a closed Phase 3.

Verified truth (re-confirmed at INTAKE review, zero findings):

- the three gates are implemented and unit-tested but have no runtime caller;
- `packages/ai-gateway` is scaffold-only (12 `README.md` + one interface file);
- `packages/governed-retrieval` (P4-A1) is deliberately provider-free and its
  own INTAKE explicitly declined to close P3-B;
- therefore P3-B cannot close without first opening Phase 4 (P4-A), which the
  roadmap itself lists as `NOT STARTED` and which session state holds parked.

## Design decision

Do not change any code. Change exactly the documents that carry the false
implication, so the roadmap states the dependency instead of hiding it.

### D1 — P3-B roadmap entry becomes explicitly dependency-blocked

**Keep the `[ ]` marker.** Add the blocking dependency as explicit text in the
entry body.

Repaired during DESIGN review as finding `P3B-DESIGN-F1`: an earlier draft of
this DESIGN proposed promoting P3-B to `[~]`. That contradicts the file's own
convention legend (`docs/implementation/EXECUTION_ROADMAP.md:16-21`), which
defines `[~]`/`PARTIAL` as "đã có một phần dùng được nhưng milestone/phase
chưa đóng" — partly usable. P3-B has zero wiring: no runtime caller exists at
all, so nothing is partly usable. `[ ]`/`NOT STARTED` is the accurate marker,
and its legend text ("scaffold, README, contract hoặc test helper không được
tính là hoàn tất") already describes P3-B's situation exactly. Verified: `[~]`
appears exactly once in the file — in the legend itself — so no item currently
uses it, and introducing it here would create a false precedent as well as an
over-claim.

The entry must state, in the roadmap itself:

1. the three gates exist and are tested, but have zero runtime callers;
2. no real AI call site exists anywhere in the codebase today;
3. P3-B therefore cannot close until P4-A opens under its own authority;
4. P3-B is not a Phase 3 blocker that Phase 3 can resolve by itself.

### D2 — Phase 3 header stops implying one small item remains

`Phase 3 — 🟡 PARTIAL (5/6)` stays numerically accurate, but gains a
qualifier noting that the single remaining item is dependency-blocked on
Phase 4 and is not closeable within Phase 3. The `Còn lại để đóng` cell in
the status table at line 28 is updated to match.

### D3 — Phase 3 exit gate records the same boundary

The Phase 3 exit-gate paragraph (line 432-433) gains one sentence recording
that the exit gate as written is satisfiable only for the five closed items,
and that full Phase 3 closure is deferred behind P4-A.

### D4 — Session state records the disposition

`SESSION/ACTIVE_SESSION_STATE.json` `next_allowed_move` and `blocked_work`
record that P3-B is `BLOCKED_PENDING_P4A_AUTHORITY`, so a future session
cannot re-open it as a standalone lane without noticing the dependency.

## Explicit non-goals

This DESIGN does not, and its BUILD must not:

- add, modify, or delete any line of package/application source code;
- create a usage ledger, AI service, provider binding, or call site;
- call an LLM, provider, network service, product API, or browser;
- add provider credentials, models, or deployment configuration;
- mark P3-B `[x]`, `DONE`, `CLOSED`, or `CLOSED_BOUNDED`;
- claim any of the three gates is load-bearing;
- open, schedule, or grant authority to P4-A, P4-A2, or any Phase 4 item;
- alter P3-A, P3-C, or any closed tranche's recorded truth;
- alter the Phase 3 `5/6` count (the count is correct; only its
  interpretation was misleading).

## Acceptance criteria

BUILD is acceptable only if independent review confirms:

1. exactly four artifacts changed: `docs/implementation/EXECUTION_ROADMAP.md`,
   `SESSION/ACTIVE_SESSION_STATE.json`, its `CVF_SESSION/` mirror, and
   `SESSION/ACTIVE_SESSION_BOOTSTRAP_READ_MODEL.json` — plus the active
   handoff and `SESSION/SESSION_MEMORY.md` as continuity carriers;
2. zero changes under `packages/`, `apps/`, `database/`, or `tests/`;
3. `git diff --stat` shows no source file;
4. the roadmap's P3-B entry names the P4-A dependency explicitly and retains
   its `[ ]` marker (per finding `P3B-DESIGN-F1`);
5. Phase 3 is not marked closed, and the `5/6` count is unchanged;
6. no gate is described as load-bearing;
7. `python scripts/testing/validate_repository.py` PASS
   (catalog + session state + file-size);
8. `SESSION/SESSION_MEMORY.md` stays within its 4096-byte budget;
9. canonical state, mirror, and bootstrap read model agree (drift check PASS);
10. no provider, network, product-API, or database call occurs.

## Verification plan

- `python scripts/testing/validate_repository.py` — must PASS.
- `python scripts/check_session_state.py` — must PASS (drift + byte budget).
- `git diff --stat` — must show documentation/continuity files only.
- Re-read the edited P3-B entry cold and confirm a reader cannot conclude
  P3-B is closeable inside Phase 3.

Full pytest is not required: this tranche changes no code, no test, and no
fixture. That claim is verified by acceptance criteria 2 and 3, not asserted.

## Risk and evidence posture

`R1`. No runtime, provider, network, credential, database, or external effect.
`AGENTS.md`'s Mandatory Governance Proof (real provider API call) is not
triggered, because this tranche makes no claim that CVF governs AI/agent
behavior — it does the opposite, recording that the AI-governance gates are
*not* yet load-bearing.

## Claim boundary

This DESIGN authorizes a documentation and continuity correction only. It
does not prove a real call site exists, does not make any gate load-bearing,
does not close P3-B or Phase 3, and does not open Phase 4. It only ensures
the project's own records stop implying P3-B is closeable without Phase 4.

## Next governed move

One independent DESIGN review. On `DESIGN_REVIEW_PASS`, the same bounded
change set may proceed directly to BUILD under this DESIGN's acceptance
criteria — SPEC and WORK_ORDER are collapsed into this artifact because the
authorized change set is four documents with no code, no contract, and no
testable runtime behavior. That collapse is itself a decision the DESIGN
reviewer must accept or reject.
