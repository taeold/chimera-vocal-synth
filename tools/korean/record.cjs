// Frame-exact capture of a duet show: a virtual clock replaces the audio clock, performance.now and
// requestAnimationFrame, so frame k is the page at k/FPS seconds. Usage:
//   node record.cjs <show> <fps> <seconds|test> <outdir>
const { chromium } = require('/tmp/chimera-vocal-synth/node_modules/playwright-core');
const [show, fpsArg, secArg, outDir] = process.argv.slice(2);
const FPS = Number(fpsArg);
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5 });
  await p.addInitScript(() => {
    let vt = 0, perf = 1000;
    const queue = new Map(); let id = 0;
    window.requestAnimationFrame = (cb) => { queue.set(++id, cb); return id; };
    window.cancelAnimationFrame = (i) => queue.delete(i);
    performance.now = () => perf;
    Object.defineProperty(BaseAudioContext.prototype, 'currentTime', { get: () => vt });
    AudioContext.prototype.getOutputTimestamp = () => ({ contextTime: vt, performanceTime: perf });
    window.__step = (dt) => {
      vt += dt; perf += dt * 1000;
      const cbs = [...queue.values()]; queue.clear();
      for (const cb of cbs) cb(perf);
    };
  });
  const errs = [];
  p.on('pageerror', (e) => errs.push(String(e)));
  await p.goto(`http://127.0.0.1:8006/?show=${show}`);
  await p.waitForFunction(() => !document.body.innerText.includes('Loading the song'), null, { timeout: 60000 });
  for (let i = 0; i < 10; i++) await p.evaluate(() => window.__step(0.001));
  await p.getByRole('button', { name: /play/i }).first().click();
  const total = secArg === 'test' ? 0 : Number(secArg);
  const frames = secArg === 'test' ? [Math.round(3.6 * FPS)] : null;
  const n = frames ? frames[0] + 1 : Math.round(total * FPS);
  const t0 = Date.now();
  for (let k = 0; k < n; k++) {
    if (!frames || frames.includes(k)) await p.screenshot({ path: `${outDir}/f${String(k).padStart(5, '0')}.png` });
    await p.evaluate((dt) => window.__step(dt), 1 / FPS);
    if (!frames && k % 60 === 0) console.log(`frame ${k}/${n}  ${((Date.now() - t0) / 1000).toFixed(0)} s`);
  }
  console.log('errors:', errs, 'time on page:', await p.evaluate(() => document.querySelector('.duet-time')?.textContent));
  await b.close();
})();
