// Local render check for index.html. Not part of the site; run with:
//   NODE_PATH=$(npm root -g) node scripts/verify.js
//
// Set PW_CHROMIUM to a Chromium binary if Playwright's own download isn't on
// this machine (the CI image keeps one at /opt/pw-browsers/chromium); leave it
// unset to use whatever `npx playwright install chromium` put in place.
const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const errors = [];
  const launchOpts = process.env.PW_CHROMIUM ? { executablePath: process.env.PW_CHROMIUM } : {};
  const browser = await chromium.launch(launchOpts);

  for (const scheme of ['light', 'dark']) {
    const ctx = await browser.newContext({ colorScheme: scheme });
    const page = await ctx.newPage();
    page.on('console', m => { if (m.type() === 'error') errors.push(`[${scheme}] ${m.text()}`); });
    page.on('pageerror', e => errors.push(`[${scheme}] pageerror: ${e.message}`));

    await page.goto('file://' + path.resolve(__dirname, '..', 'index.html'));
    await page.waitForTimeout(400);

    const counts = await page.evaluate(() => ({
      qcards: document.querySelectorAll('.qcard').length,
      hits: document.querySelectorAll('.hit').length,
      watch: document.querySelectorAll('#watchList .watchcard').length,
      insufficient: document.querySelectorAll('#insufficientList .watchcard').length,
      tiles: document.querySelectorAll('.tile').length,
      historyRows: document.querySelectorAll('#historyTable tbody tr').length,
      navlinks: document.querySelectorAll('#navlinks a').length,
      bannerShown: !document.getElementById('banner').hidden,
      uncheckedFlags: document.querySelectorAll('.hit-foot .unchecked').length,
      notesLen: document.getElementById('notesBody').textContent.length,
      bodyBg: getComputedStyle(document.body).backgroundColor,
      horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth + 1,
    }));
    console.log(scheme, JSON.stringify(counts, null, 1));

    await page.screenshot({ path: `/tmp/fs_${scheme}.png`, fullPage: false });
    await ctx.close();
  }

  // mobile viewport check
  const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await ctx.newPage();
  await page.goto('file://' + path.resolve(__dirname, '..', 'index.html'));
  await page.waitForTimeout(300);
  const mobile = await page.evaluate(() => ({
    horizontalOverflow: document.documentElement.scrollWidth > window.innerWidth + 1,
    scrollWidth: document.documentElement.scrollWidth,
  }));
  console.log('mobile', JSON.stringify(mobile));
  await page.screenshot({ path: '/tmp/fs_mobile.png', fullPage: false });
  await ctx.close();

  await browser.close();
  if (errors.length) { console.log('FAIL', errors); process.exit(1); }
  console.log('PASS: no console/page errors');
})();
