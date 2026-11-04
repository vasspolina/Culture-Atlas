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

test('a post by staff or visitors is marked as one, never as press', () => {
  for (const x of live.items.filter((i) => i.type === 'account')) {
    assert.equal(x.who_says, 'user_post', x.id);
    assert.equal(x.status, 'user', x.id);
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
    } else if (x.type === 'account') {
      // A staff or visitor post: one of the record's accounts, at the same address, posted on the same day.
      const a = ((inst.gossip_data || {}).accounts || []).find((i) => i.id === x.id && (i.sources || []).some((s) => s && s.url === x.urls[0]));
      assert.ok(a, 'no such account on the record: ' + x.id);
      assert.ok(JSON.stringify(a.fields).includes(x.when), 'the post date is not the record’s: ' + x.id);
    } else if (x.type === 'leak') {
      // One cable can carry two findings about a space, so the entry is found by its id, address and words together.
      const w = (inst.wikileaks_records || []).find((i) => i.doc_id === x.id && (i.sources || []).includes(x.urls[0]) && i.what_shows === x.said);
      assert.ok(w, 'no such document on the record: ' + x.id);
      assert.ok(String(w.date).includes(x.when));
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
