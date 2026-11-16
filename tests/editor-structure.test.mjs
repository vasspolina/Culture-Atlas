// editor/structure.js shows a text as sentences, or a critique note as cited works, and must give back the stored text
// character for character, so a field that is only looked at in the data editor is saved unchanged.
import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
createRequire(import.meta.url)('../editor/structure.js');
const { sentences, joinSentences, citations, joinCitations } = globalThis.AtlasStructure;
const ALL = JSON.parse(readFileSync(new URL('../institutions.json', import.meta.url)));

test('every text in institutions.json splits into sentences and joins back unchanged', () => {
  const walk = v => {
    if (typeof v === 'string') { const { parts, gaps } = sentences(v); assert.equal(joinSentences(parts, gaps), v); }
    else if (v && typeof v === 'object') Object.values(v).forEach(walk);
  };
  ALL.forEach(walk);
});

test('initials, abbreviations and U.S. do not end a sentence', () => {
  assert.deepEqual(sentences('T. J. Demos argues this. Over 200 people, e.g. Mr. Smith, signed. The U.S. Embassy said so. It ends.').parts,
    ['T. J. Demos argues this.', 'Over 200 people, e.g. Mr. Smith, signed.', 'The U.S. Embassy said so.', 'It ends.']);
});

test('every critique note splits into cited works and joins back unchanged', () => {
  const notes = ALL.filter(r => r.critique_note);
  assert.ok(notes.length > 0);
  for (const r of notes) {
    const c = citations(r.critique_note);
    assert.ok(c, r.id);
    assert.equal(joinCitations(c), r.critique_note, r.id);
    for (const e of c) assert.match(e.head, /^\S.*, .*\(.+, .*\d{4}.*\)$/, `${r.id}: ${e.head}`);
  }
});

test('a title with ?! inside stays in its citation', () => {
  const t = "A Author, Work One (e-flux, 2020): It says one thing. Veda Popovici, So You Think You're Political?! Notes (ArtLeaks Gazette, 2013): Popovici says another.";
  assert.deepEqual(citations(t).map(e => e.head), ['A Author, Work One (e-flux, 2020)', "Veda Popovici, So You Think You're Political?! Notes (ArtLeaks Gazette, 2013)"]);
});
