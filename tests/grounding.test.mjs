import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

// The file is a browser script that also sets module.exports; run it as plain script and read the global it sets.
const ctx = {};
vm.runInNewContext(readFileSync(new URL('../assets/grounding.js', import.meta.url), 'utf8'), ctx);
const { formatRecord, placeSummary, FULL, SHORT } = ctx.AtlasGrounding;
const GRADE = { 1: { letter: 'A' }, 2: { letter: 'B' }, 3: { letter: 'C' }, 4: { letter: 'D' }, 5: { letter: 'F' } };

const items = JSON.parse(readFileSync(new URL('../institutions.json', import.meta.url), 'utf8'));
const all = Array.isArray(items) ? items : (items.institutions || Object.values(items)[0]);
const tate = all.find(i => i.id === 'tate-modern');

test('a full record carries the audited figures, the cases, the governance and the sources', () => {
  const t = formatRecord(tate, { status: 'Grade F', watchGossip: true, full: true });
  assert.match(t, /Audited figures FY2025-26/);
  assert.match(t, /income GBP 194\.9 million/);
  assert.match(t, /Legal form: statutory public body/);
  assert.match(t, /Case: Democracy Now! report, 2016-03-11/);
  assert.match(t, /SOURCES:/);
  assert.match(t, /VISITING:/);
  assert.ok(t.length <= FULL + 200, 'within the full budget');
});

test('a short record stays within its budget and keeps its head and sources', () => {
  const t = formatRecord(tate, { status: 'Grade F', watchGossip: true, full: false });
  assert.ok(t.length <= SHORT + 200);
  assert.match(t, /^- INSTITUTION: Tate Modern/);
  assert.match(t, /SOURCES:/);
});

test('a thin record writes what is there and nothing invented', () => {
  const t = formatRecord({ name: 'X', city: 'Y', country: 'Z', tier: 'C' }, { status: 'Unverified' });
  assert.match(t, /Governance Classification: Unverified/);
  assert.match(t, /Funding on record: not stated/);
  assert.doesNotMatch(t, /GOVERNANCE:/);
  assert.doesNotMatch(t, /VISITING:/);
});

test('a place summary counts and tallies the place itself', () => {
  const berlin = all.filter(i => i.city === 'Berlin');
  const p = placeSummary('Berlin', berlin, GRADE);
  assert.match(p, new RegExp('Spaces on the atlas: ' + berlin.length));
  assert.match(p, /Grades: /);
  assert.match(p, /Flagged, with the reason on record/);
  assert.equal(placeSummary('Nowhere', [], GRADE), '');
});
