/* Phase 4 growth assets: social headers, Discord set, schedule graphics,
   lower thirds. Same visual language as the channel screens. */
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const B = path.resolve(__dirname, '..');
const read = p => fs.readFileSync(path.join(B, p), 'utf8');
const b64 = p => 'data:image/png;base64,' + fs.readFileSync(path.join(B, p)).toString('base64');
const LOCKUP = read('lockup/lockup-stacked-ondark-redforge-neutral.svg');
const LOCKUP_INLINE = read('lockup/lockup-inline-ondark-redforge-neutral.svg');
const MARK = read('mark/mark-full-ondark-tight.svg');
const PLATE = b64('mascot/mascot-plate.png');

const CSS = `
 @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;600;700&display=swap');
 *{margin:0;padding:0;box-sizing:border-box}
 body{margin:0;font-family:'Chakra Petch',sans-serif;color:#fff;background:transparent}
 .stage{position:relative;overflow:hidden}
 svg{max-width:100%;height:auto;display:block}
 .icon svg{width:100%}
 .ground{position:absolute;inset:0;background:
   radial-gradient(120% 90% at 20% 0%, #1A2027 0%, #0F1215 58%)}
 .shard{position:absolute;inset:0;z-index:0;background:
   linear-gradient(118deg, transparent 0 46%, rgba(214,35,37,.95) 46% 47.2%,
   transparent 47.2% 49.4%, rgba(214,35,37,.30) 49.4% 50.1%, transparent 50.1%)}
 .cap{font-weight:600;letter-spacing:.30em;color:#D62325;text-transform:uppercase}
 .rule{height:3px;background:linear-gradient(90deg,#D62325,rgba(214,35,37,0))}
 .muted{color:#9AA5AF;font-weight:400}
 .panel{background:rgba(17,21,26,.92);border-left:5px solid #D62325;border-radius:3px}
`;

const DAYS = ['MON','TUE','WED','THU','FRI','SAT','SUN'];

const A = {
 'social/header-3x1': { w:1500, h:500, html: s => `
   <div class="ground"></div><div class="shard"></div>
   <img src="${PLATE}" style="position:absolute;right:50px;bottom:0;height:104%;z-index:1;
        object-fit:contain;object-position:bottom">
   <div class="icon" style="position:absolute;left:60px;top:44%;transform:translateY(-50%);
        width:720px;z-index:3">${LOCKUP}</div>
   <div class="rule" style="position:absolute;left:60px;top:70%;width:240px;z-index:3"></div>
   <div class="cap" style="position:absolute;left:60px;top:76%;font-size:17px;z-index:3">Forged live</div>` },

 'discord/server-banner': { w:960, h:540, html: s => `
   <div class="ground"></div><div class="shard"></div>
   <img src="${PLATE}" style="position:absolute;right:24px;bottom:0;height:100%;z-index:1;
        object-fit:contain;object-position:bottom">
   <div class="icon" style="position:absolute;left:46px;top:42%;transform:translateY(-50%);
        width:470px;z-index:3">${LOCKUP}</div>
   <div class="rule" style="position:absolute;left:46px;top:66%;width:180px;z-index:3"></div>
   <div class="cap" style="position:absolute;left:46px;top:72%;font-size:14px;z-index:3">The forge</div>` },

 'social/schedule-square': { w:1080, h:1080, html: s => `
   <div class="ground"></div><div class="shard"></div>
   <div class="icon" style="position:absolute;left:62px;top:56px;width:420px;z-index:3">${LOCKUP_INLINE}</div>
   <div class="cap" style="position:absolute;left:62px;top:140px;font-size:22px;z-index:3">Weekly schedule</div>
   <div class="rule" style="position:absolute;left:62px;top:190px;width:300px;z-index:3"></div>
   ${DAYS.map((d,i) => `
     <div class="panel" style="position:absolute;left:62px;right:62px;top:${236 + i*112}px;height:92px;z-index:3">
       <div style="position:absolute;inset:0;display:flex;align-items:center;gap:26px;padding:0 26px">
         <div style="font-size:30px;font-weight:700;width:92px;flex:none">${d}</div>
         <div class="muted" style="font-size:22px">PLACEHOLDER &mdash; time</div>
       </div>
     </div>`).join('')}` },

 'social/schedule-story': { w:1080, h:1920, html: s => `
   <div class="ground"></div><div class="shard"></div>
   <div class="icon" style="position:absolute;left:70px;top:150px;width:520px;z-index:3">${LOCKUP_INLINE}</div>
   <div class="cap" style="position:absolute;left:70px;top:268px;font-size:26px;z-index:3">Weekly schedule</div>
   <div class="rule" style="position:absolute;left:70px;top:330px;width:340px;z-index:3"></div>
   ${DAYS.map((d,i) => `
     <div class="panel" style="position:absolute;left:70px;right:70px;top:${410 + i*150}px;height:122px;z-index:3">
       <div style="position:absolute;inset:0;display:flex;align-items:center;gap:30px;padding:0 30px">
         <div style="font-size:38px;font-weight:700;width:116px;flex:none">${d}</div>
         <div class="muted" style="font-size:27px">PLACEHOLDER &mdash; time</div>
       </div>
     </div>`).join('')}` },

 'social/lower-third': { w:1280, h:240, transparent:true, html: s => `
   <div class="panel" style="position:absolute;left:0;top:40px;width:900px;height:160px"></div>
   <div style="position:absolute;left:34px;top:40px;height:160px;display:flex;align-items:center;gap:22px;z-index:3">
     <div class="icon" style="width:96px;flex:none">${MARK}</div>
     <div>
       <div style="font-size:40px;font-weight:700;line-height:1.05">PLACEHOLDER</div>
       <div class="muted" style="font-size:20px;letter-spacing:.08em">PLACEHOLDER &mdash; role or handle</div>
     </div>
   </div>` },
};

(async () => {
  const only = process.argv[2];
  const browser = await chromium.launch();
  for (const [name, a] of Object.entries(A)) {
    if (only && name !== only) continue;
    const page = await browser.newPage({ viewport: { width: a.w, height: a.h }, deviceScaleFactor: 1 });
    await page.setContent(`<style>${CSS}</style><div class="stage" style="width:${a.w}px;height:${a.h}px">${a.html(a)}</div>`);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(800);
    const out = path.join(B, name + '.png');
    fs.mkdirSync(path.dirname(out), { recursive: true });
    await page.screenshot({ path: out, omitBackground: !!a.transparent,
                            clip: { x:0, y:0, width:a.w, height:a.h } });
    console.log(`  ${name}  ${a.w}x${a.h}`);
    await page.close();
  }
  await browser.close();
})();
