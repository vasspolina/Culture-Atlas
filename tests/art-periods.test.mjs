// What art each funder's money goes to (assets/art-periods.json, tools/build_art_periods.py). Every period or field a space
// is given rests on a sentence of its own record, and every tie read for the art it paid for is a tie of the ledger with that
// summary, so a record edit cannot leave the page claiming what the atlas no longer says.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const read = (p) => JSON.parse(readFileSync(new URL('../' + p, import.meta.url), 'utf8'));
const art = read('assets/art-periods.json');
const insts = new Map(read('institutions.json').map((i) => [i.id, i]));
const layer = read('assets/influence.json');
const periods = new Set(art.periods.map((p) => p.key));
const fields = new Set(art.fields.map((f) => f.key));

test('every space read rests on a sentence of its own record', () => {
  let n = 0;
  for (const [id, s] of Object.entries(art.spaces)) {
    const x = insts.get(id);
    assert.ok(x, `${id} is a record`);
    const text = [x.name, ...((x.details && x.details.overview) || [])].join(' ');
    assert.ok(Array.isArray(s.q) && s.q.length, `${id}: the sentence that decided it`);
    s.q.forEach((q) => assert.ok(text.includes(q), `${id}: "${q.slice(0, 60)}" is in its record`));
    assert.ok(fields.has(s.f), `${id}: field ${s.f}`);
    (s.p || []).forEach((p) => assert.ok(periods.has(p), `${id}: period ${p}`));
    if (s.p) assert.ok(s.f === 'all' ? s.p.length >= 4 : s.p.length < 4, `${id}: four or more periods is every period`);
    n++;
  }
  assert.ok(n > 1000, 'most spaces are read');
});

test('every tie read for its art is a ledger tie with that summary', () => {
  const ties = new Map(layer.funders.flatMap((f) => f.ties.map((t) => [t.cid, t])));
  for (const [cid, t] of Object.entries(art.ties)) {
    assert.ok(ties.has(cid), `${cid} is a ledger tie`);
    assert.equal(ties.get(cid).summary, t.q, `${cid}: the summary it was read from`);
    t.p.forEach((p) => assert.ok(periods.has(p), `${cid}: period ${p}`));
  }
});

test('a building, another museum or a library is not read as the art', () => {
  const s = (id) => art.spaces[id] || {};
  const byName = (n) => [...insts.values()].find((x) => x.name === n).id;
  // "a modernist main building", "in the medieval Agnietenklooster": the building's age, not the art's.
  assert.ok(!(s(byName('Art Gallery of Western Australia')).q || []).some((q) => /modernist main building/.test(q)));
  assert.ok(!(s(byName('Centraal Museum')).p || []).includes('old'));
  // The Prado "absorbed the Museo de Arte Moderno": another museum's name.
  assert.ok(!(s(byName('Museo del Prado')).p || []).includes('modern'));
  // The Renaissance Society is a contemporary art space.
  assert.deepEqual(s(byName('The Renaissance Society')).p, ['contemporary']);
});
