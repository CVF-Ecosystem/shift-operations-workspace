const TOKEN_KEY = 'shiftops.session.token';
const PRINCIPAL_KEY = 'shiftops.session.user_id';
const terminationListeners = new Set<() => void>();

export function getToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  sessionStorage.setItem(TOKEN_KEY, token);
}

export function clearSession(notifyTermination = true): void {
  const existed = sessionStorage.getItem(TOKEN_KEY) !== null || sessionStorage.getItem(PRINCIPAL_KEY) !== null;
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(PRINCIPAL_KEY);
  if (notifyTermination && existed) terminationListeners.forEach((listener) => listener());
}

export function hasSession(): boolean {
  return getToken() !== null;
}

export function setPrincipalUserId(userId: string): void {
  sessionStorage.setItem(PRINCIPAL_KEY, userId);
}

export function getPrincipalUserId(): string | null {
  return sessionStorage.getItem(PRINCIPAL_KEY);
}

export function subscribeSessionTermination(listener: () => void): () => void {
  terminationListeners.add(listener);
  return () => terminationListeners.delete(listener);
}
