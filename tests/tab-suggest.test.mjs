import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
createRequire(import.meta.url)('../assets/tab-suggest.js');
const { suggest, buildIndex } = globalThis.AtlasTabSuggest;
const raw = JSON.parse(readFileSync(new URL('../institutions.json', import.meta.url)));
const index = buildIndex(Array.isArray(raw) ? raw : raw.institutions);

test('a question is finished from its start', () => {
  assert.equal(suggest('who fu', index), 'nds MoMA?');
  assert.equal(suggest('Which museums take o', index), 'il and gas money?');
});
test('a space or city named at the end is finished', () => {
  assert.equal(suggest('tell me about Stedelijk Mus', index), 'eum');
  assert.equal(suggest('what about Tate Mo', index), 'dern');
  assert.equal(suggest('who funds the Guggen', index), 'heim');
  assert.equal(suggest('museums in Berl', index), 'in');
});
test('accents do not get in the way', () => {
  assert.equal(suggest("musee d'ors", index), 'ay');
  assert.match(suggest('Auckland Art Gallery Toi o Ta', index), /^m[aā]ki$/);
});
test('nothing is offered for too little, a common word, or a finished name', () => {
  assert.equal(suggest('w', index), '');
  assert.equal(suggest('what about the', index), '');
  assert.equal(suggest('Who funds MoMA?', index), '');
  assert.equal(suggest('hello ', index), '');
  assert.equal(suggest('two\nlines', index), '');
});
