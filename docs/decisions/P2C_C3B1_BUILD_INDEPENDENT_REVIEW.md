# Independent BUILD Review — P2-C C3b1

- Tranche: `P2C-MUTATION-FULL-UI-2026-07-31`
- Checkpoint: `C3b1`
- BUILD parent: `8c0700db4608513123b0126b657d0903b8f90830`
- Reviewed BUILD commit: `03e57f96168bb96fd13afac232b2f0593c84f98f`
- Risk: `R2`
- Reviewer: Codex, independent from the manual implementation worker
- Final disposition: `REVIEW_PASS_AFTER_REPAIR`
- Status: `C3B1 REVIEW_PASS / PUSHED — C3B2 MAY ENTER AUTHORIZATION`

## Scope and exact set

Mechanical comparison proved exactly 36 numbered, 36 unique and 36 changed
BUILD paths, with zero outside and zero missing. The staged BUILD set was
rechecked against the reviewed Work Order plus Amendments 2 and 3 before the
commit; exactly those 36 paths were committed and pushed. Generated
`apps/workspace-web/tsconfig.tsbuildinfo` was absent and Docker-owned residue
was zero.

## Findings closed

### `C3B1-BUILD-REV-F1 GREEDY_MATCHING_FALSE_NEGATIVE`

The first candidate called its readiness algorithm maximum bipartite matching
but used greedy seat-order allocation. A manager-first/supervisor-second
receipt order falsely produced one satisfied R3 seat although a two-seat
matching existed. Repair implemented deterministic Kuhn augmenting paths and
added the adversarial-order regression. Independent exhaustive probing across
all role-hierarchy combinations up to four seats/four candidates found no
cardinality mismatch.

Disposition: `CLOSED_WITHOUT_WAIVER`.

### `C3B1-BUILD-REV-F2 MATCH_MAP_KEY_ANNOTATION_DRIFT`

The repaired algorithm indexed its assignment map with integer approver
indices while two annotations declared string keys. Both declarations now use
`dict[int, int]`; behavior is unchanged and the receipt records the repair.

Disposition: `CLOSED_WITHOUT_WAIVER`.

## Independent evidence

- focused C3b1/readiness suite: `57 passed`;
- full non-live suite: `1238 passed / 120 skipped`;
- frontend: `31/31`, typecheck and production build PASS in the F1 review
  round; F2 changed only Python annotations;
- disposable PostgreSQL 16: `110/110`, migrations `24/0` then `20/4`, exact
  container and anonymous-volume cleanup in the F1 review round; F2 did not
  change runtime behavior;
- file-size, session/mirror, catalog, repository, JSON and diff gates PASS;
- exhaustive small matching probe PASS;
- worker doctor evidence remains `PASS WITH NOTE 24/1`, solely the bounded
  legacy catalog-kit warning;
- zero provider call and no reused provider receipt claim.

## Bounded disposition

C3b1 proves only authenticated ACTIVE-assignment-scoped bounded operational
reads, current-binding approval-readiness and the typed browser transport/DTO
contract on the proven backends. It does not prove C3b2 concurrency,
CustomerRequest versioning, mutation UI, tenant/provider data scope, token
revocation, production PostgreSQL, P2-C/P2-D or Phase-2 completion.

The manual worker never staged, committed, pushed, self-reviewed or FREEZEd.
After independent review passed, Codex acted separately as commit steward and
pushed the exact BUILD commit. C3b2 may now enter DESIGN/SPEC-derived Work
Order authorization; no C3b2 BUILD authority carries forward from C3b1.
