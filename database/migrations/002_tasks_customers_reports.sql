CREATE TABLE IF NOT EXISTS tasks (
  task_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  shift_id uuid NOT NULL REFERENCES shifts(shift_id),
  title text NOT NULL,
  description text,
  status text NOT NULL CHECK (status IN ('OPEN','IN_PROGRESS','BLOCKED','DONE','CARRY_OVER','CANCELLED')),
  owner_id text,
  due_at timestamptz,
  risk risk_class NOT NULL DEFAULT 'R1',
  state data_state NOT NULL DEFAULT 'CONFIRMED',
  version integer NOT NULL DEFAULT 1,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS customer_requests (
  request_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id text NOT NULL,
  shift_id uuid REFERENCES shifts(shift_id),
  summary text NOT NULL,
  details text,
  status text NOT NULL CHECK (status IN ('NEW','ACKNOWLEDGED','IN_PROGRESS','WAITING','RESOLVED','CLOSED')),
  source_message_id uuid REFERENCES messages(message_id),
  received_at timestamptz NOT NULL DEFAULT now(),
  promised_at timestamptz,
  owner_id text
);

CREATE TABLE IF NOT EXISTS reports (
  report_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  shift_id uuid NOT NULL REFERENCES shifts(shift_id),
  report_type text NOT NULL,
  version integer NOT NULL DEFAULT 1,
  status text NOT NULL CHECK (status IN ('DRAFT','IN_REVIEW','APPROVED','FROZEN')),
  content jsonb NOT NULL,
  generated_from_cutoff timestamptz NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
