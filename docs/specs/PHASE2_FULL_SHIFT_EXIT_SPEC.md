# SPEC — Phase 2 Full-Shift Exit Gate

- Spec id: `P2-FULL-SHIFT-EXIT-SPEC-001`
- Tranche: `P2-FULL-SHIFT-EXIT-2026-08-02`
- Phase: `SPEC`
- Risk: `R2`
- Source baseline: `e1ac14beaf426ded1b763ff3373b238a065c4694`
- Status: `PROPOSED_FOR_INDEPENDENT_AUTHORIZATION_REVIEW`

## Requirements

### R1 — Evidence-only boundary

BUILD may add or adjust only evidence tests, runner plumbing, receipts and
catalog/control-mapping truth. Product source, API/OpenAPI, domain/ledger,
migrations, auth/CVF policy, dependencies/lockfile, CI and deployment remain
zero-diff.

### R2 — One lineage and scheduled interval

Every positive assertion must belong to one source shift and one destination
shift created during the run. The source `ends_at - starts_at` must equal
exactly 12 hours and remain so after durable reconnect. No wall-clock soak is
claimed.

### R3 — Real principals and assignment

Use authenticated persisted users and active assignments. The operator owns
source/destination actions; `sup1` reviews/approves/freezes; distinct `sup2`
must be assigned to both shifts, acknowledge the handover and create the Report
approval receipt. The supervisor staffing control plane is available before an
ordinary operational shift is selected, so initially unassigned `sup1` must use
the rendered staffing UI to assign both `sup1` and `sup2` to source and
destination. No assignment bootstrap API call is permitted. Client capabilities
are never authority.

### R4 — Update and task

The operator creates a real `shift_update` event and an R0 task. The task
transition is staged only while pre-dispatch offline, produces zero mutation
requests until reconnect, replays exactly once with the recorded CAS, and only
a genuine fresh read may render committed `IN_PROGRESS`. With the operator page
still open and the event absent from its confirmed
timeline, `sup1` confirms that exact event through a second rendered page; the
operator page must show the event in its confirmed timeline through polling,
without reload/manual refresh. Final event state is confirmed and final task
state remains `IN_PROGRESS` for the handover snapshot.

### R5 — Handover integrity

The operator creates the handover after the task becomes `IN_PROGRESS`.
Its immutable snapshot must be non-empty and contain the exact current open-work
item/version. `sup1` reviews and distinct destination-assigned `sup2`
acknowledges. Snapshot drift or missing destination assignment must refuse.

### R6 — Close, Report and freeze

The operator closes with current CAS, generates the current immutable
`END_SHIFT` Report and submits it to `IN_REVIEW`. `sup2` creates the durable
six-field `report.approve` receipt; `sup1` approves with expected version/status
and freezes with current shift version. Freeze must atomically produce Shift
`FROZEN`, current Report `FROZEN`, `shift.freeze` and `report.freeze` audits.
No retired override is accepted or recorded.

### R7 — Persisted lineage

After PostgreSQL engine disposal/reconnect, verify all identifiers link to the
same source lineage, source shift is FROZEN, destination remains valid, event is
confirmed, task is IN_PROGRESS, handover is ACKNOWLEDGED with unchanged
snapshot, current Report is FROZEN, approval receipt binding is exact, and the
required action/actor audit set is present with no anonymous mutation.

### R8 — Refusal matrix

The governance runner must prove anonymous shift create/close, unassigned read/mutation,
stale task/close/freeze CAS, handover acknowledgement without destination
assignment, Report approval without valid receipt, freeze before close,
freeze without acknowledged-current handover and freeze without current
approved Report fail closed with observed provider-call delta zero and no
unintended durable mutation. Separately, the real-browser spec owns transport
ambiguity: exactly one request, no queue insertion, no automatic retry, visible
`outcome_unknown`, explicit fresh-read reconciliation of the authoritative
state, and no duplicate mutation. Ambiguity does not imply the intended request
failed to commit.

### R9 — Browser action boundary

Every positive action exposed by the UI must be driven through the rendered UI.
API calls in Playwright may log in or observe final records exposed by existing
reads, and the spec must label every such call. All staffing and operational
actions use rendered UI. No route interception may fabricate a success response.

### R10 — P2-D composition

The browser run must prove one bounded queue replay and one polling-observed
remote change in the same shift lineage. It must end online with zero pending,
blocked, outcome-unknown or applied-stale queue residue and must not claim push,
exactly-once or fully-offline behavior.

### R11 — Live provider gate

The governance runner's own operational/refusal execution must keep its fresh
provider counter at zero. It must also validate a sanitized temporary JSON
result from the separately completed browser wrapper (`checkpoint`, Playwright
PASS and bounded-queue PASS) without claiming that counter observed the browser
process. Only after browser validation, durable lineage/audit verification and
exact-parent rehearsal may exactly one real call occur. Receipt data is
sanitized and contains only model, endpoint class, HTTP status, expected-token
match, call count, browser-result reference and bounded evidence summary.

### R12 — Evidence and cleanup

Frozen frontend install, typecheck/all tests/build, dedicated real-browser run,
full Python, disposable PostgreSQL live suite, repository gates, exact-parent
rehearsal and owned process/container/anonymous-volume/temp cleanup must pass.
No secret, DSN, bearer, raw provider body or raw exception may be recorded.

### R13 — Review and closure

BUILD stops for independent review with zero staged files. Only independent
`REVIEW_PASS`, exact changed-set verification and push permit a separate C4 to
mark the exit gate and Phase 2 `CLOSED_BOUNDED`. Post-Phase-2 work begins only
after that C4 and under fresh authorization.

## Acceptance criteria

- **AC-01:** exact 12-hour scheduled source shift and one destination lineage.
- **AC-02:** real JWT users/assignments and distinct operator/sup1/sup2 duties.
- **AC-03:** event create/confirm and actor audits persist.
- **AC-04:** offline task transition has zero pre-reconnect POST, one replay and
  fresh committed rendering.
- **AC-05:** operator polling reveals `sup1`'s exact event confirmation in the
  confirmed timeline without reload; task remains `IN_PROGRESS`.
- **AC-06:** handover snapshot is non-empty, exact, reviewed and acknowledged.
- **AC-07:** close→Report generate→submit→receipt→approve→freeze succeeds.
- **AC-08:** reconnect proves final records, approval and actor-bound audits.
- **AC-09:** governance-runner R8 refusals leave its counter zero; browser-owned
  ambiguity has one request/no retry/no queue and reconciles final state.
- **AC-10:** admitted proof allows exactly one sanitized real provider call.
- **AC-11:** real Chromium/FastAPI run passes and queue/process residue is zero.
- **AC-12:** disposable PostgreSQL suite/migrations/cleanup pass.
- **AC-13:** frontend/full Python/repository/file-size/catalog/session/doctor pass.
- **AC-14:** exact-parent rehearsal and exact BUILD ceiling pass.
- **AC-15:** protected product/API/schema/dependency/CI paths have zero diff.
- **AC-16:** independent reviewer returns `REVIEW_PASS` with no waiver.
- **AC-17:** C4 alone may close Phase 2 bounded and activate the parked queue.

## Stop conditions

Stop on baseline/continuity drift, missing runtime prerequisite, product repair,
mocked governance proof, UI action replaced by API arrangement, empty/stale
handover snapshot, reused/non-distinct approval identity, hidden auto-retry,
provider call before admission, unsanitized output, cleanup residue, outside or
unnecessary path, file-size violation, failing gate or claim expansion.
