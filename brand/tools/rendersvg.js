const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [svgPath, outPath, size, bg] = process.argv.slice(2);
  const svg = fs.readFileSync(svgPath, 'utf8');
  const b = browserBg(bg);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: +size, height: +size }, deviceScaleFactor: 1 });
  await page.setContent(`<style>html,body{margin:0;padding:0;background:${b};width:${size}px;height:${size}px;overflow:hidden}svg{display:block;width:${size}px;height:${size}px}</style>${svg}`);
  await page.screenshot({ path: outPath });
  await browser.close();
  function browserBg(x){ return x === 'dark' ? '#101316' : (x === 'none' ? 'transparent' : '#ffffff'); }
})();
