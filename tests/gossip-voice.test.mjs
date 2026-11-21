// Gossip mode speaks in one voice: an investigative journalist who talks the way a voice assistant with a character does
// (user, 21 Nov 2026: "make gossip mode talk like yandex alisa, it needs to sound like investigative journalist").
// It reports what others published and never claims a source of its own, and read aloud it uses a woman's voice from
// those installed on the device.
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
  lift('GOSSIP_OPENERS', /const GOSSIP_OPENERS = \[[\s\S]*?\];\n/),
  lift('GOSSIP_HOOKS', /const GOSSIP_HOOKS = \[[\s\S]*?\];\n/),
  lift('GOSSIP_OFF', /const GOSSIP_OFF = \[[\s\S]*?\];\n/),
  lift('GOSSIP_OWN_SOURCE', /const GOSSIP_OWN_SOURCE = .*\n/),
  lift('dropOwnSourceClaims', /const dropOwnSourceClaims = .*\n/),
  lift('GOSSIP_VOICE_NAMES', /const GOSSIP_VOICE_NAMES = .*\n/),
  lift('selectGossipVoice', /function selectGossipVoice\(\) \{[\s\S]*?\n    \}\n/),
].join('\n');
const ctx = { voices: [], curator: null };
ctx.refreshVoices = () => ctx.voices;
ctx.selectCuratorVoice = () => ctx.curator;
vm.createContext(ctx);
vm.runInContext(src + '\nthis.api = { GOSSIP_OPENERS, GOSSIP_HOOKS, GOSSIP_OFF, GOSSIP_OWN_SOURCE, dropOwnSourceClaims, selectGossipVoice };', ctx);
const { GOSSIP_OPENERS, GOSSIP_HOOKS, GOSSIP_OFF, GOSSIP_OWN_SOURCE, dropOwnSourceClaims, selectGossipVoice } = ctx.api;
const v = (name, lang) => ({ name, lang });

test('the page\'s own lines keep their shape', () => {
  // The model's greeting is checked against the same opening words, and a yes answers every closing question.
  for (const o of GOSSIP_OPENERS) assert.match(o, /^Gossip mode is on\b/);
  for (const o of GOSSIP_OFF) assert.match(o, /^Gossip mode is off\b/);
  for (const h of GOSSIP_HOOKS) assert.match(h, /\?$/);
  for (const line of [...GOSSIP_OPENERS, ...GOSSIP_HOOKS, ...GOSSIP_OFF]) {
    assert.doesNotMatch(line, /[—–]| - /, line);
    assert.doesNotMatch(line, GOSSIP_OWN_SOURCE, line);
  }
});

test('the model is told to report as a journalist, and not to claim a source of its own', () => {
  const greeting = lift('greeting', /const system = `You are the voice of Gossip mode[\s\S]*?`;/);
  const answers = lift('answers', /VOICE: deliver it as[^`]*?<\/gossip_mode>/);
  for (const prompt of [greeting, answers]) {
    assert.match(prompt, /investigative journalist/);
    assert.match(prompt, /First person|first person/);
    assert.match(prompt, /never claim a source, a document or an interview of your own/);
    assert.match(prompt, /never for a named person/);
  }
  assert.match(greeting, /Never state talk, a rumour or an allegation as fact/);
  assert.match(answers, /talk still stays talk/);
});

test('a claim to a source of its own is caught, and reported speech is not', () => {
  for (const t of ['My sources say the director is leaving.', 'Sources told me the board met twice.', 'I obtained the minutes.',
    'I spoke to two curators.', 'I have confirmed the settlement.', 'This comes from my own reporting.']) assert.match(t, GOSSIP_OWN_SOURCE, t);
  for (const t of ['Hyperallergic reported in March 2024 that the director is leaving.', 'The museum confirmed the settlement.',
    'I read the internet so you do not have to.', 'Here is what I dug up.', 'The union says its sources are staff emails.']) assert.doesNotMatch(t, GOSSIP_OWN_SOURCE, t);
});

test('a gossip answer loses only the sentence that claims its own source', () => {
  const out = dropOwnSourceClaims('The Art Newspaper reported in May 2025 that the board cut 30 jobs. My sources say more cuts are coming. The union denies it.\n\nThe museum has not replied.');
  assert.equal(out, 'The Art Newspaper reported in May 2025 that the board cut 30 jobs. The union denies it.\n\nThe museum has not replied.');
  const clean = 'ARTnews reported in 2024 that the gift was returned. Nobody has confirmed it.';
  assert.equal(dropOwnSourceClaims(clean), clean);
});

test('read aloud, gossip takes a woman\'s English voice from the device', () => {
  ctx.curator = v('Daniel', 'en-GB');
  // An iPhone: the Russian voice and the men's voices are passed over.
  ctx.voices = [v('Daniel', 'en-GB'), v('Karen', 'en-AU'), v('Milena', 'ru-RU'), v('Samantha', 'en-US'), v('Fred', 'en-US')];
  assert.equal(selectGossipVoice().name, 'Samantha');
  // A better copy of a voice wins.
  ctx.voices = [v('Samantha', 'en-US'), v('Ava (Premium)', 'en-US')];
  assert.equal(selectGossipVoice().name, 'Ava (Premium)');
  // Chrome on a desktop.
  ctx.voices = [v('Google Deutsch', 'de-DE'), v('Google UK English Male', 'en-GB'), v('Google US English', 'en-US'), v('Google UK English Female', 'en-GB')];
  assert.equal(selectGossipVoice().name, 'Google US English');
  // Edge: a natural woman's voice, not the first natural voice.
  ctx.voices = [v('Microsoft Andrew Online (Natural) - English (United States)', 'en-US'), v('Microsoft Aria Online (Natural) - English (United States)', 'en-US')];
  assert.match(selectGossipVoice().name, /Aria/);
});

test('with no such voice installed, the curator\'s voice reads', () => {
  ctx.curator = v('English United States', 'en-US');
  ctx.voices = [v('English United States', 'en-US'), v('Deutsch Deutschland', 'de-DE')];
  assert.equal(selectGossipVoice().name, 'English United States');
  ctx.voices = [];
  assert.equal(selectGossipVoice(), ctx.curator);
});
