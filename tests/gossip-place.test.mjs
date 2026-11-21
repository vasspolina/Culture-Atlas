// Gossip mode tells the stories of the place in view first: the open space, then its city, then its country, then everywhere.
// It once drew every story from the 40 newest of all the records, whatever was open on the map.
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
  lift('COUNTRY_LABEL', /const COUNTRY_LABEL = .*\n/),
  lift('CITY_NEAR_DEG', /const CITY_NEAR_DEG = .*\n/),
  lift('cityNear', /const cityNear = [\s\S]*?\);\n/),
  lift('gossipItems', /function gossipItems\(inst, fresh\) \{[\s\S]*?\n    \}\n/),
  lift('gossipPool', /function gossipPool\(\) \{[\s\S]*?\n    \}\n/),
  lift('gossipNorm', /const gossipNorm = .*\n/),
  lift('gossipCountry', /const gossipCountry = .*\n/),
  lift('gossipTiers', /function gossipTiers\(scope, pool\) \{[\s\S]*?\n    \}\n/),
  lift('GOSSIP_NEWEST', /const GOSSIP_NEWEST = .*\n/),
  lift('pickGossip', /function pickGossip\(pool, avoidInst, scope, peek\) \{[\s\S]*?\n    \}\n/),
  lift('gossipIn', /const gossipIn = .*\n/),
  lift('gossipLead', /function gossipLead\(main\) \{[\s\S]*?\n    \}\n/),
].join('\n');
const raw = JSON.parse(readFileSync(new URL('../institutions.json', import.meta.url)));
const ALL = Array.isArray(raw) ? raw : raw.institutions;
const ctx = { ALL_INSTITUTIONS: ALL, gossipShown: new Set(), pickOne: (arr) => arr[0] };
vm.createContext(ctx);
vm.runInContext(src + '\nthis.api = { gossipPool, gossipTiers, pickGossip, gossipLead, cityNear };', ctx);
const { gossipPool, gossipTiers, pickGossip, gossipLead, cityNear } = ctx.api;
const pool = gossipPool();
const scopeOf = (inst) => ({ inst, city: inst.city || '', country: inst.country || '', at: inst });
const same = (a, b) => String(a || '').toLowerCase().trim() === String(b || '').toLowerCase().trim();
// A space with a story of its own, in a city where another space has one too.
const own = pool.find(x => x.inst.city && pool.some(y => y.inst !== x.inst && same(y.inst.city, x.inst.city) && cityNear(x.inst, y.inst)));

test('each level of a place holds the one before it', () => {
  const sizes = gossipTiers(scopeOf(own.inst), pool).map(t => t.items.length);
  assert.equal(sizes.length, 4);
  assert.ok(sizes[0] > 0);
  for (let n = 1; n < sizes.length; n++) assert.ok(sizes[n] >= sizes[n - 1], sizes.join(' '));
  assert.equal(sizes[3], pool.length);
});
test('an open space is told its own stories first, then its city', () => {
  ctx.gossipShown.clear();
  const scope = scopeOf(own.inst), mine = pool.filter(x => x.inst === own.inst).length;
  for (let n = 0; n < mine; n++) {
    const pick = pickGossip(pool, null, scope);
    assert.equal(pick.inst, own.inst);
    assert.equal(pick.wide, false);
    assert.equal(gossipLead(pick), `At ${own.inst.name}`);
  }
  const next = pickGossip(pool, null, scope);
  assert.notEqual(next.inst, own.inst);
  assert.ok(same(next.inst.city, own.inst.city));
  assert.equal(next.wide, true);
  assert.ok(gossipLead(next).startsWith(`Elsewhere in ${next.inst.city}, at ${next.inst.name}`));
});
test('a city in view is told that city, a country that country', () => {
  ctx.gossipShown.clear();
  const city = pickGossip(pool, null, { inst: null, city: own.inst.city, country: own.inst.country, at: own.inst });
  assert.ok(same(city.inst.city, own.inst.city));
  assert.equal(city.wide, false);
  assert.equal(gossipLead(city), `At ${city.inst.name}`);
  const country = pickGossip(pool, null, { inst: null, city: '', country: own.inst.country, at: null });
  assert.ok(same(country.inst.country, own.inst.country));
  assert.equal(country.level, 'country');
  assert.equal(country.wide, false);
});
test('with nothing in view the story is one of the newest of all', () => {
  ctx.gossipShown.clear();
  const pick = pickGossip(pool, null, {});
  assert.equal(pick.level, 'world');
  assert.equal(pick.wide, false);
  assert.equal(pick.g, pool[0].g);
});
test('a story named on a chip is not counted as told', () => {
  ctx.gossipShown.clear();
  const peeked = pickGossip(pool, null, scopeOf(own.inst), true);
  assert.equal(ctx.gossipShown.size, 0);
  assert.equal(pickGossip(pool, null, scopeOf(own.inst)).g, peeked.g);
  assert.equal(ctx.gossipShown.size, 1);
});
test('a story from further out never says what the place in view lacks', () => {
  ctx.gossipShown.clear();
  const bare = ALL.find(i => i.city && !pool.some(x => x.inst === i) && pool.some(x => same(x.inst.city, i.city) && cityNear(i, x.inst)));
  const pick = pickGossip(pool, null, scopeOf(bare));
  assert.equal(pick.wide, true);
  assert.doesNotMatch(gossipLead(pick), /\b(no|not|nothing|none)\b/i);
  assert.ok(!gossipLead(pick).includes(bare.name));
});
