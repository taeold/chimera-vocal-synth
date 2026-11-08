const { chromium } = require('/tmp/chimera-vocal-synth/node_modules/playwright-core');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' });
  const p = await ctx.newPage();
  for (const q of process.argv.slice(2)) {
    await p.goto('https://onlinesequencer.net/sequences?search=' + encodeURIComponent(q), { waitUntil: 'domcontentloaded', timeout: 60000 });
    for (let i = 0; i < 20 && (await p.title()).includes('moment'); i++) await p.waitForTimeout(1000);
    await p.waitForTimeout(1500);
    const hits = await p.evaluate(() => [...document.querySelectorAll('a[href]')]
      .map(a => [a.getAttribute('href'), a.textContent.trim()])
      .filter(([h, t]) => /^\/?\d{4,}$/.test(h.replace('https://onlinesequencer.net', '')) && t));
    console.log(`== ${q}: ${hits.length}`);
    for (const [h, t] of hits.slice(0, 12)) console.log('  ', h, '|', t.slice(0, 80));
  }
  await b.close();
})();
