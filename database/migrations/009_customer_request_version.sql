-- P2C-MUTATION-FULL-UI-C3B2 (SPEC R12, ADR_2026-07-31_P2C_CUSTOMER_REQUEST_
-- CONCURRENCY_ADDENDUM): adds a concurrency version to the pre-existing
-- `customer_requests` table from 002_tasks_customers_reports.sql, mirroring
-- how 007_report_history_constraints.sql ALTERed `reports`.
--
-- Idempotently re-applicable through scripts/apply_migrations.py (each
-- statement runs in its own transaction and "already exists"/"already the
-- case" failures are tolerated). Every DDL statement below also uses an
-- IF [NOT] EXISTS guard so a second run is a true no-op.
--
-- Deterministic backfill: every existing row (including any inserted between
-- the ADD COLUMN and the UPDATE, since the WHERE clause only touches rows
-- still NULL) is set to version 1 - the same "no truthful source for a
-- different value" reasoning migration 008 used for shift assignments.

ALTER TABLE customer_requests ADD COLUMN IF NOT EXISTS version integer;

UPDATE customer_requests SET version = 1 WHERE version IS NULL;

ALTER TABLE customer_requests ALTER COLUMN version SET DEFAULT 1;
ALTER TABLE customer_requests ALTER COLUMN version SET NOT NULL;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'customer_requests_version_check'
  ) THEN
    ALTER TABLE customer_requests ADD CONSTRAINT customer_requests_version_check CHECK (version >= 1);
  END IF;
END $$;
