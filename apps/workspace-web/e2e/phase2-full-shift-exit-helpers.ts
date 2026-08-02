import { expect, type Page } from '@playwright/test';

import { createShift, loginAsOperator, loginAsSupervisor } from './operator-flow-helpers';

export const SOURCE_NAME = 'Phase2 Full Shift Source';
export const DESTINATION_NAME = 'Phase2 Full Shift Destination';
export const EVENT_TITLE = 'Full shift relay update';
export const TASK_TITLE = 'Full shift open work';
export const AMBIGUOUS_MESSAGE = 'Full shift ambiguous transport note';

export async function createFullShiftLineage(page: Page) {
  await loginAsOperator(page);
  await createShift(page, SOURCE_NAME, '2026-08-10T08:00', '2026-08-10T20:00');
  const sourceId = await page.locator('.shift-selector select').inputValue();
  await createShift(page, DESTINATION_NAME, '2026-08-10T20:00', '2026-08-11T08:00');
  const destinationId = await page.locator('.shift-selector select').inputValue();
  await page.selectOption('.shift-selector select', { label: `${SOURCE_NAME} · OPEN` });
  return { sourceId, destinationId };
}

export async function assignThroughStaffing(page: Page, shiftName: string, user: 'sup1' | 'sup2') {
  await page.selectOption('#staffing-shift', { label: `${shiftName} (OPEN)` });
  await page.selectOption('#staffing-user', { label: `${user} (shift_supervisor)` });
  await page.getByRole('form', { name: 'Assign user' }).getByRole('button', { name: 'Assign' }).click();
  await expect(page.getByRole('list', { name: 'Assignment history' }).getByRole('listitem').filter({ hasText: user })).toContainText('ACTIVE');
}

export async function staffBothShifts(page: Page) {
  await loginAsSupervisor(page, 'sup1', 'sup1-devpass');
  await expect(page.getByRole('form', { name: 'Choose staffing shift' })).toBeVisible();
  for (const shift of [SOURCE_NAME, DESTINATION_NAME]) {
    await assignThroughStaffing(page, shift, 'sup1');
    await assignThroughStaffing(page, shift, 'sup2');
  }
  await page.selectOption('.shift-selector select', { label: `${SOURCE_NAME} · OPEN` });
}

export async function createEventAndTask(page: Page) {
  const eventForm = page.getByRole('form', { name: 'Create event' });
  await eventForm.getByLabel('Title').fill(EVENT_TITLE);
  await eventForm.getByLabel('Event type').selectOption('shift_update');
  await eventForm.getByLabel('Risk class').selectOption('R0');
  await eventForm.getByRole('button', { name: 'Create event' }).click();
  // Operator projection intentionally omits unconfirmed events. The cleared
  // rendered form proves the real create action completed; sup1 observes the
  // exact unconfirmed event later through the supervisor collection.
  await expect(eventForm.getByLabel('Title')).toHaveValue('');

  const taskForm = page.getByRole('form', { name: 'Create task' });
  await taskForm.getByLabel('Title').fill(TASK_TITLE);
  await taskForm.getByLabel('Risk class').selectOption('R0');
  await taskForm.getByRole('button', { name: 'Create task' }).click();
  const task = page.locator('.task-list__item', { hasText: TASK_TITLE });
  await expect(task).toBeVisible();
  return task;
}

export async function queueStorage(page: Page): Promise<Array<{ state: string; expectedVersion: number }>> {
  return page.evaluate(() => {
    const key = Object.keys(localStorage).find((candidate) => candidate.startsWith('shiftops.offline.queue.v1.'));
    return key ? JSON.parse(localStorage.getItem(key) ?? '[]') : [];
  });
}

export async function selectSource(page: Page, status: 'OPEN' | 'CLOSED' | 'FROZEN' = 'OPEN') {
  await page.selectOption('.shift-selector select', { label: `${SOURCE_NAME} · ${status}` });
}
