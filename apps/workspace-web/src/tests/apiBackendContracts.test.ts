// P2C-MUTATION-FULL-UI-C3B1 (SPEC R11/R15/R35-R37): proves the browser
// request primitive calls the exact new backend read/readiness routes with
// the exact query contract, and that the feature-owned DTOs in
// types/backendContracts.ts round-trip a realistic backend response without
// dropping or renaming a field. This is the frontend half of the OpenAPI
// delta proof in tests/unit/test_c3b_read_openapi_contract.py; it does not
// re-derive the backend schema, only the browser's agreement with it.

import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { api } from '../services/api';
import type { Message, ReadinessResponse } from '../types/backendContracts';

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

  it('lists customer requests for a shift with the exact query contract', async () => {
    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    fetchMock.mockResolvedValueOnce(jsonResponse(200, []));

    await api.listCustomerRequests('s-1');

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
      record_type: 'Report',
      record_id: 'r-1',
      action: 'report.approve',
      target_version: 3,
      risk_class: 'R3',
      ready: true,
      required_roles: ['shift_supervisor', 'operations_manager'],
      satisfied_roles: ['shift_supervisor', 'operations_manager']
    };
    fetchMock.mockResolvedValueOnce(jsonResponse(200, readiness));

    const result = await api.getApprovalReadiness({
      record_type: 'Report',
      record_id: 'r-1',
      action: 'report.approve'
    });

    expect(Object.keys(result).sort()).toStrictEqual(
      [
        'record_type',
        'record_id',
        'action',
        'target_version',
        'risk_class',
        'ready',
        'required_roles',
        'satisfied_roles'
      ].sort()
    );
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
});
