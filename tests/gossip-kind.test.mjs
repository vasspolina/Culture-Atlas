// A question about a kind of story ("Which directors left under a cloud?") names no space. It is answered from the gossip
// items of that kind across the records; it once printed "Nothing is reported for this space in the records" instead.
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { readFileSync } from 'node:fs';

const html = readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const lift = (name, re) => {
  const m = html.match(re);
  if (!m) throw new Error('not found in index.html: ' + name);
  return m[0];
};
const src = [
  lift('GOSSIP_STATUS_LINE', /const GOSSIP_STATUS_LINE = \{[\s\S]*?\n    \};\n/),
  lift('gossipStatusLine', /const gossipStatusLine = .*\n/),
  lift('KIND_CHIP', /const KIND_CHIP = \{[\s\S]*?\n    \};\n/),
  lift('GOSSIP_KIND_ASK', /const GOSSIP_KIND_ASK = \[[\s\S]*?\n    \];\n/),
  lift('gossipKindOf', /function gossipKindOf\(query\) \{[\s\S]*?\n    \}\n/),
  lift('gossipItemLine', /function gossipItemLine\(x\) \{[\s\S]*?\n    \}\n/),
  lift('gossipPool', /function gossipPool\(\) \{[\s\S]*?\n    \}\n/),
  lift('gossipItems', /function gossipItems\(inst, fresh\) \{[\s\S]*?\n    \}\n/),
  lift('hostOf', /function hostOf\(u\) \{.*\}\n/),
].join('\n');
const raw = JSON.parse(readFileSync(new URL('../institutions.json', import.meta.url)));
const ALL = Array.isArray(raw) ? raw : raw.institutions;
const ctx = {
  ALL_INSTITUTIONS: ALL, URL,
  escapeHtml: (t) => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;'),
  placeLabel: (i) => i.city || '',
  proseEnd: (t) => /[.!?]$/.test(t) ? t : t + '.',
  gossipAttribution: (g) => `Reported by ${g.where}, ${g.when}.`,
};
vm.createContext(ctx);
vm.runInContext(src + '\nthis.api = { KIND_CHIP, gossipKindOf, gossipItemLine, gossipPool };', ctx);
const { KIND_CHIP, gossipKindOf, gossipItemLine, gossipPool } = ctx.api;

test('each chip question asks for its own kind of story', () => {
  for (const [kind, questions] of Object.entries(KIND_CHIP)) {
    for (const q of questions) assert.equal((gossipKindOf(q) || {}).kind, kind, q);
  }
});
test('the records hold items for every kind a chip asks about', () => {
  const pool = gossipPool();
  for (const kind of Object.keys(KIND_CHIP)) assert.ok(pool.some(x => x.g.kind === kind), kind);
});
test('a question about the space in view, or about something else, is not a kind question', () => {
  for (const q of ['Did its director resign?', 'Was there a strike here?', 'Who funds MoMA?', 'What is the gossip about Tate Modern?', 'Which spaces are flagged?']) {
    assert.equal(gossipKindOf(q), null, q);
  }
});
test('a line gives the space, the headline, who says it, its status and a link to the source', () => {
  const x = gossipPool().find(y => y.g.kind === 'departure');
  const line = gossipItemLine(x);
  assert.ok(line.includes(`data-name="${ctx.escapeHtml(x.inst.name)}"`));
  assert.ok(line.includes(ctx.escapeHtml(x.g.headline.replace(/\.$/, ''))));
  assert.ok(line.includes('Reported by'));
  assert.match(line, /Source: <a href="https?:\/\//);
  assert.doesNotMatch(line, /Nothing is reported/);
});
