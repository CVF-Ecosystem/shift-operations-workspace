// WO C3C-BUILD-REV-F5/REREV-F2: proves keyboard labels, aria-describedby/
// focus-to-error association, one-in-flight-submit (with real request
// counting), genuine transport lockout and the bounded P2-D connectivity UI.
import { expect, test } from '@playwright/test';
import { createShift, loginAsOperator } from './operator-flow-helpers';

test.describe('Operator Accessibility & Keyboard Flow', () => {
  test('verifies programmatic labels, aria attributes and keyboard navigation', async ({ page }) => {
    await loginAsOperator(page);

    await expect(page.locator('#create-shift-name')).toHaveAttribute('required', '');
    await expect(page.locator('.connection-indicator')).toHaveAttribute('role', 'status');

    await page.focus('#create-shift-name');
    await page.keyboard.press('Tab');
    await expect(page.locator('#create-shift-starts')).toBeFocused();
  });

  test('associates a failed submit with its feedback via aria-describedby and moves focus to it', async ({ page }) => {
    await loginAsOperator(page);
    await createShift(page, 'A11y Shift', '2026-08-01T08:00', '2026-08-01T16:00');

    // Trigger a real controlled 409: close the shift via a second session
    // first so this tab's stored expected_version is stale, then submit.
    const second = await page.context().newPage();
    await loginAsOperator(second);
    await second.selectOption('.shift-selector select', { label: 'A11y Shift · OPEN' });
    await second.click('button:has-text("Close shift")');
    // A closed shift no longer offers Close - wait for that button itself to
    // disappear rather than asserting on transient "Closing..." text, which
    // races the state update once the mutation actually resolves.
    await expect(second.locator('button:has-text("Close shift")')).toHaveCount(0);
    await second.close();

    const closeBtn = page.getByRole('button', { name: 'Close shift' });
    await closeBtn.click();

    const describedBy = await closeBtn.getAttribute('aria-describedby');
    expect(describedBy).toBeTruthy();
    // React's useId() ids (e.g. ":r1:") contain characters that are not
    // valid in a raw CSS id selector - use an attribute selector instead.
    const feedback = page.locator(`[id="${describedBy}"]`);
    await expect(feedback).toBeVisible();
    await expect(feedback).toHaveAttribute('role', 'alert');
    await expect(feedback).toBeFocused();
  });

  test('one-in-flight: two synchronous submit dispatches reach the hook, but the inFlight ref rejects the second - exactly one POST reaches FastAPI', async ({ page }) => {
    await loginAsOperator(page);
    await createShift(page, 'InFlight Shift', '2026-08-01T08:00', '2026-08-01T16:00');

    let messagePostCount = 0;
    await page.route('**/messages', async (route) => {
      if (route.request().method() === 'POST') messagePostCount += 1;
      await route.continue();
    });

    await page.fill('#msg-text', 'first message');
    const sendBtn = page.locator('form[aria-label="Append message"] button[type="submit"]');
    // A real native <button disabled> blocks a second browser click entirely
    // (Playwright force:true still cannot dispatch a click the browser
    // itself refuses), so to prove useMutationControl's own inFlight ref -
    // not merely the disabled attribute - dispatch two real form submit
    // events synchronously (no await between them) directly on the form
    // element, exactly what two near-simultaneous Enter-key submits would do.
    await page.locator('form[aria-label="Append message"]').evaluate((form: HTMLFormElement) => {
      form.requestSubmit();
      form.requestSubmit();
    });

    await expect(page.locator('.message-list__item')).toHaveCount(1);
    // The field clears itself on success, so the button is legitimately
    // disabled again by the empty-input guard, not by a stuck lock - assert
    // no error/locked feedback rendered instead of a bare not-disabled check.
    await expect(page.locator('.mutation-feedback')).toHaveCount(0);
    expect(messagePostCount).toBe(1);
  });

  test('outcome_unknown: a genuine browser transport failure locks the control with no auto-retry; only an explicit refresh that itself succeeds unlocks it, and no duplicate POST occurs', async ({ page, context }) => {
    await loginAsOperator(page);
    await createShift(page, 'Outage Shift', '2026-08-01T08:00', '2026-08-01T16:00');

    let messagePostCount = 0;
    await page.route('**/messages', async (route) => {
      if (route.request().method() === 'POST') messagePostCount += 1;
      await route.continue();
    });

    await page.fill('#msg-text', 'sent during outage');
    const sendBtn = page.locator('form[aria-label="Append message"] button[type="submit"]');

    // A real transport failure, not a mocked response: the browser context
    // itself goes offline so the actual fetch() throws.
    await context.setOffline(true);
    await sendBtn.click();

    const alert = page.locator('.mutation-feedback--locked');
    await expect(alert).toBeVisible();
    await expect(alert).toContainText('The outcome of this request could not be confirmed');
    await expect(sendBtn).toBeDisabled();

    // No automatic retry/queue while still offline: exactly the one honest
    // attempt was dispatched, and no repeat attempt follows on its own.
    await page.waitForTimeout(500);
    expect(messagePostCount).toBe(1);
    await expect(sendBtn).toBeDisabled();

    await context.setOffline(false);
    await page.click('.mutation-feedback__refresh-btn');

    // Unlock only after the real refresh (a genuine GET against FastAPI)
    // completes successfully - wait for the locked feedback to clear.
    await expect(alert).toHaveCount(0);
    await expect(sendBtn).not.toBeDisabled();
    // The original message send was never retried/queued - still exactly one attempt.
    expect(messagePostCount).toBe(1);
    await expect(page.locator('.message-list__item')).toHaveCount(0);
  });

  test('renders zero supervisor controls and truthful polling/PWA state', async ({ page }) => {
    await loginAsOperator(page);
    await createShift(page, 'Supervisor Free Shift', '2026-08-01T08:00', '2026-08-01T16:00');

    const forbidden = ['Confirm event', 'Freeze shift', 'Acknowledge incident', 'Approve report', 'Revoke approval'];
    for (const label of forbidden) {
      await expect(page.getByRole('button', { name: label })).toHaveCount(0);
    }

    await expect(page.getByRole('status').filter({ hasText: 'Polling sync:' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Offline actions' })).toHaveCount(0);
    await expect.poll(() => page.evaluate(() => 'serviceWorker' in navigator && navigator.serviceWorker.getRegistration().then(Boolean))).toBe(true);
  });
});
