CREATE TYPE handover_status AS ENUM ('DRAFT','REVIEWED','ACKNOWLEDGED');

CREATE TABLE IF NOT EXISTS handovers (
  handover_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  from_shift_id uuid NOT NULL REFERENCES shifts(shift_id),
  to_shift_id uuid NOT NULL REFERENCES shifts(shift_id),
  status handover_status NOT NULL DEFAULT 'DRAFT',
  created_by text NOT NULL,
  reviewed_by text,
  reviewed_at timestamptz,
  received_by text,
  acknowledged_at timestamptz,
  version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
  created_at timestamptz NOT NULL DEFAULT now(),
  CHECK (from_shift_id <> to_shift_id)
);

CREATE TABLE IF NOT EXISTS handover_items (
  item_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  handover_id uuid NOT NULL REFERENCES handovers(handover_id),
  source_record_type text NOT NULL CHECK (source_record_type IN ('Task','CustomerRequest','Incident')),
  source_record_id uuid NOT NULL,
  source_digest text NOT NULL,
  summary text NOT NULL,
  owner_id text,
  due_at timestamptz,
  risk risk_class NOT NULL DEFAULT 'R1',
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (handover_id, source_record_type, source_record_id)
);
