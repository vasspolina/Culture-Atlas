// In Gossip mode a money or governance question about one space is answered as asked, and the space's gossip comes first
// (user, 21 Nov 2026: "It's just giving me general answers not gossip"). The page prints those lines itself: with the chat
// model the answer to "Who funds MoMA?" was the plain funding record and no gossip at all.
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFileSync } from 'node:fs';

const html = readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const css = readFileSync(new URL('../assets/sheet.css', import.meta.url), 'utf8');
const lift = (name, re) => {
  const m = html.match(re);
  if (!m) throw new Error('not found in index.html: ' + name);
  return m[0];
};
const src = [
  lift('gossipItems', /function gossipItems\(inst, fresh\) \{[\s\S]*?\n    \}\n/),
  lift('GOSSIP_STATUS_LINE', /const GOSSIP_STATUS_LINE = \{[\s\S]*?\};\n/),
  lift('GOSSIP_MONEY', /const GOSSIP_MONEY = .*\n/),
  lift('gossipAheadLines', /function gossipAheadLines\(inst\) \{[\s\S]*?\n    \}\n/),
].join('\n');
const ctx = {
  watchIsGossip: (w) => /epstein|protest|fined/i.test(String(w || '')),
  proseEnd: (t) => { t = String(t || '').trim(); return !t ? '' : /[.!?]$/.test(t) ? t : t + '.'; },
  gossipAttribution: (g) => `Reported by ${g.where}, ${g.when}.`,
};
vm.createContext(ctx);
vm.runInContext(src + '\nthis.api = { gossipAheadLines, GOSSIP_MONEY };', ctx);
const { GOSSIP_MONEY } = ctx.api;
// An array made inside the vm context belongs to another realm, so it is copied into this one before it is compared.
const gossipAheadLines = (inst) => [...ctx.api.gossipAheadLines(inst)];
const item = (headline, kind, status, when) => ({ headline, kind, status, when, where: 'The Art Newspaper' });
const space = (watch, items) => ({ name: 'A museum', watch, gossip_data: { gossip: items } });

test('the watch line leads when it is gossip, then the two newest items about the money', () => {
  const lines = gossipAheadLines(space('A trustee keeps his seat after the Epstein payments were questioned.', [
    item('Curators walk out over the hang of the new wing', 'dispute', 'talk', '2026-10-01'),
    item('Protesters name five trustees over arms investments', 'allegation', 'talk', '2026-05-01'),
    item('A donor asks for her gift back', 'money', 'denied', '2025-11-01'),
    item('The board cuts the acquisitions budget', 'report', 'confirmed', '2025-02-01'),
  ]));
  assert.equal(lines.length, 3);
  assert.equal(lines[0], 'A trustee keeps his seat after the Epstein payments were questioned.');
  assert.equal(lines[1], 'Protesters name five trustees over arms investments. Reported by The Art Newspaper, 2026-05-01. Nobody has confirmed it.');
  assert.equal(lines[2], 'A donor asks for her gift back. Reported by The Art Newspaper, 2025-11-01. It has been denied.');
});

test('with no item about money, the newest item alone; a clean watch line is not gossip', () => {
  const lines = gossipAheadLines(space('No flagged funder found.', [
    item('Curators walk out over the hang of the new wing', 'dispute', 'confirmed', '2026-10-01'),
    item('The director leaves after two years', 'departure', 'talk', '2026-01-01'),
  ]));
  assert.deepEqual(lines, ['Curators walk out over the hang of the new wing. Reported by The Art Newspaper, 2026-10-01. It has been confirmed.']);
});

test('a stale item is not told, and a record with no gossip gets no lines', () => {
  assert.deepEqual(gossipAheadLines(space('', [item('An old row over a sponsor', 'money', 'stale', '2019-01-01')])), []);
  assert.deepEqual(gossipAheadLines(space('', [])), []);
  assert.deepEqual(gossipAheadLines(null), []);
});

test('what counts as talk about the money', () => {
  for (const t of ['over trustee Leon Black', 'a donor scandal', 'the board met', 'funding cut by a third', 'sponsors withdraw', 'an unpaid debt']) assert.match(t, GOSSIP_MONEY, t);
  for (const t of ['Curators walk out over the hang', 'The director leaves', 'A review calls the show thin']) assert.doesNotMatch(t, GOSSIP_MONEY, t);
});

test('the page puts the lines ahead of both kinds of answer, and tells the model what it printed', () => {
  // The model's answer, and the record's own answer when no model is there.
  assert.match(html, /<div class="chat-answer-sourced">\$\{ahead\}\$\{linked\}\$\{srcLine\}<\/div>/);
  assert.match(html, /answer\(`\$\{ahead\}\$\{absent\}<p>\$\{formatInstLink\(target\)\}/);
  assert.match(html, /the page prints this museum's gossip itself, above your answer/);
  assert.match(html, /const aheadLines = gossipOnNow && !isGossipMode && !themed && aboutOne \? gossipAheadLines\(aboutOne\) : \[\];/);
});

test('gossip in the chat is set upright, in its colour alone', () => {
  // User, 21 Nov 2026: "do not make it italics".
  const rules = css.match(/[^{}]*\.is-gossip \[data-gossip\][^{}]*\{[^{}]*\}/g) || [];
  assert.ok(rules.length > 0);
  for (const r of rules) assert.doesNotMatch(r, /font-style\s*:\s*italic/, r.slice(0, 120));
  assert.ok(rules.some(r => /color:#7a4416/.test(r)));
});

test('the line of the text carries the 10% added on 21 Nov 2026', () => {
  // User: "add 10% line height to all text". One factor, on the text's line and the large size's line, phone and desktop.
  assert.match(css, /--sh-up:1\.1;/);
  assert.match(css, /--sh-lead:calc\(var\(--sh-s-lh\) \* 0\.85 \* var\(--sh-up\)\);/);
  const large = css.match(/--sh-l-lh:calc\([^;}]*\)/g) || [];
  assert.equal(large.length, 2);
  for (const d of large) assert.match(d, /\* var\(--sh-up\)\)$/, d);
  // The old stylesheet's ratio (--lh) is the same line: 19 * 0.85 * 1.1 / 15.
  const lh = Number((css.match(/--lh:([\d.]+)!important/) || [])[1]);
  assert.ok(Math.abs(lh - 19 * 0.85 * 1.1 / 15) < 0.001, String(lh));
});
