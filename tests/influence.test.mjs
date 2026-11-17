// Influence mode (assets/influence-mode.js) shows only what data/influence_review.json keeps, through assets/influence.json.
// An entry reaches the page only with a summary, a kind the layer knows (or none, for pushback alone), a space the atlas has,
// and a source; and every reviewed candidate must still be a sentence of the records, or the review has gone stale.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const read = (p) => JSON.parse(readFileSync(new URL('../' + p, import.meta.url), 'utf8'));
const layer = read('assets/influence.json');
const review = read('data/influence_review.json');
const cands = read('data/influence_candidates.json');
const ids = new Set(read('institutions.json').map((i) => i.id));
const kinds = new Set(layer.kinds.map((k) => k.key));

test('every entry has a summary, known kinds, a real space and a source', () => {
  let n = 0;
  for (const f of layer.funders) {
    assert.ok(f.key && f.name, 'a funder has a key and a name');
    for (const t of f.ties) {
      n++;
      assert.ok(t.summary && t.summary.length > 8, `${f.name} at ${t.space_name}: a summary`);
      assert.ok(ids.has(t.space), `${f.name}: ${t.space} is a record`);
      t.kinds.forEach((k) => assert.ok(kinds.has(k), `${f.name} at ${t.space_name}: kind ${k}`));
      assert.ok(t.kinds.length || t.ended || t.protest, `${f.name} at ${t.space_name}: a kind, or pushback`);
      assert.ok(t.sources.length && t.sources.every((u) => /^https?:\/\//.test(u)), `${f.name} at ${t.space_name}: a source`);
      assert.ok(!/—/.test(t.summary), `${f.name} at ${t.space_name}: no em dash in a summary`);
    }
  }
  assert.ok(n > 0, 'the layer has entries');
});

test('every reviewed candidate is still in the records', () => {
  const live = new Set(cands.map((c) => c.cid));
  const stale = Object.keys(review).filter((k) => !k.startsWith('_') && !live.has(k));
  assert.deepEqual(stale, []);
});

test('the layer holds exactly the kept reviews', () => {
  const kept = Object.entries(review).filter(([k, v]) => !k.startsWith('_') && !v.drop).length;
  assert.equal(layer.funders.reduce((s, f) => s + f.ties.length, 0), kept);
});

// The sender's side (data/influence_senders.json): every fact is a short sentence with a known kind, a date and its own
// source, and every key is a funder the layer has, so a misspelt key cannot silently drop a funder's facts.
test('every sender fact has a known kind, a date and a source', () => {
  const senders = read('data/influence_senders.json');
  const keys = new Set(layer.funders.map((f) => f.key));
  const factKinds = new Set(['harm', 'scale', 'lobbying', 'politics', 'after']);
  for (const [k, v] of Object.entries(senders)) {
    if (k.startsWith('_')) continue;
    assert.ok(keys.has(k), `${k} is a funder in the layer`);
    for (const x of v.facts || []) {
      assert.ok(factKinds.has(x.kind), `${k}: kind ${x.kind}`);
      assert.ok(x.text && x.text.length > 8 && !/—/.test(x.text), `${k}: a sentence with no em dash`);
      assert.ok(/^(19|20)\d\d(-\d\d)?$/.test(String(x.date)), `${k}: a date, ${x.date}`);
      assert.ok(/^https?:\/\//.test(x.source), `${k}: a source`);
    }
  }
});

// The map's measures (Influence mode's filters) read each funder's `figures`: cultural giving next to lobbying and political
// giving. Every figure is a number with its own source, so a measure on the map can always be traced to a filing.
test('every funder figure is a number with a source', () => {
  const senders = read('data/influence_senders.json');
  for (const [k, v] of Object.entries(senders)) {
    if (k.startsWith('_') || !v.figures) continue;
    const f = v.figures;
    assert.ok(f.culture && Number.isInteger(f.culture.spaces), `${k}: culture spaces`);
    if (f.culture.largest_gift) assert.ok(f.culture.largest_gift.amount > 0 && /^https?:\/\//.test(f.culture.largest_gift.source) && !/—/.test(f.culture.largest_gift.text), `${k}: largest gift`);
    if (f.us_lobbying) assert.ok(f.us_lobbying.usd > 0 && /lda\.gov/.test(f.us_lobbying.source), `${k}: US lobbying`);
    if (f.eu_lobbying) assert.ok(f.eu_lobbying.eur_max > f.eu_lobbying.eur_min && /lobbyfacts\.eu/.test(f.eu_lobbying.source), `${k}: EU lobbying`);
    if (f.personal) {
      assert.ok(f.personal.usd > 0 && Array.isArray(f.personal.people) && f.personal.people.length, `${k}: personal giving`);
      f.personal.people.forEach((x) => assert.ok(x.name && x.usd > 0 && /fec\.gov/.test(x.source), `${k}: personal giving by ${x.name}`));
      assert.ok(Math.abs(f.personal.people.reduce((t, x) => t + x.usd, 0) - f.personal.usd) < 1, `${k}: personal total is the sum of its people`);
    }
    if (f.political) assert.ok(f.political.usd > 0 && f.political.rep_usd >= 0 && f.political.dem_usd >= 0 && f.political.rep_usd + f.political.dem_usd <= f.political.usd * 1.05 && /fec\.gov/.test(f.political.source), `${k}: political giving`);
  }
});

// Checked against source pages: an entry says how far it is checked, and a checked one links the page that bears it out.
test('every entry says how far it is checked, and a checked one names its page', () => {
  for (const f of layer.funders) for (const t of f.ties) {
    assert.ok(['source', 'source-partly', 'record'].includes(t.check), `${f.name} at ${t.space_name}: check ${t.check}`);
    if (t.check !== 'record') assert.ok(/^https?:\/\//.test(t.checked_source || ''), `${f.name} at ${t.space_name}: the page that bears it out`);
    if (t.check === 'source-partly') assert.ok(t.checked_missing && !/—/.test(t.checked_missing), `${f.name} at ${t.space_name}: what the page does not give`);
  }
});
