/* Vertical alerts, 9:16. Redrawn in portrait -- not the horizontal art
   re-anchored.

   The horizontal alert reads left-to-right: mascot, then a panel with a red
   left edge. Rotating that into 9:16 wastes the frame, so the portrait
   version stacks it: mascot above, panel below, and the red bar becomes the
   panel's TOP edge. The mascot's feet overlap into the panel exactly as they
   overlapped the panel's left edge before, and the bar passes BEHIND the
   legs -- same stacking rule as the horizontal set.

   Timing is identical to tools/alertanim.js, impact at 450ms included, so one
   sound library serves both orientations. The entry directions are rotated to
   match the layout: the bar draws out sideways, the panel opens downward, and
   the exit drifts down instead of left.

   Everything sits inside the safe rectangle from tools/vertical.js. */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
const B = path.resolve(__dirname, '..');
const b64 = p => 'data:image/png;base64,' + fs.readFileSync(path.join(B, p)).toString('base64');
const read = p => fs.readFileSync(path.join(B, p), 'utf8');
const MARK = read('mark/mark-full-ondark-tight.svg');
const P = n => b64('mascot/poses/pose-' + n + '.png');

const FPS = 30;
const W = 840;                       // <= SAFE.w (856) in tools/vertical.js
const FRAME = { width: 1080, height: 1920 };
const SAFE = { x: 60, y: 220, w: 856, h: 1220 };   // keep in step with vertical.js
const STILL_T = 2.5;                 // the hold, used for the PNG still

const A = {
 'follow':    { pose:'wave-2',      cap:'New follower', sub:'Welcome to the forge' },
 'sub':       { pose:'celebrate-2', cap:'New sub',      sub:'Thanks for the support' },
 'resub':     { pose:'celebrate-2', cap:'Resub',        sub:'PLACEHOLDER — months', impacts:[0.45,0.63] },
 'giftsub':   { pose:'celebrate-3', cap:'Gifted subs',  sub:'PLACEHOLDER — count' },
 'bits':      { pose:'celebrate-1', cap:'Cheer',        sub:'PLACEHOLDER — bits' },
 'tip':       { pose:'celebrate-1', cap:'Tip',          sub:'PLACEHOLDER — amount' },
 'raid':      { pose:'celebrate-2', cap:'Raid',         sub:'PLACEHOLDER — raiders', big:true, dur:5.2, heavy:true },
 'ytmember':  { pose:'celebrate-3', cap:'New member',   sub:'YouTube' },
 'kicksub':   { pose:'celebrate-2', cap:'New sub',      sub:'Kick' },
};

const css = (H, PT) => `
 @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;600;700&display=swap');
 *{margin:0;padding:0;box-sizing:border-box}
 body{background:transparent;font-family:'Chakra Petch',sans-serif;color:#fff;overflow:hidden}
 .stage{position:relative;width:${W}px;height:${H}px;overflow:hidden}
 .edge{position:absolute;left:20px;right:20px;top:${PT}px;height:6px;
   background:#D62325;transform-origin:left center;z-index:1}
 .panel{position:absolute;left:20px;right:20px;top:${PT + 6}px;bottom:24px;overflow:hidden;
   background:rgba(17,21,26,.92);border-radius:0 0 4px 4px;
   box-shadow:0 6px 30px rgba(0,0,0,.6);transform-origin:top center}
 .flash{position:absolute;inset:0;background:#FFEDE8;opacity:0}
 .sheen{position:absolute;top:-40px;bottom:-40px;width:300px;left:0;
   transform:skewX(-18deg);opacity:0;
   background:linear-gradient(90deg,rgba(255,255,255,0) 0%,rgba(255,255,255,.17) 45%,rgba(255,255,255,.26) 55%,rgba(255,255,255,0) 100%)}
 .mwrap{position:absolute;left:0;right:0;top:0;height:${PT + 50}px;z-index:2}
 .mascot{position:absolute;left:50%;bottom:0;transform:translateX(-50%);
   object-fit:contain;object-position:bottom}
 .body{position:absolute;left:34px;right:34px;top:${PT + 76}px;bottom:30px;z-index:3;
   display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}
 .cap{font-size:21px;font-weight:600;letter-spacing:.30em;color:#D62325;text-transform:uppercase}
 .who{font-size:58px;font-weight:700;line-height:1.08;margin-top:12px;max-width:100%;
      white-space:nowrap;overflow:hidden;text-overflow:ellipsis;transform-origin:center}
 .sub{font-size:25px;color:#9AA5AF;margin-top:12px}
 .icon{position:absolute;right:38px;top:${PT + 24}px;width:52px;z-index:4}
 .icon svg{width:100%;height:auto;display:block}
`;

