/* Phase 5: vertical / TikTok assets at 1080x1920.
   Safe zone is the CONSERVATIVE UNION of conflicting third-party figures,
   because no source documents TikTok LIVE's interface directly:
     top 220  bottom 480  left 60  right 164
   -> usable rectangle 856 x 1220 at (60, 220).
   Everything that must be seen lives inside it. */
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const B = path.resolve(__dirname, '..');
const read = p => fs.readFileSync(path.join(B, p), 'utf8');
const b64 = p => 'data:image/png;base64,' + fs.readFileSync(path.join(B, p)).toString('base64');
const LOCKUP = read('lockup/lockup-stacked-ondark-redforge-neutral.svg');
const MARK = read('mark/mark-full-ondark-tight.svg');
const PLATE = b64('mascot/mascot-plate.png');

const W = 1080, H = 1920;
const SAFE = { x: 60, y: 220, w: 856, h: 1220 };

const CSS = `
 @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;600;700&display=swap');
 *{margin:0;padding:0;box-sizing:border-box}
 body{margin:0;font-family:'Chakra Petch',sans-serif;color:#fff;background:transparent}
 .stage{position:relative;overflow:hidden;width:${W}px;height:${H}px}
 svg{max-width:100%;height:auto;display:block}
 .icon svg{width:100%}
 .ground{position:absolute;inset:0;background:
   radial-gradient(110% 70% at 50% 28%, #1A2027 0%, #0F1215 62%)}
 .shard{position:absolute;inset:0;z-index:0;background:
   linear-gradient(160deg, transparent 0 44%, rgba(214,35,37,.95) 44% 45.4%,
   transparent 45.4% 47.6%, rgba(214,35,37,.30) 47.6% 48.3%, transparent 48.3%)}
 .cap{font-weight:600;letter-spacing:.30em;color:#D62325;text-transform:uppercase}
 .rule{height:4px;background:linear-gradient(90deg,#D62325,rgba(214,35,37,0))}
 .panel{background:rgba(17,21,26,.92);border-left:6px solid #D62325;border-radius:4px}
 .muted{color:#9AA5AF;font-weight:400}
 .guide{position:absolute;border:3px dashed rgba(0,229,255,.9);z-index:9}
 .blocked{position:absolute;background:rgba(214,35,37,.16);z-index:8}
`;

const scene = (label, guides) => `
  <div class="ground"></div><div class="shard"></div>
  <img src="${PLATE}" style="position:absolute;left:50%;transform:translateX(-50%);
       bottom:${H - (SAFE.y + SAFE.h)}px;height:${Math.round(SAFE.h*0.62)}px;z-index:1;
       object-fit:contain;object-position:bottom">
  <div class="icon" style="position:absolute;left:${SAFE.x + 20}px;top:${SAFE.y + 40}px;
       width:${SAFE.w - 40}px;z-index:3">${LOCKUP}</div>
  <div class="rule" style="position:absolute;left:${SAFE.x + 20}px;top:${SAFE.y + 300}px;
       width:${Math.round(SAFE.w*0.42)}px;z-index:3"></div>
  <div class="cap" style="position:absolute;left:${SAFE.x + 20}px;top:${SAFE.y + 340}px;
       font-size:40px;z-index:3">${label}</div>
  ${guides ? guideHTML() : ''}`;

function guideHTML() {
  return `
   <div class="blocked" style="left:0;top:0;width:${W}px;height:${SAFE.y}px"></div>
   <div class="blocked" style="left:0;top:${SAFE.y + SAFE.h}px;width:${W}px;height:${H - SAFE.y - SAFE.h}px"></div>
   <div class="blocked" style="left:0;top:${SAFE.y}px;width:${SAFE.x}px;height:${SAFE.h}px"></div>
   <div class="blocked" style="left:${SAFE.x + SAFE.w}px;top:${SAFE.y}px;width:${W - SAFE.x - SAFE.w}px;height:${SAFE.h}px"></div>
   <div class="guide" style="left:${SAFE.x}px;top:${SAFE.y}px;width:${SAFE.w}px;height:${SAFE.h}px"></div>
   <div class="cap" style="position:absolute;left:${SAFE.x + 14}px;top:${SAFE.y + SAFE.h - 54}px;
        font-size:24px;color:#00E5FF;z-index:10">Safe ${SAFE.w} x ${SAFE.h}</div>`;
}

const A = {
 'scene-starting':  { html: () => scene('Starting soon', false) },
 'scene-brb':       { html: () => scene('Be right back', false) },
 'scene-ending':    { html: () => scene('Thanks for watching', false) },
 'safe-zone-guide': { html: () => scene('Safe zone guide', true) },

 'overlay': { transparent:true, html: () => `
   <div class="panel" style="position:absolute;left:${SAFE.x}px;top:${SAFE.y}px;
        width:${SAFE.w}px;height:132px;z-index:3"></div>
   <div style="position:absolute;left:${SAFE.x + 26}px;top:${SAFE.y}px;height:132px;
        display:flex;align-items:center;gap:22px;z-index:4">
     <div class="icon" style="width:88px;flex:none">${MARK}</div>
     <div><div style="font-size:38px;font-weight:700;line-height:1.05">PLAYFORGE LABS</div>
     <div class="muted" style="font-size:20px">PLACEHOLDER &mdash; @yourhandle</div></div>
   </div>
   <div class="panel" style="position:absolute;left:${SAFE.x}px;top:${SAFE.y + SAFE.h - 120}px;
        width:${Math.round(SAFE.w*0.62)}px;height:120px;z-index:3"></div>
   <div style="position:absolute;left:${SAFE.x + 26}px;top:${SAFE.y + SAFE.h - 120}px;height:120px;
        display:flex;align-items:center;z-index:4">
     <div><div class="cap" style="font-size:18px">Latest</div>
     <div style="font-size:30px;font-weight:700">&mdash;</div></div>
   </div>` },

 'clip-template': { html: () => `
   <div class="ground"></div><div class="shard"></div>
   ${guideHTML()}
   <div style="position:absolute;left:${SAFE.x}px;top:${SAFE.y}px;width:${SAFE.w}px;height:200px;
        border:3px dashed rgba(214,35,37,.7);display:flex;align-items:center;justify-content:center;z-index:5">
     <span class="muted" style="font-size:30px;letter-spacing:.14em">HOOK TEXT</span></div>
   <div style="position:absolute;left:${SAFE.x}px;top:${SAFE.y + 230}px;width:${SAFE.w}px;
        height:${SAFE.h - 420}px;border:3px dashed rgba(255,255,255,.35);
        display:flex;align-items:center;justify-content:center;z-index:5">
     <span class="muted" style="font-size:30px;letter-spacing:.14em">CLIP</span></div>
   <div class="icon" style="position:absolute;left:${SAFE.x}px;top:${SAFE.y + SAFE.h - 150}px;
        width:300px;z-index:5">${MARK}</div>` },
};

(async () => {
  const browser = await chromium.launch();
  for (const [name, a] of Object.entries(A)) {
    const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
    await page.setContent(`<style>${CSS}</style><div class="stage">${a.html()}</div>`);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(800);
    await page.screenshot({ path: path.join(B, 'vertical', name + '.png'),
                            omitBackground: !!a.transparent, clip: { x:0, y:0, width:W, height:H } });
    console.log(`  vertical/${name}  ${W}x${H}`);
    await page.close();
  }
  await browser.close();
})();
