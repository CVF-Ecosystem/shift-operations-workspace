# INTAKE — Project Knowledge Pack C4 Repair Amendment 2

- Tranche: `PROJECT-KNOWLEDGE-PACK-C4-REPAIR-AMENDMENT-2-2026-08-03`
- Parent amendment authority: `c32b5c51d51847dbd0fbf3bb582e9f7dd3fa1734`
- Risk: `R2`
- Status: `INTAKE_COMPLETE`

## Trigger and retained evidence

Amendment 1 repaired the three stale Project Context source pins. Its sole
fresh fail-stop verification sequence produced:

1. project knowledge validator PASS;
2. focused unit suite `77 passed`;
3. session-state PASS;
4. catalog PASS at 22 modules;
5. file-size FAIL because `docs/implementation/EXECUTION_ROADMAP.md` has 604
   lines against the 600-line hard limit.

The sequence stopped there. Repository validation and doctor did not run. No
retry, provider, helper, integration rehearsal, POST or further network call
occurred after the separately authorized authority push.

## Requested correction

Keep the same exact ten-path repair/closure ceiling. Condense only existing
Project Knowledge Pack roadmap prose by at least four physical lines without
removing required truth, then update only its `project-context` manifest pin
to the final roadmap SHA-256. Permit exactly one replacement fail-stop
verification sequence.

## Network reconciliation

The parent zero-network rule conflicts with mandatory pushed authority, the
doctor's unconditional CVF-core `git fetch`, and the required pushed closure.
Amendment 2 requests only three bounded git-network command invocations after
fresh R2 approval: authority `git push origin main`, one doctor invocation
containing its single core fetch, and final closure `git push origin main`.
All provider/helper/POST and all other network actions remain forbidden.

