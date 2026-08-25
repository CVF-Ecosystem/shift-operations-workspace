# Independent Work Order Authorization Review — P4-C Integration Edge

- Work order: `P4C-INTEGRATION-EDGE-WO-2026-08-23`
- Reviewed phase: `WORK_ORDER` only
- Reviewer role: `INDEPENDENT_AUTHORIZATION_REVIEWER`
- Risk ceiling: `R2`
- Review date: `2026-08-23`
- Disposition: `AUTHORIZATION_REVIEW_CHANGES_REQUIRED`

## Review boundary and evidence

This review compared
`docs/work_orders/P4C_INTEGRATION_EDGE_WORK_ORDER.md` with the accepted SPEC
and final SPEC review, both registered invariant matrices and their enforced
pins, current source/module/dependency/migration layout, the exact dirty set,
and the required evidence, role, external-effect and stop boundaries. No BUILD
or product-source action was performed.

Independent recomputation established:

- Work Order raw-byte and UTF-8 universal-newline SHA-256:
  `1c31410b33bfc0e0b87644e2225cd3693e2fbc1ec815fb2098efb7396901920a`;
- numbered BUILD ceiling: `66` entries and `66` unique paths;
- ingress matrix digest:
  `277c5211e914a44858d105cd6f5ceba7fe5d95aa35afaa85f811aba26d858b2b`;
- outbound matrix digest:
  `41f42d0b2585201a41fbed3b9f2d7e6bfd9f2adf4f2f587890addc0a7d4604a6`.

Both matrix values match SPEC R15, the machine reference and their distinct
symbols in `docs/specs/p4c_invariant_pins.py`. The pre-Work-Order P4-C
governance/continuity set independently reproduces the declared `17` paths
and LF-terminated sorted-path digest
`ad586ecfbba2b64ebccd30bd796e771ac62ca48c61f0e7b0b97ef5b67dfccc28`;
the separately protected assessment and Work Order explain the current
pre-review total of `19` dirty paths. The assessment was not opened, edited,
staged or used as substantive evidence.

`HEAD` and `origin/main` both equal the declared execution base
`0b89016df8483a4904d2c64b1a6560ccbc6b27ae`, and the staged set is empty.
Migration `010` has no filename collision after existing `001` through `009`;
the repository migration runner discovers sorted `*.sql` files. Every parent
source area is present, and new package/schema/test paths can be created
within the ceiling. Python is 3.13.12, Pydantic is 2.10.6 and the already
installed cryptography version is 49.0.0; no install was performed.

Read-only verification returned:

- `python scripts/check_invariant_families.py --json`: `PASS`;
- `python scripts/check_session_state.py`: `PASS`;
- `python scripts/generate_catalog.py --check`: `PASS`;
- `python scripts/check_file_size.py`: `PASS`;
- `git diff --check`: clean;
- workspace doctor: 24 passes and the retained bounded legacy-catalog warning.

## Numbered findings

1. **P4C-WO-AUTH-REV-F1 — The mandatory shared invariant-family proof is not
   completed in the Work Order.** The invariant-family standard requires the
   `WORK_ORDER_AUTHOR` to complete the fields in
   `docs/templates/INVARIANT_FAMILY_PROOF.md` for this triggered R2 tranche.
   The Work Order pins both family digests and generally asks for emitter and
   mutation evidence, but it does not identify each matrix's declared emitter
   identity and evidence-test paths, record the matrix-declared mutation
   exclusions with independent-review acknowledgment, provide the exact guard
   and focused-test commands, or assign the returned family-conformance
   summary to an evidence owner with the required independent reviewer
   recomputation/no-BUILD-derivation check. These are testable authorization
   fields, not presentation preferences: without them, worker return and
   completion review can choose different corpora or silently omit the
   independently acknowledged exclusions while still satisfying the current
   generic evidence bullets. Add one shared-proof section covering both
   registered families by id/digest and references only; do not duplicate
   matrix outcome rules. This repair need not change the exact BUILD ceiling.

