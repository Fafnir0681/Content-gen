/* Render Phase 1 channel-page assets at exact platform dimensions.
   Everything composes from brand/ sources — no generation. */
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const B = path.resolve(__dirname, '..');
const read = p => fs.readFileSync(path.join(B, p), 'utf8');
const b64 = p => 'data:image/png;base64,' + fs.readFileSync(path.join(B, p)).toString('base64');

const LOCKUP = read('lockup/lockup-stacked-ondark-redforge-neutral.svg');
const LOCKUP_INLINE = read('lockup/lockup-inline-ondark-redforge-neutral.svg');
const MARK = read('mark/mark-full-ondark-tight.svg');
const LOCKUP_WHITE = read('lockup/lockup-stacked-ondark-neutral.svg');
const PLATE = b64('mascot/mascot-plate.png');
const BUST  = b64('mascot/mascot-bust.png');

const CSS = `
 @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;600;700&display=swap');
 *{margin:0;padding:0;box-sizing:border-box}
 body{font-family:'Chakra Petch',sans-serif;background:#0F1215;color:#fff;overflow:hidden}
 .stage{position:relative;overflow:hidden;background:
    radial-gradient(120% 90% at 18% 0%, #1A2027 0%, #0F1215 55%)}
 /* diagonal forge shard, echoes the glass sweep */
 .shard{position:absolute;inset:0;z-index:0;background:
    linear-gradient(118deg, transparent 0 38%, rgba(214,35,37,.95) 38% 39.1%,
    transparent 39.1% 41%, rgba(214,35,37,.30) 41% 41.7%, transparent 41.7%)}
 .shard-r{position:absolute;inset:0;z-index:0;background:
    linear-gradient(118deg, transparent 0 54%, rgba(214,35,37,.95) 54% 55.1%,
    transparent 55.1% 57%, rgba(214,35,37,.30) 57% 57.7%, transparent 57.7%)}
 .grain{position:absolute;inset:0;z-index:0;opacity:.05;background-image:
    repeating-linear-gradient(0deg,#fff 0 1px,transparent 1px 3px)}
 .plate{position:absolute;bottom:0;height:100%;object-fit:contain;object-position:bottom}
 .lock svg{display:block}
 .label{font-weight:600;letter-spacing:.42em;color:#D62325;text-transform:uppercase}
 .ph{color:#8A959F;font-weight:400}
 .zones{position:absolute;inset:0;display:flex;align-items:center;gap:1%}
 .zL{flex:1 1 54%;min-width:0;display:flex;flex-direction:column;align-items:flex-start}
 .zR{flex:0 0 42%;height:100%;display:flex;align-items:flex-end;justify-content:center;position:relative}
 .zR img{object-fit:contain;object-position:bottom;max-width:100%;display:block}
 .lock svg{width:100%;height:auto;display:block}
 .stage svg{max-width:100%;height:auto;display:block}
 .icon svg{width:100%;height:auto;display:block}
 .rule{margin-top:5%;margin-bottom:3.5%;height:2px;background:linear-gradient(90deg,#D62325,rgba(214,35,37,0))}
`;

const YT = { w:2560, h:1440, safeW:1546, safeH:423 };
const PANELS = ['About','Schedule','Rules','Specs','Commands','Support'];

const SCENES = {
 'scene-starting':  { w:1920, h:1080, fn:s => sceneLeft('Starting soon', s.w, s.h) },
 'scene-brb':       { w:1920, h:1080, fn:s => sceneLeft('Be right back', s.w, s.h) },
 'scene-technical': { w:1920, h:1080, fn:s => sceneLeft('Technical difficulties', s.w, s.h) },
 'scene-ending':    { w:1920, h:1080, fn:s => sceneLeft('Thanks for watching', s.w, s.h) },
 'twitch-offline': { w:1920, h:1080, custom:null, fn:s => screen16('Currently offline', true, s.w, s.h) },
 'kick-offline':   { w:1920, h:1080, fn:s => screen16('Stream ended', true, s.w, s.h) },
 'kick-banner':    { w:1920, h:1080, fn:s => screen16('Forged live', false, s.w, s.h) },
 'twitch-banner':  { w:1200, h:480,  fn:s => screenWide('Forged live', s.w, s.h) },
 'wide-live':      { w:1546, h:423,  fn:s => screenWide('Forged live', s.w, s.h) },
 'wide-offline':   { w:1546, h:423,  fn:s => screenWide('Currently offline', s.w, s.h) },
};

