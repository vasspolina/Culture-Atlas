import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
createRequire(import.meta.url)('../assets/names.js');
// The file registers itself on globalThis in Node (package.json is type: module, so module.exports is not set there).
const { findNamedSpace, stems } = globalThis.AtlasNames;
const raw = JSON.parse(readFileSync(new URL('../institutions.json', import.meta.url)));
const ALL = Array.isArray(raw) ? raw : raw.institutions;
const byName = (n) => ALL.find(i => i.name === n);

test('stems translate the museum words to English', () => {
  assert.deepEqual(stems('Jüdisches Museum Berlin'), ['jewish', 'museum', 'berlin']);
  assert.deepEqual(stems("Musée d'Orsay"), ['museum', 'd', 'orsay']);
});
test('the English name of a German space resolves, in either order', () => {
  assert.equal(findNamedSpace('Jewish museum berlin', ALL), byName('Jüdisches Museum Berlin'));
  assert.equal(findNamedSpace('berlin jewish museum', ALL), byName('Jüdisches Museum Berlin'));
  assert.equal(findNamedSpace('tell me about the jewish museum berlin?', ALL), byName('Jüdisches Museum Berlin'));
});
test('a city plus "museum" names no one space', () => {
  assert.equal(findNamedSpace('museums in berlin', ALL), null);
  assert.equal(findNamedSpace('berlin museum', ALL), null);
  assert.equal(findNamedSpace('berlin', ALL), null);
  assert.equal(findNamedSpace('museums in Sofia', ALL), null);
  assert.equal(findNamedSpace('state museums berlin', ALL), null);
});
test('a name typed as spelled still resolves', () => {
  assert.equal(findNamedSpace('Deutsches Historisches Museum', ALL), byName('Deutsches Historisches Museum'));
  assert.equal(findNamedSpace('german history museum', ALL), byName('Deutsches Historisches Museum'));
  assert.equal(findNamedSpace('neue nationalgalerie berlin', ALL), byName('Neue Nationalgalerie'));
});
