/* On-stream overlay components. Transparent PNGs sized per component,
   positioned in OBS. Same visual language as the channel screens:
   dark panel, red accent edge, Chakra Petch, mark where it earns a place. */
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const B = path.resolve(__dirname, '..');
const read = p => fs.readFileSync(path.join(B, p), 'utf8');
const MARK = read('mark/mark-full-ondark-tight.svg');
const LOCKUP_INLINE = read('lockup/lockup-inline-ondark-redforge-neutral.svg');

const CSS = `
 @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;600;700&display=swap');
 *{margin:0;padding:0;box-sizing:border-box}
 body{background:transparent;font-family:'Chakra Petch',sans-serif;color:#fff}
 .stage{position:relative;overflow:hidden}
 svg{max-width:100%;height:auto;display:block}
 .icon svg{width:100%}
 /* shared panel: dark glass with a red leading edge */
 .panel{position:absolute;inset:0;background:rgba(17,21,26,.90);
   border-left:5px solid #D62325;border-radius:3px;
   box-shadow:0 2px 18px rgba(0,0,0,.45)}
 .cap{font-size:13px;font-weight:600;letter-spacing:.30em;color:#D62325;text-transform:uppercase}
 .val{font-weight:700;letter-spacing:.01em}
 .muted{color:#9AA5AF;font-weight:400}
 .row{position:absolute;inset:0;display:flex;align-items:center;gap:16px;padding:0 20px}
`;

const C = {
 'nameplate': { w:640, h:112, html:`
   <div class="panel"></div>
   <div class="row">
     <div class="icon" style="width:72px;flex:none">${MARK}</div>
     <div style="min-width:0">
       <div class="val" style="font-size:30px;line-height:1.05">PLAYFORGE LABS</div>
       <div class="muted" style="font-size:15px;letter-spacing:.08em">PLACEHOLDER &mdash; @yourhandle</div>
     </div>
   </div>` },

 'chatbox': { w:400, h:660, html:`
   <div class="panel" style="border-left:5px solid #D62325"></div>
   <div style="position:absolute;left:0;right:0;top:0;height:60px;
        background:rgba(214,35,37,.12);border-bottom:1px solid rgba(214,35,37,.5)"></div>
   <div style="position:absolute;left:20px;top:21px"><span class="cap">Chat</span></div>
   <div class="icon" style="position:absolute;right:16px;top:14px;width:32px">${MARK}</div>` },

 'recent-events': { w:460, h:172, html:`
   <div class="panel"></div>
   <div style="position:absolute;left:20px;top:18px"><span class="cap">Latest</span></div>
   <div style="position:absolute;left:20px;top:52px">
     <div class="muted" style="font-size:14px;letter-spacing:.14em">FOLLOWER</div>
     <div class="val" style="font-size:26px">&mdash;</div>
   </div>
   <div style="position:absolute;left:250px;top:52px">
     <div class="muted" style="font-size:14px;letter-spacing:.14em">SUB</div>
     <div class="val" style="font-size:26px">&mdash;</div>
   </div>` },

 'goalbar-frame': { w:560, h:84, html:`
   <div class="panel"></div>
   <div style="position:absolute;left:20px;top:14px"><span class="cap">Goal</span></div>
   <div style="position:absolute;left:20px;right:20px;bottom:16px;height:16px;
        border:2px solid rgba(255,255,255,.28);border-radius:9px"></div>` },

 'goalbar-fill': { w:560, h:84, html:`
   <div style="position:absolute;left:22px;bottom:18px;width:516px;height:12px;
        background:#D62325;border-radius:7px"></div>` },

 'now-playing': { w:460, h:104, html:`
   <div class="panel"></div>
   <div class="row">
     <div style="width:40px;height:40px;flex:none;border:2px solid #D62325;border-radius:50%;
          display:grid;place-items:center;font-size:18px;color:#D62325">&#9834;</div>
     <div style="min-width:0">
       <div class="cap" style="font-size:11px">Now playing</div>
       <div class="val" style="font-size:19px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis">&mdash;</div>
     </div>
   </div>` },

 'socials-strip': { w:760, h:92, html:`
   <div class="panel"></div>
   <div class="row" style="gap:28px">
     <div style="width:190px;flex:none" class="icon">${LOCKUP_INLINE}</div>
     <div class="muted" style="font-size:17px;letter-spacing:.10em">PLACEHOLDER &mdash; @yourhandle</div>
   </div>` },

 'label-donate':   { w:320, h:70, label:'Donate' },
 'label-discord':  { w:320, h:70, label:'Discord' },
 'label-commands': { w:320, h:70, label:'!commands' },

 'gameplay-frame': { w:1920, h:1080, html:`
   <div style="position:absolute;inset:0;border:4px solid rgba(214,35,37,.55);border-radius:4px"></div>
   <div style="position:absolute;left:0;top:0;width:190px;height:4px;background:#D62325"></div>
   <div style="position:absolute;right:0;bottom:0;width:190px;height:4px;background:#D62325"></div>` },
};

function labelHTML(text) {
  return `<div class="panel"></div>
   <div class="row" style="gap:12px">
     <div class="icon" style="width:34px;flex:none">${MARK}</div>
     <div class="val" style="font-size:22px;letter-spacing:.06em">${text.toUpperCase()}</div>
   </div>`;
}

(async () => {
  const only = process.argv[2];
  const browser = await chromium.launch();
  for (const [name, c] of Object.entries(C)) {
    if (only && name !== only) continue;
    const page = await browser.newPage({ viewport: { width: c.w, height: c.h }, deviceScaleFactor: 1 });
    const inner = c.html !== undefined ? c.html : labelHTML(c.label);
    await page.setContent(`<style>${CSS}</style><div class="stage" style="width:${c.w}px;height:${c.h}px">${inner}</div>`);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(700);
    await page.screenshot({ path: path.join(B, 'overlay', name + '.png'), omitBackground: true,
                            clip: { x:0, y:0, width:c.w, height:c.h } });
    console.log(`  ${name}  ${c.w}x${c.h}`);
    await page.close();
  }
  await browser.close();
})();
