// P2C-MUTATION-FULL-UI-C3D (SPEC R2, ADR D1, C3D-WO-REV-F4): staffing plane
// tests. A 403 on either staffing read hides the panel without client-side
// role ranking and without touching operational state. Assign/revoke success
// refreshes staffing plus the ordinary shift list; self-revoke that removes
// the selected shift from the refreshed list clears selection and retained
// operational state instead of leaving a stale disclosure.
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App } from '../app/App';
import { setToken } from '../features/authentication/session';
import { StaffingActions } from '../features/supervisor-actions/StaffingActions';
import { supervisorApi } from '../services/supervisorApi';
import type { ShiftAssignment } from '../types/supervisorContracts';

const jsonResponse = (status: number, body: unknown): Response =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

const shift = (id: string, name: string) => ({ shift_id: id, name, starts_at: '2026-08-02T00:00:00Z', ends_at: '2026-08-02T08:00:00Z', status: 'OPEN', version: 1, created_at: '2026-08-02T00:00:00Z' });
const emptyOpenWork = (id: string) => ({ shift_id: id, tasks: [], customer_requests: [], incidents: [] });

function baseReads(fetchMock: ReturnType<typeof vi.fn>, opts: { staffingForbidden?: boolean; assignedShifts?: unknown[] } = {}) {
  const assignedShifts = opts.assignedShifts ?? [shift('s1', 'Day shift')];
  fetchMock.mockImplementation((url: string) => {
    if (url.includes('/staffing/shifts')) {
      return opts.staffingForbidden
        ? Promise.resolve(jsonResponse(403, { detail: 'requires shift_supervisor or higher' }))
        : Promise.resolve(jsonResponse(200, [shift('s1', 'Day shift')]));
    }
    if (url.includes('/staffing/users')) {
      return opts.staffingForbidden
        ? Promise.resolve(jsonResponse(403, { detail: 'requires shift_supervisor or higher' }))
        : Promise.resolve(jsonResponse(200, [{ user_id: 'u-1', username: 'alice', role: 'operator' }]));
    }
    if (url.includes('/shifts/s1/assignments')) return Promise.resolve(jsonResponse(200, []));
    if (url.includes('/shifts') && !url.includes('open-work')) return Promise.resolve(jsonResponse(200, assignedShifts));
    if (url.includes('/events')) return Promise.resolve(jsonResponse(200, []));
    if (url.includes('open-work')) return Promise.resolve(jsonResponse(200, emptyOpenWork('s1')));
    if (url.includes('/messages')) return Promise.resolve(jsonResponse(200, []));
    if (url.includes('/tasks')) return Promise.resolve(jsonResponse(200, []));
    if (url.includes('/customer-requests')) return Promise.resolve(jsonResponse(200, []));
    if (url.includes('/capabilities')) return Promise.resolve(jsonResponse(200, { shift_id: 's1', actions: [], reasons: [] }));
    if (url.includes('/reports')) return Promise.resolve(jsonResponse(200, []));
    if (url.includes('/incidents')) return Promise.resolve(jsonResponse(200, []));
    if (url.includes('/handovers')) return Promise.resolve(jsonResponse(200, []));
    return Promise.resolve(jsonResponse(404, { detail: 'not found' }));
  });
}

