// Packs the logos tools/build_funder_logos.py saved into one sheet of one-colour masks: assets/funder-logos.png and
// assets/funder-logos.json ({ key: [x, y, w, h] }, the office key of assets/hq.json).
//
//   node tools/pack_funder_logos.mjs <jobs.json> <assets folder>
//
// Each logo is drawn in Chromium (Playwright), trimmed to its ink and turned into a mask: white at the opacity of how
// far each pixel is from white, so a white ground (a JPEG, a white box behind a word) falls away and the mark stays. A
// logo that is white on nothing would vanish that way, so one with almost no ink left keeps its own opacity instead.
// A logo that is a white mark knocked out of a filled block would be a solid block as a mask, so it is left out.
// The page fills the mask with the company colour (assets/layers.js, MONEY MODE), so the sheet holds no colour.
// A cell is 48 px high, three times the 16 px the map draws it at, and at most 3.5 times as wide as it is high.
import { readFileSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const [jobsPath, outDir] = process.argv.slice(2);
const jobs = JSON.parse(readFileSync(jobsPath, 'utf8'));

// One file can serve several keys (the same body under two keys): draw it once.
const byPath = new Map();
jobs.forEach(j => { if (!byPath.has(j.path)) byPath.set(j.path, []); byPath.get(j.path).push(j.key); });
// The cache holds Wikimedia thumbnails (PNG, or JPEG for a photographed logo): the type is read from the file's first bytes.
const typeOf = b => b[0] === 0x89 ? 'image/png' : b[0] === 0xff ? 'image/jpeg' : b[0] === 0x47 ? 'image/gif' : b[0] === 0x52 ? 'image/webp' : 'image/svg+xml';
const files = [...byPath.keys()].map(p => { const b = readFileSync(p); return { p, uri: `data:${typeOf(b)};base64,${b.toString('base64')}` }; });

const browser = await chromium.launch();
const page = await browser.newPage();
await page.setContent('<canvas id="sheet"></canvas>');
const result = await page.evaluate(async (files) => {
  const H = 48, MAXW = 168, PAD = 2, SHEET_W = 1024;
  const cells = [];
  for (const f of files) {
    const img = new Image();
    const ok = await new Promise(res => { img.onload = () => res(true); img.onerror = () => res(false); img.src = f.uri; });
    if (!ok || !img.naturalWidth) { cells.push(null); continue; }
    // Big enough to trim from: 400 px on the long side.
    const k = 400 / Math.max(img.naturalWidth, img.naturalHeight);
    const w = Math.max(1, Math.round(img.naturalWidth * k)), h = Math.max(1, Math.round(img.naturalHeight * k));
    const c = new OffscreenCanvas(w, h), x = c.getContext('2d', { willReadFrequently: true });
    x.drawImage(img, 0, 0, w, h);
    const d = x.getImageData(0, 0, w, h), px = d.data;
    const ink = new Float32Array(w * h); let max = 0, sum = 0;
    for (let i = 0; i < w * h; i++) {
      const a = px[i * 4 + 3] / 255, dark = 1 - Math.min(px[i * 4], px[i * 4 + 1], px[i * 4 + 2]) / 255;
      ink[i] = a * dark; if (ink[i] > max) max = ink[i]; sum += ink[i];
    }
    // A white logo on nothing: its own opacity is the mark.
    const useAlpha = max < 0.25 || sum / (w * h) < 0.004;
    for (let i = 0; i < w * h; i++) {
      // A levels curve: a pale grey in the logo is still part of the mark, so it comes out at full strength, not faded.
      const raw = useAlpha ? px[i * 4 + 3] / 255 : ink[i] / Math.max(max, 0.01);
      const v = Math.max(0, Math.min(1, (raw - 0.08) / 0.5));
      px[i * 4] = px[i * 4 + 1] = px[i * 4 + 2] = 255; px[i * 4 + 3] = Math.round(v * 255);
    }
    let x0 = w, y0 = h, x1 = -1, y1 = -1;
    for (let yy = 0; yy < h; yy++) for (let xx = 0; xx < w; xx++) if (px[(yy * w + xx) * 4 + 3] > 24) {
      if (xx < x0) x0 = xx; if (xx > x1) x1 = xx; if (yy < y0) y0 = yy; if (yy > y1) y1 = yy;
    }
    if (x1 < 0) { cells.push(null); continue; }
    // A logo that is a white mark on a filled block becomes a solid block as a mask, the mark lost: it is left out.
    let fill = 0;
    for (let yy = y0; yy <= y1; yy++) for (let xx = x0; xx <= x1; xx++) fill += px[(yy * w + xx) * 4 + 3] / 255;
    if (fill / ((x1 - x0 + 1) * (y1 - y0 + 1)) > 0.8) { cells.push(null); continue; }
    x.putImageData(d, 0, 0);
    const tw = x1 - x0 + 1, th = y1 - y0 + 1, s = Math.min(H / th, MAXW / tw);
    const cw = Math.max(1, Math.round(tw * s)), ch = Math.max(1, Math.round(th * s));
    const cell = new OffscreenCanvas(cw, ch), cx = cell.getContext('2d');
    cx.imageSmoothingQuality = 'high';
    cx.drawImage(c, x0, y0, tw, th, 0, 0, cw, ch);
    cells.push({ cell, w: cw, h: ch });
  }
  // Rows, left to right.
  let px = PAD, py = PAD;
  const rects = cells.map(c => {
    if (!c) return null;
    if (px + c.w + PAD > SHEET_W) { px = PAD; py += H + PAD; }
    const r = [px, py, c.w, c.h]; px += c.w + PAD; return r;
  });
  const sheet = document.getElementById('sheet');
  sheet.width = SHEET_W; sheet.height = py + H + PAD;
  const sx = sheet.getContext('2d');
  cells.forEach((c, i) => { if (c) sx.drawImage(c.cell, rects[i][0], rects[i][1]); });
  return { png: sheet.toDataURL('image/png'), rects };
}, files);
await browser.close();

const index = {};
files.forEach((f, i) => { if (result.rects[i]) byPath.get(f.p).forEach(key => { index[key] = result.rects[i]; }); });
const sorted = Object.fromEntries(Object.keys(index).sort().map(k => [k, index[k]]));
writeFileSync(path.join(outDir, 'funder-logos.png'), Buffer.from(result.png.split(',')[1], 'base64'));
writeFileSync(path.join(outDir, 'funder-logos.json'), JSON.stringify(sorted) + '\n');
const failed = files.filter((f, i) => !result.rects[i]).map(f => path.basename(f.p));
console.log(`packed ${files.length - failed.length} logos for ${Object.keys(sorted).length} keys` + (failed.length ? `; left out (no mark, or a solid block): ${failed.join(', ')}` : ''));
