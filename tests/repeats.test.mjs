import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';

const ctx = {};
vm.runInNewContext(readFileSync(new URL('../assets/repeats.js', import.meta.url), 'utf8'), ctx);
const { dropRepeatedText, repeats, sentences } = ctx.AtlasRepeats;

test('a sentence the answer already gave is dropped the second time', () => {
  const t = 'Repsol is a fossil-fuel funder of the museum. Naturgy executives sit on the board.\n\n'
    + 'The board has eleven members. Repsol is a fossil-fuel funder of the museum.';
  assert.equal(dropRepeatedText(t), 'Repsol is a fossil-fuel funder of the museum. Naturgy executives sit on the board.\n\nThe board has eleven members.');
});

test('case, accents, quotes and bold do not hide a repeat', () => {
  const t = '**Musée d’Orsay** is funded by the French state and by patrons.\n\n- musee d\'orsay is funded by the French state and by patrons.';
  assert.equal(dropRepeatedText(t), '**Musée d’Orsay** is funded by the French state and by patrons.');
});

test('a sentence held whole in an earlier one is a repeat; a short label is never touched', () => {
  const t = 'Grade D. Black paid Epstein $158 million from 2012 to 2017, according to a 2021 Dechert review.\n\n'
    + 'Black paid Epstein $158 million from 2012 to 2017.\n\nGrade D.';
  assert.equal(dropRepeatedText(t), 'Grade D. Black paid Epstein $158 million from 2012 to 2017, according to a 2021 Dechert review.\n\nGrade D.');
});

test('near-identical sentences (nine words in ten) count as one', () => {
  const t = 'The museum received EUR 30.6M in project funds from the federal state in 2024.\n'
    + 'The museum received EUR 30.6M in project funds from the federal state during 2024.';
  assert.deepEqual(Array.from(repeats(t)), ['The museum received EUR 30.6M in project funds from the federal state during 2024.']);
});

test('initials, abbreviations and decimals do not split a sentence', () => {
  assert.equal(sentences('Run by the James H.W. Thompson Foundation since 1976. It shows silk.').length, 2);
  assert.equal(sentences('Income was EUR 3.5 million in 2024. Costs rose.').length, 2);
  assert.equal(sentences('It sits on St. Mark\'s Place, e.g. near the river. Free on Fridays.').length, 2);
});

test('headings and tables keep their shape; distinct text is untouched', () => {
  const t = '## Funding\n\n| a | b |\n|---|---|\n\nThe city funds it.\n\n## Funding';
  assert.equal(dropRepeatedText(t), t);
});

test('a source in brackets closing a sentence is not part of what it says', () => {
  const t = 'It is one of the theatres of the April Spring Friendship Art Festival (English Wikipedia).\n\n'
    + 'It is one of the theatres of the April Spring Friendship Art Festival.';
  assert.equal(dropRepeatedText(t), 'It is one of the theatres of the April Spring Friendship Art Festival (English Wikipedia).');
});
