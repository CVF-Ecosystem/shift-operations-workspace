import type { CustomerRequestStatus, IncidentStatus, TaskStatus } from '../types/operations';

export const OFFLINE_SCHEMA_VERSION = 1 as const;
export type QueueState = 'pending' | 'replaying' | 'blocked' | 'outcome_unknown' | 'applied_stale';
export type BlockedErrorKind = 'conflict' | 'forbidden' | 'not_found' | 'invalid' | 'unauthorized' | 'server' | 'storage';
export type QueueErrorKind = BlockedErrorKind | 'outcome_unknown' | 'refresh_failed' | null;
export type CommandType = 'task.transition' | 'customer_request.transition' | 'incident.transition';

interface CommandBase {
  schemaVersion: typeof OFFLINE_SCHEMA_VERSION;
  clientOperationId: string;
  actorUserId: string;
  recordId: string;
  expectedVersion: number;
  createdAt: string;
  state: QueueState;
  lastErrorKind: QueueErrorKind;
}

export type OfflineCommand =
  | (CommandBase & { commandType: 'task.transition'; targetStatus: TaskStatus })
  | (CommandBase & { commandType: 'customer_request.transition'; targetStatus: CustomerRequestStatus })
  | (CommandBase & { commandType: 'incident.transition'; targetStatus: IncidentStatus });

export interface QuarantinedEntry {
  clientOperationId: string;
  state: 'blocked';
  lastErrorKind: 'storage';
  reason: 'Invalid or expired offline item';
}

export type QueueViewItem = OfflineCommand | QuarantinedEntry;

const KEYS = ['schemaVersion', 'clientOperationId', 'actorUserId', 'commandType', 'recordId', 'targetStatus', 'expectedVersion', 'createdAt', 'state', 'lastErrorKind'];
const STATES: QueueState[] = ['pending', 'replaying', 'blocked', 'outcome_unknown', 'applied_stale'];
const BLOCKED: BlockedErrorKind[] = ['conflict', 'forbidden', 'not_found', 'invalid', 'unauthorized', 'server', 'storage'];
const TASK = ['OPEN', 'IN_PROGRESS', 'BLOCKED', 'DONE', 'CARRY_OVER', 'CANCELLED'];
const REQUEST = ['NEW', 'ACKNOWLEDGED', 'IN_PROGRESS', 'WAITING', 'RESOLVED', 'CLOSED'];
const INCIDENT = ['MITIGATING', 'RESOLVED', 'CLOSED'];
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export function parseCommand(value: unknown, actorUserId: string, now = Date.now()): OfflineCommand | null {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return null;
  const obj = value as Record<string, unknown>;
  if (Object.keys(obj).length !== KEYS.length || Object.keys(obj).some((key) => !KEYS.includes(key))) return null;
  if (obj.schemaVersion !== 1 || obj.actorUserId !== actorUserId) return null;
  if (typeof obj.clientOperationId !== 'string' || !UUID.test(obj.clientOperationId)) return null;
  if (typeof obj.recordId !== 'string' || !UUID.test(obj.recordId)) return null;
  if (!Number.isInteger(obj.expectedVersion) || (obj.expectedVersion as number) < 1) return null;
  if (typeof obj.createdAt !== 'string') return null;
  const created = Date.parse(obj.createdAt);
  if (!Number.isFinite(created) || created > now + 60_000 || now - created >= 86_400_000) return null;
  if (!STATES.includes(obj.state as QueueState) || !validError(obj.state as QueueState, obj.lastErrorKind)) return null;
  if (!validTarget(obj.commandType, obj.targetStatus)) return null;
  return obj as unknown as OfflineCommand;
}

function validError(state: QueueState, error: unknown): boolean {
  if (state === 'pending' || state === 'replaying') return error === null;
  if (state === 'blocked') return BLOCKED.includes(error as BlockedErrorKind);
  if (state === 'outcome_unknown') return error === 'outcome_unknown';
  return error === 'refresh_failed';
}

function validTarget(type: unknown, target: unknown): boolean {
  if (typeof target !== 'string') return false;
  if (type === 'task.transition') return TASK.includes(target);
  if (type === 'customer_request.transition') return REQUEST.includes(target);
  if (type === 'incident.transition') return INCIDENT.includes(target);
  return false;
}
