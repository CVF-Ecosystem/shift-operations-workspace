INSERT INTO audit_records(action,target_type,target_id,metadata)
VALUES ('SEED_REFERENCE_DATA','system','reference-data','{"note":"Replace with organization-specific vessel, yard, equipment and terminology masters"}')
ON CONFLICT DO NOTHING;
