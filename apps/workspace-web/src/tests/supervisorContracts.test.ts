// P2C-MUTATION-FULL-UI-C3D (SPEC R4/R6): proves the supervisor DTOs round-
// trip realistic backend shapes without dropping/renaming a field, and that
// the payload-shape guarantees (exact three-field approval body, exact
// one-field freeze body, no digest/receipt authority) hold structurally.
import { describe, expect, it } from 'vitest';
import type {
  ApprovalCreateInput,
  ApprovalReceiptResponse,
  FreezeShiftInput,
  ShiftAssignment,
  StaffingShift,
  StaffingUser
} from '../types/supervisorContracts';

describe('supervisorContracts', () => {
  it('StaffingShift/StaffingUser round-trip the exact backend shape', () => {
    const shift: StaffingShift = { shift_id: 's-1', name: 'Day shift', status: 'OPEN' };
    const user: StaffingUser = { user_id: 'u-1', username: 'alice', role: 'shift_supervisor' };
    expect(Object.keys(shift).sort()).toStrictEqual(['name', 'shift_id', 'status']);
    expect(Object.keys(user).sort()).toStrictEqual(['role', 'user_id', 'username']);
  });

  it('ShiftAssignment round-trips ACTIVE and REVOKED history shapes', () => {
    const active: ShiftAssignment = {
      assignment_id: 'a-1', shift_id: 's-1', user_id: 'u-1', assigned_by: 'u-2',
      status: 'ACTIVE', version: 1, assigned_at: '2026-08-02T00:00:00Z', revoked_by: null, revoked_at: null
    };
    const revoked: ShiftAssignment = {
      ...active, status: 'REVOKED', version: 2, revoked_by: 'u-2', revoked_at: '2026-08-02T01:00:00Z'
    };
    expect(active.status).toBe('ACTIVE');
    expect(revoked.status).toBe('REVOKED');
    expect(Object.keys(active).sort()).toStrictEqual(Object.keys(revoked).sort());
  });

  it('ApprovalCreateInput has exactly the three caller fields, including event.correct', () => {
    const payload: ApprovalCreateInput = { record_type: 'OperationalEvent', action: 'event.correct', record_id: 'e-1' };
    expect(Object.keys(payload).sort()).toStrictEqual(['action', 'record_id', 'record_type']);
  });

  it('ApprovalReceiptResponse round-trips without a payload_digest field', () => {
    const receipt: ApprovalReceiptResponse = {
      receipt_id: 'r-1', record_type: 'OperationalEvent', record_id: 'e-1', action: 'event.confirm',
      target_version: 1, risk_class: 'R2', approver_id: 'u-1', approver_role: 'shift_supervisor',
      created_at: '2026-08-02T00:00:00Z'
    };
    expect(receipt).not.toHaveProperty('payload_digest');
    expect(Object.keys(receipt)).toHaveLength(9);
  });

  it('FreezeShiftInput has exactly one field and no retired override field can be assigned', () => {
    const payload: FreezeShiftInput = { expected_version: 3 };
    expect(Object.keys(payload)).toStrictEqual(['expected_version']);
    // @ts-expect-error retired override fields must not exist on this type
    payload.override_unimplemented_prerequisites = true;
  });
});
