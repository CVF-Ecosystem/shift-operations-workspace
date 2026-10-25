# P5-A2 supplied history/numeric worker return

Status: `REPAIR_RETURN_FOR_INDEPENDENT_REREVIEW`; risk R2; implementation/repair worker Sol. Root independently reviews, owns metadata/catalog reconciliation and commits. Product milestone P5-A2 and Phase 5 remain open. Full Product Milestone Binding: `docs/decisions/P5A2_PROACTIVE_REPORTING_INTAKE_DESIGN_2026-10-24.md`; accepted SPEC: `docs/specs/P5A2_PROACTIVE_REPORTING_SPEC.md`; approved bounded Work Order: `docs/work_orders/P5A2_PROACTIVE_HISTORY_NUMERIC_WORK_ORDER.md`. All live/key/model/CSV work remains deferred.

Initial worker packet was `18/18` focused and `41/41` with P2-R snapshot regression. Independent round-1 review `CHANGES_REQUIRED` found NUM-R1-1..5; those initial passes remain historical and do not prove the missing cases. Repair round 1 produced `24/24` focused and `47/47` with the snapshot regression. Independent rereview accepted those five fixes but found NUM-R2-1: a 501-record visible candidate was serialized before cap refusal. Repair round 2 now has `25/25` focused and `48/48` with the snapshot regression, pending final independent rereview and root's full gate.

The new `reporting_engine.proactive_analysis.analyze` accepts explicit supplied canonical Report candidates, an exhaustive eligible-shift manifest, aware `[start,end)` window and completeness assertions. It either returns a deterministic next-eligible-shift snapshot incident-count projection with lineage/evaluation digests, rational residual envelope and signals, or abstains with a reason and no published forecast/signals. It has no ledger, scheduler, network, provider, API/UI, RAG, persistence, approval or operational writeback. Caller-provided scope/retention flags are **input assertions**, not actual authorization or database exhaustiveness proof.

| Proof | Worker evidence and limit |
|---|---|
| H1 | Selected `Report` fully reconstructed; canonical aggregate and per-record manifest recomputed. Visible duplicate versions compare immutable content bytes in both orders; lifecycle-only flags do not claim historical approval. Malformed copied content is a controlled refusal. |
| H2 | At each historical origin, select highest visible version with both report cutoff and creation time bounded; current/status flags never select historical truth. Late successor fold lineage probe passes. |
| H3 | Aware UTC-normalized half-open window and source event time checked; naive, contradictory and end-exclusive probes refuse, equivalent offsets preserve digest. |
| H4 | Only literal `True` completeness/retention assertions admitted; malformed containers and mixed version types are controlled refusals. Missing expected report and >500 candidate shift/report/incident bounds refuse before analysis. A spy regression proves a visible 501-incident candidate **first** in input is refused before `ReportContent.model_dump`; a future-created oversized candidate is excluded before this check. This does not establish real DB scope completeness. |
| N1 | Independent pre-BUILD vectors cover median, ties-to-even, raw fractional band, trend/MAD threshold equality, zero/500 domain boundaries. |
| N2 | Most recent twelve folds reconstruct visible history at each target origin; >18-observation and late-correction tests inspect target IDs, selected versions, prediction numerators and target exclusion. Fewer than six visible prior observations has available/required diagnostics. |
| N3 | Assessment MAE versus persistence, in-sample residual envelope, exact 24h and drift equality boundaries; stale/drifted results publish no forecast or signals. No accuracy or prospective coverage claim. |
| N4 | Independent test preimages reproduce exact outer, training and evaluation SHA-256 values. Training payload retains the original query window and separate origin as-of, including a report cutoff equal to origin. Pure history context exposes source refs and supplied actor/completeness assertions; no source fields are mutated. |
| P1 | Product modules import no environment, credential, network or persistence code. Success/refusal tests compare canonical supplied input serialization before/after. |
| P2 | Repaired focused new tests `25/25`, with P2-R snapshot regression `48/48`; inheritance and file-size guards pass after round 2. Earlier invariant, session and knowledge guards passed without their surfaces changing. Initial `18/41`, round-1 `24/47` and root's findings remain retained. Repository validator previously reported catalog metrics drift for the five new files; root owns regeneration, independent rereview and normal full pre-commit. |

