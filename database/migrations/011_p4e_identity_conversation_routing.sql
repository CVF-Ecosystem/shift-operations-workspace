CREATE TABLE IF NOT EXISTS external_identity_observations (
  observation_id text PRIMARY KEY,
  external_key_digest text NOT NULL,
  workspace_digest text NOT NULL,
  endpoint_id text NOT NULL,
  channel_id text NOT NULL,
  provider_account_digest text NOT NULL,
  subject_kind text NOT NULL,
  extraction_policy_id text NOT NULL,
  extraction_policy_version text NOT NULL,
  raw_envelope_id text NOT NULL,
  external_message_id text NOT NULL,
  received_at timestamptz NOT NULL DEFAULT now()
);

-- At most one immutable observation per complete external identity key plus
-- envelope lineage (SPEC R5).
CREATE UNIQUE INDEX IF NOT EXISTS external_identity_observations_key_envelope_unique
  ON external_identity_observations (external_key_digest, raw_envelope_id);

CREATE TABLE IF NOT EXISTS identity_mappings (
  mapping_id text PRIMARY KEY,
  external_key_digest text NOT NULL,
  target_kind text NOT NULL DEFAULT 'INTERNAL_USER',
  target_user_id text REFERENCES users(user_id),
  proposal_evidence_digest text NOT NULL,
  proposer_id text NOT NULL REFERENCES users(user_id),
  status text NOT NULL CHECK (status IN ('PROPOSED','CONFIRMED','REJECTED','REVOKED')),
  version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  confirmer_id text REFERENCES users(user_id),
  rejector_id text REFERENCES users(user_id),
  revoker_id text REFERENCES users(user_id),
  successor_mapping_id text,
  predecessor_mapping_id text,
  is_current boolean NOT NULL DEFAULT false
);

-- At most one current confirmed mapping per complete external key (SPEC R6).
CREATE UNIQUE INDEX IF NOT EXISTS identity_mappings_current_unique
  ON identity_mappings (external_key_digest)
  WHERE is_current = true;

CREATE TABLE IF NOT EXISTS route_bindings (
  binding_id text PRIMARY KEY,
  mapping_id text NOT NULL REFERENCES identity_mappings(mapping_id),
  mapping_version integer NOT NULL,
  target_kind text NOT NULL CHECK (target_kind IN ('WORKSPACE','SHIFT','INCIDENT')),
  target_id text NOT NULL,
  target_version integer NOT NULL,
  creator_id text NOT NULL REFERENCES users(user_id),
  status text NOT NULL CHECK (status IN ('ACTIVE','REVOKED')) DEFAULT 'ACTIVE',
  version integer NOT NULL DEFAULT 1 CHECK (version >= 1),
  created_at timestamptz NOT NULL DEFAULT now(),
  successor_binding_id text,
  is_current boolean NOT NULL DEFAULT true
);

-- At most one current active binding per confirmed mapping (SPEC R13).
CREATE UNIQUE INDEX IF NOT EXISTS route_bindings_current_unique
  ON route_bindings (mapping_id)
  WHERE is_current = true;

CREATE TABLE IF NOT EXISTS p4e_proposals (
  proposal_id text PRIMARY KEY,
  envelope_id text NOT NULL UNIQUE,
  channel text NOT NULL,
  external_id text NOT NULL,
  candidate jsonb NOT NULL,
  provenance_digest text NOT NULL,
  sender_evidence jsonb,
  idempotency_key text NOT NULL UNIQUE,
  lineage_digest text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS p4e_placement_work (
  work_item_id text PRIMARY KEY,
  proposal_id text NOT NULL UNIQUE REFERENCES p4e_proposals(proposal_id),
  state text NOT NULL CHECK (state IN ('PENDING','CLAIMED','COMPLETE')) DEFAULT 'PENDING',
  attempt_count integer NOT NULL DEFAULT 0,
  claim_token text,
  claimed_at timestamptz,
  version integer NOT NULL DEFAULT 1,
  lineage_digest text NOT NULL
);

CREATE TABLE IF NOT EXISTS p4e_placement_decisions (
  decision_id text PRIMARY KEY,
  proposal_id text NOT NULL UNIQUE REFERENCES p4e_proposals(proposal_id),
  outcome text NOT NULL CHECK (outcome IN ('PLACED','FALLBACK','REFUSED')),
  reason text,
  mapping_id text,
  binding_id text,
  target_kind text,
  target_id text,
  conversation_key text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS p4e_action_receipts (
  idempotency_key text PRIMARY KEY,
  action text NOT NULL,
  payload_digest text NOT NULL,
  receipt jsonb NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
