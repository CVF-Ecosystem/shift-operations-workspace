# Independent Core-binding adoption review

Status: REVIEWER_ACCEPTED_BOUNDED

Independent reviewer: delegated reviewer, separate from implementation worker.
Reviewed 2026-11-04 against the changed project files and installed public
Core. Product Milestone Binding: P5-A2 G04/G05 preflight support only; the
complete G01–G14 reconciliation and owner/destination table are in
`docs/work_orders/CVF_CORE_BINDING_ADOPTION_2026-11-04.md`.

## Evidence and disposition

- Installed Core HEAD `c4c8767ac8861854f40d466ba338ffd11eb9558e`
  is clean; origin matches the declared public repository.
- Both selected control artifacts have zero diff from old pin `aa672d1`;
  LF SHA-256 values match the manifest (`8f00c642…`, `b3af2fcb…`).
- Current AGENTS pin, manifest, state/bootstrap/mirror, handoff, registry and
  generated index align. Native preflight COMPLIANT/0; session, catalog and
  diff checks PASS. File-size guard PASS.
- The work-order status is a recognized non-dispatch state. Native
  closeability reports NOT_APPLICABLE_WITH_REASON; it did **not** validate
  a gate-to-role contract. This bootstrap correction had no active worker
  dispatch or future redispatch authority.
- No changed `docs/decisions/` packet self-declares a worker return or
  completion review marker. Pinned `check_recheck` is not applicable for
  this adoption; the native CLI does not auto-scan that legacy family.

The first normal hook attempt failed: 3530 tests passed, 148 skipped,
2 failed and 17 errored. One failure family was ambient provider credential
refusal in the NO_AI demo; the other was project knowledge source-pin drift
after the binding/status edits. The knowledge pack was refreshed and its
validator now passes. Independent repair review accepted removing the two
ambient provider-key names from the child process that runs the unchanged
normal hook. This does not bypass a test or read a secret value. The rerun
passed 3549 tests, 148 skipped and 4 warnings. Material commit
`4b4488f890d741481f907a2c898486f94ea7e927` was independently reviewed
as an exact 15-path clean committed range; terminal material review PASS with
findings/waivers NONE/NONE. The reviewer did not independently capture or rerun
the full hook stdout; the hook result is the commit process's reported receipt.

Disposition: PASS for the bounded Core-binding adoption. No blocking findings
or waivers. Normal pre-commit hook, material commit, actual-SHA continuity and
clean committed-range review remain before FREEZE.

P5-A2 remains OPEN, Phase 5 remains 0/5. AM4 UI acceptance is UNMET and
attempt SPENT. This review does not establish AI-governance behavior or
authorize runtime, provider, browser, SQL, reset, push or deployment effects.