Evidence: `docs/decisions/P5A2_PROACTIVE_HISTORY_NUMERIC_EVIDENCE_2026-10-24.json`. Every new Python file is below 300 lines. Source paths are the five `packages/reporting-engine/src/reporting_engine/proactive_*.py` modules, package README, `tests/unit/proactive_helpers.py`, `tests/unit/test_proactive_numeric.py`, `tests/unit/test_proactive_history.py`, and `tests/integration/test_proactive_supplied_contract.py`; no other product path was changed by this worker.

| Exact changed product/test path | SHA-256 bytes |
|---|---|
| `packages/reporting-engine/src/reporting_engine/proactive_models.py` | `f61fbbfc141b872294e6a1cccf1a389ecc05eea34e61b3025c1183f289172004` |
| `packages/reporting-engine/src/reporting_engine/proactive_history.py` | `cad9546dcc46d137ecbea2cfab24d656b7990f6075a72875b012b5196c044c9f` |
| `packages/reporting-engine/src/reporting_engine/proactive_metrics.py` | `fff29594b6431c1d1180c54e878ff5a09eaf9f564e1d8f49bf9336a835d3cbb7` |
| `packages/reporting-engine/src/reporting_engine/proactive_evaluation.py` | `6f9c50591e4e234911cd30a7702e0b3d2729e46441b77e489b73d3cfc17e2caf` |
| `packages/reporting-engine/src/reporting_engine/proactive_analysis.py` | `4e5a2c26e3b6f524131e70d1dcdac1b145574606c569c2c2729cad90af1c005c` |
| `packages/reporting-engine/README.md` | `f346076228bde004ed7f65fce35b8e5a04c1c06cc4bc16127b139e36e9232ac1` |
| `tests/unit/proactive_helpers.py` | `72aaef3653e9b4886d3cb8cf322a2b3596983813d6b7e5b75dea45cf4598de25` |
| `tests/unit/test_proactive_numeric.py` | `06794358165457057cd63a0bab538da1e3c75a8c4cbb07c10b11d76fa9dcf8bd` |
| `tests/unit/test_proactive_history.py` | `6c59cb687cc5da8826da5d1d1dade9f1b763f7672ae6b6778cab04720d5e0aeb` |
| `tests/integration/test_proactive_supplied_contract.py` | `88746f7c8c98ea938d98370d490b244b1e22110eaf29ee458a88b2b99af3ddac` |

| Gap | Return status and remaining owner/destination |
|---|---|
| A2-G01 | BLOCKED: Root/operator P5-A A7 decision and closure. |
| A2-G02 | BLOCKED: Root with backend/UI workers, operational RAG/context gate. |
| A2-G03 | PURE NUMERIC IMPLEMENTED FOR REVIEW; Root/operator final method fit and integrated acceptance. |
| A2-G04 | SUPPLIED HISTORY IMPLEMENTED FOR REVIEW; Sol/root actual ledger adapter and SQL point-in-time proof. |
| A2-G05 | SUPPLIED TIME/COVERAGE IMPLEMENTED FOR REVIEW; Sol/root operational retention and timezone readiness. |
| A2-G06 | OPEN: Sol/root real auth, complete scoped query/pagination integration. |
| A2-G07 | OPEN: Sol/root scheduler, durable run lifecycle and drills. |
| A2-G08 | PURE SIGNAL IMPLEMENTED FOR REVIEW; Sol/Luna/root application display/business evaluation. |
| A2-G09 | PURE BASELINE/FOLDS IMPLEMENTED FOR REVIEW; Sol/root operational forecast evaluation. |
| A2-G10 | PURE BAND/DRIFT IMPLEMENTED FOR REVIEW; Sol/Luna/root prospective quality/display, P5-B shared telemetry. |
| A2-G11 | OPEN: Sol API, Luna UI, Root review at P5-A2 integration. |
| A2-G12 | OPEN: Sol/Luna/root exact human approval and action gate. |
| A2-G13 | NUMERIC/INPUT PROBES IMPLEMENTED FOR REVIEW; Sol/root scheduler/recovery/auth/context/SQL/browser drills remain. |
| A2-G14 | PARKED: Root/operator future admitted real-provider evidence only for applicable CVF AI-governance claim. |

P5-B dashboard/search/shared observability, P5-C backup/restore/resilience/security/performance and P5-D deployment/runbook/Shadow Mode/freeze remain open at `docs/implementation/EXECUTION_ROADMAP.md`, Root accountable, Sol backend and Luna UI, operator final business acceptance. No gap or milestone is marked closed by this worker return. Next governed move: one consolidated independent source/evidence review, same-scope repair if findings, root-owned catalog and full gate, then bounded material commit and continuity synchronization.
