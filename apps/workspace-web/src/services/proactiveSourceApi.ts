import { ApiError } from './api';
import { clearSession, getPrincipalUserId, getToken } from '../features/authentication/session';
import type { SourceWindow } from '../types/proactiveSource';

const baseUrl = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export async function readProactiveSource(window: SourceWindow, token: string,
  principal: string, signal: AbortSignal): Promise<unknown> {
  if (!token || !principal || signal.aborted || getToken() !== token ||
      getPrincipalUserId() !== principal) throw new ApiError('cancelled', 'Source request cancelled');
  const query = new URLSearchParams({ query_start: window.query_start,
    query_end: window.query_end, run_as_of: window.run_as_of });
  let response: Response;
  try {
    response = await fetch(`${baseUrl}/proactive/source?${query}`, {
      method: 'GET', headers: { Authorization: `Bearer ${token}` },
      cache: 'no-store', signal
    });
  } catch {
    if (signal.aborted || getToken() !== token || getPrincipalUserId() !== principal)
      throw new ApiError('cancelled', 'Source request cancelled');
    throw new ApiError('network', 'Source unavailable');
  }
  if (signal.aborted || getToken() !== token || getPrincipalUserId() !== principal)
    throw new ApiError('cancelled', 'Source request cancelled');
  if (!response.ok) {
    if (response.status === 401) {
      clearSession();
      throw new ApiError('unauthorized', 'Authentication required');
    }
    throw new ApiError(response.status === 403 ? 'forbidden' :
      response.status === 422 ? 'invalid' : 'server', 'Source unavailable');
  }
  try {
    const payload: unknown = await response.json();
    if (signal.aborted || getToken() !== token || getPrincipalUserId() !== principal)
      throw new ApiError('cancelled', 'Source request cancelled');
    return payload;
  } catch (cause) {
    if (cause instanceof ApiError) throw cause;
    throw new ApiError('server', 'Source unavailable');
  }
}
