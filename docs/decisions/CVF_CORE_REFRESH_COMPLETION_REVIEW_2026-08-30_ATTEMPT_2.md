# Independent Completion Review — CVF Core Refresh Target Rebase — Attempt 2

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-2026-08-30`
- Phase reviewed: `BUILD`
- Risk: `R2`
- Role: `INDEPENDENT_COMPLETION_REVIEWER`
- Worker outcome reviewed: `FAILURE_ROLLED_BACK`
- Disposition: `REVIEW_PASS_FAILURE_ROLLED_BACK`
- Findings: `NONE`
- Waivers: `NONE`

## Review boundary

This review decides only whether the failed attempt and its preservation-first
rollback complied with the accepted Work Order. It does not reinterpret the
attempt as target adoption, successful Core refresh, tranche success, release,
or product/runtime adoption. Core target `d7860138350130d6d105826ce186f1beeaba3c2d`
was not adopted. The active hidden Core, both downstream pin carriers and the
ignored binding remain restored to `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`.

The reviewer used only local, read-only, allowlisted checks of the accepted
artifacts, the worker receipt/return, the contained attempt-2 evidence, the
declared 17 workspace-root targets, declared downstream carriers, declared
protected artifacts, and the active/retained Core repositories. No doctor,
network operation, reconciler, initializer, retry, repair, provider call,
credential access, installation, product/runtime/database action, deployment,
commit or push was performed. The protected assessment was not opened, read,
hashed, staged, inventoried or used. No broad downstream untracked inventory
was performed. Creation of this review is the reviewer's only mutation; this
artifact intentionally does not self-hash.

## Accepted contract and hash bindings

Raw hashes were recomputed from current bytes:

| Artifact | SHA-256 |
|---|---|
| Accepted Work Order | `df321b5eb481eb441b7e32de58b9baff45b8d9757f763ff0b3d9742152986810` |
| Final accepted SPEC | `f8c2de27e5aca67f53bb530cd9bbce17abc1f3b65a56ad7bfe5ba0a1fb044161` |
| Final SPEC review/rereview | `b9fadce65a8f40da68e82dc0a832dfede1e327ce1fc2b2656247a9dcfc182ecb` |
| Invariant matrix raw/canonical | `dc0c35298fb584d995f51ed8cf996f599f12b934617afd51e1a27b24ce47f4cc` |
| Machine-pin file | `4ce97c9823ae63447ffe158ae9b0d81ac7690a19c019b368ce00da5be8793b66` |
| Invariant registry | `e22195a46528feff89ee7f622ac1d964a0a94e9acc8b85f82a93de77c57525c5` |
| Authorization review | `abb218b4d75cf5013c71fc10f14442730ba84584e18d0be8ab349cede15c87b4` |
| Worker root-effects receipt | `18d656e0b38de4c931222edae1019d38a53de46db98a2867e0a96906968c8c21` |
| Worker return | `5366d23fc91aca0afd510df414ec976a1c1efc0ada7d9a6b39f63e58aba0869c` |

The matrix canonical digest equals the statically extracted machine-pin value.
The registry contains exactly the expected active R2 family
`CVF-CORE-REFRESH-TARGET-REBASE-OUTCOMES-2026-08-30`, owned by `SPEC_AUTHOR`,
at the accepted matrix path. The authorization review is
`AUTHORIZATION_REVIEW_PASS`, findings/waivers `NONE/NONE`; the later operator
approval of this exact Work Order is recorded in the active handoff. It grants
only the bounded BUILD graph and excludes every effect listed in the review
boundary above.

The accepted tool/profile bindings were independently reproduced. At both the
old Core and retained target Core, reconciler raw/blob are
`96ac0cce3bf9df5733ffe2c6f5a7850db0ccfdc4403daaa70fdb6981dc58196c` /
`4b705c6bf7b10bda62520dca488ecb453a4f4945`; doctor raw/blob are
`2410bbabf88f12581d2e34a71efe247fe9080ebb299a58eb6f9ff6a35818796b` /
`2ad83efee05c738fec40aa1779929da07f3d1c8c`; new-workspace raw/blob are
`7e5567c55026f3be44f11c924d44835d6fb98b1fb4268dfedf6453af89927032` /
`5f311a1a1c8dc787c7b19011bf34c5a84fc773c7`; and the operation tree is
`23fe8bd39ae102d3302d34de1d80208e2ef9bbb6`. The downstream initializer is
`bb37b16256a693853bddfdbcb40c2f7211e6984a90a972da83899962fae209c8`.
`CVF_RULE_PACKS/ACTIVE_RULE_PACK.json` selects `operator-local` and hashes to
the accepted `f51bacd206ec4e95b92f4f4479bc7c68ee605db3752d514ff3094bdff02dc855`.

## Preflight, sanctioned graph and initial target checkpoint

`preflight.json` hashes to
`93fe779221ef1b4f0ec1b48a4bcbc94faa4bdedb772575633986b0f9904866da`;
its preimage manifest hashes to
`35e905142f753ece8a5607229820ec7f65bd26d102d08066488538116051dfa1`.
The records establish the exact contained paths, expected public remote, clean
old Core at `a7a797d...`, local target `d786013...`, ancestry `0` ahead / `5`
behind, staged zero, accepted hashes/profile, all six attempt-2 lifecycle paths
absent before creation, protected-assessment exclusion, and recoverable
preimages. The independent byte checks below confirm those preimages remained
usable.

The retained transcripts and checkpoints show exactly the sanctioned graph:

- reconciler: exactly `1`, exit `0`, transcript
  `9a3be6dc2d5c23d6fdeaf82a4e9cae79f4f7e1592f4fab387955c6e6b5e6201a`;
- scoped two-pin bridge: exactly `1`, checkpoint
  `4d23d5751d223cce88cc55a1b19d20b39cd8b6a73ef7f2448f7666c73512e811`;
- initializer: exactly `1`, exit `0`, transcript
  `644dc750b01a844888ab5fc3b31ec0132c04e7a960ce44de97c812cced47f44d`;
- original sanctioned Git network prefix: exactly `3` in order—reconciler
  clone, initializer fetch, initializer-doctor fetch; and
- reconciliation retries and manual Git network operations: `0`.

The immediate reconciler checkpoint records clean Core HEAD and origin/main at
the frozen target. After the bridge and initializer, checkpoint
`b911d9c8cf7b3aabe9564a31490e7c7d0fa7a1546d617299e2b37f5753533039`
records clean five-way equality among Core HEAD, Core origin/main, manifest,
AGENTS and binding at `d786013...`. The initializer doctor transcript records
`24` passes and the single bounded legacy-catalog warning.

## Independently inspected conformance failure

The failure is genuine and is not inferred from the worker summary. The raw
seven emitted positives, conformance summary and transcript were inspected.
They show `7` positives, `686` generated one-fact mutations with per-shape
counts `75, 93, 107, 73, 79, 144, 115`, and `40` temporal judgments (`38`
accepted, `2` cross-owner rejections). The repository matcher accepted `6/7`;
the worker's independent validator accepted `7/7`.

The exact disagreement is
`REVIEW_TARGET_MOVEMENT_ROLLED_BACK_VALID`. Its raw preserved positive hashes
to `44ea0a805a15bf5c5f10273a5ced3bcdb193acba2a66065059641eb1004d7144`
and contains literal `"x"` in these six fields:
`success_receipt_pre_sha256`, `success_receipt_post_sha256`,
`worker_return_pre_sha256`, `worker_return_post_sha256`,
`target_movement_review_pre_sha256`, and
`target_movement_review_post_sha256`. Each matrix domain requires
`^[0-9a-f]{64}$`. The repository matcher therefore correctly returns no match;
the worker's second validator was lenient on those regex domains and accepted
the otherwise closed/equal object. This independently reproduces the recorded
`6/7` versus `7/7` mismatch and explains it from raw bytes.

The worker classified it exactly as `DOWNSTREAM_SYNCHRONIZATION:P3`, preserved
the failure trigger at SHA-256
`5b20f7a65b2231fd33cfb2bf00955da1b879bf433f1a5294f345b3d31af765d8`,
did not retry, did not rewrite the failed evidence into success, and entered
preservation-first rollback. That behavior is required by the Work Order.

## Independent invariant-family proof

Fresh positives were generated from the accepted matrix domains without using
BUILD output as expected truth. Both the repository matcher and a separately
implemented strict closed-object validator accepted each of the `7/7`
positives exclusively. Their canonical positive hashes in matrix order are:

1. `5ecf72db47ebfd2e7bb56a748fee7667cfd1506453edd61183f120a04676e1e0`
2. `12f3f56bec5757e407cd2c88058bd24631ca6de7d0eaefee80e4fef60e03a768`
3. `d25498357bd311a6f390b1d0b96771087381add57ff24b2f26e59d4ed1829dbc`
4. `9fa92eac2626909cc3057ef2961156d8b3f7e394c97539917deafa1c7c35e82d`
5. `a177a292bf34516c15c0a6e1c4e5461b95830de80428cb94b751170a20154a77`
6. `c65ee87f4301776806f291bce1fe3d3e89a4c87c837f046f16fde95bfb9eb984`
7. `5c196510cf06e9bf5746996a3483d320a2b70e126d6fdfdb63bbe99247d12bf5`

Both surfaces rejected the complete fresh `686/686` mutation corpus; mutation
exclusions are `NONE`. The focused cross-product independently returned
`40/40` correct judgments (`38` accepted and `2` rejected). Applying both
surfaces to the worker receipt's terminal projection yields exactly one match:
`FAILURE_ROLLED_BACK_VALID`. No success or reviewer-movement outcome matches.

Fresh deterministic checks all passed:

- session-state/mirror guard: `PASS`;
- Project Knowledge guard: `PASS`;
- invariant-family repository guard: `PASS`, diagnostics empty;
- focused invariant tests: `35 passed, 2 skipped`;
- catalog verification: `PASS`, 26 modules current;
- file-size guard: `PASS`; and
- scoped staged set: zero.

## Preservation-first rollback and final effects

The retained target Core is clean at `d786013...` with the expected public
remote. The old Core preimage is clean at `a7a797d...`, and the active hidden
Core is independently clean at that same old pin and remote. The rollback
checkpoint hashes to
`9e5bfe981c575aa843123138559e20940ddd3ef44b0f7fcffed8a350857f15b7`.

Direct comparison against the frozen preflight/preimage manifest proves:

- workspace-root targets: exact `17/17`; all `14` originally present targets
  match byte-for-byte in the current root and their retained preimages, while
  all `3` originally absent overlay targets remain absent;
- pin carriers: `2/2` restored byte-for-byte and both parse to `a7a797d...`;
- shared continuity carriers: exact `9/9` authorized final worker effects;
- ignored binding: `1/1` restored byte-for-byte and resolves the old pin;
- protected artifacts: `17/17` current bytes and retained preimages match,
  including the three P4-E artifacts, accepted governance lineage and all
  three attempt-1 worker/review artifacts; and
- P4-E remains `DESIGN_REVIEW_PASS`.

The final scoped tracked set is exactly `11/13`: the two pins have zero final
effect, the nine shared carriers have authorized failure-continuity effects,
and the receipt/worker return are the two authorized creates. Nothing is
staged. Before this review was created, all three later attempt-2 review/
conditional paths were absent. After this one authorized create, both
conditional rollback/rereview artifacts remain absent.

Exactly one rollback verifier was run. Its exit-code file records `1`, and
transcript
`fd509a40f123a472bd73f04c07b6710d92aff03a019d75578e14f69d3d654d6a`
records the expected restored-stale-Core result: `BEHIND_PUBLIC_REMOTE`,
`23/25` checks passed, one failed freshness check and the single bounded
legacy-catalog warning. This is the matrix-authorized rollback verifier, not a
failed rollback and not a retry. No additional reviewer doctor was run.

The receipt records zero provider calls, credential reads, installs, product
changes, database actions, deployments, commits, pushes, manual Git network
operations, reconciliation retries, protected-assessment contacts and broad
untracked inventories. The retained command transcripts, scoped repository
state and protected/preimage comparisons contain no contradictory effect.

## Reviewer tooling note

Two local read-only PowerShell wrappers produced minor parser/name-resolution
errors during review: one helper name collided with the built-in history alias,
and one `foreach` pipeline form was syntactically invalid. Neither wrapper
reached a mutation, Git write, network operation or external action. Corrected
allowlisted wrappers reran successfully and produced the results recorded
above. These zero-effect reviewer tooling errors do not waive or replace any
required evidence.

## Numbered findings

`NONE`.

The preserved conformance disagreement is the truthful BUILD failure trigger,
not an open finding against rollback compliance. The failed attempt neither
adopted the target nor claimed success, and its complete rollback satisfies the
accepted failure outcome.

## Waivers

`NONE`.

## Final disposition

`REVIEW_PASS_FAILURE_ROLLED_BACK`.

Attempt 2 failed at `DOWNSTREAM_SYNCHRONIZATION:P3`, stopped without retry and
completed the exact preservation-first rollback. The only accepted terminal
projection is `FAILURE_ROLLED_BACK_VALID`. This disposition permits only the
governed closure/synchronization of that failed-and-rolled-back outcome. It
does not authorize target adoption, reconciliation retry, Core/root/pin/
binding repair, P4-E SPEC, provider/credential use, installation, product or
database change, deployment, commit or push.
