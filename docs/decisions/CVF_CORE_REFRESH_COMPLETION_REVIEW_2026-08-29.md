# Independent Completion Review — CVF Public-Core Refresh

- Tranche: `CVF-CORE-REFRESH-2026-08-29`
- Risk: `R2`
- Phase reviewed: `BUILD`
- Role: `INDEPENDENT_COMPLETION_REVIEWER`
- Worker outcome: `FAILURE_ROLLED_BACK`
- Disposition: `REVIEW_PASS_FAILURE_ROLLED_BACK`
- Findings: `NONE`
- Waivers: `NONE`

## Review boundary

This review compares the immutable BUILD worker outcome against the accepted
SPEC, invariant matrix and Work Order. It uses only allowlisted local reads and
deterministic checks. It did not run a completion doctor, reconciler,
initializer or any network operation. It performed no hidden-Core,
workspace-root, product, continuity, provider, credential, installation,
database, deployment, commit or push mutation. It did not open, read, hash,
inventory or otherwise touch the protected operator assessment and did not
perform a broad downstream untracked inventory.

The reviewer-owned creation of this document is the review's sole mutation.
The worker receipt, worker return and contained evidence remain unchanged.

## Contract and preflight verification

The accepted contract bindings recompute as follows:

- SPEC raw SHA-256:
  `03932a375516ff100e452a40c92fa4886e5e4b1bb10488d446dc8faa162b4f01`.
- Work Order raw SHA-256:
  `1de50c0f4545f975aa415cde4924db02b401a191a7703c6ec2d272d6c994518f`.
- Reconciler raw SHA-256:
  `96ac0cce3bf9df5733ffe2c6f5a7850db0ccfdc4403daaa70fdb6981dc58196c`.
- Initializer raw SHA-256:
  `bb37b16256a693853bddfdbcb40c2f7211e6984a90a972da83899962fae209c8`.
- Matrix raw/canonical SHA-256:
  `5f6e477d8d76e11965c91c0034f0ff4f7d82e1beab5d41c2266526957a5a8025`.
- Machine-pin artifact raw SHA-256:
  `6ad871371d551ff55ca263a0d605573176e5218108b8e3032888e4cfe84511ae`;
  its pinned digest equals the matrix digest.
- Active profile raw SHA-256:
  `f51bacd206ec4e95b92f4f4479bc7c68ee605db3752d514ff3094bdff02dc855`;
  the profile value remains `operator-local`.

The retained `preflight.json` has raw SHA-256
`772ed5b0d3dbef830394e7f0412f61490c28d3bd07a486fb4ff1a30efeca4699`
and records `PASS`: exact contained workspace/project/Core paths, expected
remote, clean old Core, frozen target object and ancestry, project
`HEAD == origin/main == a8e2ad8199d700a238d7d74bdbf85329446228de`,
staged zero, matching contract/tool/profile hashes, five future evidence paths
absent, protected assessment `EXCLUDED_NOT_OBSERVED`, and
`broadUntrackedInventoryPerformed: false`. No refusal predicate was triggered
before external execution.

## Execution and rollback evidence

1. The reconciler transcript raw SHA-256 is
   `edb9df3d9bd5169f6e5cd9ef51c10cf5a759a1edfcb4796984b53048c41640b2`.
   Its separate exit record is `0`. The transcript contains exactly the
   sanctioned reconciler invocation's clone and reports public Core
   `d7860138350130d6d105826ce186f1beeaba3c2d`.
2. The immediate checkpoint records clean
   `HEAD == origin/main == d7860138350130d6d105826ce186f1beeaba3c2d`,
   not frozen target
   `06c3d040a3dc8fa22fa27f2f9c3e40739def075e`. Therefore
   `RECONCILER_RETURN_CHECKPOINT:P1` is the required terminal stop.
3. Command/accounting evidence contains one reconciler operation, zero pin
   patches, initializer `NOT_RUN`, zero retry and no second reconciliation
   attempt. Provider, credential, install, product, database, deployment,
   commit and push counts are all zero.
4. The preserved replacement is present, clean, uses the expected public
   remote and has `HEAD == origin/main == d786013...`. The retained old-Core
   preimage is present and clean at `a7a797d...`; the restored active Core is
   also clean at `a7a797d...`, with the expected public remote. Its local
   `origin/main == d786013...` is the expected stale condition after rollback.
