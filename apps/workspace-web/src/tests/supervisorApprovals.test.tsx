// P2C-MUTATION-FULL-UI-C3D (SPEC R4, C3D-WO-REV-F1/F2): approval receipt UI
// tests. Capability absence of approval.create must not suppress controls;
// all five pairs including event.correct must post the exact three-field
// payload; event.correct must never call the readiness GET.
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ApprovalActions } from '../features/supervisor-actions/ApprovalActions';
import { setToken } from '../features/authentication/session';
import type { Incident, OperationalEvent } from '../types/operations';
import type { ReportEntry } from '../services/operatorApi';

const jsonResponse = (status: number, body: unknown): Response =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

const event = (id: string, title: string): OperationalEvent => ({
  event_id: id, shift_id: 's-1', event_type: 'x', title, description: null, risk_class: 'R1',
  state: 'PROPOSED', starts_at: null, ends_at: null, owner_id: null, evidence: [], version: 1
});
const incident = (id: string, summary: string): Incident => ({
  incident_id: id, shift_id: 's-1', risk_class: 'R2', summary, description: null,
  status: 'REPORTED', owner_id: null, evidence: [], version: 1, created_at: '2026-08-02T00:00:00Z'
});
const report = (id: string): ReportEntry => ({
  report_id: id, shift_id: 's-1', report_type: 'END_SHIFT', version: 1, status: 'IN_REVIEW', is_current: true,
  sections: [], source_manifest: [], snapshot_digest: 'x', generated_from_cutoff: '2026-08-02T00:00:00Z', created_at: '2026-08-02T00:00:00Z'
});

describe('ApprovalActions', () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    sessionStorage.clear();
    setToken('test-token');
    fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => vi.unstubAllGlobals());

  it('renders every one of the five pairs regardless of capability advisory content (C3D-WO-REV-F1)', () => {
    // No capabilities prop exists on this component at all - it is never
    // gated by the advisory action list, proving absence of approval.create
    // cannot suppress controls.
    render(<ApprovalActions events={[event('e-1', 'Evt')]} incidents={[]} reports={[]} onRefresh={vi.fn()} />);
    const select = screen.getByLabelText('Target pair') as HTMLSelectElement;
    const labels = Array.from(select.options).map((o) => o.textContent);
    expect(labels).toStrictEqual([
      'Event confirm', 'Event correct', 'Task create (by intent id)', 'Incident acknowledge', 'Report approve'
    ]);
  });

  it('posts exactly the three-field payload for event.confirm', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(201, { receipt_id: 'r-1' }));
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { record_type: 'OperationalEvent', record_id: 'e-1', action: 'event.confirm', target_version: 1, risk_class: 'R1', ready: true, required_roles: [], satisfied_roles: [] }));
    const onRefresh = vi.fn().mockResolvedValue(undefined);
    render(<ApprovalActions events={[event('e-1', 'Evt')]} incidents={[]} reports={[]} onRefresh={onRefresh} />);

    await userEvent.selectOptions(screen.getByLabelText('Record'), 'e-1');
    await userEvent.click(screen.getByRole('button', { name: 'Create approval receipt' }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/approvals'),
      expect.objectContaining({ body: JSON.stringify({ record_type: 'OperationalEvent', action: 'event.confirm', record_id: 'e-1' }) })
    ));
    // Readiness IS called for event.confirm (one of the four supported pairs).
    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/approvals/readiness'), expect.anything()));
  });

  it('event.correct posts the receipt but never calls the unsupported readiness route', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(201, { receipt_id: 'r-2' }));
    const onRefresh = vi.fn().mockResolvedValue(undefined);
    render(<ApprovalActions events={[event('e-1', 'Evt')]} incidents={[]} reports={[]} onRefresh={onRefresh} />);

    await userEvent.selectOptions(screen.getByLabelText('Target pair'), '1');
    await userEvent.selectOptions(screen.getByLabelText('Record'), 'e-1');
    await userEvent.click(screen.getByRole('button', { name: 'Create approval receipt' }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/approvals'),
      expect.objectContaining({ body: JSON.stringify({ record_type: 'OperationalEvent', action: 'event.correct', record_id: 'e-1' }) })
    ));
    expect(fetchMock).not.toHaveBeenCalledWith(expect.stringContaining('/approvals/readiness'), expect.anything());
  });

  it('task.create accepts a manually entered stored intent id, not a discovery list', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(201, { receipt_id: 'r-3' }));
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { record_type: 'Task', record_id: 'intent-1', action: 'task.create', target_version: 1, risk_class: 'R2', ready: true, required_roles: [], satisfied_roles: [] }));
    const onRefresh = vi.fn().mockResolvedValue(undefined);
    render(<ApprovalActions events={[]} incidents={[]} reports={[]} onRefresh={onRefresh} />);

    await userEvent.selectOptions(screen.getByLabelText('Target pair'), '2');
    expect(screen.queryByLabelText('Record')).not.toBeInTheDocument();
    await userEvent.type(screen.getByLabelText('Stored task-creation intent id'), 'intent-1');
    await userEvent.click(screen.getByRole('button', { name: 'Create approval receipt' }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/approvals'),
      expect.objectContaining({ body: JSON.stringify({ record_type: 'Task', action: 'task.create', record_id: 'intent-1' }) })
    ));
  });

  it('incident.acknowledge and report.approve render targets from the passed collections', async () => {
    render(<ApprovalActions events={[]} incidents={[incident('i-1', 'Line down')]} reports={[report('r-1')]} onRefresh={vi.fn()} />);

    await userEvent.selectOptions(screen.getByLabelText('Target pair'), '3');
    const incidentSelect = screen.getByLabelText('Record');
    expect(within(incidentSelect).getByText('Line down')).toBeInTheDocument();

    await userEvent.selectOptions(screen.getByLabelText('Target pair'), '4');
    const reportSelect = screen.getByLabelText('Record');
    expect(within(reportSelect).getByText('Report 1')).toBeInTheDocument();
  });
});
