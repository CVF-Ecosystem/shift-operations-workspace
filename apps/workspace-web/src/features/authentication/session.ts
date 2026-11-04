const TOKEN_KEY = 'shiftops.session.token';
const PRINCIPAL_KEY = 'shiftops.session.user_id';
const terminationListeners = new Set<() => void>();
const changeListeners = new Set<() => void>();

export function getToken(): string | null {
  return sessionStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  const changed = getToken() !== token;
  sessionStorage.setItem(TOKEN_KEY, token);
  if (changed) changeListeners.forEach((listener) => listener());
}

export function clearSession(notifyTermination = true): void {
  const existed = sessionStorage.getItem(TOKEN_KEY) !== null || sessionStorage.getItem(PRINCIPAL_KEY) !== null;
  sessionStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(PRINCIPAL_KEY);
  changeListeners.forEach((listener) => listener());
  if (notifyTermination && existed) terminationListeners.forEach((listener) => listener());
}

export function hasSession(): boolean {
  return getToken() !== null;
}

export function setPrincipalUserId(userId: string): void {
  const changed = getPrincipalUserId() !== userId;
  sessionStorage.setItem(PRINCIPAL_KEY, userId);
  if (changed) changeListeners.forEach((listener) => listener());
}

export function getPrincipalUserId(): string | null {
  return sessionStorage.getItem(PRINCIPAL_KEY);
}

export function subscribeSessionTermination(listener: () => void): () => void {
  terminationListeners.add(listener);
  return () => terminationListeners.delete(listener);
}

export function subscribeSessionChange(listener: () => void): () => void {
  changeListeners.add(listener);
  return () => changeListeners.delete(listener);
}
