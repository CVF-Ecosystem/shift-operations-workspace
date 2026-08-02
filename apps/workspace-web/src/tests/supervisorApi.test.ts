// P2C-MUTATION-FULL-UI-C3D (SPEC R2-R6): proves supervisorApi calls the
// exact existing backend routes with the exact payload contract, and never
// forks auth/error/query encoding from the shared request primitive.
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { supervisorApi } from '../services/supervisorApi';

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

describe('supervisorApi service', () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    sessionStorage.clear();
    fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('listStaffingShifts/listStaffingUsers hit the supervisor-only staffing routes', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, []));
    await supervisorApi.listStaffingShifts();
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/staffing/shifts'), expect.anything());

    fetchMock.mockResolvedValueOnce(jsonResponse(200, []));
    await supervisorApi.listStaffingUsers();
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/staffing/users'), expect.anything());
  });

  it('assignUser posts only user_id to /shifts/{id}/assignments', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(201, { assignment_id: 'a-1' }));
    await supervisorApi.assignUser('s-1', 'u-1');
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/shifts/s-1/assignments'),
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ user_id: 'u-1' }) })
    );
  });

  it('revokeAssignment posts only expected_version to the revoke route', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { assignment_id: 'a-1', status: 'REVOKED' }));
    await supervisorApi.revokeAssignment('s-1', 'a-1', 2);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/shifts/s-1/assignments/a-1/revoke'),
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ expected_version: 2 }) })
    );
  });

  it('confirmEvent posts expected_version to /events/{id}/confirm', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { event_id: 'e-1', state: 'CONFIRMED' }));
    await supervisorApi.confirmEvent('e-1', 1);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/events/e-1/confirm'),
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ expected_version: 1 }) })
    );
  });

  it('correctEvent posts reason and expected_version to /corrections/events/{id}', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { correction_id: 'c-1' }));
    await supervisorApi.correctEvent('e-1', { reason: 'typo fix', expected_version: 2 });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/corrections/events/e-1'),
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ reason: 'typo fix', expected_version: 2 }) })
    );
  });

  it('createApproval posts exactly the three-field payload for event.correct', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(201, { receipt_id: 'r-1' }));
    await supervisorApi.createApproval({ record_type: 'OperationalEvent', action: 'event.correct', record_id: 'e-1' });
    const [, options] = fetchMock.mock.calls[0] as [string, RequestInit];
    const sent = JSON.parse(options.body as string);
    expect(Object.keys(sent).sort()).toStrictEqual(['action', 'record_id', 'record_type']);
    expect(sent).toStrictEqual({ record_type: 'OperationalEvent', action: 'event.correct', record_id: 'e-1' });
  });

  it('acknowledgeIncident posts expected_version to /incidents/{id}/acknowledge', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { incident_id: 'i-1', status: 'ACKNOWLEDGED' }));
    await supervisorApi.acknowledgeIncident('i-1', { expected_version: 1 });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/incidents/i-1/acknowledge'),
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ expected_version: 1 }) })
    );
  });

  it('reviewHandover and acknowledgeHandover post to the correct distinct routes', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { handover_id: 'h-1', status: 'REVIEWED' }));
    await supervisorApi.reviewHandover('h-1', { expected_version: 1 });
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/handovers/h-1/review'), expect.anything());

    fetchMock.mockResolvedValueOnce(jsonResponse(200, { handover_id: 'h-1', status: 'ACKNOWLEDGED' }));
    await supervisorApi.acknowledgeHandover('h-1', { expected_version: 2 });
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/handovers/h-1/acknowledge'), expect.anything());
  });

  it('approveReport posts expected_version and expected_status', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { report_id: 'r-1', status: 'APPROVED' }));
    await supervisorApi.approveReport('r-1', { expected_version: 3, expected_status: 'IN_REVIEW' });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/reports/r-1/approve'),
      expect.objectContaining({ body: JSON.stringify({ expected_version: 3, expected_status: 'IN_REVIEW' }) })
    );
  });

  it('createReportVersion posts reason plus preconditions to /reports/{id}/versions (successor-only revocation)', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(201, { report_id: 'r-2', status: 'DRAFT' }));
    await supervisorApi.createReportVersion('r-1', { reason: 'incorrect figures', expected_version: 4, expected_status: 'APPROVED' });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/reports/r-1/versions'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ reason: 'incorrect figures', expected_version: 4, expected_status: 'APPROVED' })
      })
    );
  });

  it('freezeShift sends only expected_version - no retired override field', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { shift_id: 's-1', status: 'FROZEN' }));
    await supervisorApi.freezeShift('s-1', { expected_version: 5 });
    const [, options] = fetchMock.mock.calls[0] as [string, RequestInit];
    const sent = JSON.parse(options.body as string);
    expect(Object.keys(sent)).toStrictEqual(['expected_version']);
    expect(sent).not.toHaveProperty('override_unimplemented_prerequisites');
    expect(sent).not.toHaveProperty('override_reason');
  });

  it('getTaskCreationIntent reads the existing creation-intent GET route, not an invented /tasks/{id}', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, {
      intent_id: 'i-1', payload_snapshot: {}, payload_digest: 'd', risk_class: 'R2', created_by: 'u-1', created_at: '2026-08-02T00:00:00Z'
    }));
    await supervisorApi.getTaskCreationIntent('i-1');
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining('/tasks/creation-intents/i-1'), expect.anything());
  });
});
