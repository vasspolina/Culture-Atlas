import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
const { detectSubTopic, subTopicBlock, subTopicRecordAnswer } = createRequire(import.meta.url)('../assets/subtopic.js');

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
