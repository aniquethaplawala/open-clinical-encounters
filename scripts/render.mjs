import { chromium } from 'playwright';
import fs from 'fs'; import path from 'path';
const dir = process.argv[2];
const b = await chromium.launch(); const p = await b.newPage();
for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.html'))) {
  await p.goto('file://' + path.resolve(dir, f)); await p.waitForLoadState('networkidle'); await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: path.resolve(dir, f.replace('.html', '.pdf')), format: 'Letter', printBackground: true, preferCSSPageSize: true });
  console.log(f);
}
await b.close();
