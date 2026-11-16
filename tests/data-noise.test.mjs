// Noise in the records that a reader meets as a broken link or an empty point (found 16 Nov 2026).
// tools/import_details_reports.py once cut every address at its first ")" — 70 source links such as
// https://en.wikipedia.org/wiki/Mostyn_(gallery led nowhere — and kept a bare "-" line as a point.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
const ALL = JSON.parse(readFileSync(new URL('../institutions.json', import.meta.url)));

function* strings(v, path = '') {
  if (typeof v === 'string') yield [path, v];
  else if (Array.isArray(v)) for (const [i, x] of v.entries()) yield* strings(x, `${path}[${i}]`);
  else if (v && typeof v === 'object') for (const [k, x] of Object.entries(v)) yield* strings(x, path ? `${path}.${k}` : k);
}

test('no address in a record opens a bracket it does not close', () => {
  const bad = [];
  for (const r of ALL) for (const [p, s] of strings(r))
    for (const u of s.match(/https?:\/\/\S+/g) || []) {
      const core = u.replace(/[.,;:]+$/, '');
      if ((core.match(/\(/g) || []).length > (core.match(/\)/g) || []).length) bad.push(`${r.id} ${p}: ${core}`);
    }
  assert.deepEqual(bad, []);
});

test('no point or list item is only a dash or a bullet mark', () => {
  const bad = [];
  for (const r of ALL) for (const [p, s] of strings(r)) if (/^\s*[-–—•*]\s*$/.test(s)) bad.push(`${r.id} ${p}`);
  assert.deepEqual(bad, []);
});
