/* Alert frames. Transparent PNGs; the alert widget overlays the live
   username/amount on the slots. Sound is sourced separately. */
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const B = path.resolve(__dirname, '..');
const b64 = p => 'data:image/png;base64,' + fs.readFileSync(path.join(B, p)).toString('base64');
const read = p => fs.readFileSync(path.join(B, p), 'utf8');
const MARK = read('mark/mark-full-ondark-tight.svg');
const P = n => b64('mascot/poses/pose-' + n + '.png');

const CSS = `
 @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;600;700&display=swap');
 *{margin:0;padding:0;box-sizing:border-box}
 body{background:transparent;font-family:'Chakra Petch',sans-serif;color:#fff}
 .stage{position:relative;overflow:hidden}
 .panel{position:absolute;left:300px;right:0;top:46px;bottom:46px;
   background:rgba(17,21,26,.92);border-left:5px solid #D62325;border-radius:3px;
   box-shadow:0 4px 26px rgba(0,0,0,.55)}
 .mascot{position:absolute;left:0;bottom:0;z-index:2;object-fit:contain;object-position:bottom}
 .body{position:absolute;left:336px;right:28px;top:50%;transform:translateY(-50%);z-index:3}
 .cap{font-size:17px;font-weight:600;letter-spacing:.30em;color:#D62325;text-transform:uppercase}
 .who{font-size:44px;font-weight:700;line-height:1.1;margin-top:8px;
      white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
 .sub{font-size:19px;color:#9AA5AF;margin-top:8px}
 .icon{position:absolute;right:20px;top:62px;width:40px;z-index:3}
 .icon svg{width:100%;height:auto;display:block}
`;

const A = {
 'alert-follow':    { pose:'wave-2',      cap:'New follower',   sub:'Welcome to the forge' },
 'alert-sub':       { pose:'celebrate-2', cap:'New sub',        sub:'Thanks for the support' },
 'alert-resub':     { pose:'celebrate-2', cap:'Resub',          sub:'PLACEHOLDER — months' },
 'alert-giftsub':   { pose:'celebrate-3', cap:'Gifted subs',    sub:'PLACEHOLDER — count' },
 'alert-bits':      { pose:'celebrate-1', cap:'Cheer',          sub:'PLACEHOLDER — bits' },
 'alert-tip':       { pose:'celebrate-1', cap:'Tip',            sub:'PLACEHOLDER — amount' },
 'alert-raid':      { pose:'celebrate-2', cap:'Raid',           sub:'PLACEHOLDER — raiders', big:true },
 'alert-ytmember':  { pose:'celebrate-3', cap:'New member',     sub:'YouTube' },
 'alert-kicksub':   { pose:'celebrate-2', cap:'New sub',        sub:'Kick' },
};

(async () => {
  const only = process.argv[2];
  const browser = await chromium.launch();
  for (const [name, a] of Object.entries(A)) {
    if (only && name !== only) continue;
    const W = 920, H = a.big ? 460 : 420;
    const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
    await page.setContent(`<style>${CSS}</style>
      <div class="stage" style="width:${W}px;height:${H}px">
        <div class="panel"></div>
        <img class="mascot" src="${P(a.pose)}" style="height:${a.big ? 100 : 94}%">
        <div class="icon">${MARK}</div>
        <div class="body">
          <div class="cap">${a.cap}</div>
          <div class="who">PLACEHOLDER</div>
          <div class="sub">${a.sub}</div>
        </div>
      </div>`);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(700);
    await page.screenshot({ path: path.join(B, 'alerts', name + '.png'), omitBackground: true,
                            clip: { x:0, y:0, width:W, height:H } });
    console.log(`  ${name}  ${W}x${H}  (${a.pose})`);
    await page.close();
  }
  await browser.close();
})();
