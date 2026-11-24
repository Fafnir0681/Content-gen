/* Mascot idle loop. A 6s seamless cycle for the webcam-replacement plate.

   With no face-cam the plate is the only thing on screen carrying a pulse, so
   a static PNG reads as a frozen stream. This is deliberately low-amplitude:
   it has to survive being looked at for four hours without becoming a tic.

   Every motion period divides the 6s loop exactly, and the last frame is NOT
   rendered (frame 180 would duplicate frame 0 and stutter the loop).

   Beats, all simultaneous and all seamless:
     breathing      3.0s   scale from the feet, +0.6% -- chest rises, boots don't
     weight shift   6.0s   +/-0.22 deg rotation about the feet
     forge light    1.2s + 0.75s   summed, so the flicker never repeats visibly
     flask glow     1.5s + 1.0s    the liquid brightens, it is not painted over
     hammer rune    2.0s   the head is still hot
     embers         3.0s   six, phase-offset, rising off the hammer
*/
const { chromium } = require('playwright');
const { execFileSync } = require('child_process');
const fs = require('fs'), path = require('path');
const B = path.resolve(__dirname, '..');
const PLATE = 'data:image/png;base64,' +
  fs.readFileSync(path.join(B, 'mascot/mascot-plate.png')).toString('base64');

const W = 484, H = 680, FPS = 30, LOOP = 6.0;
const FRAMES = Math.round(FPS * LOOP);          // 180, frame 180 omitted

// measured off the art, not estimated
const FLASK = { x: 450, y: 160, r: 66 };
const RUNE  = { x: 53,  y: 408, r: 50 };

const EMBERS = Array.from({ length: 6 }, (_, i) => ({
  x: 34 + (i * 37) % 92,      // spread across the hammer head
  drift: (i % 2 ? 1 : -1) * (5 + i * 2),
  size: 1.6 + (i % 3) * 0.7,
  phase: i / 6,               // evenly offset so the stream never gaps
}));

const CSS = `
 *{margin:0;padding:0;box-sizing:border-box}
 body{background:transparent;overflow:hidden}
 .stage{position:relative;width:${W}px;height:${H}px;overflow:hidden}
 .fig{position:absolute;inset:0;transform-origin:50% 100%}
 .fig img{position:absolute;inset:0;width:${W}px;height:${H}px;display:block}
 /* A masked, brightened copy of the art itself. Fading it in makes the real
    pixels glow, where painting a red blob over them just flattens the line. */
 .hot{position:absolute;inset:0;opacity:0}
 .hot.flask{-webkit-mask-image:radial-gradient(circle at ${FLASK.x}px ${FLASK.y}px,#000 0%,rgba(0,0,0,.65) 42%,transparent 72%)}
 .hot.rune{-webkit-mask-image:radial-gradient(circle at ${RUNE.x}px ${RUNE.y}px,#000 0%,rgba(0,0,0,.6) 38%,transparent 70%)}
 .hot.flask img{filter:brightness(1.75) saturate(1.25)}
 .hot.rune img{filter:brightness(1.9) saturate(1.15)}
 /* Light spilling into the air. This one is allowed outside the silhouette. */
 .halo{position:absolute;border-radius:50%;opacity:0;pointer-events:none}
 .ember{position:absolute;border-radius:50%;background:#FF7A3C;opacity:0}
`;

