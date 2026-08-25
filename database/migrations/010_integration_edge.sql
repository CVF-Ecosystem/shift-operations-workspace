CREATE TABLE IF NOT EXISTS edge_raw_envelopes (
    envelope_id text PRIMARY KEY,
    channel text NOT NULL,
    endpoint text NOT NULL,
    external_id text NOT NULL,
    payload_digest text NOT NULL CHECK (length(payload_digest) = 64),
    key_id text NOT NULL,
    nonce bytea NOT NULL CHECK (octet_length(nonce) = 12),
    ciphertext bytea,
    tag bytea CHECK (tag IS NULL OR octet_length(tag) = 16),
    aad bytea NOT NULL,
    tombstoned_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_edge_raw_key_nonce UNIQUE (key_id, nonce),
    CONSTRAINT ck_edge_raw_tombstone CHECK (
      (tombstoned_at IS NULL AND ciphertext IS NOT NULL AND tag IS NOT NULL)
      OR (tombstoned_at IS NOT NULL AND ciphertext IS NULL AND tag IS NULL)
    )
);

CREATE TABLE IF NOT EXISTS edge_ingress_reservations (
    channel text NOT NULL,
    external_id text NOT NULL,
    payload_digest text NOT NULL CHECK (length(payload_digest) = 64),
    envelope_id text NOT NULL REFERENCES edge_raw_envelopes(envelope_id),
    PRIMARY KEY (channel, external_id)
);

CREATE TABLE IF NOT EXISTS edge_quarantines (
    quarantine_id text PRIMARY KEY,
    envelope_id text NOT NULL REFERENCES edge_raw_envelopes(envelope_id),
    original_envelope_id text REFERENCES edge_raw_envelopes(envelope_id),
    reason text NOT NULL CHECK (reason IN ('KEY_COLLISION','MALFORMED_SCHEMA','UNSUPPORTED_TYPE','AMBIGUOUS_CONTENT','UNSAFE_ATTACHMENT','SCAN_UNAVAILABLE','POLICY_DRIFT','ROUTE_POLICY_REFUSED')),
    released_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS edge_external_proposals (
    proposal_id text PRIMARY KEY,
    envelope_id text NOT NULL UNIQUE REFERENCES edge_raw_envelopes(envelope_id),
    channel text NOT NULL,
    external_id text NOT NULL,
    proposal_json jsonb NOT NULL,
    trust_class text NOT NULL CHECK (trust_class = 'UNTRUSTED_EXTERNAL'),
    content_class text NOT NULL CHECK (content_class = 'RAW'),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS edge_rate_counters (
    budget text NOT NULL CHECK (budget IN ('PREAUTH','POSTAUTH','OUTBOUND')),
    counter_key text NOT NULL,
    count integer NOT NULL CHECK (count >= 0),
    PRIMARY KEY (budget, counter_key)
);

CREATE TABLE IF NOT EXISTS edge_service_nonces (
    issuer text NOT NULL,
    nonce text NOT NULL,
    expires_at timestamptz NOT NULL,
    PRIMARY KEY (issuer, nonce)
);

CREATE TABLE IF NOT EXISTS edge_outbound_attempts (
    command_id text PRIMARY KEY,
    prerequisite_digest text NOT NULL CHECK (length(prerequisite_digest) = 64),
    outcome text NOT NULL CHECK (outcome IN ('NOT_ATTEMPTED','SENT_ACCEPTED','DELIVERED','PROVIDER_REFUSED','RATE_LIMITED','OUTCOME_UNKNOWN','TERMINAL_FAILED')),
    reason text,
    delivery_id text,
    delivery_attempts integer NOT NULL CHECK (delivery_attempts IN (0,1)),
    receipt_json jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);
