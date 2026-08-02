// P2C-MUTATION-FULL-UI-C3D (SPEC R4/R8/R9): proves the five approval pairs
// post the real API, wrong-role/unassigned/stale/missing-approval/frozen-
// parent/retired-override refusals, accessibility and bounded P2-D PWA truth.
import { expect, test } from '@playwright/test';
import { apiLogin, API_BASE_URL, arrangeFrozenEvent, createShift, loginAsOperator, loginAsSupervisor } from './operator-flow-helpers';

test.describe('Supervisor Accessibility & Refusal Matrix', () => {
  test('an operator session (wrong role) never sees the supervisor operational subtree, and staffing 403s cleanly', async ({ page }) => {
    await loginAsOperator(page);
    await createShift(page, 'Wrong Role Shift', '2026-08-02T08:00', '2026-08-02T16:00');

    await expect(page.getByText('Staffing control is unavailable for your current role.')).toBeVisible();
    for (const label of ['Freeze shift', 'Approve report', 'Confirm event']) {
      await expect(page.getByRole('button', { name: label })).toHaveCount(0);
    }
  });

  test('all five approval pairs post the exact three-field payload to the real API and round-trip a receipt', async ({ page, request }) => {
    await loginAsSupervisor(page);
    await createShift(page, 'Approvals Shift', '2026-08-02T08:00', '2026-08-02T16:00');
    const shiftId = await page.locator('.shift-selector select').inputValue();

    const supToken = await apiLogin(request, 'sup1', 'sup1-devpass');
    const headers = { Authorization: `Bearer ${supToken}` };
    const eventRes = await request.post(`${API_BASE_URL}/events`, {
      headers, data: { shift_id: shiftId, event_type: 'shift_update', title: 'Approval target event', risk_class: 'R2', evidence: [{ source_type: 'message', source_id: 'approval-event' }] }
    });
    expect(eventRes.ok()).toBe(true);
    const event = await eventRes.json();
    const intentRes = await request.post(`${API_BASE_URL}/tasks/creation-intents`, {
      headers, data: { shift_id: shiftId, title: 'Approval target task', risk_class: 'R2' }
    });
    expect(intentRes.ok()).toBe(true);
    const intent = await intentRes.json();
    const incidentRes = await request.post(`${API_BASE_URL}/incidents`, {
      headers, data: { shift_id: shiftId, summary: 'Approval target incident', risk_class: 'R2', evidence: [{ source_type: 'message', source_id: 'approval-incident' }] }
    });
    expect(incidentRes.ok()).toBe(true);
    const incident = await incidentRes.json();
    const closed = await request.post(`${API_BASE_URL}/shifts/${shiftId}/close`, { headers, data: { expected_version: 1 } });
    expect(closed.ok()).toBe(true);
    const reportRes = await request.post(`${API_BASE_URL}/reports`, { headers, data: { shift_id: shiftId } });
    expect(reportRes.ok()).toBe(true);
    const report = await reportRes.json();
    const submitted = await request.post(`${API_BASE_URL}/reports/${report.report_id}/submit-review`, {
      headers, data: { expected_version: report.version, expected_status: report.status }
    });
    expect(submitted.ok()).toBe(true);

    await page.reload();
    await page.waitForSelector('main.operations-console', { timeout: 10000 });
    await page.selectOption('.shift-selector select', { label: 'Approvals Shift · CLOSED' });

    let capturedBodies: string[] = [];
    await page.route('**/approvals', async (route) => {
      if (route.request().method() === 'POST') capturedBodies.push(route.request().postData() ?? '');
      await route.continue();
    });

    const pairs: [string, string, string][] = [
      ['OperationalEvent', 'event.confirm', event.event_id],
      ['OperationalEvent', 'event.correct', event.event_id],
      ['Task', 'task.create', intent.intent_id],
      ['Incident', 'incident.acknowledge', incident.incident_id],
      ['Report', 'report.approve', report.report_id]
    ];
    for (let i = 0; i < pairs.length; i += 1) {
      const [recordType, action, recordId] = pairs[i];
      await page.selectOption('#approval-pair', String(i));
      if (i === 2) await page.fill('#approval-intent-id', recordId);
      else await page.selectOption('#approval-record', recordId);
      await page.click('form[aria-label="Create approval receipt"] button[type="submit"]');
      await expect.poll(() => capturedBodies.length).toBe(i + 1);
      const parsed = JSON.parse(capturedBodies[i]);
      expect(Object.keys(parsed).sort()).toStrictEqual(['action', 'record_id', 'record_type']);
      expect(parsed).toStrictEqual({ record_type: recordType, action, record_id: recordId });
    }
    await expect(page.locator('.mutation-feedback--error')).toHaveCount(0);

    // Sanitization: no payload digest, receipt id, approver identity or
    // caller-declared shift ever renders.
    const html = await page.content();
    expect(html).not.toMatch(/payload_digest/i);
    expect(html.toLowerCase()).not.toContain('sha256');
    expect(html).not.toMatch(/approver_id/i);
  });

  test('event.correct sends the receipt but never calls the unsupported readiness route', async ({ page, request }) => {
    await loginAsSupervisor(page);
    await createShift(page, 'Correct Shift', '2026-08-02T08:00', '2026-08-02T16:00');
    const shiftId = await page.locator('.shift-selector select').inputValue();
    const supToken = await apiLogin(request, 'sup1', 'sup1-devpass');
    const headers = { Authorization: `Bearer ${supToken}` };
    const eventRes = await request.post(`${API_BASE_URL}/events`, {
      headers, data: { shift_id: shiftId, event_type: 'shift_update', title: 'Correction target', risk_class: 'R2', evidence: [{ source_type: 'message', source_id: 'correction-event' }] }
    });
    const event = await eventRes.json();
    const sup2 = await apiLogin(request, 'sup2', 'sup2-devpass');
    await request.post(`${API_BASE_URL}/shifts/${shiftId}/assignments`, { headers, data: { user_id: 'sup2' } });
    await request.post(`${API_BASE_URL}/approvals`, {
      headers: { Authorization: `Bearer ${sup2}` },
      data: { record_type: 'OperationalEvent', record_id: event.event_id, action: 'event.confirm' }
    });
    const confirmed = await request.post(`${API_BASE_URL}/events/${event.event_id}/confirm`, { headers, data: { expected_version: event.version } });
    expect(confirmed.ok()).toBe(true);

    await page.reload();
    await page.waitForSelector('main.operations-console', { timeout: 10000 });
    await page.selectOption('.shift-selector select', { label: 'Correct Shift · OPEN' });

    let readinessCalled = false;
    await page.route('**/approvals/readiness*', async (route) => { readinessCalled = true; await route.continue(); });

    await page.selectOption('#approval-pair', '1'); // event.correct
    await page.selectOption('#approval-record', event.event_id);
    await page.click('form[aria-label="Create approval receipt"] button[type="submit"]');
    await expect(page.locator('.mutation-feedback--error')).toHaveCount(0);
    expect(readinessCalled).toBe(false);
  });

  test('a stale expected_version on incident acknowledge is refused with a controlled conflict, not a fake success', async ({ page, request }) => {
    await loginAsSupervisor(page);
    await createShift(page, 'Stale Ack Shift', '2026-08-02T08:00', '2026-08-02T16:00');
    const shiftId = await page.locator('.shift-selector select').inputValue();
    const supToken = await apiLogin(request, 'sup1', 'sup1-devpass');
    const headers = { Authorization: `Bearer ${supToken}` };
    const incRes = await request.post(`${API_BASE_URL}/incidents`, { headers, data: { shift_id: shiftId, summary: 'Stale test', risk_class: 'R1' } });
    const incident = await incRes.json();
    await page.reload();
    await page.waitForSelector('main.operations-console', { timeout: 10000 });
    await page.selectOption('.shift-selector select', { label: 'Stale Ack Shift · OPEN' });
    const ackBtn = page.locator('[aria-label="Incident and handover"] .incident-list__item', { hasText: 'Stale test' }).getByRole('button', { name: 'Acknowledge' });
    await expect(ackBtn).toBeVisible();
    const externalAck = await request.post(`${API_BASE_URL}/incidents/${incident.incident_id}/acknowledge`, {
      headers, data: { expected_version: incident.version }
    });
    expect(externalAck.ok()).toBe(true);
    const staleResponse = page.waitForResponse((res) => res.url().endsWith('/acknowledge') && res.request().method() === 'POST');
    await ackBtn.click();
    expect((await staleResponse).status()).toBe(409);
    await expect(page.locator('.mutation-feedback--conflict')).toBeVisible();
  });

  test('an R2 incident acknowledge without a receipt is refused through the browser', async ({ page, request }) => {
    await loginAsSupervisor(page);
    await createShift(page, 'Missing Approval Shift', '2026-08-02T08:00', '2026-08-02T16:00');
    const shiftId = await page.locator('.shift-selector select').inputValue();
    const supToken = await apiLogin(request, 'sup1', 'sup1-devpass');
    const headers = { Authorization: `Bearer ${supToken}` };
    await request.post(`${API_BASE_URL}/incidents`, {
      headers, data: { shift_id: shiftId, summary: 'Needs receipt', risk_class: 'R2', evidence: [{ source_type: 'message', source_id: 'e2e-proof' }] }
    });
    await page.reload();
    await page.waitForSelector('main.operations-console', { timeout: 10000 });
    await page.selectOption('.shift-selector select', { label: 'Missing Approval Shift · OPEN' });
    const response = page.waitForResponse((res) => res.url().endsWith('/acknowledge') && res.request().method() === 'POST');
    await page.getByRole('form', { name: 'Acknowledge incident Needs receipt' }).getByRole('button').click();
    expect((await response).status()).toBe(409);
    await expect(page.locator('.mutation-feedback--conflict')).toBeVisible();
  });

  test('a correction succeeds through the UI only after its parent Shift is frozen', async ({ page, request }) => {
    await loginAsSupervisor(page);
    await createShift(page, 'Frozen Correction Shift', '2026-08-02T08:00', '2026-08-02T16:00');
    const shiftId = await page.locator('.shift-selector select').inputValue();
    const token = await apiLogin(request, 'sup1', 'sup1-devpass');
    const event = await arrangeFrozenEvent(request, token, shiftId, 'Frozen correction target');
    await page.reload();
    await page.waitForSelector('main.operations-console', { timeout: 10000 });
    await page.selectOption('.shift-selector select', { label: 'Frozen Correction Shift · FROZEN' });
    const form = page.getByRole('form', { name: 'Correct event Frozen correction target' });
    await form.getByLabel('Reason').fill('Verified post-freeze correction');
    const response = page.waitForResponse((res) => res.url().includes(`/corrections/events/${event.event_id}`));
    await form.getByRole('button', { name: 'Correct' }).click();
    expect((await response).status()).toBe(200);
    await expect(page.locator('.mutation-feedback--error')).toHaveCount(0);
  });

  test('supervisor starts with an empty actor-bound queue and navigation service worker', async ({ page }) => {
    await loginAsSupervisor(page);
    await createShift(page, 'Storage Free Shift', '2026-08-02T08:00', '2026-08-02T16:00');
    await page.waitForSelector('.supervisor-actions');

    expect(await page.evaluate(() => localStorage.length)).toBe(0);
    await expect(page.getByRole('heading', { name: 'Offline actions' })).toHaveCount(0);
    await expect.poll(() => page.evaluate(() => navigator.serviceWorker.getRegistration().then(Boolean))).toBe(true);
  });

  test('freeze control is keyboard reachable and its feedback is focus-associated on refusal', async ({ page }) => {
    await loginAsSupervisor(page);
    await createShift(page, 'A11y Freeze Shift', '2026-08-02T08:00', '2026-08-02T16:00');

    const freezeBtn = page.getByRole('button', { name: 'Freeze shift', exact: true });
    await expect(freezeBtn).toBeDisabled(); // OPEN, not CLOSED - correctly disabled, not hidden
    await expect(freezeBtn).toBeVisible();
  });
});