## Waivers

1. `NONE`. No finding is waived or deferred.

## Accepted authorization boundaries

Apart from F1, the exact 66-path ceiling is unique and feasible against the
current tree. It covers the package/dependency surfaces, next migration,
edge/core port implementations, closed schemas, focused/security/parity/live-
database tests and generator-owned catalog outputs required by the accepted
SPEC. The role separation, zero provider/external HTTP/credential/install/
deployment/commit/push budget, disposable-local PostgreSQL boundary, no-real-
adapter/no-business-truth obligations, exact cleanup evidence and stop
conditions are appropriately bounded.

No provider call was needed or authorized for this authorization-contract
review, which makes no implemented-governance claim.

## Disposition

`AUTHORIZATION_REVIEW_CHANGES_REQUIRED`.

BUILD remains unauthorized. Return only `P4C-WO-AUTH-REV-F1` for bounded Work
Order repair and independent rereview; all other reviewed authorization
boundaries are accepted without waiver.

## Bounded authorization rereview — P4C-WO-AUTH-REV-F1

- Rereview role: `INDEPENDENT_AUTHORIZATION_REVIEWER`
- Repaired Work Order raw SHA-256:
  `d9d2f139a3bec12674200266a93f8667cb054f7edffd7bacb8eff1eefb6ebea2`
- Finding `P4C-WO-AUTH-REV-F1`: `CLOSED`
- Findings: `NONE`
- Waivers: `NONE`
- Disposition: `AUTHORIZATION_REVIEW_PASS`

The new shared proof is reference-only and completes every mandatory field in
the invariant-family standard/template for both registered families. It states
`APPLICABLE`; identifies both exact family ids and canonical digests; binds the
two matrix-declared `REAL_SERVICE_EMITTER` identities and both declared
evidence-test paths; identifies the authorized raw-emitter sample test; records
the sole matrix-declared `RECURSE_NESTED_OBJECTS` exclusions for every flat
shape, their exact reason and required independent-review acknowledgment; and
provides exact guard/focused-test commands.

Evidence ownership is separated correctly: the worker returns conformance
outputs and raw positives but cannot approve them. The independent completion
reviewer must recompute both digests, rerun the same corpus/commands, sample a
raw positive from the declared real emitter for every outcome in both
families, and reject any expectation derived from BUILD implementation. No
outcome, field, relation or mutation rule is duplicated outside the matrices.

Independent canonical recomputation produced ingress digest
`277c5211e914a44858d105cd6f5ceba7fe5d95aa35afaa85f811aba26d858b2b`
and outbound digest
`41f42d0b2585201a41fbed3b9f2d7e6bfd9f2adf4f2f587890addc0a7d4604a6`.
Both match the Work Order, SPEC, machine reference and enforced pin symbols.
The invariant-family guard passed, and the currently materialized shared
corpus passed `35 passed, 2 skipped`; the third exact command path is the
authorized future BUILD emitter test inside the unchanged ceiling.

The numbered BUILD ceiling remains exactly 66 entries and 66 unique paths.
All previously accepted role, disposable-local PostgreSQL, cleanup, stop and
zero provider/external HTTP/credential/install/deployment/commit/push
boundaries remain unchanged. Session-state and `git diff --check` guards pass,
the staged set is empty, and local Core is clean at
`HEAD == origin/main == 864c4e0e6139f3e32067dea41f43f240e505c0d8`.
No doctor, network, provider, credential, install, database, deployment, BUILD,
commit or push occurred during this rereview. This PASS closes only F1 and
authorizes no external effect by the reviewer.

## Independent authorization review — Work Order Amendment 1 / path 67

- Review date: `2026-08-25`
- Reviewer role: `INDEPENDENT_AUTHORIZATION_REVIEWER`
- Scope: `docs/work_orders/P4C_INTEGRATION_EDGE_PATH67_WORK_ORDER_AMENDMENT_2026-08-25.md`
- Disposition: `AUTHORIZATION_REVIEW_CHANGES_REQUIRED`
- Waivers: `NONE`

