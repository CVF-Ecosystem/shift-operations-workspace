import { clearSession, getToken } from '../features/authentication/session';
import type {
  CustomerRequest,
  Handover,
  Incident,
  OpenWorkResponse,
  OperationalEvent,
  Shift,
  Task,
  TokenResponse
} from '../types/operations';
import type { Message, ReadinessQuery, ReadinessResponse } from '../types/backendContracts';

const baseUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

// P2C-MUTATION-FULL-UI-C3B1 (SPEC R16/R36): 'outcome_unknown' is the
// controlled category for an ambiguous transport failure (aborted vs.
// genuinely lost is indistinguishable from fetch's rejection alone) - the
// caller must invalidate local state and require a fresh read, never retry
// automatically. 'cancelled' remains distinct: it is reported only when the
// caller's own AbortSignal was the one that fired.
export type ApiErrorKind =
  | 'network'
  | 'unauthorized'
  | 'forbidden'
  | 'not_found'
  | 'conflict'
  | 'invalid'
  | 'server'
  | 'cancelled'
  | 'outcome_unknown';

export class ApiError extends Error {
  readonly kind: ApiErrorKind;

  constructor(kind: ApiErrorKind, message: string) {
    super(message);
    this.kind = kind;
  }
}

function kindForStatus(status: number): ApiErrorKind {
  if (status === 401) return 'unauthorized';
  if (status === 403) return 'forbidden';
  if (status === 404) return 'not_found';
  if (status === 409) return 'conflict';
  if (status === 422) return 'invalid';
  return 'server';
}

async function readDetail(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === 'string') return body.detail;
  } catch {
    // no JSON body; fall through to a generic message.
  }
  return `Request failed with status ${response.status}`;
}

export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

interface RequestOptions {
  method?: HttpMethod;
  body?: unknown;
  query?: Record<string, string | number | boolean | undefined>;
  signal?: AbortSignal;
}

function buildQueryString(query: RequestOptions['query']): string {
  if (!query) return '';
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(query)) {
    if (value !== undefined) params.set(key, String(value));
  }
  const encoded = params.toString();
  return encoded ? `?${encoded}` : '';
}

// P2C-MUTATION-FULL-UI-C3B1 (SPEC R16): the single typed request primitive -
// method/body/query/AbortSignal, bearer auth preserved, no automatic retry.
// 401 clears the tab-scoped session (the caller still receives the thrown
// ApiError so it can redirect); 403/404/409/422 map to their controlled
// kind; a network-level rejection that is NOT the caller's own abort maps to
// 'outcome_unknown' rather than 'network', because a fetch-level rejection
// after a body was sent cannot distinguish "never reached the server" from
// "reached it but the response was lost" — never logs the token, body or raw
// transport exception.
async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, query, signal } = options;
  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) headers.Authorization = `Bearer ${token}`;
  if (body !== undefined) headers['Content-Type'] = 'application/json';

  let response: Response;
  try {
    response = await fetch(`${baseUrl}${path}${buildQueryString(query)}`, {
      method,
      headers,
      signal,
      body: body !== undefined ? JSON.stringify(body) : undefined
    });
  } catch (cause) {
    if (signal?.aborted) throw new ApiError('cancelled', 'Request was cancelled');
    throw new ApiError('outcome_unknown', 'Unable to confirm the request outcome; refresh before retrying');
  }

  if (!response.ok) {
    const detail = await readDetail(response);
    if (response.status === 401) clearSession();
    throw new ApiError(kindForStatus(response.status), detail);
  }

  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

export async function login(username: string, password: string): Promise<TokenResponse> {
  let response: Response;
  try {
    response = await fetch(`${baseUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
  } catch {
    throw new ApiError('network', 'Unable to reach the server');
  }
  if (!response.ok) {
    const detail = await readDetail(response);
    throw new ApiError(kindForStatus(response.status), detail);
  }
  return (await response.json()) as TokenResponse;
}

export const api = {
  health: () => request<{ status: string; mode: string }>('/health'),
  listShifts: (signal?: AbortSignal) => request<Shift[]>('/shifts', { signal }),
  listEvents: (shiftId: string, signal?: AbortSignal) =>
    request<OperationalEvent[]>('/events', { query: { shift_id: shiftId }, signal }),
  getOpenWork: (shiftId: string, signal?: AbortSignal) =>
    request<OpenWorkResponse>(`/shifts/${encodeURIComponent(shiftId)}/open-work`, { signal }),
  listIncidents: (shiftId: string, signal?: AbortSignal) =>
    request<Incident[]>('/incidents', { query: { shift_id: shiftId }, signal }),
  listHandovers: (shiftId: string, signal?: AbortSignal) =>
    request<Handover[]>('/handovers', { query: { from_shift_id: shiftId }, signal }),
  // P2C-MUTATION-FULL-UI-C3B1 (SPEC R11): browser-required reads added by
  // C3b1. No React feature calls these yet - C3c consumes them.
  listMessages: (shiftId: string, signal?: AbortSignal) =>
    request<Message[]>('/messages', { query: { shift_id: shiftId }, signal }),
  listTasks: (shiftId: string, signal?: AbortSignal) =>
    request<Task[]>('/tasks', { query: { shift_id: shiftId }, signal }),
  listCustomerRequests: (shiftId: string, signal?: AbortSignal) =>
    request<CustomerRequest[]>('/customer-requests', { query: { shift_id: shiftId }, signal }),
  getApprovalReadiness: (query: ReadinessQuery, signal?: AbortSignal) =>
    request<ReadinessResponse>('/approvals/readiness', {
      query: { record_type: query.record_type, record_id: query.record_id, action: query.action },
      signal
    })
};
