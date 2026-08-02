// P2C-MUTATION-FULL-UI-C3B1 (SPEC R11/R15/R35-R37): proves the browser
// request primitive calls the exact new backend read/readiness routes with
// the exact query contract, and that the feature-owned DTOs in
// types/backendContracts.ts round-trip a realistic backend response without
// dropping or renaming a field. This is the frontend half of the OpenAPI
// delta proof in tests/unit/test_c3b_read_openapi_contract.py; it does not
// re-derive the backend schema, only the browser's agreement with it.

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { api } from '../services/api';
import { operatorApi } from '../services/operatorApi';
import { OPERATIONAL_EVENT_TYPES } from '../types/backendContracts';
import type { CapabilitiesResponse, Message, ReadinessResponse, ReportResponse } from '../types/backendContracts';
import type { CustomerRequest } from '../types/operations';

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });
}

describe('backend contract reads (C3b1)', () => {
  beforeEach(() => {
    sessionStorage.clear();
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('lists messages for a shift with the exact query contract', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    const message: Message = {
      message_id: 'm-1',
      shift_id: 's-1',
      source: 'internal',
      sender_id: 'u-1',
      text: 'hello',
      state: 'RAW',
      created_at: '2026-08-01T00:00:00Z',
      evidence: []
    };
    fetchMock.mockResolvedValueOnce(jsonResponse(200, [message]));

    const result = await api.listMessages('s-1');

    expect(result).toStrictEqual([message]);
    const [url] = fetchMock.mock.calls[0] as [string];
    expect(url).toContain('/messages?');
    expect(url).toContain('shift_id=s-1');
  });

  it('lists tasks for a shift with the exact query contract', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    fetchMock.mockResolvedValueOnce(jsonResponse(200, []));

    await api.listTasks('s-1');

    const [url] = fetchMock.mock.calls[0] as [string];
    expect(url).toContain('/tasks?');
    expect(url).toContain('shift_id=s-1');
  });

  it('lists customer requests for a shift with the exact query contract and round-trips version', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    const customerRequest: CustomerRequest = {
      request_id: 'cr-1',
      customer_id: 'c-1',
      shift_id: 's-1',
      summary: 'Delayed delivery',
      details: null,
      status: 'NEW',
      source_message_id: null,
      received_at: '2026-08-01T00:00:00Z',
      promised_at: null,
      owner_id: null,
      version: 1
    };
    fetchMock.mockResolvedValueOnce(jsonResponse(200, [customerRequest]));

    const result = await api.listCustomerRequests('s-1');

    expect(result).toStrictEqual([customerRequest]);
    const [url] = fetchMock.mock.calls[0] as [string];
    expect(url).toContain('/customer-requests?');
    expect(url).toContain('shift_id=s-1');
  });

  it('requests approval readiness with the exact three query parameters and round-trips the sanitized response', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    const readiness: ReadinessResponse = {
      record_type: 'OperationalEvent',
      record_id: 'e-1',
      action: 'event.confirm',
      target_version: 1,
      risk_class: 'R2',
      ready: false,
      required_roles: ['shift_supervisor'],
      satisfied_roles: []
    };
    fetchMock.mockResolvedValueOnce(jsonResponse(200, readiness));

    const result = await api.getApprovalReadiness({
      record_type: 'OperationalEvent',
      record_id: 'e-1',
      action: 'event.confirm'
    });

    expect(result).toStrictEqual(readiness);
    const [url] = fetchMock.mock.calls[0] as [string];
    expect(url).toContain('/approvals/readiness?');
    expect(url).toContain('record_type=OperationalEvent');
    expect(url).toContain('record_id=e-1');
    expect(url).toContain('action=event.confirm');
  });

  it('never exposes a payload digest, receipt id, approver identity or credential field on the readiness DTO', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    const readiness: ReadinessResponse = {
      record_type: 'Report', record_id: 'r-1', action: 'report.approve', target_version: 3, risk_class: 'R3',
      ready: true, required_roles: ['shift_supervisor', 'operations_manager'], satisfied_roles: ['shift_supervisor']
    };
    fetchMock.mockResolvedValueOnce(jsonResponse(200, readiness));
    const result = await api.getApprovalReadiness({ record_type: 'Report', record_id: 'r-1', action: 'report.approve' });
    expect(Object.keys(result).sort()).toStrictEqual(Object.keys(readiness).sort());
  });

  it('maps a readiness 404 to the controlled not_found kind', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    fetchMock.mockResolvedValueOnce(jsonResponse(404, { detail: 'Operational resource not found' }));

    await expect(
      api.getApprovalReadiness({ record_type: 'Task', record_id: 'missing', action: 'task.create' })
    ).rejects.toMatchObject({ kind: 'not_found' });
  });

  it('maps a bounded-list 422 to the controlled invalid kind without silent truncation', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    fetchMock.mockResolvedValueOnce(
      jsonResponse(422, { detail: 'Message list exceeds 500-record maximum; pagination not yet implemented' })
    );

    await expect(api.listMessages('s-1')).rejects.toMatchObject({ kind: 'invalid' });
  });

  it('reads capabilities in the real {shift_id, actions, reasons} shape (WO C3C-BUILD-REV-F2), not {capabilities}', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    const response: CapabilitiesResponse = {
      shift_id: 's-1', actions: ['task.create', 'incident.report'],
      reasons: ['active_assignment_required', 'server_reauthorizes_every_mutation']
    };
    fetchMock.mockResolvedValueOnce(jsonResponse(200, response));
    const result = await operatorApi.getCapabilities('s-1');
    expect(result).toStrictEqual(response);
    expect(Object.keys(result).sort()).toStrictEqual(['actions', 'reasons', 'shift_id']);
  });

  it('round-trips a Report with the exact backend ReportStatus/ReportType and never invents REVIEW_REQUESTED', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    const report: ReportResponse = {
      report_id: 'r-1', shift_id: 's-1', report_type: 'END_SHIFT', version: 2, status: 'IN_REVIEW', is_current: true,
      sections: [], source_manifest: [], snapshot_digest: 'SECRET_DIGEST',
      generated_from_cutoff: '2026-08-01T00:00:00Z', created_at: '2026-08-01T00:00:00Z'
    };
    fetchMock.mockResolvedValueOnce(jsonResponse(200, [report]));
    const [result] = await operatorApi.listReports('s-1');
    expect(result.status).toBe('IN_REVIEW');
    expect(result.report_type).toBe('END_SHIFT');
  });

  it('exposes the exact bounded OperationalEvent.event_type domain-lock allowlist including equipment_downtime', () => {
    expect(OPERATIONAL_EVENT_TYPES).toContain('equipment_downtime');
    expect(OPERATIONAL_EVENT_TYPES).toHaveLength(10);
  });
});
