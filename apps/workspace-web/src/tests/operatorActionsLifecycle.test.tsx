import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CustomerRequestActions } from '../features/operator-actions/CustomerRequestActions';
import { IncidentActions } from '../features/operator-actions/IncidentActions';
import { HandoverActions } from '../features/operator-actions/HandoverActions';
import { setToken } from '../features/authentication/session';
import type { CustomerRequest, Incident, Shift } from '../types/operations';

const jsonResponse = (status: number, body: unknown): Response =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

describe('operator lifecycle action components', () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    sessionStorage.clear();
    setToken('test-token');
    fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => vi.unstubAllGlobals());

  it('CustomerRequestActions creates request bound to selected shift, and WAITING cannot skip straight to CLOSED (WO C3C-BUILD-REV-F4)', async () => {
    const onRefresh = vi.fn();
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { request_id: 'cr-1', customer_id: 'cust-100', summary: 'Need help' }));

    const existing: CustomerRequest = {
      request_id: 'cr-1', customer_id: 'cust-100', shift_id: 's-1', summary: 'Need help', details: null,
      status: 'WAITING', source_message_id: null, received_at: '2026-08-01T00:00:00Z', promised_at: null, owner_id: null, version: 1
    };

    render(<CustomerRequestActions shiftId="s-1" customerRequests={[existing]} onRefresh={onRefresh} />);

    await userEvent.type(screen.getByLabelText('Customer ID'), 'cust-200');
    await userEvent.type(screen.getByLabelText('Summary'), 'Urgent request');
    await userEvent.click(screen.getByRole('button', { name: 'Create request' }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/customer-requests'),
      expect.objectContaining({ body: JSON.stringify({ shift_id: 's-1', customer_id: 'cust-200', summary: 'Urgent request' }) })
    ));

    const options = Array.from(screen.getByLabelText('Target status for Need help').querySelectorAll('option')).map((o) => o.value);
    expect(options).toStrictEqual(['IN_PROGRESS']);
    expect(options).not.toContain('CLOSED');
  });

  it('IncidentActions waits for supervisor ACKNOWLEDGED before offering any operator transition, then allows MITIGATING/RESOLVED and RESOLVED->CLOSED', async () => {
    const reported: Incident = {
      incident_id: 'inc-1', shift_id: 's-1', risk_class: 'R2', summary: 'Water leak', description: null,
      status: 'REPORTED', owner_id: null, evidence: [], version: 1, created_at: '2026-08-01T00:00:00Z'
    };
    const { rerender } = render(<IncidentActions shiftId="s-1" incidents={[reported]} onRefresh={vi.fn()} />);
    expect(screen.queryByLabelText('Target status for Water leak')).not.toBeInTheDocument();
    expect(screen.getByText(/Waiting for supervisor acknowledgement/)).toBeInTheDocument();

    const acknowledged: Incident = { ...reported, status: 'ACKNOWLEDGED', version: 2 };
    rerender(<IncidentActions shiftId="s-1" incidents={[acknowledged]} onRefresh={vi.fn()} />);
    const ackOptions = Array.from(screen.getByLabelText('Target status for Water leak').querySelectorAll('option')).map((o) => o.value);
    expect(ackOptions).toStrictEqual(['MITIGATING', 'RESOLVED']);

    const resolved: Incident = { ...reported, status: 'RESOLVED', version: 3 };
    rerender(<IncidentActions shiftId="s-1" incidents={[resolved]} onRefresh={vi.fn()} />);
    const resolvedOptions = Array.from(screen.getByLabelText('Target status for Water leak').querySelectorAll('option')).map((o) => o.value);
    expect(resolvedOptions).toStrictEqual(['CLOSED']);
  });

  it('HandoverActions creates handover to a destination and excludes non-OPEN shifts and the source shift', async () => {
    const onRefresh = vi.fn();
    const shifts: Shift[] = [
      { shift_id: 's-1', name: 'Shift 1', starts_at: '', ends_at: '', status: 'OPEN', version: 1, created_at: '' },
      { shift_id: 's-2', name: 'Shift 2', starts_at: '', ends_at: '', status: 'OPEN', version: 1, created_at: '' },
      { shift_id: 's-3', name: 'Closed shift', starts_at: '', ends_at: '', status: 'CLOSED', version: 1, created_at: '' }
    ];

    fetchMock.mockResolvedValueOnce(jsonResponse(200, { handover_id: 'h-1' }));

    render(<HandoverActions fromShiftId="s-1" shifts={shifts} onRefresh={onRefresh} />);

    const options = Array.from(screen.getByLabelText('Destination shift').querySelectorAll('option')).map((o) => o.value);
    expect(options).toStrictEqual(['s-2']);

    await userEvent.click(screen.getByRole('button', { name: 'Create handover' }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/handovers'),
      expect.objectContaining({ body: JSON.stringify({ from_shift_id: 's-1', to_shift_id: 's-2' }) })
    ));
  });

  it('HandoverActions resets a stale destination when fromShiftId changes so a self-target can never be submitted', async () => {
    const shifts: Shift[] = [
      { shift_id: 's-1', name: 'Shift 1', starts_at: '', ends_at: '', status: 'OPEN', version: 1, created_at: '' },
      { shift_id: 's-2', name: 'Shift 2', starts_at: '', ends_at: '', status: 'OPEN', version: 1, created_at: '' }
    ];
    const { rerender } = render(<HandoverActions fromShiftId="s-1" shifts={shifts} onRefresh={vi.fn()} />);
    expect(screen.getByLabelText('Destination shift')).toHaveValue('s-2');

    rerender(<HandoverActions fromShiftId="s-2" shifts={shifts} onRefresh={vi.fn()} />);
    await waitFor(() => expect(screen.getByLabelText('Destination shift')).toHaveValue('s-1'));
  });
});