const DRIVER = `
 const clamp=x=>x<0?0:x>1?1:x;
 const span=(t,a,b)=>clamp((t-a)/(b-a));
 const outCubic=x=>1-Math.pow(1-x,3);
 const inCubic=x=>x*x*x;
 const outBack=x=>{const c=1.9;return 1+(c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
 const E=document.querySelector('.edge'), PA=document.querySelector('.panel'),
       FL=document.querySelector('.flash'), SH=document.querySelector('.sheen'),
       MW=document.querySelector('.mwrap'), MI=document.querySelector('.mascot'),
       CA=document.querySelector('.cap'), WH=document.querySelector('.who'),
       SU=document.querySelector('.sub'), IC=document.querySelector('.icon'),
       ST=document.querySelector('.stage');
 function textIn(el,t,a,b,scale){
   const p=outCubic(span(t,a,b));
   el.style.opacity=p.toFixed(3);
   el.style.transform='translateY('+((1-p)*12).toFixed(2)+'px) scale('
     +(scale?(0.96+0.04*p):1).toFixed(4)+')';
 }
 window.setT=function(t){
   let hit=0;
   for(const b of IMPACTS){ if(t>=b) hit=Math.max(hit,Math.max(0,1-(t-b)/0.18)); }
   const hit2=hit*hit;

   E.style.transform='scaleX('+outCubic(span(t,0.00,0.14)).toFixed(4)+')';
   E.style.boxShadow='0 0 '+(10+34*hit2).toFixed(1)+'px '+(2+7*hit2).toFixed(1)
     +'px rgba(214,35,37,'+(0.55*hit2).toFixed(3)+')';

   PA.style.transform='scaleY('+outCubic(span(t,0.12,0.42)).toFixed(4)+')';
   FL.style.opacity=(FLASH*hit2).toFixed(3);

   MW.style.transform='translateY('+((1-outBack(span(t,0.16,0.58)))*70).toFixed(2)+'px)';
   MW.style.opacity=outCubic(span(t,0.16,0.34)).toFixed(3);
   MI.style.filter='brightness('+(1+0.26*hit2).toFixed(3)+')';

   textIn(CA,t,0.42,0.60,false);
   textIn(WH,t,0.50,0.72,true);
   textIn(SU,t,0.60,0.80,false);

   const ip=span(t,0.30,0.48);
   IC.style.opacity=ip.toFixed(3);
   IC.style.transform='scale('+(0.8+0.2*outCubic(ip)+0.35*hit2).toFixed(4)+')';

   const sp=span(t,1.00,1.75);
   SH.style.opacity=(sp>0&&sp<1)?'1':'0';
   SH.style.transform='skewX(-18deg) translateX('+(-360+sp*(PANELW+460)).toFixed(1)+'px)';

   const xp=inCubic(span(t,DUR-0.42,DUR));
   ST.style.opacity=(1-xp).toFixed(3);
   ST.style.transform='translateY('+(26*xp).toFixed(2)+'px)';
 };
`;