function panelHTML(title, w, h) {
  return `<div class="shard"></div>
   <div style="position:absolute;inset:0;display:flex;align-items:center;gap:${h*0.11}px;padding:0 ${h*0.14}px">
     <div class="icon" style="width:${h*0.46}px;flex:none">${MARK}</div>
     <div style="min-width:0">
       <div style="font-size:${h*0.19}px;font-weight:700;letter-spacing:.02em;line-height:1;white-space:nowrap">${title.toUpperCase()}</div>
       <div class="rule" style="width:${h*0.62}px;margin-top:${h*0.09}px;margin-bottom:0"></div>
     </div>
   </div>`;
}


/* Scene screens: mascot on the LEFT, type to his right.
   Same vertical rhythm and type treatment as the approved offline screen. */
function sceneLeft(label, w, h) {
  const k = w / 1920;
  return `
   <div class="shard-r"></div><div class="grain"></div>
   <img src="${PLATE}" style="position:absolute;left:${30*k}px;bottom:0;height:100%;
        object-fit:contain;object-position:bottom;z-index:2">
   <div class="lock" style="position:absolute;left:${880*k}px;top:40%;
        transform:translateY(-50%);width:${930*k}px;z-index:3">${LOCKUP_WHITE}</div>
   <div class="rule" style="position:absolute;left:${880*k}px;top:55%;width:${300*k}px;margin:0;z-index:3"></div>
   <div class="label" style="position:absolute;left:${880*k}px;top:62%;
        font-size:${62*k}px;font-weight:700;z-index:3">${label}</div>`;
}

function screen16(label, showPh, w, h) {
  const k = w / 1920;
  return `
   <div class="shard"></div><div class="grain"></div>
   <div class="lock" style="position:absolute;left:${130*k}px;top:40%;
        transform:translateY(-50%);width:${1382*k}px;z-index:3">${LOCKUP_WHITE}</div>
   <div class="rule" style="position:absolute;left:${130*k}px;top:55%;width:${330*k}px;margin:0;z-index:3"></div>
   ${showPh ? `<div class="ph" style="position:absolute;left:${130*k}px;top:59%;
        font-size:${34*k}px;line-height:1.7;color:#FFFFFF;z-index:3">
     <div>PLACEHOLDER &mdash; your schedule here</div>
     <div>PLACEHOLDER &mdash; @yourhandle</div></div>` : ''}
   <div class="label" style="position:absolute;left:${760*k}px;top:72%;
        font-size:${62*k}px;font-weight:700;z-index:3">${label}</div>`;
}

function screenWide(label, w, h) {
  const k = w / 1920;
  return `
   <div class="shard"></div><div class="grain"></div>
   <div class="lock" style="position:absolute;left:${130*k}px;top:40%;
        transform:translateY(-50%);width:${1382*k}px;z-index:3">${LOCKUP_WHITE}</div>
   <div class="rule" style="position:absolute;left:${130*k}px;top:62%;width:${330*k}px;margin:0;z-index:3"></div>
   <div class="label" style="position:absolute;left:${760*k}px;top:74%;
        font-size:${62*k}px;font-weight:700;z-index:3">${label}</div>`;
}

