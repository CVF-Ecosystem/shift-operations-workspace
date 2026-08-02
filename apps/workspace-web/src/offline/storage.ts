import { parseCommand, type OfflineCommand, type QueueViewItem, type QuarantinedEntry } from './types';

const PREFIX = 'shiftops.offline.queue.v1.';
const MAX_ITEMS = 50;

export function storageKey(actorUserId: string): string {
  return `${PREFIX}${encodeURIComponent(actorUserId)}`;
}

export function readStored(actorUserId: string): QueueViewItem[] {
  const raw = readRaw(actorUserId);
  if (!raw) return [invalid(0)];
  const result: QueueViewItem[] = [];
  raw.slice(0, MAX_ITEMS).forEach((item, index) => result.push(parseCommand(item, actorUserId) ?? invalid(index)));
  if (raw.length > MAX_ITEMS) result.push(invalid(MAX_ITEMS));
  return result;
}

export function appendStored(actorUserId: string, command: OfflineCommand): void {
  const raw = readRaw(actorUserId);
  if (!raw || raw.some((item) => parseCommand(item, actorUserId) === null)) {
    throw new Error('offline queue contains quarantined data');
  }
  if (raw.length >= MAX_ITEMS) throw new Error('offline queue limit reached');
  if (!parseCommand(command, actorUserId)) throw new Error('invalid offline queue write');
  raw.push(command);
  writeRaw(actorUserId, raw);
}

export function mutateStored(actorUserId: string, operationId: string, update: (item: OfflineCommand) => OfflineCommand | null): void {
  const raw = readRaw(actorUserId);
  if (!raw) return;
  const index = raw.findIndex((item) => parseCommand(item, actorUserId)?.clientOperationId === operationId);
  if (index < 0) return;
  const current = parseCommand(raw[index], actorUserId);
  if (!current) return;
  const replacement = update(current);
  if (replacement) {
    if (!parseCommand(replacement, actorUserId)) throw new Error('invalid offline queue update');
    raw[index] = replacement;
  } else raw.splice(index, 1);
  writeRaw(actorUserId, raw);
}

export function discardStored(actorUserId: string, operationId: string): void {
  const raw = readRaw(actorUserId);
  if (!raw) {
    if (operationId === 'invalid-0') localStorage.removeItem(storageKey(actorUserId));
    return;
  }
  const invalidMatch = /^invalid-(\d+)$/.exec(operationId);
  if (invalidMatch) {
    const index = Number(invalidMatch[1]);
    if (index < raw.length && (index >= MAX_ITEMS || parseCommand(raw[index], actorUserId) === null)) {
      raw.splice(index, 1);
      writeRaw(actorUserId, raw);
    }
    return;
  }
  mutateStored(actorUserId, operationId, () => null);
}

function invalid(index: number): QuarantinedEntry {
  return { clientOperationId: `invalid-${index}`, state: 'blocked', lastErrorKind: 'storage', reason: 'Invalid or expired offline item' };
}

function readRaw(actorUserId: string): unknown[] | null {
  try {
    const parsed: unknown = JSON.parse(localStorage.getItem(storageKey(actorUserId)) ?? '[]');
    return Array.isArray(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

function writeRaw(actorUserId: string, raw: unknown[]): void {
  localStorage.setItem(storageKey(actorUserId), JSON.stringify(raw));
}
