"""Actual PostgreSQL transaction observations and bounded concurrent writers."""
from __future__ import annotations

from datetime import timedelta
from threading import Event, Thread
from uuid import UUID, NAMESPACE_DNS, uuid5

from sqlalchemy import event, select, update

from operations_domain.assignment_models import ShiftAssignment
from operations_domain.models import Shift
from operations_ledger import _proactive_source_sql as source_sql
from operations_ledger import _proactive_source_sql_content as content_sql
from operations_ledger.tables import shift_assignments, shifts
from workspace_api.application.proactive_source import query_source

from p5a2_scoped_source_pg_fixture import context, when


def assert_closed_refusal(result, reason: str) -> None:
    assert result.payload is None
    assert result.receipt == {
        "outcome": "SOURCE_REFUSED", "receipt_version": "P5A2-SOURCE-RECEIPT-1",
        "cohort_policy_version": "P5A2-COHORT-ENDS-1",
        "numeric_policy_version": "P5A2-INITIAL-1", "reason": reason,
    }


def counted_query(ledger, row: dict, coverage, monkeypatch):
    """Spy on native body loader and SQL body SELECT, after fixture seed."""
    loads, body_selects = [], []
    original = content_sql.load_reports

    def load(conn, models, report_ids):
        loads.append(len(report_ids))
        return original(conn, models, report_ids)

    def statement(_conn, _cursor, sql, _params, _ctx, _many):
        lowered = sql.lower()
        if "from reports" in lowered and ("reports.content," in lowered or
                                         "reports.content as" in lowered):
            body_selects.append(sql.splitlines()[0][:80])

    principal, scope, start, end, as_of = context(row)
    with monkeypatch.context() as patch:
        patch.setattr(content_sql, "load_reports", load)
        event.listen(ledger.engine, "before_cursor_execute", statement)
        try:
            result = query_source(principal, scope, start, end, as_of, ledger, coverage)
        finally:
            event.remove(ledger.engine, "before_cursor_execute", statement)
    return result, {"body_load_calls": len(loads), "body_rows": sum(loads),
                    "body_select_calls": len(body_selects)}


def _identity(conn) -> dict:
    transaction = conn.get_transaction()
    assert transaction is not None, "transaction boundary not established"
    pid, snapshot = conn.exec_driver_sql(
        "SELECT pg_backend_pid(), txid_current_snapshot()::text").first()
    return {"backend_pid": int(pid), "snapshot": str(snapshot),
            "transaction_object_id": id(transaction)}


def traced_ready_query(ledger, row: dict, coverage, foreign_id, monkeypatch):
    """Observe real cohort/candidates/scalar/body on one RR unit, then fresh."""
    calls, transactions = [], []
    old_cohort = source_sql._cohort
    old_candidates = source_sql.SqlSourceUnit.candidates
    old_refs = content_sql.incident_ref_counts
    old_bodies = content_sql.load_reports

    def cohort(conn, *args):
        transactions.append(conn.get_transaction())
        calls.append(("cohort", _identity(conn)))
        return old_cohort(conn, *args)

    def candidates(unit, ids):
        transactions.append(unit.conn.get_transaction())
        calls.append(("candidates", _identity(unit.conn)))
        return old_candidates(unit, ids)

    def refs(conn, ids):
        transactions.append(conn.get_transaction())
        calls.append(("scalar_refs", _identity(conn)))
        return old_refs(conn, ids)

    def bodies(conn, models, ids):
        assert foreign_id not in ids, "foreign Report body entered authorized loader"
        transactions.append(conn.get_transaction())
        calls.append(("body", _identity(conn)))
        return old_bodies(conn, models, ids)

    principal, scope, start, end, as_of = context(row)
    with monkeypatch.context() as patch:
        patch.setattr(source_sql, "_cohort", cohort)
        patch.setattr(source_sql.SqlSourceUnit, "candidates", candidates)
        patch.setattr(content_sql, "incident_ref_counts", refs)
        patch.setattr(content_sql, "load_reports", bodies)
        result = query_source(principal, scope, start, end, as_of, ledger, coverage)
    assert [name for name, _ in calls] == ["cohort", "candidates", "scalar_refs", "body", "cohort"]
    assert all(tx is transactions[0] for tx in transactions[:4])
    assert transactions[-1] is not transactions[0]
    assert len({(x["backend_pid"], x["snapshot"]) for _name, x in calls[:4]}) == 1
    return result, {"source": calls[0][1], "fresh": calls[-1][1],
                    "stages": [name for name, _identity in calls]}


def _writer_mutation(conn, writer, row: dict, fixture) -> None:
    assignment = fixture.assignments[0]
    if row["id"] == "revoke":
        writer.revoke_assignment(assignment.assignment_id, revoked_by=assignment.user_id,
                                 expected_version=1, unit=conn)
    elif row["id"] == "add":
        detail = row["mutationFields"]
        shift_id = UUID(detail["new_shift_id"])
        end = when(detail["ends_at"])
        shift = Shift(shift_id=shift_id, name="POST-SEAL-ADDED",
                      starts_at=end - timedelta(hours=1), ends_at=end,
                      created_at=end - timedelta(hours=2))
        writer.create_shift(shift, unit=conn)
        writer.add_assignment(ShiftAssignment(
            assignment_id=uuid5(NAMESPACE_DNS, f"pg-source-add-{shift_id}"),
            shift_id=shift_id, user_id=assignment.user_id,
            assigned_by=assignment.user_id, assigned_at=end - timedelta(hours=2)), unit=conn)
    elif row["id"] == "assignment_version":
        changed = conn.execute(update(shift_assignments).where(
            shift_assignments.c.assignment_id == assignment.assignment_id,
            shift_assignments.c.version == row["mutationFields"]["before"]
        ).values(version=row["mutationFields"]["after"]))
        assert changed.rowcount == 1
    elif row["id"] == "shift_time":
        changed = conn.execute(update(shifts).where(
            shifts.c.shift_id == fixture.shifts[0].shift_id
        ).values(ends_at=when(row["mutationFields"]["ends_at"])))
        assert changed.rowcount == 1
    else:
        raise AssertionError("unknown frozen writer case")


