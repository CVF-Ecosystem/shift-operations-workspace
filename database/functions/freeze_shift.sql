CREATE OR REPLACE FUNCTION freeze_shift(p_shift_id uuid) RETURNS void AS $$
BEGIN
  UPDATE shifts SET status='FROZEN', version=version+1 WHERE shift_id=p_shift_id AND status <> 'FROZEN';
END;
$$ LANGUAGE plpgsql;
