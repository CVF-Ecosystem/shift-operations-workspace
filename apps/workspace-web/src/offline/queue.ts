export type OfflineCommand = { clientOperationId: string; type: string; payload: unknown; createdAt: string };
const KEY = 'shiftops.offline.queue';
export function enqueue(command: OfflineCommand) { const q = JSON.parse(localStorage.getItem(KEY) ?? '[]') as OfflineCommand[]; q.push(command); localStorage.setItem(KEY, JSON.stringify(q)); }
export function readQueue(): OfflineCommand[] { return JSON.parse(localStorage.getItem(KEY) ?? '[]') as OfflineCommand[]; }
export function clearQueue() { localStorage.removeItem(KEY); }
