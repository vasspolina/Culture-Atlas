// assets/analytics.js: off without an address, off when the browser asks not to be tracked, and what a count carries.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const SRC = fs.readFileSync(new URL('../assets/analytics.js', import.meta.url), 'utf8');

function load({ url = 'https://x.goatcounter.com/count', host = 'vasspolina.github.io', dnt, gpc, protocol = 'https:', referrer = '' } = {}) {
  const sent = [];
  const window = { ATLAS_ANALYTICS_URL: url, screen: { width: 390 } };
  const ctx = {
    window, URL,
    navigator: { doNotTrack: dnt, globalPrivacyControl: gpc, sendBeacon: (u) => { sent.push(new URL(u)); return true; } },
    location: { protocol, hostname: host, host, pathname: '/Culture-Atlas/', search: '?q=secret', hash: '#tate' },
    document: { visibilityState: 'visible', title: 'Leaving it on the table', referrer, addEventListener() {} },
    Image: function () {},
  };
  vm.runInNewContext(SRC, ctx);
  return { sent, count: window.atlasCount };
}

test('counts one page view with the path only', () => {
  const { sent } = load({ referrer: 'https://news.example/story?id=9' });
  assert.equal(sent.length, 1);
  const p = sent[0].searchParams;
  assert.equal(sent[0].origin + sent[0].pathname, 'https://x.goatcounter.com/count');
  assert.equal(p.get('p'), '/Culture-Atlas/');
  assert.equal(p.get('r'), 'https://news.example/story');
  assert.equal(p.get('s'), '390');
  assert.ok(!sent[0].href.includes('secret') && !sent[0].href.includes('tate'));
});

test('sends nothing without an address, on localhost, from a file, or when asked not to track', () => {
  for (const o of [{ url: '' }, { url: 'http://insecure.example/count' }, { host: 'localhost' }, { protocol: 'file:' }, { dnt: '1' }, { gpc: true }]) {
    const { sent, count } = load(o);
    count('record/tate-modern', 'Tate Modern');
    assert.equal(sent.length, 0, JSON.stringify(o));
  }
});

test('an event carries its name, and a repeat within two seconds counts once', () => {
  const { sent, count } = load();
  count('record/tate-modern', 'Tate Modern');
  count('record/tate-modern', 'Tate Modern');
  count('chat/question');
  assert.equal(sent.length, 3);
  assert.equal(sent[1].searchParams.get('p'), 'record/tate-modern');
  assert.equal(sent[1].searchParams.get('e'), 'true');
  assert.equal(sent[2].searchParams.get('p'), 'chat/question');
});
