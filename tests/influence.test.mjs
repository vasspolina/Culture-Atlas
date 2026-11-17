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
