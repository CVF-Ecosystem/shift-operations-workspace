# Independent INTAKE Review — CVF Public-Core Target Rebase

- Tranche: `CVF-CORE-REFRESH-TARGET-REBASE-2026-08-30`
- Phase reviewed: `INTAKE`
- Risk: `R2`
- Role: `INDEPENDENT_INTAKE_REVIEWER`
- Reviewed INTAKE SHA-256:
  `f4efd86c242132082949432f7c44e0f1304599826b0e823fdff3abd39cf77294`
- Disposition: `INTAKE_REVIEW_PASS`
- Findings: `NONE`
- Waivers: `NONE`

## Review boundary and method

The reviewer did not author the INTAKE. Review used only the named downstream
continuity, prior-attempt evidence and local Git objects already present in the
restored hidden Core. Read-only checks resolved the Core `HEAD`, local
`origin/main`, configured remote, tracked cleanliness, left/right revision
count, intervening log, cumulative changed-path set, selected blob/tree object
ids and the downstream initializer SHA-256. No fetch, reconciler, initializer,
doctor, provider call, credential read, package installation, Core/workspace-
root/product/database/deployment mutation, commit or push occurred.

The protected operator assessment was not opened, read, hashed, staged,
inventoried or used. No broad downstream untracked inventory was performed.
The staged set was zero before this reviewer-owned artifact was created.

## Independent evidence

### Core refs, ancestry and cumulative delta

- Restored Core `HEAD` is
  `a7a797d7111be472ef2cbd928cbeffc70ccb6bc6`, with no tracked dirty entry and
  the expected public remote.
- Existing local `refs/remotes/origin/main` is
  `d7860138350130d6d105826ce186f1beeaba3c2d`. No network operation was used.
- Local `rev-list --left-right --count` for old versus proposed target is
  exactly `0 5`.
- The five commits, oldest first, are:
  `06c3d040a3dc8fa22fa27f2f9c3e40739def075e`,
  `2aa17841892fac3cde74214ad0471814084294e0`,
  `771cb3949678907d02c045e40772e008bd138245`,
  `a64bbc83756d8e30a917f97510866795df491130`, and
  `d7860138350130d6d105826ce186f1beeaba3c2d`. All five are dated 2026-08-29;
  the tip title is
  `sync: public EARTR source-pack profile from governance@e9d718c2e`.
- The cumulative tracked delta is exactly `202` paths. Applying the INTAKE's
  Markdown/docs-only classification — a path is inside that class when it is
  Markdown or under `docs/` or `documentation/` — leaves exactly `121` paths
  outside the class. The refresh is therefore correctly classified as not
  documentation-only.

### Sanctioned command surfaces

Old and proposed-target Git object ids are equal for every selected Core
surface:

- `scripts/update_cvf_workspace_public_core.ps1`:
  `4b705c6bf7b10bda62520dca488ecb453a4f4945`;
- `scripts/check_cvf_workspace_agent_enforcement.ps1`:
  `2ad83efee05c738fec40aa1779929da07f3d1c8c`;
- `scripts/new-cvf-workspace.ps1`:
  `5f311a1a1c8dc787c7b19011bf34c5a84fc773c7`; and
- `governance/toolkit/05_OPERATION` tree:
  `23fe8bd39ae102d3302d34de1d80208e2ef9bbb6`.

The corresponding scoped name-status comparison is empty. The downstream
sanctioned initializer currently hashes to
`bb37b16256a693853bddfdbcb40c2f7211e6984a90a972da83899962fae209c8`,
equal to the hash recorded by the accepted prior Work Order and independent
completion review. The INTAKE's no-tool-drift premise is supported.

### Prior attempt and preservation truth

The prior root-effects receipt independently hashes to
`0f81655e859b0c6e370cd1eeb79e2ae12fb75a4bfc9ca8b85844389ac89621eb`;
the independent completion review hashes to
`0340fce5248c1f1b5ed57191e946364c55ee62d23e53cd894e8143daed31a0b9`.
They consistently record `FAILURE_ROLLED_BACK` and
`REVIEW_PASS_FAILURE_ROLLED_BACK`, findings/waivers `NONE/NONE`: one
reconciler operation observed `d786013...`, followed by zero pin patches,
zero initializer run and zero retry; the old Core, `17/17` root targets,
`2/2` pins, `9/9` shared carriers and `1/1` binding were restored. P4-E stayed
at `DESIGN_REVIEW_PASS` and prohibited-effect counts were zero.

The accepted prior Work Order hashes to
`1de50c0f4545f975aa415cde4924db02b401a191a7703c6ec2d272d6c994518f`.
Its attempt-1 evidence paths and retained evidence directory remain historical
inputs only. The new INTAKE correctly requires DESIGN to assign a wholly
collision-free attempt-2 worker receipt, worker return, completion review,
evidence directory and any conditional rollback/rereview paths, prove each
future path absent before external effect, preserve prior evidence immutably,
and use preservation-first rollback with no retry or in-BUILD target rebase.

## Risk, authority and claim review

`R2` is correct because a later attempt would use public Git network and may
mutate the hidden Core plus declared workspace governance carriers. Current
authority covers only this fresh INTAKE and its independent local review. It
does not authorize DESIGN, SPEC, Work Order, BUILD, target adoption, network,
Core/root mutation, provider or credential use, installation, product/database
change, deployment, commit, push, retry, or P4-E SPEC.

The live-evidence rule remains active. This review makes no claim that CVF
controls AI/agent behavior and uses no mock or provider output as governance
proof. P4-E remains separately parked at accepted `DESIGN_REVIEW_PASS`; XR1
debt remains unresolved. The protected-assessment exclusion and immutable
prior-evidence boundary are explicit and fail-closed.

## Findings

`NONE`.

## Waivers

`NONE`.

## Disposition

`INTAKE_REVIEW_PASS`.

The INTAKE accurately bounds the proposed target rebase to local target
`d7860138350130d6d105826ce186f1beeaba3c2d`, carries forward rollback and
collision-free evidence obligations, and preserves the R2/external-effect and
P4-E stop boundaries. This disposition closes only the INTAKE review gate. A
separately recorded phase transition is required before DESIGN; no external
effect is authorized by this review.
