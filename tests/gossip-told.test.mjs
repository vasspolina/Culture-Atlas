// In Gossip mode a gossip item is told in the mode's voice: its `told`, shown in place of `said` (user, 21 Nov 2026: "it just
// not changing content to gossip", then "Retell in gossip voice"). A retelling adds nothing to the item it retells.
// tools/attach_gossip.py (told_errors) is the gate when a retelling is written; this checks what is in the files.
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFileSync } from 'node:fs';

const read = (p) => readFileSync(new URL('../' + p, import.meta.url), 'utf8');
const html = read('index.html');
const items = JSON.parse(read('data/gossip_items.json'));
const records = JSON.parse(read('institutions.json'));
const told = items.filter(it => it.told);
const plain = (s) => String(s || '').replace(/[“”]/g, '"').replace(/[‘’]/g, "'");
const source = (it) => plain(['headline', 'said', 'response', 'outcome', 'where', 'institution'].map(f => it[f] || '').join(' '));
const figures = (s) => new Set(s.match(/\d+(?:[.,]\d+)*/g) || []);

test('some items are retold, and each retelling is text of a sane length', () => {
  assert.ok(told.length > 0);
  for (const it of told) {
    assert.equal(typeof it.told, 'string', it.id);
    assert.ok(it.told.length >= 80 && it.told.length <= it.said.length * 1.2 + 80, it.id);
  }
});

test('a retelling has no figure and no quotation its item does not carry', () => {
  for (const it of told) {
    const src = source(it), t = plain(it.told);
    for (const n of figures(t)) assert.ok(figures(src).has(n), `${it.id}: figure ${n}`);
    for (const m of t.matchAll(/"([^"]+)"/g)) assert.ok(src.includes(m[1].replace(/[.,]+$/, '')), `${it.id}: quotation ${m[1].slice(0, 40)}`);
  }
});

test('a retelling has no dash and claims no source of its own', () => {
  const own = /\b(?:my (?:own )?(?:sources?|reporting|investigation)|sources? (?:tell|told) me|I (?:have )?(?:obtained|interviewed|spoke(?:n)? (?:to|with)|uncovered|confirmed|verified))\b/i;
  for (const it of told) {
    assert.doesNotMatch(it.told, /[—–]|\s-\s/, it.id);
    assert.doesNotMatch(it.told, own, it.id);
  }
});

test('the records carry the same retellings as the items file', () => {
  const onRecords = new Map();
  records.forEach(r => (((r.gossip_data || {}).gossip) || []).forEach(g => { if (g.told) onRecords.set(g.id, g.told); }));
  assert.equal(onRecords.size, told.length);
  for (const it of told) assert.equal(onRecords.get(it.id), it.told, it.id);
});

test('the page shows the retelling only while Gossip mode is on', () => {
  const src = html.match(/const gossipSaid = .*\n/)[0];
  const ctx = { isGossipModeActive: false };
  vm.createContext(ctx);
  vm.runInContext(src + '\nthis.gossipSaid = gossipSaid;', ctx);
  const g = { said: 'The record.', told: 'The retelling.' };
  assert.equal(ctx.gossipSaid(g), 'The record.');
  vm.runInContext('isGossipModeActive = true;', ctx);
  assert.equal(ctx.gossipSaid(g), 'The retelling.');
  assert.equal(ctx.gossipSaid({ said: 'The record.' }), 'The record.');
  // The feed's cards do the same, and the model is still given the record's words.
  const feed = read('assets/phone-maps.js');
  assert.match(feed, /const said = gossipOn\(\) && x\.told \? x\.told : saidRest\(x\);/);
  assert.doesNotMatch(read('assets/grounding.js'), /\.told\b/);
});
