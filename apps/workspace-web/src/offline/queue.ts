import { getPrincipalUserId } from '../features/authentication/session';
import { appendStored, discardStored, mutateStored, readStored } from './storage';
import { OFFLINE_SCHEMA_VERSION, parseCommand, type CommandType, type OfflineCommand, type QueueViewItem } from './types';

const listeners = new Set<() => void>();
const volatileApplied = new Map<string, OfflineCommand>();
const volatileKey = (actor: string, id: string) => `${encodeURIComponent(actor)}:${id}`;
const TOMBSTONE_PREFIX = 'shiftops.offline.applied.v1.';
const tombstoneKey = (actor: string) => `${TOMBSTONE_PREFIX}${encodeURIComponent(actor)}`;

export class OfflineQueuedError extends Error {
  constructor(readonly clientOperationId: string) {
    super('Mutation staged for reconnect');
  }
}

export function enqueueTransition(commandType: CommandType, recordId: string, targetStatus: string, expectedVersion: number): never {
  const actorUserId = getPrincipalUserId();
  if (!actorUserId) throw new Error('Authenticated principal is not established');
  const command = {
    schemaVersion: OFFLINE_SCHEMA_VERSION,
    clientOperationId: crypto.randomUUID(),
    actorUserId,
    commandType,
    recordId,
    targetStatus,
    expectedVersion,
    createdAt: new Date().toISOString(),
    state: 'pending',
    lastErrorKind: null
  } as OfflineCommand;
  appendStored(actorUserId, command);
  emit();
  throw new OfflineQueuedError(command.clientOperationId);
}

export function queueItems(): QueueViewItem[] {
  const actor = getPrincipalUserId();
  if (!actor) return [];
  const overlays = [...readTombstones(actor), ...volatileApplied.values()].filter((item) => item.actorUserId === actor);
  const overlayIds = new Set(overlays.map((item) => item.clientOperationId));
  const stored = readStored(actor).map((item) => overlayIds.has(item.clientOperationId)
    ? overlays.find((overlay) => overlay.clientOperationId === item.clientOperationId)!
    : item);
  const storedIds = new Set(stored.map((item) => item.clientOperationId));
  return [...overlays.filter((item) => !storedIds.has(item.clientOperationId)), ...stored];
}

export function updateItem(id: string, update: (item: OfflineCommand) => OfflineCommand | null): void {
  const actor = getPrincipalUserId();
  if (!actor) return;
  updateActorItem(actor, id, update);
}

export function updateActorItem(actor: string, id: string, update: (item: OfflineCommand) => OfflineCommand | null): void {
  const key = volatileKey(actor, id);
  const tombstone = readTombstone(actor, id);
  if (tombstone) {
    const replacement = update(tombstone);
    if (replacement) putTombstone(actor, replacement);
    else {
      try { discardStored(actor, id); } catch { emit(); return; }
      removeTombstone(actor, id);
    }
    emit();
    return;
  }
  const volatile = volatileApplied.get(key);
  if (volatile?.actorUserId === actor) {
    const replacement = update(volatile);
    if (replacement) volatileApplied.set(key, replacement);
    else volatileApplied.delete(key);
  } else mutateStored(actor, id, update);
  emit();
}

export function markAppliedStale(actor: string, command: OfflineCommand): void {
  const applied = { ...command, state: 'applied_stale', lastErrorKind: 'refresh_failed' } as OfflineCommand;
  let tombstoneStored = false;
  try {
    putTombstone(actor, applied);
    tombstoneStored = true;
  } catch {}
  try {
    mutateStored(actor, command.clientOperationId, () => applied);
    if (tombstoneStored) removeTombstone(actor, command.clientOperationId);
  } catch {
    try { discardStored(actor, command.clientOperationId); } catch {}
    if (!tombstoneStored) volatileApplied.set(volatileKey(actor, command.clientOperationId), applied);
  }
  emit();
}

export function discardItem(id: string): void {
  const actor = getPrincipalUserId();
  if (!actor) return;
  if (readTombstone(actor, id)) updateActorItem(actor, id, () => null);
  else if (volatileApplied.delete(volatileKey(actor, id))) emit();
  else { discardStored(actor, id); emit(); }
}

export function subscribeQueue(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

export function notifyQueue(): void { emit(); }
export function resetQueueForTests(): void { volatileApplied.clear(); }
function emit(): void { listeners.forEach((listener) => listener()); }

function readTombstone(actor: string, id: string): OfflineCommand | null {
  return readTombstones(actor).find((item) => item.clientOperationId === id) ?? null;
}

function readTombstones(actor: string): OfflineCommand[] {
  try {
    const raw: unknown = JSON.parse(sessionStorage.getItem(tombstoneKey(actor)) ?? '[]');
    if (!Array.isArray(raw)) return [];
    return raw.slice(0, 50)
      .map((item) => parseCommand(item, actor))
      .filter((item): item is OfflineCommand => item !== null && item.state === 'applied_stale');
  } catch { return []; }
}

function putTombstone(actor: string, command: OfflineCommand): void {
  const commands = readTombstones(actor).filter((item) => item.clientOperationId !== command.clientOperationId);
  if (commands.length >= 50) throw new Error('offline applied tombstone limit reached');
  commands.push(command);
  sessionStorage.setItem(tombstoneKey(actor), JSON.stringify(commands));
}

function removeTombstone(actor: string, id: string): void {
  const commands = readTombstones(actor).filter((item) => item.clientOperationId !== id);
  if (commands.length) sessionStorage.setItem(tombstoneKey(actor), JSON.stringify(commands));
  else sessionStorage.removeItem(tombstoneKey(actor));
}
