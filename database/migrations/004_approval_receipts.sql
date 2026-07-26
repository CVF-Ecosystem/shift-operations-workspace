CREATE TABLE IF NOT EXISTS task_creation_intents (
  intent_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  shift_id uuid NOT NULL REFERENCES shifts(shift_id),
  risk_class risk_class NOT NULL,
  payload_snapshot jsonb NOT NULL,
  payload_digest text NOT NULL,
  created_by text NOT NULL REFERENCES users(user_id),
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS approval_receipts (
  receipt_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  record_type text NOT NULL,
  record_id uuid NOT NULL,
  action text NOT NULL,
  target_version integer NOT NULL,
  risk_class risk_class NOT NULL,
  payload_digest text,
  approver_id text NOT NULL REFERENCES users(user_id),
  approver_role text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (record_type, record_id, action, target_version, approver_id)
);
