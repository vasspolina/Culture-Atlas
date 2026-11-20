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
  // The case is the test's own: the record's case notes change with the research, the rule that a full record carries them does not.
  const withCase = { ...tate, case_notes: [{ title: 'BP sponsorship ends', meta: '2016-03-11', text: 'BP ended its Tate sponsorship.', sources: ['https://example.org'] }] };
  const t = formatRecord(withCase, { status: 'Grade F', watchGossip: true, full: true });
  assert.match(t, /Audited figures FY2025-26/);
  assert.match(t, /income GBP 194\.9 million/);
  assert.match(t, /Legal form: statutory public body/);
  assert.match(t, /Case: BP sponsorship ends, 2016-03-11/);
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
  assert.match(p, new RegExp('Museums on the atlas: ' + berlin.length));
  assert.match(p, /Grades: /);
  assert.match(p, /Flagged, with the reason on record/);
  assert.equal(placeSummary('Nowhere', [], GRADE), '');
});

// What funders got in return (user, 20 Nov 2026: the chat "did not answer the second half of the question (what funders get in
// return), although the influence data holds it"). The ledger here is the test's own, so the rule is tested and not the research.
const { returnsFor, returnsMarkdown, UNGRADED_WHY } = ctx.AtlasGrounding;
const ledger = { funders: [
  { key: 'oilco', name: 'OilCo', ties: [
    { space: 'm1', space_name: 'Museum One', kinds: ['building'], summary: 'Paid for the new wing, announced in 2023', date: '2023-12', ended: false },
    { space: 'm1', space_name: 'Museum One', kinds: ['access'], summary: 'Held its annual reception at the museum.', date: '2015-11', ended: false },
    { space: 'm1', space_name: 'Museum One', kinds: [], summary: 'A trustee resigned over the deal.', date: '2019', ended: false },
    { space: 'm2', space_name: 'Museum Two', kinds: ['name'], summary: 'Its name on the portrait prize.', date: '2020', ended: true }
  ] },
  { key: 'trust', name: 'Quiet Trust', ties: [{ space: 'm1', space_name: 'Museum One', kinds: ['money'], summary: 'Is named as a funder.', date: '2021', ended: false }] }
] };
const labels = { building: 'A building or endowment', access: 'Galas and perks', name: 'Its name on a building, room or prize' };

test('what funders got in return at a museum leaves out money-only ties and protests', () => {
  const got = returnsFor(ledger, { space: 'm1', labels });
  assert.equal(got.length, 2);
  assert.deepEqual(Array.from(got, x => x.funder), ['OilCo', 'OilCo']);
  assert.match(got[0].summary, /new wing/);   // newest first
  const md = returnsMarkdown(got);
  assert.match(md, /^- OilCo: a building or endowment\. Paid for the new wing, announced in 2023\.$/m);
  assert.doesNotMatch(md, /Quiet Trust|resigned/);
});

test('a funder named with no museum gets its ties museum by museum, and an ended tie says so', () => {
  const got = returnsFor(ledger, { funders: ['oilco'], labels });
  assert.equal(got.length, 3);
  const md = returnsMarkdown(got, { bySpace: true, max: 2 });
  assert.match(md, /^- Museum One: /m);
  assert.match(md, /^- 1 more on the record\.$/m);
  assert.match(returnsMarkdown(got, { bySpace: true }), /Museum Two: its name on a building, room or prize\. Its name on the portrait prize\. The tie has ended\./);
  assert.equal(returnsMarkdown([]), '');
});

test('a place summary says why its ungraded museums have no grade', () => {
  const p = placeSummary('Testville', [{ name: 'Graded', grade: 5 }, { name: 'Ungraded' }], GRADE);
  assert.match(p, /Grades: 1 Grade F, 1 not graded \(not graded because /);
  assert.ok(p.includes(UNGRADED_WHY));
});
