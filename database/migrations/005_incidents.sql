CREATE TABLE IF NOT EXISTS incidents (
  incident_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  shift_id uuid NOT NULL REFERENCES shifts(shift_id),
  risk risk_class NOT NULL DEFAULT 'R1',
  summary text NOT NULL,
  description text,
  status text NOT NULL CHECK (status IN ('REPORTED','ACKNOWLEDGED','MITIGATING','RESOLVED','CLOSED')) DEFAULT 'REPORTED',
  owner_id text,
  version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
  created_at timestamptz NOT NULL DEFAULT now()
);