describe('supervisor staffing plane', () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    sessionStorage.clear();
    setToken('test-token');
    fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it('hides the staffing panel on a 403 without client-side role ranking, while operational reads stay unaffected', async () => {
    baseReads(fetchMock, { staffingForbidden: true });
    render(<App />);
    await waitFor(() => expect(screen.getByLabelText('Shift')).toBeInTheDocument());

    await waitFor(() => expect(screen.getByText('Staffing control is unavailable for your current role.')).toBeInTheDocument());
    await userEvent.selectOptions(screen.getByLabelText('Shift'), 's1');
    await screen.findByRole('form', { name: 'Create event' });
  });

  it('shows the staffing panel and lists shifts/users when staffing reads succeed', async () => {
    baseReads(fetchMock);
    render(<App />);
    await waitFor(() => expect(document.getElementById('shift-select')).toBeInTheDocument());

    await waitFor(() => expect(document.getElementById('staffing-shift')).toBeInTheDocument());
    const staffingShiftSelect = document.getElementById('staffing-shift') as HTMLSelectElement;
    expect(within(staffingShiftSelect).getByText('Day shift (OPEN)')).toBeInTheDocument();
  });

  it('never commits an out-of-order assignment response for a previously selected staffing shift', async () => {
    let resolveS1!: (value: ShiftAssignment[]) => void;
    const s1Pending = new Promise<ShiftAssignment[]>((resolve) => { resolveS1 = resolve; });
    const assignment = (id: string, shiftId: string, userId: string): ShiftAssignment => ({
      assignment_id: id, shift_id: shiftId, user_id: userId, assigned_by: 'sup1',
      status: 'ACTIVE', version: 1, assigned_at: '2026-08-02T00:00:00Z', revoked_by: null, revoked_at: null
    });
    vi.spyOn(supervisorApi, 'listAssignments').mockImplementation((id) =>
      id === 's1' ? s1Pending : Promise.resolve([assignment('a-2', 's2', 'user-b')])
    );
    render(<StaffingActions
      staffingShifts={[shift('s1', 'First'), shift('s2', 'Second')]}
      staffingUsers={[]}
      staffingAvailable
      onStaffingRefresh={async () => {}}
    />);

    await userEvent.selectOptions(screen.getByLabelText('Shift'), 's1');
    await userEvent.selectOptions(screen.getByLabelText('Shift'), 's2');
    await screen.findByText('user-b');
    resolveS1([assignment('a-1', 's1', 'user-a')]);

    await waitFor(() => expect(screen.queryByText('user-a')).not.toBeInTheDocument());
    expect(screen.getByText('user-b')).toBeInTheDocument();
  });

  it('self-revoke that drops the selected shift from the refreshed list clears selection and stale operational records', async () => {
    // Assignment starts ACTIVE so a Revoke control is present from the
    // first assignments read - no mid-test mock swap needed, avoiding a
    // fragile dependency on when React re-runs the assignments effect.
    let assignmentRevoked = false;
    fetchMock.mockImplementation((url: string) => {
      if (url.includes('/staffing/shifts')) return Promise.resolve(jsonResponse(200, [shift('s1', 'Day shift')]));
      if (url.includes('/staffing/users')) return Promise.resolve(jsonResponse(200, [{ user_id: 'u-1', username: 'alice', role: 'operator' }]));
      if (url.includes('assignments/a-1/revoke')) {
        assignmentRevoked = true;
        return Promise.resolve(jsonResponse(200, {
          assignment_id: 'a-1', shift_id: 's1', user_id: 'u-1', assigned_by: 'u-2', status: 'REVOKED', version: 2,
          assigned_at: '2026-08-02T00:00:00Z', revoked_by: 'u-1', revoked_at: '2026-08-02T01:00:00Z'
        }));
      }
      if (url.includes('/shifts/s1/assignments')) return Promise.resolve(jsonResponse(200, [{
        assignment_id: 'a-1', shift_id: 's1', user_id: 'u-1', assigned_by: 'u-2', status: 'ACTIVE', version: 1,
        assigned_at: '2026-08-02T00:00:00Z', revoked_by: null, revoked_at: null
      }]));
      // The self-revoked supervisor's own assignment was the one revoked, so
      // once it lands, the ordinary assignment-scoped shift list no longer
      // returns s1.
      if (url.includes('/shifts') && !url.includes('open-work') && !url.includes('assignments')) {
        return Promise.resolve(jsonResponse(200, assignmentRevoked ? [] : [shift('s1', 'Day shift')]));
      }
      if (url.includes('/events')) return Promise.resolve(jsonResponse(200, []));
      if (url.includes('open-work')) return Promise.resolve(jsonResponse(200, emptyOpenWork('s1')));
      if (url.includes('/messages')) return Promise.resolve(jsonResponse(200, []));
      if (url.includes('/tasks')) return Promise.resolve(jsonResponse(200, []));
      if (url.includes('/customer-requests')) return Promise.resolve(jsonResponse(200, []));
      if (url.includes('/capabilities')) return Promise.resolve(jsonResponse(200, { shift_id: 's1', actions: [], reasons: [] }));
      if (url.includes('/reports')) return Promise.resolve(jsonResponse(200, []));
      if (url.includes('/incidents')) return Promise.resolve(jsonResponse(200, []));
      if (url.includes('/handovers')) return Promise.resolve(jsonResponse(200, []));
      return Promise.resolve(jsonResponse(404, { detail: 'not found' }));
    });

    render(<App />);
    await waitFor(() => expect(document.getElementById('shift-select')).toBeInTheDocument());
    const operationalShiftSelect = document.getElementById('shift-select') as HTMLSelectElement;
    await userEvent.selectOptions(operationalShiftSelect, 's1');
    await screen.findByRole('form', { name: 'Create event' });

    const staffingShiftSelect = document.getElementById('staffing-shift') as HTMLSelectElement;
    await userEvent.selectOptions(staffingShiftSelect, 's1');
    await waitFor(() => expect(screen.getByText('Revoke')).toBeInTheDocument());

    await userEvent.click(screen.getByText('Revoke'));

    // C3D-WO-REV-F4: once the refreshed ordinary list no longer contains
    // s1, selection clears and the stale operator subtree for s1 is gone
    // rather than left showing disclosure for an unassigned shift. The now-
    // empty ordinary list correctly renders the "no shifts" empty state
    // instead of a stale s1 selection.
    await waitFor(() => expect(screen.queryByRole('form', { name: 'Create event' })).not.toBeInTheDocument());
    expect(screen.getByText('No shifts available.')).toBeInTheDocument();
  });
});
