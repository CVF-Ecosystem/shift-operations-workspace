import { getToken } from '../features/authentication/session';
import type {
  Handover,
  Incident,
  OpenWorkResponse,
  OperationalEvent,
  Shift,
  TokenResponse
} from '../types/operations';

const baseUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export type ApiErrorKind =
  | 'network'
  | 'unauthorized'
  | 'forbidden'
  | 'not_found'
  | 'conflict'
  | 'invalid'
  | 'server'
  | 'cancelled';

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

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) headers.Authorization = `Bearer ${token}`;

  let response: Response;
  try {
    response = await fetch(`${baseUrl}${path}`, { headers, signal });
  } catch (cause) {
    if (signal?.aborted) throw new ApiError('cancelled', 'Request was cancelled');
    throw new ApiError('network', 'Unable to reach the server');
  }

  if (!response.ok) {
    const detail = await readDetail(response);
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
  listShifts: (signal?: AbortSignal) => request<Shift[]>('/shifts', signal),
  listEvents: (shiftId: string, signal?: AbortSignal) =>
    request<OperationalEvent[]>(`/events?shift_id=${encodeURIComponent(shiftId)}`, signal),
  getOpenWork: (shiftId: string, signal?: AbortSignal) =>
    request<OpenWorkResponse>(`/shifts/${encodeURIComponent(shiftId)}/open-work`, signal),
  listIncidents: (shiftId: string, signal?: AbortSignal) =>
    request<Incident[]>(`/incidents?shift_id=${encodeURIComponent(shiftId)}`, signal),
  listHandovers: (shiftId: string, signal?: AbortSignal) =>
    request<Handover[]>(`/handovers?from_shift_id=${encodeURIComponent(shiftId)}`, signal)
};