(async () => {
  const only = process.argv[2];
  const browser = await chromium.launch();

  for (const [name, a] of Object.entries(A)) {
    if (only === 'guide') break;
    if (only && name !== only) continue;
    const H = a.big ? 840 : 760;
    const PT = a.big ? 470 : 420;          // panel top
    const MH = a.big ? 500 : 440;          // mascot height
    const DUR = a.dur || 4.4;
    const FRAMES = Math.round(FPS * DUR) + 1;
    const impacts = a.impacts || [0.45];
    const out = path.join(B, '..', '.valert-frames', name);
    fs.rmSync(out, { recursive: true, force: true });
    fs.mkdirSync(out, { recursive: true });

    const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
    await page.setContent(`<style>${css(H, PT)}</style>
      <div class="stage">
        <div class="panel"><div class="sheen"></div><div class="flash"></div></div>
        <div class="edge"></div>
        <div class="mwrap"><img class="mascot" src="${P(a.pose)}" style="height:${MH}px"></div>
        <div class="icon">${MARK}</div>
        <div class="body">
          <div class="cap">${a.cap}</div>
          <div class="who">PLACEHOLDER</div>
          <div class="sub">${a.sub}</div>
        </div>
      </div>
      <script>
        const IMPACTS=${JSON.stringify(impacts)}, DUR=${DUR},
              PANELW=${W - 40}, FLASH=${a.heavy ? 0.20 : 0.13};
        ${DRIVER}
      <\/script>`);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(500);

    for (let f = 0; f < FRAMES; f++) {
      await page.evaluate(t => window.setT(t), f / FPS);
      await page.screenshot({ path: path.join(out, String(f).padStart(4,'0') + '.png'),
                              omitBackground: true, clip: { x:0, y:0, width:W, height:H } });
    }
    // the hold frame doubles as the still, so PNG and WebM can never disagree
    await page.evaluate(t => window.setT(t), STILL_T);
    await page.screenshot({ path: path.join(B, 'vertical', 'alert-' + name + '.png'),
                            omitBackground: true, clip: { x:0, y:0, width:W, height:H } });
    await page.close();

    execFileSync('bash', ['-c', `for f in ${out}/*.png; do convert "$f" PNG32:"$f"; done`]);
    const webm = path.join(B, 'vertical', 'alert-' + name + '.webm');
    execFileSync('ffmpeg', ['-y','-loglevel','error','-framerate',String(FPS),
      '-i', path.join(out,'%04d.png'),
      '-c:v','libvpx-vp9','-pix_fmt','yuva420p','-auto-alt-ref','0','-lag-in-frames','0',
      '-b:v','0','-crf','28', webm]);
    console.log(`  vertical/alert-${name}  ${W}x${H}  ${DUR}s  ${(fs.statSync(webm).size/1024).toFixed(0)}KB`);
  }

  // Placement guide: where the alert sits in the real frame, against the safe box.
  if (!only || only === 'guide') {
    const AX = SAFE.x + Math.round((SAFE.w - W) / 2);
    const AY = SAFE.y + Math.round((SAFE.h - 760) / 2);
    const page = await browser.newPage({ viewport: FRAME, deviceScaleFactor: 1 });
    await page.setContent(`<style>
      @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;600&display=swap');
      *{margin:0;padding:0;box-sizing:border-box}
      body{font-family:'Chakra Petch',sans-serif;overflow:hidden}
      .f{position:relative;width:${FRAME.width}px;height:${FRAME.height}px;overflow:hidden;
         background:radial-gradient(110% 70% at 50% 28%,#1A2027 0%,#0F1215 62%)}
      .blocked{position:absolute;background:rgba(214,35,37,.16);z-index:8}
      .guide{position:absolute;border:3px dashed rgba(0,229,255,.9);z-index:9}
      .lab{position:absolute;color:#00E5FF;font-size:24px;z-index:10}
    </style>
    <div class="f">
      <img src="${b64('vertical/alert-follow.png')}" style="position:absolute;
           left:${AX}px;top:${AY}px;width:${W}px;z-index:5">
      <div class="blocked" style="left:0;top:0;width:${FRAME.width}px;height:${SAFE.y}px"></div>
      <div class="blocked" style="left:0;top:${SAFE.y + SAFE.h}px;width:${FRAME.width}px;height:${FRAME.height - SAFE.y - SAFE.h}px"></div>
      <div class="blocked" style="left:0;top:${SAFE.y}px;width:${SAFE.x}px;height:${SAFE.h}px"></div>
      <div class="blocked" style="left:${SAFE.x + SAFE.w}px;top:${SAFE.y}px;width:${FRAME.width - SAFE.x - SAFE.w}px;height:${SAFE.h}px"></div>
      <div class="guide" style="left:${SAFE.x}px;top:${SAFE.y}px;width:${SAFE.w}px;height:${SAFE.h}px"></div>
      <div class="lab" style="left:${SAFE.x}px;top:${SAFE.y - 34}px">Safe ${SAFE.w} x ${SAFE.h}</div>
      <div class="lab" style="left:${AX}px;top:${AY + 760 + 12}px">Alert ${W} x 760 at (${AX}, ${AY})</div>
    </div>`);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(600);
    await page.screenshot({ path: path.join(B, 'vertical', 'alert-position-guide.png'),
                            clip: { x:0, y:0, width:FRAME.width, height:FRAME.height } });
    await page.close();
    console.log(`  vertical/alert-position-guide  ${FRAME.width}x${FRAME.height}  alert at (${AX}, ${AY})`);
  }
  await browser.close();
})();
