import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';

// The page's own name matching, lifted out of index.html so a typed name is tested against the real records.
createRequire(import.meta.url)('../assets/names.js');
const html = readFileSync(new URL('../index.html', import.meta.url), 'utf8');
const lift = (name, re) => {
  const m = html.match(re);
  if (!m) throw new Error('not found in index.html: ' + name);
  return m[0];
};
const src = [
  lift('PLACE_LEAD_IN', /const PLACE_LEAD_IN = \/.*\/;\n/),
  lift('computeLevenshteinDistance', /function computeLevenshteinDistance\([^)]*\) \{[\s\S]*?\n    \}\n/),
  lift('computeWordSimilarity', /function computeWordSimilarity\(w1, w2\) \{[\s\S]*?\n    \}\n/),
  lift('normalizePhoneticString', /function normalizePhoneticString\(s\) \{[\s\S]*?\n    \}\n/),
  lift('findFuzzyInstitutionMatch', /function findFuzzyInstitutionMatch\(query, threshold = 0\.65\) \{[\s\S]*?\n    \}\n/),
  lift('isNameRequest', /function isNameRequest\(text, inst\) \{[\s\S]*?\n    \}\n/),
].join('\n');
const raw = JSON.parse(readFileSync(new URL('../institutions.json', import.meta.url)));
const ALL = Array.isArray(raw) ? raw : raw.institutions;
const ctx = { ALL_INSTITUTIONS: ALL, ALL_CITIES: [...new Set(ALL.map(i => i.city).filter(Boolean))], ALL_COUNTRIES_REGISTRY: [...new Set(ALL.map(i => i.country).filter(Boolean))].map(name => ({ name })), window: { AtlasNames: globalThis.AtlasNames }, AtlasNames: globalThis.AtlasNames };
vm.createContext(ctx);
vm.runInContext(src + '\nthis.isNameRequest = isNameRequest; this.findFuzzyInstitutionMatch = findFuzzyInstitutionMatch;', ctx);
const { isNameRequest, findFuzzyInstitutionMatch } = ctx;
const byName = (n) => ALL.find(i => i.name === n);
const eflux = byName('e-flux');

test('a name or alias typed as spelled is a name request', () => {
  assert.equal(isNameRequest('Eflux', eflux), true);
  assert.equal(isNameRequest('e-flux', eflux), true);
  assert.equal(isNameRequest('show me e flux', eflux), true);
});
test('a name typed with a slip in it is still a name request for the closest record', () => {
  for (const typed of ['eflx', 'e-flix', 'eflux jornal']) {
    const near = findFuzzyInstitutionMatch(typed.toLowerCase(), 0.65);
    assert.equal(near && near.inst, eflux, typed);
    assert.equal(isNameRequest(typed, eflux), true, typed);
  }
});
test('a question about the space is not a name request', () => {
  assert.equal(isNameRequest('who funds eflux', eflux), false);
  assert.equal(isNameRequest('is eflux flagged', eflux), false);
});
test('a place on its own is not a name request', () => {
  const inst = ALL.find(i => i.city === 'Berlin');
  assert.equal(isNameRequest('Berlin', inst), false);
});
test('a place asked for with a map verb is not a name request', () => {
  const co = byName('C/O Berlin');
  for (const typed of ['zoom in on Berlin', 'zoom to Berlin', 'take me to Berlin', 'fly to Berlin', 'show me Berlin']) {
    assert.equal(isNameRequest(typed, co), false, typed);
  }
  assert.equal(isNameRequest('zoom in on C/O Berlin', co), true);
});
test('the map verbs come off before the place check', () => {
  const re = new RegExp(html.match(/const PLACE_LEAD_IN = \/(.*)\/;\n/)[1]);
  for (const typed of ['zoom in on berlin', 'zoom into berlin', 'zoom to berlin', 'please zoom in on berlin', 'can you take me to berlin', 'fly to berlin', 'go to berlin', 'center on berlin', 'what about berlin']) {
    assert.equal(typed.replace(re, ''), 'berlin', typed);
  }
});
