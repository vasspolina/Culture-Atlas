// assets/live.json is what the phone's Top story feed, its alerts and Gossip mode's minute-by-minute check read
// (tools/build_live_feed.py writes it). These tests hold it to the rule that nothing in it is made up: every item is a
// record's own item, word for word, with a date and an address to check it against.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const live = JSON.parse(readFileSync(new URL('../assets/live.json', import.meta.url)));
const stamp = JSON.parse(readFileSync(new URL('../assets/live-stamp.json', import.meta.url)));
const raw = JSON.parse(readFileSync(new URL('../institutions.json', import.meta.url)));
const ALL = Array.isArray(raw) ? raw : raw.institutions;
const byId = new Map(ALL.map((i) => [i.id || i.name, i]));

test('the stamp describes the file', () => {
  assert.equal(stamp.count, live.items.length);
  assert.equal(stamp.newest, live.newest);
  assert.equal(stamp.generated, live.generated);
});

test('every item has a date and at least one web address', () => {
  for (const x of live.items) {
    assert.match(x.when, /^\d{4}-\d{2}(-\d{2})?$/, x.headline);
    assert.ok(x.urls.length > 0, x.headline);
    for (const u of x.urls) assert.match(u, /^https?:\/\//, x.headline);
  }
});

test('every gossip item names its source and the day its addresses were last opened', () => {
  for (const x of live.items.filter((i) => i.type === 'gossip')) {
    assert.ok(x.who_says && x.where, x.headline);
    assert.match(x.checked, /^\d{4}-\d{2}-\d{2}$/, x.headline);
  }
});

test('every item is a record’s own, word for word', () => {
  for (const x of live.items) {
    const inst = byId.get(x.inst);
    assert.ok(inst, 'no record for ' + x.inst);
    if (x.type === 'gossip') {
      const g = ((inst.gossip_data || {}).gossip || []).find((i) => i.headline === x.headline);
      assert.ok(g, 'not on the record: ' + x.headline);
      assert.equal(x.said, g.said || '');
      assert.equal(x.where, g.where);
      assert.equal(x.when, g.when);
      assert.equal(x.status, g.status || 'talk');
    } else {
      // Several case notes share a title ("Democracy Now! report"), so the note is found by title, date and text together.
      const c = (inst.case_notes || []).find((i) => i.title === x.headline && i.meta === x.when && (i.text || '') === x.said);
      assert.ok(c, 'not on the record: ' + x.headline + ', ' + x.when);
    }
  }
});

test('the feed is current with the records (rerun tools/build_live_feed.py after changing institutions.json)', () => {
  const onRecord = ALL.reduce((n, i) => n + (((i.gossip_data || {}).gossip || []).filter((g) => g && g.headline && g.retrieved_on && (g.urls || []).length).length), 0);
  const inFeed = live.items.filter((i) => i.type === 'gossip').length;
  assert.equal(inFeed, onRecord);
});

test('items run newest first', () => {
  for (let i = 1; i < live.items.length; i++) assert.ok(live.items[i - 1].when >= live.items[i].when);
});
