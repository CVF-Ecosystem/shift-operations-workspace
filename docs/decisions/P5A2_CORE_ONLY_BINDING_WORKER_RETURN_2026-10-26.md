# P5-A2 Core-only binding correction — worker return

Status: COMPLETE_PENDING_REVIEW

Date: 2026-10-26. Role REPAIR_WORKER; BUILD/R2. Independent rereview and Root commit/continuity remain pending. Authority: accepted [SPEC](P5A2_CORE_ONLY_BINDING_DESIGN_SPEC_2026-10-26.md), [Work Order](../work_orders/P5A2_CORE_ONLY_BINDING_WORK_ORDER.md) `APPROVED_FOR_EXECUTION`, Root's fresh BUILD acknowledgment and same-scope F1/F2 repair release.

Self-declared worker-return artifact: yes

## Product Milestone Binding

The accepted SPEC and WO retain the complete current G01–G14 evidence/remainder/owner/destination table and P5-A2 user outcome. This correction only unblocks review/closure of the already completed synthetic SQL substrate for G04/G05/G13; it does not close their operational criteria. G01/A7/G02 remain blocked; G06 scoped query, auth, caps, cohort and retention remain open/unknown; operational G03/G08–G10/G13, G07/G11/G12 remain open, G14 live held. Root is accountable and owns configuration, review coordination and commit; Sol owns backend controls, Luna independent review/UI, operator business acceptance. P5-A2 gate and P5-B/C/D roadmap destinations remain; Phase 5 remains 0/5. Next product work is G04–G06 SPEC after bounded SQL result closure.

## Changed worker surfaces and source proof

| Path | SHA-256 | Result |
|---|---|---|
| `scripts/check_cvf_core_machine_inheritance.py` | `a876c9727f3e25706f64df7bebe06e34404b05f7380a518cb8b18b2c13e534f0` | Thin adapter; verifies before `-I` native Core CLI and propagates `--base/--head/--enforce` and exit. |
| `scripts/_cvf_core_binding.py` | `f80271b2a201da98b36746a452c15ac510a612a96bca465b1e761d4eeb8dfbe8` | Exact local public origin/HEAD, Core-only manifest/policy and live flags, selected tracked Git blobs and LF SHA-256; no private path, remote freshness or network. |
| `scripts/initialize_cvf_clone.ps1` | `5e5c1b0652e938f4b482f285e120b5822e262899ecd82e3a08bfcdd428cd3403` | F1 repair: checks preexisting Core origin and exact HEAD read-only; only a clone created by this invocation may set config or check out the declared pin. No latest-main doctor/fetch. |
| `tests/unit/test_cvf_core_machine_inheritance.py` | `cc34dcade3d324b25bfdd88395b3517468e262a133e551f6e637cb551eda962b` | F2 repair: actual native CLI rejects malformed active Work Order and self-declared return; direct native `check_recheck` validates this decision-path return with anchored applicability. |
| `tests/unit/test_cvf_core_binding.py` | `ed0bcbed5c1f133e438be94d06e34af3ea3af8c1f0889096c207d5be65ca8cc7` | F1 disposable PowerShell/Git regression preserves existing Core HEAD/config/status; distinct missing Core, malformed pin and well-formed wrong digest negatives added. |
| `tests/integration/test_project_knowledge_ingest_rehearsal.py` | `904d149bda37717f30c332c3f06095180132d0bf6c4302d2de4ea31ab9bd0176` | AM1 repair: inherits current local binding, checks exact HEAD/approved origin and pinned helper Git blob/raw SHA; removes `origin/main` equality. Native PowerShell ingest/index, token scan, negative cases and cleanup remain. |

The worker did not edit Root-owned manifest/policy/AGENTS/knowledge/continuity, CVF repositories, hooks, SQL source, oracle or historical Docker receipt. Existing native checker and standard remain pinned at Core `aa672d11910ae1982557e4810a2a8002a611e9e6` with manifest SHA-256 `8f00c6421eebe3c1b237e5307ac6e2b0b0343c9a35cf635bbab17aa886e00e8e` and `b3af2fcbd09160d9f2ae88c861bd67d45ba1425bd21e577bf880cb0f1f29ea3c`.

## Focused verification and limits

- Initial focused proof before independent review: **15 passed**. Independent review then recorded CORE-BUILD-F1/F2; the same-scope repair is described above, without erasing those findings.
- `python -X utf8 -m pytest -q tests/unit/test_cvf_core_machine_inheritance.py tests/unit/test_cvf_core_binding.py`: **21 passed** after repair. The temporary preexisting-Core initializer invocation exited nonzero before any Core config, HEAD or working-state mutation; no fetch or provider call.
- `python -X utf8 scripts/check_cvf_core_machine_inheritance.py --enforce`: exit **0**, native guard `Violations: 0`, `COMPLIANT` on current project. Native malformed active Work Order and scanned `docs/reviews/` return each exit **2**. The current project's `docs/decisions/` worker return is **outside native CLI automatic return scanning**; the pinned native `check_recheck` is invoked directly on its exact bytes in the focused test and returns `[]`, after asserting the standalone applicability marker.
- `check_session_state.py`, `check_project_knowledge.py`, `check_file_size.py`, `check_invariant_families.py`, `generate_catalog.py --check`: each **PASS**.
- The first normal full material hook was attempted by Root after independent source acceptance and stopped without a commit: **1 failed, 3244 passed, 147 skipped, 4 warnings, 8 errors**, 206.99 s; retained `.venv/p5a2-core-only-material-20261026.log`. All nine implicated results traced to the same ingest test helper `HEAD == origin/main == pin` assertion; cleanup errors followed the aborted callback. No result was waived, skipped or deselected.
- AM1 separately authorized this exact sixth test path and Root reacknowledged BUILD. One focused run of the nine ingest tests plus 21 Core-focused tests returned **30 passed in 19.74 s**. The pinned ingest helper raw SHA remains `856b99d9273b0384c40c05bc2132eae66e9dce20b9a9c8b75c3d91ae7016d2c6`; helper working bytes match pinned Git blob after LF normalization. Final adapter, session, knowledge, size, invariant-family and catalog guards each **PASS**.
- The initializer was not run against the real Core. No package, image, container, DB, network, provider, credential, model, CSV, staging or commit action occurred in this AM1 repair. Routine control integrity and packet syntax do not prove CVF AI-governance behavior. The Docker SQL receipt and its spent acquisition history remain unchanged. Independent AM1 rereview and an unmodified normal full hook are Root's next gates.

## Return-Time Closeability Recheck

closeabilityDisposition: CLOSEABLE
outsideAuthorityBlockers: NONE
nextRepairRoute: NONE
workerRedispatchAllowed: YES

These scalar values describe source/return closeability within the current WO. Root and independent reviewer must inspect the complete changed set before material commit; no self-approval or further worker effects are authorized by this return.
