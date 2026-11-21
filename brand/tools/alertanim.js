/* Animated alerts. Renders transparent PNG frames per alert and encodes each
   to WebM VP9 with a real alpha channel.

   Beats (seconds, absolute — same for every alert so one sound note covers
   all of them):
     0.00-0.14  red edge bar drops in from the top
     0.12-0.42  panel wipes open rightward from that bar
     0.16-0.58  mascot rises with an overshoot and settles
     0.45       IMPACT — flash, edge glow, mark pop. The hammer strike lands here.
     0.42-0.80  caption, name, subline stagger in
     1.00-1.75  sheen sweeps across the panel
     ...hold...
     last 0.42  stage drifts left and fades out

   Sound is sourced separately; alert widgets play audio as its own input, so
   these are production-ready video without it. */
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
const B = path.resolve(__dirname, '..');
const b64 = p => 'data:image/png;base64,' + fs.readFileSync(path.join(B, p)).toString('base64');
const read = p => fs.readFileSync(path.join(B, p), 'utf8');
const MARK = read('mark/mark-full-ondark-tight.svg');
const P = n => b64('mascot/poses/pose-' + n + '.png');

const FPS = 30;

const A = {
 'alert-follow':    { pose:'wave-2',      cap:'New follower', sub:'Welcome to the forge' },
 'alert-sub':       { pose:'celebrate-2', cap:'New sub',      sub:'Thanks for the support' },
 'alert-resub':     { pose:'celebrate-2', cap:'Resub',        sub:'PLACEHOLDER — months', impacts:[0.45,0.63] },
 'alert-giftsub':   { pose:'celebrate-3', cap:'Gifted subs',  sub:'PLACEHOLDER — count' },
 'alert-bits':      { pose:'celebrate-1', cap:'Cheer',        sub:'PLACEHOLDER — bits' },
 'alert-tip':       { pose:'celebrate-1', cap:'Tip',          sub:'PLACEHOLDER — amount' },
 'alert-raid':      { pose:'celebrate-2', cap:'Raid',         sub:'PLACEHOLDER — raiders', big:true, dur:5.2, heavy:true },
 'alert-ytmember':  { pose:'celebrate-3', cap:'New member',   sub:'YouTube' },
 'alert-kicksub':   { pose:'celebrate-2', cap:'New sub',      sub:'Kick' },
};

const CSS = `
 @import url('https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;600;700&display=swap');
 *{margin:0;padding:0;box-sizing:border-box}
 body{background:transparent;font-family:'Chakra Petch',sans-serif;color:#fff;overflow:hidden}
 .stage{position:relative;overflow:hidden}
 .edge{position:absolute;left:300px;top:46px;bottom:46px;width:5px;
   background:#D62325;transform-origin:top center;z-index:1}
 .panel{position:absolute;left:305px;right:0;top:46px;bottom:46px;overflow:hidden;
   background:rgba(17,21,26,.92);border-radius:0 3px 3px 0;
   box-shadow:0 4px 26px rgba(0,0,0,.55);transform-origin:left center}
 .flash{position:absolute;inset:0;background:#FFEDE8;opacity:0}
 .sheen{position:absolute;top:-40px;bottom:-40px;width:300px;left:0;
   transform:skewX(-18deg);opacity:0;
   background:linear-gradient(90deg,rgba(255,255,255,0) 0%,rgba(255,255,255,.17) 45%,rgba(255,255,255,.26) 55%,rgba(255,255,255,0) 100%)}
 .mwrap{position:absolute;left:0;bottom:0;top:0;width:300px;z-index:2}
 .mascot{position:absolute;left:0;bottom:0;object-fit:contain;object-position:bottom}
 .body{position:absolute;left:336px;right:28px;top:50%;transform:translateY(-50%);z-index:3}
 .cap{font-size:17px;font-weight:600;letter-spacing:.30em;color:#D62325;text-transform:uppercase}
 .who{font-size:44px;font-weight:700;line-height:1.1;margin-top:8px;
      white-space:nowrap;overflow:hidden;text-overflow:ellipsis;transform-origin:left center}
 .sub{font-size:19px;color:#9AA5AF;margin-top:8px}
 .icon{position:absolute;right:20px;top:62px;width:40px;z-index:3}
 .icon svg{width:100%;height:auto;display:block}
`;

