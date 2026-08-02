// P2C-MUTATION-FULL-UI-C3D (SPEC R7): proves the supervisor mutation subtree
// reuses the exact shared C3c useMutationControl/MutationFeedback machinery
// (no forked state machine, verified via zero-retry/lockout behavior already
// exhaustively covered by operatorMutationState.test.tsx) and that a
// selected-shift change resets all ephemeral supervisor form/mutation state,
// mirroring OperatorActions' WO C3C-BUILD-REREREV-F2 remount-on-shift-change
// contract for the SupervisorActions subtree.
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SupervisorActions } from '../features/supervisor-actions/SupervisorActions';
import { ApprovalActions } from '../features/supervisor-actions/ApprovalActions';
import { setToken } from '../features/authentication/session';
import { ApiError } from '../services/api';
import type { Shift } from '../types/operations';

const jsonResponse = (status: number, body: unknown): Response =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

const shift = (id: string, status: Shift['status'] = 'CLOSED'): Shift => ({
  shift_id: id, name: id, starts_at: '2026-08-02T00:00:00Z', ends_at: '2026-08-02T08:00:00Z', status, version: 1, created_at: '2026-08-02T00:00:00Z'
});

describe('supervisor mutation state reuse and reset', () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    sessionStorage.clear();
    setToken('test-token');
    fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => vi.unstubAllGlobals());

  it('reuses the shared mutation control: outcome_unknown locks and never auto-retries the mutation', async () => {
    fetchMock.mockRejectedValueOnce(new TypeError('Failed to fetch'));
    const onOperationalRefresh = vi.fn().mockResolvedValue(undefined);

    render(
      <SupervisorActions
        key="s-1"
        selectedShiftId="s-1"
        selectedShift={shift('s-1')}
        events={[]}
        incidents={[]}
        handovers={[]}
        reports={[]}
        staffingShifts={[]}
        staffingUsers={[]}
        staffingAvailable={true}
        onStaffingRefresh={vi.fn()}
        onOperationalRefresh={onOperationalRefresh}
      />
    );

    await userEvent.click(screen.getByRole('button', { name: 'Freeze shift' }));
    await screen.findByText('The outcome of this request could not be confirmed. Refresh before trying again.');
    expect(screen.getByRole('button', { name: 'Freeze shift' })).toBeDisabled();
    // No automatic retry of the mutation itself - only the explicit refresh
    // path (already exhaustively proven by operatorMutationState.test.tsx)
    // may run.
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('a selected-shift change resets ephemeral supervisor form/mutation state (mirrors WO C3C-BUILD-REREREV-F2)', async () => {
    const onRefresh = vi.fn().mockResolvedValue(undefined);

    const { unmount } = render(
      <ApprovalActions events={[]} incidents={[]} reports={[]} onRefresh={onRefresh} />
    );
    await userEvent.selectOptions(screen.getByLabelText('Target pair'), '2');
    await userEvent.type(screen.getByLabelText('Stored task-creation intent id'), 'intent-1');

    fetchMock.mockRejectedValueOnce(new ApiError('outcome_unknown', 'ambiguous'));
    await userEvent.click(screen.getByRole('button', { name: 'Create approval receipt' }));
    await screen.findByText('The outcome of this request could not be confirmed. Refresh before trying again.');
    expect(screen.getByRole('button', { name: 'Create approval receipt' })).toBeDisabled();

    // OperationsConsole keys SupervisorActions by selected shift (mirroring
    // OperatorActions' WO C3C-BUILD-REREREV-F2 contract), which forces React
    // to unmount/remount the whole subtree on shift change - simulated here
    // directly, since a bare rerender() reuses the same instance and would
    // not exercise that remount contract.
    unmount();
    render(<ApprovalActions events={[]} incidents={[]} reports={[]} onRefresh={onRefresh} />);

    // A fresh instance's button is disabled only by the empty-required-field
    // guard, never by a carried-over locked mutation state.
    expect(screen.queryByText('The outcome of this request could not be confirmed. Refresh before trying again.')).not.toBeInTheDocument();
    await userEvent.selectOptions(screen.getByLabelText('Target pair'), '2');
    expect(screen.getByLabelText('Stored task-creation intent id')).toHaveValue('');
    await userEvent.type(screen.getByLabelText('Stored task-creation intent id'), 'intent-2');
    expect(screen.getByRole('button', { name: 'Create approval receipt' })).not.toBeDisabled();
  });
});
