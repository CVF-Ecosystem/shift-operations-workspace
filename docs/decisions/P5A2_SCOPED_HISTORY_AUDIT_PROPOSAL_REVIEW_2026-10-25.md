# P5-A2 G04–G06 synthetic-first proposal — independent DESIGN review

Date 2026-10-25. INTERNAL_AGENT independent REVIEWER, R2, phase DESIGN. Reviewed Root-authored `P5A2_SCOPED_HISTORY_AUDIT_AND_SYNTHETIC_DATA_PROPOSAL_2026-10-25.md` at project `552612603bb35fd97a9f688787948542dc59e86e`, accepted 20-source SHA-pinned `P5A2_SCOPED_HISTORY_SOURCE_VERIFICATION_2026-10-25.md`, four bounded test excerpts recorded there, [parent P5-A2 binding](P5A2_PROACTIVE_REPORTING_INTAKE_DESIGN_2026-10-24.md#product-milestone-binding), [SPEC](../specs/P5A2_PROACTIVE_REPORTING_SPEC.md), canonical continuity, status/index and [Phase 5 roadmap](../implementation/EXECUTION_ROADMAP.md). Inheritance `--enforce`: 0 violations. This review consumes source evidence; it did not run tests, open a database, invoke a provider, or re-audit the repository.

## Product Milestone Binding and review question

P5-A2 user outcome is integrated assignment-scoped scheduled signals and forecasts with lineage/current/history/freshness, plus approval of the exact run/version/source digest before any durable recommendation or operational action. Full acceptance is G01–G14 in the parent binding; Root is accountable, Sol owns backend/contracts/analytics/scheduler, Luna UI, independent Root review, operator final business fit. This review checks only whether the proposed G04–G06 source design can use synthetic data without overstating operational or CVF-governance proof. It grants no SPEC, Work Order or BUILD authority.

| Gap set | Current evidence and remaining acceptance | Owner / concrete destination |
|---|---|---|
| G01–G02 | P5-A A7 blocked after 401; operational RAG unproved | Root/operator P5-A A7 admission/closure; Root/Sol P5-A2 integrated-context gate |
| G03–G05 | Pure supplied-input metric/history/time portions accepted; actual cohort/ledger/time/retention and business fit remain OPEN/UNKNOWN | Root/Sol/operator P5-A2 source SPEC, integrated evidence and metric acceptance |
| G06 | Current assignment exists; exhaustive bounded revocation-safe query unproved | Sol/Root P5-A2 API/security source integration |
| G07 | Schedule/run lifecycle and recovery open | Sol/Root P5-A2 scheduler/drills |
| G08–G10 | Pure anomaly/forecast/calibration portions accepted; operational quality/drift/display unproved | Sol/Root/operator P5-A2 signal/forecast/quality; Luna P5-A2 display; P5-B observability |
| G11–G12 | Forecast API/UI and exact human approval open | Sol/Luna/Root/operator P5-A2 application/approval integration |
| G13 | Pure chronology evidence accepted; actual scheduler/failure/recovery drills open | Sol/Root P5-A2 evaluation/drills |
| G14 | Applicable real-provider CVF governance proof held | Root/operator fresh external-effect admission and P5-A2 REVIEW |

P5-B dashboard/search/observability, P5-C backup/restore/resilience/security/performance, and P5-D deployment/Shadow Mode/release stay with their roadmap owners and gates. P5-A/P5-A2 remain OPEN; Phase 5 remains 0/5.

## Findings and disposition

**REVIEW_PASS_BOUNDED.** Blocking design findings: none. The proposal correctly separates three proof levels: synthetic fixture ground truth for numeric/query behavior; actual InMemory/SQL backend mechanics on that fixture; and later owner-certified operational coverage/quality. It explicitly refuses to treat fixture completeness as production retention or `complete=true` for an unknown corpus. It also separates synthetic PUBLIC payload from a mock provider: any claim that CVF controlled AI still needs an admitted real provider request/response, and all live/key/model/CSV work remains held.

The source direction reuses native Report immutable version/content/manifest/digest, Ledger and assignment/JWT ownership, accepted pure H1–P2 logic and existing harness excerpts. F01–F06 trace the relevant missing links: reportless-shift cohort, count before materialization, one consistent read snapshot, SQLite naive-time refusal, retention authority, and integration evidence. The suggested `ends_at in [start,end)` cohort is clearly a **candidate for the next reviewed SPEC**, not a silently accepted change to the current cutoff-based observation policy. Its treatment of reportless shifts, aware Shift time and late Report cutoff must be specified there before query implementation. No positive SQLite timezone readiness is inferred from refusal.

The next SPEC/WO should keep the proposed 36-shift fixture and 501 boundary probes as **separate bounded scenarios** with independent expected manifests, then define backend-specific isolation/authorization rechecks and authoritative retention ownership. This is review guidance within the stated next product packet, not a blocking finding or an automatic support tranche. The future shared query/outcome contract follows [invariant-family standard](../cvf/INVARIANT_FAMILY_STANDARD.md); this static review changes no matrix and is NOT_APPLICABLE for registration now.

**Static tranche:** design proposal accepted for bounded direction, subject to Root's normal material/actual-SHA continuity gates. **Milestone:** no G01–G14 integrated criterion, P5-A2, or Phase 5 milestone closes. Next governed move is one reviewed G04–G06 cohort/query/coverage/snapshot/cap SPEC and bounded Work Order before implementation; operational and live gates remain with their named owners.
