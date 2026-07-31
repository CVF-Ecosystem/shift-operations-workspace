CREATE TABLE IF NOT EXISTS shift_assignments (
  assignment_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  shift_id uuid NOT NULL REFERENCES shifts(shift_id),
  user_id text NOT NULL REFERENCES users(user_id),
  status text NOT NULL CHECK (status IN ('ACTIVE','REVOKED')) DEFAULT 'ACTIVE',
  assigned_by text NOT NULL REFERENCES users(user_id),
  assigned_at timestamptz NOT NULL DEFAULT now(),
  revoked_by text REFERENCES users(user_id),
  revoked_at timestamptz,
  version integer NOT NULL DEFAULT 1 CHECK (version >= 1)
);

-- At most one ACTIVE assignment per (shift_id, user_id). Revoked rows are
-- retained as separate history rows, never overwritten in place.
CREATE UNIQUE INDEX IF NOT EXISTS shift_assignments_active_unique
  ON shift_assignments (shift_id, user_id)
  WHERE status = 'ACTIVE';
