import { SOURCE_REASON_LABELS, type SourceView, type SourceWindow } from '../../types/proactiveSource';

let P5A2_SCOPED_SOURCE_MATRIX_CANONICAL_DIGEST: string;
P5A2_SCOPED_SOURCE_MATRIX_CANONICAL_DIGEST = "6fec188950fe752ac438e2952ec3d4e2ffd3b4156efa0b9a2e06e1048c568754"
export { P5A2_SCOPED_SOURCE_MATRIX_CANONICAL_DIGEST };

const COMMON = ['outcome', 'receipt_version', 'cohort_policy_version', 'numeric_policy_version'];
const READY = [...COMMON, 'scope_id', 'actor_id', 'query_start', 'query_end', 'run_as_of',
  'coverage_mode', 'eligible_count', 'selected_count', 'candidate_version_count',
  'max_snapshot_incident_refs', 'canonical_manifest', 'source_digest'];
const REFUSED = [...COMMON, 'reason'];
const SHA_HEX = /^[0-9a-f]{64}$/;

function record(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function exact(value: Record<string, unknown>, fields: string[]): boolean {
  return Object.keys(value).length === fields.length &&
    fields.every((field) => Object.prototype.hasOwnProperty.call(value, field));
}

function integer(value: unknown, min: number, max: number): value is number {
  return typeof value === 'number' && Number.isInteger(value) && value >= min && value <= max;
}

function common(value: Record<string, unknown>): boolean {
  return value.receipt_version === 'P5A2-SOURCE-RECEIPT-1' &&
    value.cohort_policy_version === 'P5A2-COHORT-ENDS-1' &&
    value.numeric_policy_version === 'P5A2-INITIAL-1';
}

async function digestMatches(manifest: string, digest: string): Promise<boolean> {
  try {
    if (!globalThis.crypto?.subtle || !SHA_HEX.test(digest)) return false;
    const bytes = new TextEncoder().encode(manifest);
    const hashed = await globalThis.crypto.subtle.digest('SHA-256', bytes);
    return Array.from(new Uint8Array(hashed), (byte) => byte.toString(16).padStart(2, '0')).join('') === digest;
  } catch {
    return false;
  }
}

/** Validates the registered flat HTTP representation, then discards private fields. */
export async function projectSourceReceipt(raw: unknown, actorId: string, window: SourceWindow): Promise<SourceView | null> {
  if (!actorId || typeof actorId !== 'string' ||
      !window || typeof window.query_start !== 'string' || !window.query_start ||
      typeof window.query_end !== 'string' || !window.query_end ||
      typeof window.run_as_of !== 'string' || !window.run_as_of ||
      !record(raw) || !common(raw)) return null;
  if (raw.outcome === 'SOURCE_REFUSED') {
    if (!exact(raw, REFUSED) || typeof raw.reason !== 'string' ||
        !Object.prototype.hasOwnProperty.call(SOURCE_REASON_LABELS, raw.reason)) return null;
    return { outcome: 'SOURCE_REFUSED', reason: raw.reason as keyof typeof SOURCE_REASON_LABELS };
  }
  if (raw.outcome !== 'SOURCE_READY' || !exact(raw, READY)) return null;
  if (typeof raw.scope_id !== 'string' || !raw.scope_id || raw.actor_id !== actorId ||
      raw.query_start !== window.query_start || raw.query_end !== window.query_end ||
      raw.run_as_of !== window.run_as_of || raw.coverage_mode !== 'SYNTHETIC_FIXTURE' ||
      typeof raw.canonical_manifest !== 'string' || !raw.canonical_manifest ||
      typeof raw.source_digest !== 'string') return null;
  if (!integer(raw.eligible_count, 1, 500) || !integer(raw.selected_count, 1, 500) ||
      !integer(raw.candidate_version_count, 1, 500) ||
      !integer(raw.max_snapshot_incident_refs, 0, 500) ||
      raw.eligible_count !== raw.selected_count ||
      !(await digestMatches(raw.canonical_manifest, raw.source_digest))) return null;
  return {
    outcome: 'SOURCE_READY', coverage: 'SYNTHETIC_FIXTURE', window: { ...window },
    eligibleCount: raw.eligible_count, selectedCount: raw.selected_count,
    candidateVersionCount: raw.candidate_version_count,
    maxSnapshotIncidentRefs: raw.max_snapshot_incident_refs
  };
}
