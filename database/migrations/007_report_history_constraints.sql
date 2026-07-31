-- P2R-OPERATIONAL-REPORT-FREEZE-PREREQUISITE (SPEC R23): adds a real
-- current-version selector and history-uniqueness guarantee to the
-- pre-existing `reports` table from 002_tasks_customers_reports.sql.
--
-- Idempotently re-applicable through scripts/apply_migrations.py, which
-- executes each statement in its own transaction and tolerates "already
-- exists"/"already the case" failures (see that script's docstring). Every
-- DDL statement below uses an IF [NOT] EXISTS guard so a second run is a
-- true no-op rather than relying on the runner's SQLSTATE tolerance alone.
--
-- Ambiguous duplicate (shift_id, report_type, version) history fails this
-- migration outright (via the unique constraint below) rather than silently
-- picking a survivor - there is no pre-existing production data, so no
-- backfill needs to reconcile real duplicates; an empty reports table is the
-- expected starting state this migration runs against.

ALTER TABLE reports ADD COLUMN IF NOT EXISTS is_current boolean;

-- Backfill deterministically: only the highest version per (shift_id,
-- report_type) is marked current. Written as a single deterministic UPDATE
-- (not a loop) so it is naturally idempotent - re-running it after
-- is_current is already NOT NULL just recomputes the same result.
UPDATE reports r
SET is_current = (
  r.version = (
    SELECT MAX(r2.version)
    FROM reports r2
    WHERE r2.shift_id = r.shift_id AND r2.report_type = r.report_type
  )
)
WHERE r.is_current IS NULL;

ALTER TABLE reports ALTER COLUMN is_current SET DEFAULT true;
ALTER TABLE reports ALTER COLUMN is_current SET NOT NULL;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'reports_version_check'
  ) THEN
    ALTER TABLE reports ADD CONSTRAINT reports_version_check CHECK (version >= 1);
  END IF;
END $$;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'reports_shift_type_version_unique'
  ) THEN
    ALTER TABLE reports
      ADD CONSTRAINT reports_shift_type_version_unique UNIQUE (shift_id, report_type, version);
  END IF;
END $$;

-- Partial unique index: at most one current row per (shift_id, report_type).
-- This is the real database-side guarantee that a duplicate/ambiguous
-- "current" Report can never be committed by a concurrent writer, backing
-- SPEC R20's "reject zero/multiple current candidates" freeze check.
CREATE UNIQUE INDEX IF NOT EXISTS reports_current_unique
  ON reports (shift_id, report_type)
  WHERE is_current;
