CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TYPE data_state AS ENUM ('RAW','NORMALIZED','PROPOSED','CONFIRMED','REJECTED','CORRECTED','FROZEN');
CREATE TYPE risk_class AS ENUM ('R0','R1','R2','R3','R4');
CREATE TYPE shift_status AS ENUM ('OPEN','HANDOVER_PENDING','CLOSED','FROZEN');

CREATE TABLE IF NOT EXISTS shifts (
  shift_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  starts_at timestamptz NOT NULL,
  ends_at timestamptz NOT NULL,
  status shift_status NOT NULL DEFAULT 'OPEN',
  version integer NOT NULL DEFAULT 1,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (ends_at > starts_at)
);

CREATE TABLE IF NOT EXISTS messages (
  message_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  shift_id uuid NOT NULL REFERENCES shifts(shift_id),
  source text NOT NULL,
  sender_id text NOT NULL,
  text_content text,
  state data_state NOT NULL DEFAULT 'RAW',
  raw_payload jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS operational_events (
  event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  shift_id uuid NOT NULL REFERENCES shifts(shift_id),
  event_type text NOT NULL,
  title text NOT NULL,
  description text,
  risk risk_class NOT NULL DEFAULT 'R1',
  state data_state NOT NULL DEFAULT 'PROPOSED',
  starts_at timestamptz,
  ends_at timestamptz,
  owner_id text,
  version integer NOT NULL DEFAULT 1,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (ends_at IS NULL OR starts_at IS NULL OR ends_at >= starts_at)
);

CREATE TABLE IF NOT EXISTS evidence_links (
  evidence_link_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  record_type text NOT NULL,
  record_id uuid NOT NULL,
  source_type text NOT NULL,
  source_id text NOT NULL,
  sha256 text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS approvals (
  approval_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  record_type text NOT NULL,
  record_id uuid NOT NULL,
  decision text NOT NULL CHECK (decision IN ('APPROVE','REJECT','REQUEST_CHANGES')),
  actor_id text NOT NULL,
  reason text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS corrections (
  correction_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  record_type text NOT NULL,
  record_id uuid NOT NULL,
  previous_version integer NOT NULL,
  new_version integer NOT NULL,
  reason text NOT NULL,
  requested_by text NOT NULL,
  before_data jsonb NOT NULL,
  after_data jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (new_version > previous_version)
);

CREATE TABLE IF NOT EXISTS audit_records (
  audit_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_id text,
  action text NOT NULL,
  target_type text NOT NULL,
  target_id text NOT NULL,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  occurred_at timestamptz NOT NULL DEFAULT now()
);
