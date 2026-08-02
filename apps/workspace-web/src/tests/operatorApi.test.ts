import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { operatorApi } from '../services/operatorApi';

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

describe('operatorApi service', () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    sessionStorage.clear();
    fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('createShift posts to /shifts with query params', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { shift_id: 's-1' }));
    await operatorApi.createShift('Morning', '2026-08-01T08:00:00Z', '2026-08-01T16:00:00Z');
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/shifts?name=Morning&starts_at=2026-08-01T08%3A00%3A00Z&ends_at=2026-08-01T16%3A00%3A00Z'),
      expect.objectContaining({ method: 'POST' })
    );
  });

  it('closeShift posts expected_version to /shifts/{id}/close', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { shift_id: 's-1', status: 'CLOSED' }));
    await operatorApi.closeShift('s-1', 2);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/shifts/s-1/close'),
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ expected_version: 2 }) })
    );
  });

  it('createMessage posts shift_id and text to /messages', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { message_id: 'm-1' }));
    await operatorApi.createMessage('s-1', 'hello team');
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/messages'),
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ shift_id: 's-1', text: 'hello team' }) })
    );
  });

  it('createEvent posts event fields to /events', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { event_id: 'e-1' }));
    await operatorApi.createEvent('s-1', 'equipment_downtime', 'Server reboot', 'R1');
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/events'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ shift_id: 's-1', event_type: 'equipment_downtime', title: 'Server reboot', risk_class: 'R1' })
      })
    );
  });

  it('createTaskIntent and createTask post to /tasks endpoints', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(201, { intent_id: 'i-1', payload_digest: 'abc', risk_class: 'R2', created_at: '2026-08-01T00:00:00Z' }));
    const intentRes = await operatorApi.createTaskIntent('s-1', 'Critical task', 'R2');
    expect(intentRes.intent_id).toBe('i-1');

    fetchMock.mockResolvedValueOnce(jsonResponse(200, { task_id: 't-1' }));
    await operatorApi.createTask('s-1', 'Critical task', 'R2', 'i-1');
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/tasks'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ shift_id: 's-1', title: 'Critical task', risk_class: 'R2', intent_id: 'i-1' })
      })
    );
  });

  it('reportIncident and transitionIncident post expected bodies', async () => {
    fetchMock.mockResolvedValueOnce(jsonResponse(200, { incident_id: 'inc-1' }));
    await operatorApi.reportIncident('s-1', 'Power outage', 'R2');
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/incidents'),
      expect.objectContaining({ method: 'POST' })
    );

    fetchMock.mockResolvedValueOnce(jsonResponse(200, { incident_id: 'inc-1', status: 'MITIGATING' }));
    await operatorApi.transitionIncident('inc-1', 'MITIGATING', 1);
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/incidents/inc-1/transition'),
      expect.objectContaining({ method: 'POST', body: JSON.stringify({ target_status: 'MITIGATING', expected_version: 1 }) })
    );
  });
});
