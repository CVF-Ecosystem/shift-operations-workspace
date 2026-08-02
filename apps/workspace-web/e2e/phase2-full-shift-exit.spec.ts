import { expect, test } from '@playwright/test';
import { writeFile } from 'node:fs/promises';

import { API_BASE_URL, apiLogin, loginAsOperator, loginAsSupervisor } from './operator-flow-helpers';
import {
  AMBIGUOUS_MESSAGE, DESTINATION_NAME, EVENT_TITLE, SOURCE_NAME, TASK_TITLE,
  createEventAndTask, createFullShiftLineage, queueStorage, selectSource, staffBothShifts,
} from './phase2-full-shift-exit-helpers';

test.describe('Phase 2 full-shift exit evidence', () => {
  test('composes assignment, offline replay, polling, handover, Report and freeze in one lineage', async ({ page, context, request }) => {
    const { sourceId, destinationId } = await createFullShiftLineage(page);
    const createdTaskResponse = page.waitForResponse((response) => {
      const url = new URL(response.url());
      return response.request().method() === 'POST' && url.pathname === '/tasks' && response.ok();
    });
    const task = await createEventAndTask(page);
    const createdTask = await (await createdTaskResponse).json() as { task_id: string; version: number };

    type ObservedTaskGet = { order: number; tasks: Array<{ task_id: string; version: number; status: string }> };
    const successfulTaskGets: ObservedTaskGet[] = [];
    let responseOrder = 0;
    let replayResponseOrder = 0;
    page.on('response', async (response) => {
      const order = ++responseOrder;
      const url = new URL(response.url());
      if (response.request().method() === 'POST' && url.pathname.endsWith('/transition') && response.ok()) {
        replayResponseOrder = order;
      }
      if (response.request().method() === 'GET' && url.pathname === '/tasks' && response.ok()) {
        const body = await response.json().catch(() => null);
        if (Array.isArray(body)) successfulTaskGets.push({ order, tasks: body });
      }
    });

    let transitionPosts = 0;
    await page.route('**/tasks/*/transition', async (route) => {
      if (route.request().method() === 'POST') transitionPosts += 1;
      await route.continue();
    });
    await context.setOffline(true);
    await task.getByRole('button', { name: 'Update' }).click();
    await expect(page.getByText('Queued on this device.')).toBeVisible();
    expect(transitionPosts).toBe(0);
    const staged = await queueStorage(page);
    expect(staged).toHaveLength(1);
    const recordedCas = staged[0].expectedVersion;
    const successfulTaskGetsBeforeReconnect = successfulTaskGets.length;
    const replayResponse = page.waitForResponse((response) => {
      const url = new URL(response.url());
      return response.request().method() === 'POST' && url.pathname.endsWith('/transition') && response.ok();
    });
    await context.setOffline(false);
    await expect.poll(() => transitionPosts).toBe(1);
    const committedTask = await (await replayResponse).json() as { task_id: string; version: number; status: string };
    expect(committedTask.task_id).toBe(createdTask.task_id);
    expect(committedTask.status).toBe('IN_PROGRESS');
    await expect.poll(() => replayResponseOrder).toBeGreaterThan(0);
    await expect.poll(() => successfulTaskGets.length).toBeGreaterThan(successfulTaskGetsBeforeReconnect);
    await expect.poll(() => successfulTaskGets.some(({ order, tasks }) => order > replayResponseOrder && tasks.some((item) =>
      item.task_id === createdTask.task_id && item.version === committedTask.version && item.status === 'IN_PROGRESS',
    ))).toBe(true);
    await expect(task).toContainText('IN_PROGRESS');
    await expect.poll(async () => (await queueStorage(page)).length).toBe(0);
    expect(recordedCas).toBe(1);

    // The backend commits this same-lineage message, but the browser loses
    // the response. There is one request, no retry/queue, visible ambiguity,
    // then an explicit authoritative refresh reconciles the committed state.
    const messageForm = page.getByRole('form', { name: 'Append message' });
    await messageForm.getByLabel('Message text').fill(AMBIGUOUS_MESSAGE);
    let ambiguousPosts = 0;
    await page.route('**/messages', async (route) => {
      if (route.request().method() !== 'POST') { await route.continue(); return; }
      ambiguousPosts += 1;
      await route.fetch();
      await route.abort('connectionreset');
    });
    await messageForm.getByRole('button', { name: 'Send message' }).click();
    await expect(messageForm.locator('.mutation-feedback--locked')).toBeVisible();
    expect(await queueStorage(page)).toHaveLength(0);
    await page.waitForTimeout(750);
    expect(ambiguousPosts).toBe(1);
    await messageForm.getByRole('button', { name: 'Refresh' }).click();
    await expect(page.getByRole('list', { name: 'Message list' })).toContainText(AMBIGUOUS_MESSAGE);

    const supervisor = await context.newPage();
    await staffBothShifts(supervisor);
    await expect(page.locator('.shift-timeline')).not.toContainText(EVENT_TITLE);
    const event = supervisor.getByRole('list', { name: 'Event list' }).getByRole('listitem').filter({ hasText: EVENT_TITLE });
    await event.getByRole('button', { name: 'Confirm' }).click();
    await expect(page.locator('.shift-timeline')).toContainText(EVENT_TITLE, { timeout: 12000 });
    await expect(task).toContainText('IN_PROGRESS');

    const handoverForm = page.getByRole('form', { name: 'Create handover' });
    await handoverForm.getByLabel('Destination shift').selectOption({ label: DESTINATION_NAME });
    await handoverForm.getByRole('button', { name: 'Create handover' }).click();
    const review = supervisor.getByRole('list', { name: 'Handovers awaiting review' }).getByRole('listitem');
    await expect(review).toContainText(`${sourceId} → ${destinationId}`);
    await review.getByRole('button', { name: 'Review' }).click();

    const receiver = await context.newPage();
    await loginAsSupervisor(receiver, 'sup2', 'sup2-devpass');
    await selectSource(receiver);
    const acknowledge = receiver.getByRole('list', { name: 'Handovers awaiting acknowledgement' }).getByRole('listitem');
    await expect(acknowledge).toContainText(`${sourceId} → ${destinationId}`);
    await acknowledge.getByRole('button', { name: 'Acknowledge' }).click();
    await expect(receiver.getByRole('list', { name: 'Handovers awaiting acknowledgement' }).getByRole('listitem')).toHaveCount(0);

    await page.getByRole('button', { name: `Close shift ${SOURCE_NAME}` }).click();
    await expect(page.locator('.shift-selector select')).toHaveValue(sourceId);
    const reportPanel = page.getByRole('region', { name: 'End-shift report' });
    await reportPanel.getByRole('button', { name: 'Generate report' }).click();
    await reportPanel.getByRole('button', { name: 'Submit for review' }).click();
    await expect(reportPanel).toContainText('IN_REVIEW');

    await receiver.reload();
    await receiver.waitForSelector('main.operations-console');
    await selectSource(receiver, 'CLOSED');
    const receiptForm = receiver.getByRole('form', { name: 'Create approval receipt' });
    await receiptForm.getByLabel('Target pair').selectOption({ label: 'Report approve' });
    await receiptForm.getByLabel('Record').selectOption({ label: 'Report 1' });
    await receiptForm.getByRole('button', { name: 'Create approval receipt' }).click();

    await supervisor.reload();
    await supervisor.waitForSelector('main.operations-console');
    await selectSource(supervisor, 'CLOSED');
    await supervisor.getByRole('form', { name: 'Approve report' }).getByRole('button', { name: 'Approve report' }).click();
    await supervisor.getByRole('form', { name: 'Freeze shift' }).getByRole('button', { name: 'Freeze shift' }).click();
    await expect(supervisor.locator('.shift-selector select')).toHaveValue(sourceId);
    await expect(supervisor.locator('.shift-selector select option:checked')).toContainText('FROZEN');

    // Observation-only API reads: no positive action is substituted here.
    const opToken = await apiLogin(request, 'op1', 'op1-devpass');
    const headers = { Authorization: `Bearer ${opToken}` };
    const shifts = await (await request.get(`${API_BASE_URL}/shifts`, { headers })).json();
    const source = shifts.find((item: { shift_id: string }) => item.shift_id === sourceId);
    expect(new Date(source.ends_at).getTime() - new Date(source.starts_at).getTime()).toBe(12 * 60 * 60 * 1000);
    expect(source.status).toBe('FROZEN');
    const tasks = await (await request.get(`${API_BASE_URL}/tasks`, { headers, params: { shift_id: sourceId } })).json();
    expect(tasks.find((item: { title: string }) => item.title === TASK_TITLE).status).toBe('IN_PROGRESS');
    const handovers = await (await request.get(`${API_BASE_URL}/handovers`, { headers, params: { from_shift_id: sourceId } })).json();
    expect(handovers[0].status).toBe('ACKNOWLEDGED');
    expect(handovers[0].items.length).toBeGreaterThan(0);
    await expect.poll(async () => (await queueStorage(page)).length).toBe(0);

    const runId = process.env.PHASE2_BROWSER_EVIDENCE_RUN_ID;
    const assertionPath = process.env.PHASE2_BROWSER_ASSERTION_PATH;
    if (runId && assertionPath) {
      await writeFile(assertionPath, `${JSON.stringify({
        schema_version: 1,
        producer_id: 'phase2-full-shift-exit-playwright-v1',
        run_id: runId,
        browser_contract: {
          positive_actions: 'rendered_ui',
          transport_requests: ambiguousPosts,
          automatic_retries: Math.max(0, ambiguousPosts - 1),
          queue_insertions: (await queueStorage(page)).length,
          authoritative_reconciliation: true,
        },
        task_reconciliation: {
          fresh_get_after_replay: successfulTaskGets.some(({ order }) => order > replayResponseOrder),
          exact_task_id: committedTask.task_id === createdTask.task_id,
          exact_committed_version: successfulTaskGets.some(({ order, tasks }) => order > replayResponseOrder && tasks.some((item) => item.task_id === createdTask.task_id && item.version === committedTask.version)),
          status_in_progress: committedTask.status === 'IN_PROGRESS',
          dom_after_get: true,
        },
      })}\n`, { encoding: 'utf8', flag: 'wx' });
    }
    await receiver.close();
    await supervisor.close();
  });
});
