import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
createRequire(import.meta.url)('../assets/subtopic.js');
// The file registers itself on globalThis in Node (package.json is type: module, so module.exports is not set there).
const { detectSubTopic, subTopicBlock, subTopicRecordAnswer } = globalThis.AtlasSubTopic;

const moma = { name: 'MoMA (The Museum of Modern Art)', grade: 3, highlight: "A modernist museum holding Van Gogh's Starry Night. It has been audited for private equity board ties.", funding: 'Admissions, Bloomberg Philanthropies, UNIQLO.' };
const withArchive = { name: 'Example Museum', highlight: 'Holds a film archive of 4,000 reels. Founded 1950.' };

test('archive beside a resolved space is a sub-topic', () => {
  assert.equal(detectSubTopic('tell me about museum archive at moma', moma).key, 'archive');
  assert.equal(detectSubTopic('tell me about MoMA', moma), null);
});
test("the space's own name is not a sub-topic", () => {
  assert.equal(detectSubTopic('who funds the Wiener Library', { name: 'Wiener Library' }), null);
});
test('record without the topic: block says so, fallback does not return the generic record', () => {
  const t = detectSubTopic('museum archive at moma', moma);
  assert.match(subTopicBlock(t, moma), /holds nothing on it/);
  const a = subTopicRecordAnswer(t, moma);
  assert.equal(a.held, false);
  assert.match(a.text, /no record on the archive of MoMA/);
  assert.doesNotMatch(a.text, /Grade|funder|Bloomberg/);
});
test('record with the topic: only those lines are given', () => {
  const t = detectSubTopic('the archive at example museum', withArchive);
  const a = subTopicRecordAnswer(t, withArchive);
  assert.equal(a.held, true);
  assert.equal(a.text, 'Holds a film archive of 4,000 reels.');
  assert.match(subTopicBlock(t, withArchive), /- Holds a film archive/);
});

const yemisi = { name: 'Yemisi Shyllon Museum of Art', funding: 'University museum opened 2019, endowed by collector Prince Yemisi Shyllon.', watch: 'On the Pan-Atlantic University campus.', highlight: 'Designed by the architect Jess Castellote.' };
test('anything else asked about a space is a free topic, answered from its lines or not at all', () => {
  const { detectFreeTopic } = globalThis.AtlasSubTopic;
  const sym = detectFreeTopic('symbol of the museum', yemisi);
  assert.equal(sym.label, 'symbol');
  const a = subTopicRecordAnswer(sym, yemisi);
  assert.equal(a.held, false);
  assert.match(a.text, /no record on the symbol of Yemisi Shyllon Museum of Art/);
  assert.doesNotMatch(a.text, /Funding|endowed|Pan-Atlantic/);
  const arch = subTopicRecordAnswer(detectFreeTopic('who is the architect of the Yemisi Shyllon Museum of Art?', yemisi), yemisi);
  assert.equal(arch.held, true);
  assert.equal(arch.text, 'Designed by the architect Jess Castellote.');
});
test('a question about the space as a whole is not a free topic', () => {
  const { detectFreeTopic } = globalThis.AtlasSubTopic;
  for (const q of ['tell me about Yemisi Shyllon Museum of Art', 'what is this museum?', 'tell me more about it', 'Yemisi Shyllon Museum of Art']) assert.equal(detectFreeTopic(q, yemisi), null, q);
});
