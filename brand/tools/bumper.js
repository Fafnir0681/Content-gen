/* Intro / outro bumper. Unlike the stinger this is NOT a transition: nothing
   shows through it, so it renders on an opaque ground and the lockup is the
   subject. Final frame doubles as a still end card. */
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const B = path.resolve(__dirname, '..');
const read = p => fs.readFileSync(path.join(B, p), 'utf8');
const LOCKUP = read('lockup/lockup-stacked-ondark-redforge-neutral.svg');

const W = 1920, H = 1080, FPS = 30, SECS = 4.0;
const FRAMES = Math.round(FPS * SECS);
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const ease = x => 1 - Math.pow(1 - x, 3);

function frameHTML(t) {
  // A: shards sweep across and cover        0.00 - 0.42
  // B: shards slide off, lockup arrives     0.42 - 0.62
  // C: hold, red rule draws                 0.62 - 1.00
  const sweep = clamp(t / 0.42, 0, 1);
  const clear = clamp((t - 0.42) / 0.20, 0, 1);
  const prog  = ease(sweep) * 0.55 + ease(clear) * 0.45;
  const bands = Array.from({length: 7}, (_, i) => {
    const x = 1920 + i*430 - prog*5240;
    const red = (i === 3);
    return `<div style="position:absolute;top:-80px;height:${H+160}px;width:700px;
      left:${x}px;transform:skewX(-18deg);
      background:${red ? '#D62325' : '#141A20'};
      box-shadow:-10px 0 0 0 ${red ? '#141A20' : '#D62325'}"></div>`;
  }).join('');

  const appear = clamp((t - 0.44) / 0.16, 0, 1);
  const scale = (0.90 + 0.10 * ease(appear)).toFixed(4);
  const rule  = clamp((t - 0.62) / 0.26, 0, 1);

  return `<style>*{margin:0;padding:0;box-sizing:border-box}
    body{margin:0;background:#0F1215;overflow:hidden}
    svg{width:100%;height:auto;display:block}</style>
    <div style="position:relative;width:${W}px;height:${H}px;overflow:hidden;
         background:radial-gradient(120% 90% at 50% 40%, #1A2027 0%, #0F1215 60%)">
      ${bands}
      <div style="position:absolute;left:50%;top:50%;
           transform:translate(-50%,-50%) scale(${scale});width:1180px;
           opacity:${appear.toFixed(3)};z-index:5">${LOCKUP}</div>
      <div style="position:absolute;left:50%;top:63%;transform:translateX(-50%);
           width:${(560*ease(rule)).toFixed(0)}px;height:3px;z-index:5;
           background:linear-gradient(90deg,#D62325,rgba(214,35,37,0))"></div>
    </div>`;
}

(async () => {
  const out = path.join(B, '..', '.bumper-frames');
  fs.rmSync(out, { recursive: true, force: true });
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  for (let f = 0; f < FRAMES; f++) {
    await page.setContent(frameHTML(f / (FRAMES - 1)));
    await page.screenshot({ path: path.join(out, String(f).padStart(4,'0') + '.png'),
                            clip: { x:0, y:0, width:W, height:H } });
  }
  await browser.close();
  console.log(`  ${FRAMES} frames at ${FPS}fps (${SECS}s) -> ${out}`);
})();
