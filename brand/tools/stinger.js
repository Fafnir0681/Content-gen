/* Stinger transition: diagonal forge shards sweep across, cover the frame at
   the midpoint (the OBS transition point), then sweep off.
   Renders transparent PNG frames; encode to WebM VP9 alpha with ffmpeg. */
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const B = path.resolve(__dirname, '..');
const read = p => fs.readFileSync(path.join(B, p), 'utf8');
const LOCKUP = read('lockup/lockup-stacked-ondark-redforge-neutral.svg');

const W = 1920, H = 1080, FPS = 30, SECS = 1.6;
const FRAMES = Math.round(FPS * SECS);
const BANDS = 7, BW = 700, GAP = 430, TRAVEL = 5240;

function frameHTML(t) {
  // ease so the cover lands crisply and the exit accelerates
  const e = t < 0.5 ? 2*t*t : 1 - Math.pow(-2*t + 2, 2) / 2;
  const bands = Array.from({length: BANDS}, (_, i) => {
    const x = 1920 + i*GAP - e*TRAVEL;
    const red = (i === 3);
    return `<div style="position:absolute;top:-80px;height:${H+160}px;width:${BW}px;
      left:${x}px;transform:skewX(-18deg);
      background:${red ? '#D62325' : '#0F1215'};
      box-shadow:-10px 0 0 0 ${red ? '#0F1215' : '#D62325'}"></div>`;
  }).join('');
  // Lockup fades in approaching the cover, holds through the shard exit,
  // then fades out before the clip ends. It must not still be opaque on the
  // last frame or it hard-cuts over the newly revealed scene.
  let peak;
  if (t < 0.34)      peak = 0;
  else if (t < 0.50) peak = (t - 0.34) / 0.16;   // fade in
  else if (t < 0.86) peak = 1;                   // hold through the exit
  else               peak = Math.max(0, 1 - (t - 0.86) / 0.14); // fade out
  const lock = peak > 0.01
    ? `<div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%) scale(${0.94 + 0.06*peak});
         width:1100px;opacity:${peak.toFixed(3)};z-index:5">${LOCKUP}</div>` : '';
  return `<style>*{margin:0;padding:0;box-sizing:border-box}
    body{background:transparent;overflow:hidden}
    svg{width:100%;height:auto;display:block}</style>
    <div style="position:relative;width:${W}px;height:${H}px;overflow:hidden">${bands}${lock}</div>`;
}

(async () => {
  const out = path.join(B, '..', '.stinger-frames');
  fs.rmSync(out, { recursive: true, force: true });
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  for (let f = 0; f < FRAMES; f++) {
    const t = f / (FRAMES - 1);
    await page.setContent(frameHTML(t));
    await page.screenshot({ path: path.join(out, String(f).padStart(4,'0') + '.png'),
                            omitBackground: true, clip: { x:0, y:0, width:W, height:H } });
  }
  await browser.close();
  console.log(`  ${FRAMES} frames at ${FPS}fps (${SECS}s) -> ${out}`);
  console.log(`  transition point: frame ${Math.round(FRAMES/2)} = ${Math.round(SECS*500)}ms`);
})();