def _committed_writer(engine, writer, row: dict, fixture, go: Event, done: Event,
                      identities: list, errors: list) -> None:
    try:
        if not go.wait(12):
            raise AssertionError("source-to-writer barrier timed out")
        with engine.begin() as conn:
            identities.append(_identity(conn))
            _writer_mutation(conn, writer, row, fixture)
        identities[-1]["committed"] = True
    except BaseException as exc:
        errors.append(f"{type(exc).__name__}: {exc}")
    finally:
        done.set()


def race_query(ledger, writer, row: dict, fixture, monkeypatch) -> tuple[object, dict]:
    """Writer commits only after first unit seals, before actual native fresh view."""
    go, done = Event(), Event()
    writers, errors, reads, transactions = [], [], [], []
    thread = Thread(target=_committed_writer,
                    args=(writer.engine, writer, row, fixture, go, done, writers, errors), daemon=True)
    original_fresh = ledger.fresh_scoped_cohort
    original_cohort = source_sql._cohort

    def observed_cohort(conn, user_id, start, end):
        transactions.append(conn.get_transaction())
        reads.append(_identity(conn))
        return original_cohort(conn, user_id, start, end)

    def fresh(*args):
        go.set()
        assert done.wait(15), "writer commit barrier timed out"
        thread.join(timeout=2)
        assert not thread.is_alive() and not errors and writers and writers[0]["committed"]
        return original_fresh(*args)

    principal, scope, start, end, as_of = context(row)
    with monkeypatch.context() as patch:
        patch.setattr(source_sql, "_cohort", observed_cohort)
        patch.setattr(ledger, "fresh_scoped_cohort", fresh)
        thread.start()
        try:
            result = query_source(principal, scope, start, end, as_of, ledger, fixture)
        finally:
            go.set()
            done.wait(15)
            thread.join(timeout=2)
    assert not errors and not thread.is_alive()
    assert len(reads) == 2 and transactions[0] is not transactions[1]
    assert reads[0]["snapshot"] != reads[1]["snapshot"]
    assert writers[0]["backend_pid"] != reads[0]["backend_pid"]
    return result, {"source": reads[0], "fresh": reads[1], "writer": writers[0]}


def repeatable_read_probe(ledger, writer, row: dict, fixture) -> dict:
    """Physical writer commits while one read-only RR unit is still open."""
    principal, _scope, start, end, as_of = context(row)
    assignment = fixture.assignments[0]
    go, done = Event(), Event()
    writers, errors = [], []
    thread = Thread(target=_committed_writer,
                    args=(writer.engine, writer, {**row, "id": "assignment_version",
                         "mutationFields": {"before": 1, "after": 2}}, fixture,
                          go, done, writers, errors), daemon=True)
    thread.start()
    try:
        with ledger.scoped_source_read(principal.user_id, start, end, as_of) as unit:
            source_tx = unit.conn.get_transaction()
            before = unit.cohort()
            source_id = _identity(unit.conn)
            isolation = unit.conn.exec_driver_sql("SHOW transaction_isolation").scalar_one()
            readonly = unit.conn.exec_driver_sql("SHOW transaction_read_only").scalar_one()
            assert len(before) == 1 and before[0].assignment_version == 1
            go.set()
            assert done.wait(15), "snapshot writer barrier timed out"
            thread.join(timeout=2)
            assert not errors and not thread.is_alive() and writers[0]["committed"]
            inside = unit.cohort()
            after_id = _identity(unit.conn)
            assert inside == before and after_id == source_id
            assert unit.candidates((before[0].shift_id,))
        fresh_id = {}
        fresh_tx = []
        original = source_sql._cohort

        def observed(conn, user_id, window_start, window_end):
            fresh_tx.append(conn.get_transaction())
            fresh_id.update(_identity(conn))
            return original(conn, user_id, window_start, window_end)

        source_sql._cohort = observed
        try:
            fresh = ledger.fresh_scoped_cohort(principal.user_id, start, end,
                                               (before[0].shift_id,))
        finally:
            source_sql._cohort = original
        assert fresh.cohort[0].assignment_version == 2
        assert fresh_tx[0] is not source_tx
        assert fresh_id["snapshot"] != source_id["snapshot"]
        assert writers[0]["backend_pid"] != source_id["backend_pid"]
        assert isolation == row["isolation"] and readonly == row["readOnly"]
        return {"source": source_id, "fresh": fresh_id, "writer": writers[0],
                "isolation": isolation, "read_only": readonly,
                "before_version": 1, "inside_version": inside[0].assignment_version,
                "fresh_version": fresh.cohort[0].assignment_version}
    finally:
        go.set()
        done.wait(15)
        thread.join(timeout=2)