Independent recomputation confirmed the parent Work Order remains byte-exact
at SHA-256
`d9d2f139a3bec12674200266a93f8667cb054f7edffd7bacb8eff1eefb6ebea2`.
Its 66 numbered paths are unique; appending only
`knowledge/manifest.json` produces exactly 67 unique paths. Project
`HEAD == origin/main == 0b89016df8483a4904d2c64b1a6560ccbc6b27ae`, the
staged set is empty, and Core HEAD/origin, manifest and AGENTS all agree at
`9c01832930226f2f770eafa346e01279160f22cb`.

The three declared current SHA values exactly match the existing path-67
entries, and all three required values independently reproduce the named
source bytes. The pre-existing `IMPLEMENTATION_STATUS.json` pin already equals
its source at
`c416f4cb642c757fe6766991e927efe99e0156292202fa3639af0d9d4d42fd93`
and is explicitly protected. Role separation, fourth-value/path-68 stop
conditions, guard-preservation rule, retained disposable-database evidence and
zero provider/external HTTP/credential/install/deployment/commit/push effects
are otherwise authorization-ready.

### Numbered finding

1. **P4C-WO-A1-AUTH-F1 — Required repository-validation command points to a
   nonexistent path.** Evidence command 8 specifies
   `python testing/validate_repository.py`, but no `testing/` directory or file
   exists there. The repository-owned validator is
   `scripts/testing/validate_repository.py`, and the Makefile invokes
   `python scripts/testing/validate_repository.py`. The corrected command ran
   successfully during this review, alongside PASS results for invariant,
   session, catalog and file-size guards. Replace only command 8 with the real
   repository path so the worker has an executable mandatory evidence set.

### Current amendment disposition

`AUTHORIZATION_REVIEW_CHANGES_REQUIRED`.

Return only `P4C-WO-A1-AUTH-F1` for bounded Work Order amendment repair and
independent rereview. BUILD remains stopped. No provider call was required or
authorized for this deterministic contract review, which makes no
implemented-governance claim.

## Bounded authorization rereview — P4C-WO-A1-AUTH-F1

- Rereview date: `2026-08-25`
- Rereview role: `INDEPENDENT_AUTHORIZATION_REVIEWER`
- Finding `P4C-WO-A1-AUTH-F1`: `CLOSED`
- Findings: `NONE`
- Waivers: `NONE`
- Disposition: `AUTHORIZATION_REVIEW_PASS`

Evidence command 8 now points to the repository-owned executable path,
`python scripts/testing/validate_repository.py`. The file exists and the exact
command returned PASS, including its catalog, session-state, file-size and
invariant-family checks. A separate session-state guard also passed.

Bounded textual rereview confirmed that only the finding's command path was
corrected. The parent Work Order remains at SHA-256
`d9d2f139a3bec12674200266a93f8667cb054f7edffd7bacb8eff1eefb6ebea2`;
the amended ceiling remains 67 entries and 67 unique paths; path 67 remains
unmodified at this review checkpoint; the three authorized current-to-required
SHA replacements, pre-existing `IMPLEMENTATION_STATUS.json` pin preservation,
roles, stop conditions and zero-effect boundary are unchanged. Core HEAD and
origin remain equal at `9c01832930226f2f770eafa346e01279160f22cb`, and the
staged set is empty.

The earlier `AUTHORIZATION_REVIEW_CHANGES_REQUIRED` disposition remains above
as history and is superseded by this bounded rereview. Exact-67 BUILD may
resume only through the recorded role/state transition and only for the three
authorized path-67 replacements plus the already authorized parent ceiling.
Commit, push, provider, external HTTP, credential, install and deployment
authority remain zero. No provider call was required or authorized for this
deterministic authorization rereview.