// The per-frame styler runs in the page. Keeping it there means the DOM and
// the base64 mascot are parsed once per alert, not once per frame.
const DRIVER = `
 const clamp=(x)=>x<0?0:x>1?1:x;
 const span=(t,a,b)=>clamp((t-a)/(b-a));
 const outCubic=x=>1-Math.pow(1-x,3);
 const inCubic=x=>x*x*x;
 const outBack=x=>{const c=1.9;return 1+ (c+1)*Math.pow(x-1,3)+c*Math.pow(x-1,2)};
 const E=document.querySelector('.edge'), PA=document.querySelector('.panel'),
       FL=document.querySelector('.flash'), SH=document.querySelector('.sheen'),
       MW=document.querySelector('.mwrap'), MI=document.querySelector('.mascot'),
       CA=document.querySelector('.cap'), WH=document.querySelector('.who'),
       SU=document.querySelector('.sub'), IC=document.querySelector('.icon'),
       ST=document.querySelector('.stage');
 function textIn(el,t,a,b,scale){
   const p=outCubic(span(t,a,b));
   el.style.opacity=p.toFixed(3);
   const s=scale?(0.96+0.04*p):1;
   el.style.transform='translateY('+((1-p)*12).toFixed(2)+'px) scale('+s.toFixed(4)+')';
 }
 window.setT=function(t){
   // impact envelope: instant attack, ~0.22s decay, summed over every beat
   let hit=0;
   for(const b of IMPACTS){ if(t>=b) hit=Math.max(hit, Math.max(0,1-(t-b)/0.18)); }
   const hit2=hit*hit;

   E.style.transform='scaleY('+outCubic(span(t,0.00,0.14)).toFixed(4)+')';
   E.style.boxShadow='0 0 '+(10+34*hit2).toFixed(1)+'px '+(2+7*hit2).toFixed(1)+'px rgba(214,35,37,'+(0.55*hit2).toFixed(3)+')';

   PA.style.transform='scaleX('+outCubic(span(t,0.12,0.42)).toFixed(4)+')';
   FL.style.opacity=(FLASH*hit2).toFixed(3);

   const mp=span(t,0.16,0.58);
   MW.style.transform='translateY('+((1-outBack(mp))*70).toFixed(2)+'px)';
   MW.style.opacity=outCubic(span(t,0.16,0.34)).toFixed(3);
   MI.style.filter='brightness('+(1+0.26*hit2).toFixed(3)+')';

   textIn(CA,t,0.42,0.60,false);
   textIn(WH,t,0.50,0.72,true);
   textIn(SU,t,0.60,0.80,false);

   const ip=span(t,0.30,0.48);
   IC.style.opacity=ip.toFixed(3);
   IC.style.transform='scale('+(0.8+0.2*outCubic(ip)+0.35*hit2).toFixed(4)+')';

   // sheen: travels the panel width plus its own width so it clears both edges
   const sp=span(t,1.00,1.75);
   SH.style.opacity=(sp>0&&sp<1)?'1':'0';
   SH.style.transform='skewX(-18deg) translateX('+(-360+sp*(PANELW+460)).toFixed(1)+'px)';

   const xp=inCubic(span(t,DUR-0.42,DUR));
   ST.style.opacity=(1-xp).toFixed(3);
   ST.style.transform='translateX('+(-26*xp).toFixed(2)+'px)';
 };
`;

(async () => {
  const only = process.argv[2];
  const browser = await chromium.launch();
  const made = [];

  for (const [name, a] of Object.entries(A)) {
    if (only && name !== only) continue;
    const W = 920, H = a.big ? 460 : 420;
    const DUR = a.dur || 4.4;
    const FRAMES = Math.round(FPS * DUR) + 1;
    const impacts = a.impacts || [0.45];
    const out = path.join(B, '..', '.alert-frames', name);
    fs.rmSync(out, { recursive: true, force: true });
    fs.mkdirSync(out, { recursive: true });

    const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
    await page.setContent(`<style>${CSS}</style>
      <div class="stage" style="width:${W}px;height:${H}px">
        <div class="panel"><div class="sheen"></div><div class="flash"></div></div>
        <div class="edge"></div>
        <div class="mwrap"><img class="mascot" src="${P(a.pose)}" style="height:${a.big ? 100 : 94}%"></div>
        <div class="icon">${MARK}</div>
        <div class="body">
          <div class="cap">${a.cap}</div>
          <div class="who">PLACEHOLDER</div>
          <div class="sub">${a.sub}</div>
        </div>
      </div>
      <script>
        const IMPACTS=${JSON.stringify(impacts)}, DUR=${DUR},
              PANELW=${W - 305}, FLASH=${a.heavy ? 0.20 : 0.13};
        ${DRIVER}
      </script>`);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(500);

    for (let f = 0; f < FRAMES; f++) {
      await page.evaluate(t => window.setT(t), f / FPS);
      await page.screenshot({ path: path.join(out, String(f).padStart(4,'0') + '.png'),
                              omitBackground: true, clip: { x:0, y:0, width:W, height:H } });
    }
    await page.close();

    // Frames that happen to be fully opaque save without an alpha channel, and
    // a mixed sequence makes ffmpeg drop alpha for the whole clip.
    execFileSync('bash', ['-c', `for f in ${out}/*.png; do convert "$f" PNG32:"$f"; done`]);

    const webm = path.join(B, 'alerts', name + '.webm');
    execFileSync('ffmpeg', ['-y','-loglevel','error','-framerate',String(FPS),
      '-i', path.join(out,'%04d.png'),
      '-c:v','libvpx-vp9','-pix_fmt','yuva420p','-auto-alt-ref','0','-lag-in-frames','0',
      '-b:v','0','-crf','28', webm]);

    const kb = (fs.statSync(webm).size/1024).toFixed(0);
    made.push({ name, W, H, DUR, FRAMES, kb, impacts });
    console.log(`  ${name}  ${W}x${H}  ${DUR}s  ${FRAMES}f  ${kb}KB  impact@${impacts.map(i=>i*1000+'ms').join(',')}`);
  }
  await browser.close();
  console.log(`\n  ${made.length} animated alerts -> brand/alerts/*.webm`);
})();
