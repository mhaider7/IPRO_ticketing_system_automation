// Run with a live server at HAWK_BASE_URL (default http://127.0.0.1:8000).
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');

(async () => {
  const browser = await chromium.launch({ headless: true, ...(process.env.HAWK_BROWSER_CHANNEL ? { channel: process.env.HAWK_BROWSER_CHANNEL } : {}) });
  const baseURL = process.env.HAWK_BASE_URL || 'http://127.0.0.1:8000';
  const screenshots = process.env.HAWK_SCREENSHOT_DIR || path.join(__dirname, '..', '.browser-output');
  await fs.mkdir(screenshots, { recursive: true });
  const context = await browser.newContext({ viewport: { width: 1366, height: 900 }, permissions: ['clipboard-read', 'clipboard-write'] });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  async function send(text) {
    await page.locator('#message').fill(text);
    await page.locator('#send').click();
    await page.waitForFunction(() => !document.getElementById('message').disabled);
  }
  async function reset() { await page.locator('#reset').click(); }
  try {
    await page.goto(baseURL);
    await page.locator('#launcher').click();
    await send('My Wi-Fi will not connect');
    assert.match(await page.locator('#messages').innerText(), /Test response:.*Wi-Fi/);
    await send('It still does that on my phone');
    assert.equal(await page.locator('.user').count(), 2);
    await page.locator('#close').click();
    await page.locator('#launcher').click();
    assert.equal(await page.locator('.user').count(), 2);
    await page.locator('#escalate').click();
    await page.locator('.email').waitFor();
    assert.match(await page.locator('.email textarea').inputValue(), /still does that/);
    await page.locator('.copy').click();
    await page.waitForFunction(() => document.querySelector('.copy-status').textContent.startsWith('Copied.'));
    assert.match(await page.evaluate(() => navigator.clipboard.readText()), /Subject: OTS Support Request: Wi-Fi/);
    await page.screenshot({ path: path.join(screenshots, 'hawk-desktop.png') });

    await reset();
    await page.locator('#escalate').click();
    await page.waitForFunction(() => document.querySelector('#messages').textContent.includes('What problem would you like OTS'));
    await send('Wi-Fi fails on a fictional laptop');
    await page.locator('.email').waitFor();
    assert.equal(await page.locator('.email').count(), 1);

    for (const trigger of ['What is my ticket status?', 'Can you predict the weather?', 'I want to talk to a technician']) {
      await reset();
      await send(trigger);
      if (await page.locator('.email').count() === 0) await send('skip');
      await page.locator('.email').waitFor();
    }

    await reset();
    let fail = true;
    const failure = async route => fail ? route.abort() : route.continue();
    await page.route('**/api/chat', failure);
    await page.locator('#message').fill('Printing on campus');
    await page.locator('#send').click();
    await page.locator('#retry').waitFor();
    assert.equal(await page.locator('.user').count(), 1);
    fail = false;
    await page.locator('#retry').click();
    await page.waitForFunction(() => !document.getElementById('message').disabled);
    assert.equal(await page.locator('.user').count(), 1);
    await page.unroute('**/api/chat', failure);

    // An in-flight response must not reappear after New chat.
    await reset();
    let release;
    let started;
    const entered = new Promise(resolve => { started = resolve; });
    const gate = new Promise(resolve => { release = resolve; });
    const delayed = async route => { started(); await gate; await route.fulfill({ json: { reply: 'STALE RESPONSE', sources: [], escalate: false, escalation_reason: null } }).catch(() => {}); };
    await page.route('**/api/chat', delayed);
    await page.locator('#message').fill('Wi-Fi fails');
    await page.locator('#send').click();
    await entered;
    await reset();
    release();
    await page.unrouteAll({ behavior: 'wait' });
    assert.equal(await page.locator('.user').count(), 0);
    assert.doesNotMatch(await page.locator('#messages').innerText(), /STALE RESPONSE/);

    // Server outage on escalation can be retried without duplicating a student message.
    let escalationFail = true;
    await page.route('**/api/escalate', route => escalationFail ? route.fulfill({ status: 503, json: { detail: 'Draft service unavailable. Please try again.' } }) : route.continue());
    await page.locator('#escalate').click();
    await page.locator('#retry').waitFor();
    escalationFail = false;
    await page.locator('#retry').click();
    await page.waitForFunction(() => !document.getElementById('message').disabled);
    await send('My Wi-Fi fails on a fictional laptop at the library');
    await page.locator('.email').waitFor();
    await page.unrouteAll({ behavior: 'wait' });

    // Clipboard denial still leaves a selectable, editable draft.
    await page.evaluate(() => { navigator.clipboard.writeText = () => Promise.reject(new Error('denied')); });
    await page.locator('.copy').click();
    await page.waitForFunction(() => document.querySelector('.copy-status').textContent.startsWith('Clipboard unavailable.'));
    for (const width of [390, 320]) {
      await page.setViewportSize({ width, height: 844 });
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
      assert.equal(await page.evaluate(() => document.getElementById('chat').getBoundingClientRect().right <= innerWidth), true);
    }
    await page.screenshot({ path: path.join(screenshots, 'hawk-mobile.png') });
    await page.reload();
    await page.locator('#launcher').click();
    assert.equal(await page.locator('.user').count(), 0);
    assert.deepEqual(errors, []);
    console.log('PASS: chat, follow-up, all escalation triggers, clarification, copy/fallback, retries, reset race, mobile layout, reload privacy; no uncaught browser errors.');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
