// The page reloads itself when the release it was built as (ATLAS_RELEASE in index.html) differs from the live one
// (CACHE_NAME in sw.js). If the two drift apart, every new tab loads, paints, and loads again, so they must match.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const read = (p) => readFileSync(new URL('../' + p, import.meta.url), 'utf8');

test('index.html and sw.js name the same release', () => {
  const page = /const ATLAS_RELEASE = '([^']+)'/.exec(read('index.html'));
  const worker = /CACHE_NAME\s*=\s*'([^']+)'/.exec(read('sw.js'));
  assert.ok(page && worker, 'both release names are found');
  assert.equal(page[1], worker[1]);
});
