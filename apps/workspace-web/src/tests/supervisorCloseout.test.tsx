// P2C-MUTATION-FULL-UI-C3D (SPEC R5/R6): closeout controls - incident
// acknowledge, handover review/acknowledge (destination assignment enforced
// server-side only), Report approve/revoke-via-successor, and Shift freeze
// sending only expected_version.
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { IncidentHandoverActions } from '../features/supervisor-actions/IncidentHandoverActions';
import { ReportFreezeActions } from '../features/supervisor-actions/ReportFreezeActions';
import { setToken } from '../features/authentication/session';
import type { Handover, Incident, Shift } from '../types/operations';
import type { ReportEntry } from '../services/operatorApi';

const jsonResponse = (status: number, body: unknown): Response =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

describe('closeout controls', () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    sessionStorage.clear();
    setToken('test-token');
    fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => vi.unstubAllGlobals());

  it('acknowledges only REPORTED incidents, sending expected_version', async () => {
    const incidents: Incident[] = [
      { incident_id: 'i-1', shift_id: 's-1', risk_class: 'R2', summary: 'Line down', description: null, status: 'REPORTED', owner_id: null, evidence: [], version: 2, created_at: '2026-08-02T00:00:00Z' },
      { incident_id: 'i-2', shift_id: 's-1', risk_class: 'R1', summary: 'Already ack', description: null, status: 'ACKNOWLEDGED', owner_id: null, evidence: [], version: 1, created_at: '2026-08-02T00:00:00Z' }
    ];
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { incident_id: 'i-1', status: 'ACKNOWLEDGED' }));
    const onRefresh = vi.fn().mockResolvedValue(undefined);
    render(<IncidentHandoverActions incidents={incidents} handovers={[]} onRefresh={onRefresh} />);

    expect(screen.getByText('Line down')).toBeInTheDocument();
    expect(screen.queryByText('Already ack')).not.toBeInTheDocument();

    await userEvent.click(screen.getByRole('button', { name: 'Acknowledge' }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/incidents/i-1/acknowledge'),
      expect.objectContaining({ body: JSON.stringify({ expected_version: 2 }) })
    ));
  });

  it('reviews DRAFT handovers and acknowledges REVIEWED handovers as distinct steps', async () => {
    const draft: Handover = {
      handover_id: 'h-1', from_shift_id: 's-1', to_shift_id: 's-2', status: 'DRAFT', items: [],
      created_by: 'u-1', reviewed_by: null, reviewed_at: null, received_by: null, acknowledged_at: null,
      version: 1, created_at: '2026-08-02T00:00:00Z', acknowledged: false
    };
    const reviewed: Handover = { ...draft, handover_id: 'h-2', status: 'REVIEWED', version: 2 };
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { ...draft, status: 'REVIEWED' }));
    const onRefresh = vi.fn().mockResolvedValue(undefined);
    render(<IncidentHandoverActions incidents={[]} handovers={[draft, reviewed]} onRefresh={onRefresh} />);

    await userEvent.click(screen.getByRole('button', { name: 'Review' }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/handovers/h-1/review'),
      expect.objectContaining({ body: JSON.stringify({ expected_version: 1 }) })
    ));

    fetchMock.mockResolvedValueOnce(jsonResponse(200, { ...reviewed, status: 'ACKNOWLEDGED' }));
    await userEvent.click(screen.getByRole('button', { name: 'Acknowledge' }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/handovers/h-2/acknowledge'),
      expect.objectContaining({ body: JSON.stringify({ expected_version: 2 }) })
    ));
  });

  it('surfaces a controlled refusal, not a fake success, when acknowledge lacks destination assignment', async () => {
    const reviewed: Handover = {
      handover_id: 'h-3', from_shift_id: 's-1', to_shift_id: 's-2', status: 'REVIEWED', items: [],
      created_by: 'u-1', reviewed_by: 'u-1', reviewed_at: '2026-08-02T00:00:00Z', received_by: null, acknowledged_at: null,
      version: 1, created_at: '2026-08-02T00:00:00Z', acknowledged: false
    };
    fetchMock.mockResolvedValueOnce(jsonResponse(403, { detail: 'requires an active assignment for the destination shift' }));
    render(<IncidentHandoverActions incidents={[]} handovers={[reviewed]} onRefresh={vi.fn()} />);

    await userEvent.click(screen.getByRole('button', { name: 'Acknowledge' }));
    await screen.findByText('Action not permitted. Check your role or approval prerequisites.');
  });

  it('approves an IN_REVIEW report with exact preconditions', async () => {
    const shift: Shift = { shift_id: 's-1', name: 'Day', starts_at: '2026-08-02T00:00:00Z', ends_at: '2026-08-02T08:00:00Z', status: 'CLOSED', version: 3, created_at: '2026-08-02T00:00:00Z' };
    const report: ReportEntry = {
      report_id: 'r-1', shift_id: 's-1', report_type: 'END_SHIFT', version: 1, status: 'IN_REVIEW', is_current: true,
      sections: [], source_manifest: [], snapshot_digest: 'x', generated_from_cutoff: '2026-08-02T00:00:00Z', created_at: '2026-08-02T00:00:00Z'
    };
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { ...report, status: 'APPROVED' }));
    const onRefresh = vi.fn().mockResolvedValue(undefined);
    render(<ReportFreezeActions selectedShift={shift} reports={[report]} onRefresh={onRefresh} />);

    await userEvent.click(screen.getByRole('button', { name: 'Approve report' }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/reports/r-1/approve'),
      expect.objectContaining({ body: JSON.stringify({ expected_version: 1, expected_status: 'IN_REVIEW' }) })
    ));
  });

  it('revokes an APPROVED report via successor creation with a required reason, never a client status mutation', async () => {
    const shift: Shift = { shift_id: 's-1', name: 'Day', starts_at: '2026-08-02T00:00:00Z', ends_at: '2026-08-02T08:00:00Z', status: 'CLOSED', version: 3, created_at: '2026-08-02T00:00:00Z' };
    const report: ReportEntry = {
      report_id: 'r-1', shift_id: 's-1', report_type: 'END_SHIFT', version: 2, status: 'APPROVED', is_current: true,
      sections: [], source_manifest: [], snapshot_digest: 'x', generated_from_cutoff: '2026-08-02T00:00:00Z', created_at: '2026-08-02T00:00:00Z'
    };
    render(<ReportFreezeActions selectedShift={shift} reports={[report]} onRefresh={vi.fn().mockResolvedValue(undefined)} />);

    const submitButton = screen.getByRole('button', { name: /Revoke approval/ });
    expect(submitButton).toBeDisabled(); // empty reason

    fetchMock.mockResolvedValueOnce(jsonResponse(201, { ...report, report_id: 'r-2', version: 1, status: 'DRAFT' }));
    await userEvent.type(screen.getByLabelText('Revocation reason'), 'Incorrect figures found');
    await userEvent.click(screen.getByRole('button', { name: /Revoke approval/ }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/reports/r-1/versions'),
      expect.objectContaining({ body: JSON.stringify({ reason: 'Incorrect figures found', expected_version: 2, expected_status: 'APPROVED' }) })
    ));
  });

  it('freeze sends only expected_version and is disabled unless the shift is CLOSED', async () => {
    const openShift: Shift = { shift_id: 's-1', name: 'Day', starts_at: '2026-08-02T00:00:00Z', ends_at: '2026-08-02T08:00:00Z', status: 'OPEN', version: 1, created_at: '2026-08-02T00:00:00Z' };
    const { rerender } = render(<ReportFreezeActions selectedShift={openShift} reports={[]} onRefresh={vi.fn()} />);
    expect(screen.getByRole('button', { name: 'Freeze shift' })).toBeDisabled();

    const closedShift: Shift = { ...openShift, status: 'CLOSED', version: 2 };
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { ...closedShift, status: 'FROZEN' }));
    rerender(<ReportFreezeActions selectedShift={closedShift} reports={[]} onRefresh={vi.fn().mockResolvedValue(undefined)} />);

    await userEvent.click(screen.getByRole('button', { name: 'Freeze shift' }));
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/shifts/s-1/freeze'),
      expect.objectContaining({ body: JSON.stringify({ expected_version: 2 }) })
    ));
  });
});