function overlap(s) {
  const L = s.lockFile ? read('lockup/' + s.lockFile) : LOCKUP;
  return `
   <div class="shard"></div><div class="grain"></div>
   <div class="lock" style="position:absolute;left:${s.pad}px;top:50%;
        transform:translateY(-50%);width:${s.lock}px;z-index:3">${L}</div>
   <div class="rule" style="position:absolute;left:${s.pad}px;top:63%;
        width:${Math.round(s.lock*0.56)}px;margin:0;z-index:3"></div>
   <div class="label" style="position:absolute;left:${s.pad}px;top:68%;
        font-size:${s.ls}px;z-index:3">${s.label}</div>
   <img src="${PLATE}" style="position:absolute;right:${Math.round(s.pad*0.9)}px;bottom:0;
        height:${s.plate};object-fit:contain;object-position:bottom;z-index:1">`;
}

function render(s) {
  return `
   <div class="shard"></div><div class="grain"></div>
   <div class="zones" style="padding:0 ${s.pad}px">
     <div class="zL">
       <div class="lock" style="width:${s.lock}px">${LOCKUP}</div>
       <div class="rule" style="width:${Math.round(s.lock*0.62)}px"></div>
       <div class="label" style="font-size:${s.ls}px">${s.label}</div>
     </div>
     <div class="zR"><img src="${PLATE}" style="height:${s.plate}"></div>
   </div>`;
}
const EXTRA = {
 'youtube-banner': { w:YT.w, h:YT.h, custom:`
   <div class="shard"></div><div class="grain"></div>
   <div style="position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
        width:${YT.safeW}px;height:${YT.safeH}px;overflow:hidden">
     ${screenWide('Forged live', YT.safeW, YT.safeH)}
   </div>` },
 'youtube-thumbnail-template': { w:1280, h:720, custom:`
   <div class="shard"></div><div class="grain"></div>
   <div style="position:absolute;inset:0;border:3px dashed rgba(255,255,255,.18)"></div>
   <div style="position:absolute;left:64px;top:64px;width:620px;height:470px;
        border:3px dashed rgba(214,35,37,.65);display:flex;align-items:center;justify-content:center">
     <span class="ph" style="font-size:26px;letter-spacing:.14em">HEADLINE SLOT</span></div>
   <div style="position:absolute;right:64px;bottom:64px;width:420px;height:470px;
        border:3px dashed rgba(255,255,255,.3);display:flex;align-items:flex-end;justify-content:center">
     <img src="${PLATE}" style="height:100%;object-fit:contain;object-position:bottom;opacity:.5"></div>
   <div class="icon" style="position:absolute;left:64px;bottom:54px;width:300px">${LOCKUP_INLINE}</div>` },
 'youtube-watermark': { w:150, h:150, custom:`
   <div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center">
     <div style="width:132px">${MARK}</div></div>` },
};

(async () => {
  const only = process.argv[2];
  const browser = await chromium.launch();
  const ALL = Object.assign({}, SCENES, EXTRA);
  for (const [name, w, h] of PANELS.map(t => [t, 320, 160]))
    ALL['panel-twitch-' + name.toLowerCase()] = { w, h, custom: panelHTML(name, w, h) };
  for (const [name, w, h] of PANELS.map(t => [t, 640, 320]))
    ALL['panel-kick-' + name.toLowerCase()] = { w, h, custom: panelHTML(name, w, h) };
  for (const [name, s] of Object.entries(ALL)) {
    if (only && name !== only) continue;
    const page = await browser.newPage({ viewport: { width: s.w, height: s.h }, deviceScaleFactor: 1 });
    const inner = s.fn ? s.fn(s) : (s.custom !== undefined && s.custom !== null ? s.custom : (s.overlap ? overlap(s) : render(s)));
    await page.setContent(`<style>${CSS}</style><div class="stage" style="width:${s.w}px;height:${s.h}px">${inner}</div>`);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(900);
    const out = path.join(B, 'channel', name + '.png');
    await page.screenshot({ path: out, clip: { x:0, y:0, width:s.w, height:s.h } });
    console.log(`  ${name}  ${s.w}x${s.h}`);
    await page.close();
  }
  await browser.close();
})();
