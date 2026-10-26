import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
// @ts-expect-error Browser tsconfig omits Node types; Vitest runs on the installed Node runtime.
import { createHash, webcrypto } from 'node:crypto';
import matrixText from '../../../../docs/cvf/invariants/p5a2-scoped-source-outcomes.json?raw';
import { projectSourceReceipt, P5A2_SCOPED_SOURCE_MATRIX_CANONICAL_DIGEST } from '../features/proactive-source/sourceReceipt';
import { ACTOR, mutationCases, mutatedReceipt, positives, refusalSamples } from './proactiveSourceTestData';

const window = positives[0].window;

describe('scoped source HTTP receipt projection', () => {
  beforeEach(() => vi.stubGlobal('crypto', webcrypto));
  afterEach(() => vi.unstubAllGlobals());

  it('uses the admitted native family digest and projects both full positive contexts', async () => {
    const nativeLfDigest = createHash('sha256').update(matrixText.replace(/\r\n?/g, '\n'), 'utf8').digest('hex');
    expect(P5A2_SCOPED_SOURCE_MATRIX_CANONICAL_DIGEST).toBe(nativeLfDigest);
    for (const sample of positives) {
      const view = await projectSourceReceipt(sample.receipt, ACTOR, sample.window);
      expect(view).toEqual({ outcome: 'SOURCE_READY', coverage: 'SYNTHETIC_FIXTURE',
        window: sample.window, eligibleCount: sample.receipt.eligible_count,
        selectedCount: sample.receipt.selected_count,
        candidateVersionCount: sample.receipt.candidate_version_count,
        maxSnapshotIncidentRefs: sample.receipt.max_snapshot_incident_refs });
      expect(Object.keys(view ?? {}).sort()).toEqual(['candidateVersionCount', 'coverage', 'eligibleCount',
        'maxSnapshotIncidentRefs', 'outcome', 'selectedCount', 'window']);
    }
  });

  it('accepts all nine fixed refusal reasons', async () => {
    expect(Object.keys(refusalSamples)).toHaveLength(9);
    for (const [reason, receipt] of Object.entries(refusalSamples)) {
      expect(await projectSourceReceipt(receipt, ACTOR, window)).toEqual({ outcome: 'SOURCE_REFUSED', reason });
    }
  });

  it('rejects all 84 pre-frozen native mutation descriptors in the actual consumer', async () => {
    expect(mutationCases).toHaveLength(84);
    for (const mutation of mutationCases) {
      expect(await projectSourceReceipt(mutatedReceipt(mutation), ACTOR, window), mutation.mutationId).toBeNull();
    }
  });

  it('fails closed on actor, window, digest and WebCrypto failures', async () => {
    const receipt = positives[0].receipt;
    expect(await projectSourceReceipt(receipt, 'another-user', window)).toBeNull();
    expect(await projectSourceReceipt(receipt, '', window)).toBeNull();
    expect(await projectSourceReceipt(receipt, ACTOR, { ...window, query_start: '' })).toBeNull();
    expect(await projectSourceReceipt(receipt, ACTOR, { ...window, query_end: window.query_start })).toBeNull();
    expect(await projectSourceReceipt({ ...receipt, source_digest: '0'.repeat(64) }, ACTOR, window)).toBeNull();
    vi.stubGlobal('crypto', {});
    expect(await projectSourceReceipt(receipt, ACTOR, window)).toBeNull();
    vi.stubGlobal('crypto', { subtle: { digest: () => Promise.reject(new Error('private')) } });
    expect(await projectSourceReceipt(receipt, ACTOR, window)).toBeNull();
  });

  it('rejects booleans and fractions in each count field', async () => {
    for (const field of ['eligible_count', 'selected_count', 'candidate_version_count',
      'max_snapshot_incident_refs'] as const) {
      for (const value of [true, 1.5]) {
        expect(await projectSourceReceipt({ ...positives[0].receipt, [field]: value }, ACTOR, window)).toBeNull();
      }
    }
  });
});
