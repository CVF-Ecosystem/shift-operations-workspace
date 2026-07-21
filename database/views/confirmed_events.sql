CREATE OR REPLACE VIEW confirmed_events AS
SELECT * FROM operational_events WHERE state IN ('CONFIRMED','CORRECTED','FROZEN');