const DRIVER = `
 const TAU=Math.PI*2, frac=x=>x-Math.floor(x);
 const FIG=document.querySelector('.fig'),
       HF=document.querySelector('.hot.flask'), HR=document.querySelector('.hot.rune'),
       LF=document.querySelector('.halo.flask'), LR=document.querySelector('.halo.rune'),
       IMGS=[...document.querySelectorAll('.fig > img, .hot img')],
       EMS=[...document.querySelectorAll('.ember')];
 window.setT=function(t){
   const br=Math.sin(TAU*t/3.0);                       // breathing
   const sw=Math.sin(TAU*t/6.0);                       // weight shift
   FIG.style.transform='rotate('+(sw*0.22).toFixed(4)+'deg) '
     +'scale('+(1+0.0032+0.0032*br).toFixed(5)+','+(1+0.006+0.006*br).toFixed(5)+') '
     +'translateY('+(-1.3*br).toFixed(3)+'px)';

   // forge light: two periods that both divide the loop but not each other
   const fl=0.62*Math.sin(TAU*t/1.2)+0.38*Math.sin(TAU*t/0.75+1.1);
   const b=(1+0.019*fl).toFixed(4);
   for(const im of IMGS) im.style.filter=im.dataset.f
     ? im.dataset.f+' brightness('+b+')' : 'brightness('+b+')';

   const fg=0.5+0.5*(0.6*Math.sin(TAU*t/1.5)+0.4*Math.sin(TAU*t/1.0+2.2));
   HF.style.opacity=(0.30+0.42*fg).toFixed(3);
   LF.style.opacity=(0.10+0.16*fg).toFixed(3);

   const rg=0.5+0.5*Math.sin(TAU*t/2.0);
   HR.style.opacity=(0.18+0.30*rg).toFixed(3);
   LR.style.opacity=(0.05+0.10*rg).toFixed(3);

   EMS.forEach((e,i)=>{
     const d=EMBERS[i], p=frac(t/3.0+d.phase);
     // fade in over the first fifth, out over the last third -- never visible
     // at p=0 or p=1, so the wrap cannot pop
     const fade=Math.min(p/0.2,1)*Math.min((1-p)/0.33,1);
     e.style.opacity=(fade*0.55).toFixed(3);
     e.style.transform='translate('+(d.x+d.drift*p).toFixed(2)+'px,'
       +(352-150*p).toFixed(2)+'px)';
   });
 };
`;

(async () => {
  const out = path.join(B, '..', '.idle-frames');
  fs.rmSync(out, { recursive: true, force: true });
  fs.mkdirSync(out, { recursive: true });

  const halo = (c, mult) => `<div class="halo ${c}" style="left:${
    (c === 'flask' ? FLASK.x - FLASK.r * mult : RUNE.x - RUNE.r * mult)}px;top:${
    (c === 'flask' ? FLASK.y - FLASK.r * mult : RUNE.y - RUNE.r * mult)}px;width:${
    (c === 'flask' ? FLASK.r : RUNE.r) * 2 * mult}px;height:${
    (c === 'flask' ? FLASK.r : RUNE.r) * 2 * mult}px;background:radial-gradient(circle,${
    c === 'flask' ? 'rgba(255,74,60,.85)' : 'rgba(255,110,50,.8)'} 0%,transparent 68%)"></div>`;

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
  await page.setContent(`<style>${CSS}</style>
    <div class="stage">
      ${halo('rune', 1.5)}${halo('flask', 1.6)}
      <div class="fig">
        <img src="${PLATE}">
        <div class="hot flask"><img src="${PLATE}" data-f="brightness(1.75) saturate(1.25)"></div>
        <div class="hot rune"><img src="${PLATE}" data-f="brightness(1.9) saturate(1.15)"></div>
      </div>
      ${EMBERS.map(e => `<div class="ember" style="width:${e.size*2}px;height:${e.size*2}px"></div>`).join('')}
    </div>
    <script>const EMBERS=${JSON.stringify(EMBERS)};${DRIVER}<\/script>`);
  await page.waitForTimeout(400);

  for (let f = 0; f < FRAMES; f++) {
    await page.evaluate(t => window.setT(t), f / FPS);
    await page.screenshot({ path: path.join(out, String(f).padStart(4,'0') + '.png'),
                            omitBackground: true, clip: { x:0, y:0, width:W, height:H } });
  }
  await browser.close();

  execFileSync('bash', ['-c', `for f in ${out}/*.png; do convert "$f" PNG32:"$f"; done`]);
  const webm = path.join(B, 'mascot', 'mascot-plate-idle.webm');
  execFileSync('ffmpeg', ['-y','-loglevel','error','-framerate',String(FPS),
    '-i', path.join(out,'%04d.png'),
    '-c:v','libvpx-vp9','-pix_fmt','yuva420p','-auto-alt-ref','0','-lag-in-frames','0',
    '-b:v','0','-crf','30', webm]);
  console.log(`  mascot-plate-idle.webm  ${W}x${H}  ${LOOP}s  ${FRAMES}f  ${(fs.statSync(webm).size/1024).toFixed(0)}KB`);
})();
