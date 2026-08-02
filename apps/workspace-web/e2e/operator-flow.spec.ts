// WO C3C-BUILD-REV-F5/REREV-F2: exercises every R18 vertical against the
// real FastAPI backend on disposable SQLite. Each `page.request`/`request`
// call hits the live API directly (bypassing the UI) only to arrange state
// (e.g. a second shift, a stale version, or the C3d supervisor
// acknowledgement that is out of R18/operator scope); every operator ACTION
// under test is driven through the real rendered UI.
import { expect, test } from '@playwright/test';
import { apiLogin, API_BASE_URL, createShift, loginAsOperator } from './operator-flow-helpers';

test.describe('Operator UI Workflow (R18 verticals)', () => {
  test('creates a shift, selects it and verifies no offline queue storage', async ({ page }) => {
    await loginAsOperator(page);
    await createShift(page, 'E2E Test Shift', '2026-08-01T08:00', '2026-08-01T16:00');

    await page.fill('#msg-text', 'Operator E2E online check');
    await page.click('button:has-text("Send message")');
    await expect(page.locator('.message-list')).toContainText('Operator E2E online check');

    const queueContent = await page.evaluate(() => localStorage.getItem('shiftops.offline.queue'));
    expect(queueContent).toBeNull();
    expect(await page.evaluate(() => localStorage.length)).toBe(0);
  });

  test('creates an event with a bounded event_type, an R0 task with no approval step, and transitions it', async ({ page }) => {
    await loginAsOperator(page);
    await createShift(page, 'Event Task Shift', '2026-08-01T08:00', '2026-08-01T16:00');

    await page.fill('#event-title', 'Pump inspection');
    await page.selectOption('#event-type', 'equipment_downtime');
    await page.click('form[aria-label="Create event"] button[type="submit"]');
    await expect(page.locator('.mutation-feedback--error')).toHaveCount(0);

    await page.fill('#task-title', 'Routine check');
    await page.selectOption('#task-risk', 'R0');
    await page.click('form[aria-label="Create task"] button[type="submit"]');
    await expect(page.locator('.task-list__item')).toContainText('Routine check');

    await page.selectOption('[aria-label="Target status for Routine check"]', 'IN_PROGRESS');
    await page.click('[aria-label="Transition task Routine check"] button[type="submit"]');
    await expect(page.locator('.task-list__status')).toContainText('IN_PROGRESS');
  });

  test('an R3 task create requires approval and shows the bounded safe approval-needed notice, never a raw digest', async ({ page }) => {
    await loginAsOperator(page);
    await createShift(page, 'Approval Shift', '2026-08-01T08:00', '2026-08-01T16:00');

    await page.fill('#task-title', 'High risk work');
    await page.selectOption('#task-risk', 'R3');
    await page.click('form[aria-label="Create task"] button[type="submit"]');

    await expect(page.getByText('This task requires supervisor approval')).toBeVisible();
    const html = await page.content();
    expect(html).not.toMatch(/payload_digest/i);
    expect(html.toLowerCase()).not.toContain('sha256');
  });

  test('creates and transitions a CustomerRequest', async ({ page }) => {
    await loginAsOperator(page);
    await createShift(page, 'CR Shift', '2026-08-01T08:00', '2026-08-01T16:00');

    await page.fill('#cr-customer-id', 'cust-e2e-1');
    await page.fill('#cr-summary', 'Delayed shipment inquiry');
    await page.click('form[aria-label="Create customer request"] button[type="submit"]');
    await expect(page.locator('.cr-list__item')).toContainText('Delayed shipment inquiry');

    await page.click('.cr-list__item form button[type="submit"]');
    await expect(page.locator('.cr-list__status')).toContainText('ACKNOWLEDGED');
  });

  test('reports an incident and waits for supervisor acknowledgement before offering an operator transition', async ({ page }) => {
    await loginAsOperator(page);
    await createShift(page, 'Incident Shift', '2026-08-01T08:00', '2026-08-01T16:00');

    await page.fill('#inc-summary', 'Coolant leak');
    await page.selectOption('#inc-risk', 'R2');
    await page.click('form[aria-label="Report incident"] button[type="submit"]');

    await expect(page.locator('.incident-list__item')).toContainText('Coolant leak');
    await expect(page.getByText('Waiting for supervisor acknowledgement')).toBeVisible();
    await expect(page.locator('[aria-label="Target status for Coolant leak"]')).toHaveCount(0);
  });

  test('creates a handover between two operator-owned shifts', async ({ page }) => {
    await loginAsOperator(page);
    await createShift(page, 'Handover From', '2026-08-01T08:00', '2026-08-01T16:00');
    await createShift(page, 'Handover To', '2026-08-02T08:00', '2026-08-02T16:00');
    await page.selectOption('.shift-selector select', { label: 'Handover From · OPEN' });

    await page.selectOption('#handover-to-shift', { label: 'Handover To' });
    await page.click('form[aria-label="Create handover"] button[type="submit"]');
    await expect(page.locator('.mutation-feedback--error')).toHaveCount(0);
  });

  test('closes a shift with a bounded stale-version conflict, then generates, versions and submits its Report to IN_REVIEW', async ({ page }) => {
    await loginAsOperator(page);
    await createShift(page, 'Report Shift', '2026-08-01T08:00', '2026-08-01T16:00');

    // Bounded prerequisite conflict: a second tab closes the same shift
    // first, so this tab's in-memory expected_version is stale when it
    // submits close - proves the sanitized conflict path, not a fabricated one.
    const secondTab = await page.context().newPage();
    await loginAsOperator(secondTab);
    await secondTab.selectOption('.shift-selector select', { label: 'Report Shift · OPEN' });
    await secondTab.click('button:has-text("Close shift")');
    await expect(secondTab.locator('button:has-text("Close shift")')).toHaveCount(0);
    await secondTab.close();

    // WO C3C-BUILD-REREV-F1: conflict now auto-refreshes exactly once - no
    // manual click required to unlock. The bounded conflict feedback stays
    // visible with fresh values, and the shift is CLOSED (via the second
    // tab), so the Close shift control disappears once state settles.
    await page.click('button:has-text("Close shift")');
    const conflictAlert = page.locator('.mutation-feedback--conflict');
    await expect(conflictAlert).toBeVisible();
    await expect(conflictAlert).toContainText('This record changed elsewhere.');

    await expect(page.locator('button:has-text("Close shift")')).toHaveCount(0);

    // The shift is CLOSED now (via the second tab); Report generation
    // requires a CLOSED parent shift, so this must run after close.
    await page.click('button:has-text("Generate report")');
    await expect(page.locator('.report-meta')).toContainText('DRAFT');
    await expect(page.locator('.report-meta')).toContainText('1'); // version 1
    await expect(page.content().then((h) => h)).resolves.not.toMatch(/snapshot_digest/i);

    // WO C3C-BUILD-REREV-F2.1: successor version through the real UI - a
    // genuine POST /reports/{id}/versions, not a synthetic assertion.
    await page.click('button:has-text("Create new version")');
    await expect(page.locator('.report-meta')).toContainText('2'); // version 2
    await expect(page.locator('.report-meta')).toContainText('DRAFT');

    await page.click('button:has-text("Submit for review")');
    await expect(page.locator('.report-meta')).toContainText('IN_REVIEW');
    await expect(page.getByText('Approval is a supervisor action')).toBeVisible();
  });

  test('reports an incident, a real C3d supervisor acknowledgement unlocks the operator transition control, transitions to MITIGATING through the UI', async ({ page, request }) => {
    await loginAsOperator(page);
    await createShift(page, 'Incident Transition Shift', '2026-08-01T08:00', '2026-08-01T16:00');
    const shiftId = await page.locator('.shift-selector select').inputValue();

    // R1 (not R2+): the evidence policy (packages/cvf-application-profile/
    // evidence-policy.yaml) requires >=1 evidence link for R2+ before
    // acknowledge can succeed, which is unrelated to what this scenario
    // proves (the operator transition control unlocking after a real C3d
    // acknowledgement) - R1 keeps the scenario focused and deterministic.
    await page.fill('#inc-summary', 'Transformer overheating');
    await page.selectOption('#inc-risk', 'R1');
    await page.click('form[aria-label="Report incident"] button[type="submit"]');
    await expect(page.locator('.incident-list__item')).toContainText('Transformer overheating');
    await expect(page.locator('[aria-label="Target status for Transformer overheating"]')).toHaveCount(0);

    // Test arrangement only, never rendered/asserted as an operator control:
    // a real supervisor JWT assigns sup1 to the shift (required before
    // acknowledge is permitted), lists the real incident to get its
    // id/version, then genuinely calls the C3d-only acknowledge route.
    const supervisorToken = await apiLogin(request, 'sup1', 'sup1-devpass');
    const authHeaders = { Authorization: `Bearer ${supervisorToken}` };
    const assignRes = await request.post(`${API_BASE_URL}/shifts/${shiftId}/assignments`, {
      headers: authHeaders,
      data: { user_id: 'sup1' }
    });
    expect(assignRes.ok()).toBe(true);

    const incidentsRes = await request.get(`${API_BASE_URL}/incidents?shift_id=${shiftId}`, { headers: authHeaders });
    expect(incidentsRes.ok()).toBe(true);
    const incidents = (await incidentsRes.json()) as Array<{ incident_id: string; version: number; summary: string }>;
    const incident = incidents.find((i) => i.summary === 'Transformer overheating')!;

    const ackRes = await request.post(`${API_BASE_URL}/incidents/${incident.incident_id}/acknowledge`, {
      headers: authHeaders,
      data: { expected_version: incident.version }
    });
    expect(ackRes.ok()).toBe(true);

    // Refresh the operator UI (a real reload re-fetches all reads through
    // the same rendered app, exactly as an operator revisiting the shift
    // would) and prove the operator transition now appears for
    // ACKNOWLEDGED, offering only the operator-legal targets (never
    // ACKNOWLEDGE itself, never any C3d control).
    await page.reload();
    await page.waitForSelector('main.operations-console', { timeout: 10000 });
    await page.selectOption('.shift-selector select', { label: 'Incident Transition Shift · OPEN' });
    const targetSelect = page.locator('[aria-label="Target status for Transformer overheating"]');
    await expect(targetSelect).toBeVisible();
    const options = await targetSelect.locator('option').allTextContents();
    expect(options).toStrictEqual(['MITIGATING', 'RESOLVED']);
    await expect(page.getByRole('button', { name: 'Acknowledge incident' })).toHaveCount(0);

    await targetSelect.selectOption('MITIGATING');
    await page.click('[aria-label="Transition incident Transformer overheating"] button[type="submit"]');
    await expect(page.locator('.incident-list__status')).toContainText('MITIGATING');
  });
});
