const { chromium } = require('/tmp/chimera-vocal-synth/node_modules/playwright-core');
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ userAgent: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' });
  const p = await ctx.newPage();
  let done;
  const got = new Promise(r => (done = r));
  p.on('response', async r => { if (r.url().includes('get_proto.php')) { require('fs').writeFileSync('' + process.argv[3] + '', await r.body()); done(); } });
  await p.goto('https://onlinesequencer.net/' + process.argv[2] + '', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await Promise.race([got, p.waitForTimeout(40000)]);
  await b.close();
})();