5. Independent exact-path comparison against the retained preimages confirms
   all `17/17` workspace-root targets restored: fourteen present files match
   byte-exact and the three originally absent overlay targets remain absent.
   The failed-root-delta directory is retained and empty, consistent with all
   reconciler root observations being `NO_CHANGE`.
6. Both pin carriers and the ignored binding are byte-equal to their
   preimages. Core HEAD, manifest pin, generated AGENTS header and binding all
   equal old pin `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`.
7. All nine shared carriers have retained preimages. Their only final deltas
   are the bounded failure-continuity updates: moved-target/rollback state,
   next independent-review routing, evidence pointers and derived knowledge
   hashes. This is consistent with restoration followed by the SPEC R10
   failure-continuity window; no success or new-target state was introduced.
8. The three dedicated parked P4-E hashes and all thirteen allowlisted
   governance-artifact hashes from preflight remain unchanged (`16/16`). P4-E
   remains `DESIGN_REVIEW_PASS`; the active profile remains byte-preserved.
9. Exact allowlisted status inspection shows `11/13` worker tracked path
   effects: nine shared carriers and exactly two evidence `CREATE` paths. The
   two pin carriers have no final effect, the ignored binding is restored, and
   the staged set is empty.
10. The rollback verifier transcript raw SHA-256 is
    `fd509a40f123a472bd73f04c07b6710d92aff03a019d75578e14f69d3d654d6a`.
    Exactly one verifier is recorded; exit is `1`, with `23/25` checks passed,
    the single expected `BEHIND_PUBLIC_REMOTE` failure and one bounded legacy-
    catalog warning. This is valid rollback evidence, not a success doctor.

## Invariant and deterministic verification

Independent read-only recomputation produced:

- matrix digest equal to the SPEC and machine pin;
- all five stored positive projections accepted exclusively by their intended
  shapes;
- `400/400` generated one-fact mutations rejected;
- `40/40` rollback-stage/verifier-state temporal cases classified as declared
  (`20` accepted, `20` rejected, zero mismatch); and
- the actual worker projection matching only
  `FAILURE_ROLLED_BACK_VALID`.

Fresh local deterministic checks passed: session/mirror, Project Knowledge,
invariant-family guard with no diagnostics, focused invariant tests
`35 passed, 2 skipped`, catalog (`26` modules), file-size and staged-zero.
The retained deterministic-guard transcript and conformance summary hashes
also match the canonical receipt:

- guards:
  `4699baa1f344e21720d22646bc36a57cfb544149d503a9e69e17a1a80a7c7498`;
- conformance summary:
  `4994995deee70cf556152c3c70bbaddb86e7fd2c9c49abbae341f679c02709d2`.

## Final worker-artifact hashes

The reviewer independently recomputed the final raw SHA-256 values after all
read-only verification:

- `docs/decisions/CVF_CORE_REFRESH_ROOT_EFFECTS_2026-08-29.json`:
  `0f81655e859b0c6e370cd1eeb79e2ae12fb75a4bfc9ca8b85844389ac89621eb`.
- `docs/decisions/CVF_CORE_REFRESH_WORKER_RETURN_2026-08-29.md`:
  `288e8748b670897477b8e3f2587bd8c4705bf24e8ceb6cdcd99f1a5b06cdbe12`.

Neither worker artifact self-hashes or cross-hashes; this independent review
is the terminal owner of those final hashes.

## Numbered findings

`NONE`.

## Waivers

`NONE`.

## Disposition

`REVIEW_PASS_FAILURE_ROLLED_BACK`.

The failed attempt is complete and safely rolled back within its accepted
claim boundary. This disposition proves only the bounded deterministic failed
Core-refresh attempt and complete rollback. It does not prove successful Core
adoption, AI/agent governance behavior, provider behavior, product/runtime or
database behavior, deployment, production readiness or arbitrary-untracked
absence.

Recommend a bounded `FREEZE` of this failed attempt. No retry, adoption of
`d786013...` or another target, commit, push or P4-E SPEC is authorized. Any
new refresh attempt requires a fresh governed target rebase through the
applicable control-chain phases and fresh operator authority.
