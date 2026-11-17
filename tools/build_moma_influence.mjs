// Copies what the MoMA Influence Map study says about each funder, trustee, agency and protest into the Influence map
// (user, 17 Nov 2026: "add moma money map to moma on our influence map ... just add info ... skip visualisation").
//
// Reads the study's list of entries (const N in moma-money-map.html) and writes
// assets/moma-influence.json: for each entry its name, the study's group, its role, the money where the study gives a
// figure, the note and the sources, all as the study states them. The network drawing (positions, tiers, colours, the
// lines between entries) is left out. assets/influence-mode.js shows the result in MoMA's record while Influence map is on.
// Run after any edit to the study:
//
//     node tools/build_moma_influence.mjs
import { readFileSync, writeFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';

const root = new URL('../', import.meta.url);
const html = readFileSync(new URL('moma-money-map.html', root), 'utf8');
const start = html.indexOf('const N = [');
const end = html.indexOf('\n];', start);
if (start < 0 || end < 0) throw new Error('The study\'s entry list (const N) was not found in moma-money-map.html');
// The list is plain data (object literals and strings), so it is read in an empty context.
const N = runInNewContext(html.slice(start + 'const N = '.length, end + 2));

// The study's groups, in the order it lists them. An entry goes in the group of its first category.
const GROUPS = [
  ['gov', 'Government and public office'],
  ['pharma', 'Pharma and med-tech'],
  ['right', 'Right-wing donors'],
  ['epstein', 'Epstein ties'],
  ['protest', 'Protests'],
  ['other', 'Other institutions the same funders pay for'],
  ['hist', 'Historical: the Rockefellers and the Cold War'],
];
const museum = N.find(n => n.id === 'moma');
const groups = GROUPS.map(([key, title]) => ({
  key, title,
  entries: N.filter(n => n.id !== 'moma' && (n.cats || [])[0] === key).map(n => ({
    name: n.label, role: n.role || '', money: n.money || '', note: n.note || '', sources: n.src || [],
  })),
})).filter(g => g.entries.length);
const left = N.filter(n => n.id !== 'moma' && !GROUPS.some(([k]) => (n.cats || [])[0] === k));
if (left.length) throw new Error('Entries in no group: ' + left.map(n => n.id).join(', '));

const out = {
  about: 'Written by tools/build_moma_influence.mjs from the MoMA Influence Map study (moma-money-map.html). Text only; the network drawing is not copied.',
  space: 'moma-the-museum-of-modern-art',
  page: 'moma-money-map.html',
  museum: museum ? { role: museum.role || '', note: museum.note || '', sources: museum.src || [] } : null,
  groups,
};
writeFileSync(new URL('assets/moma-influence.json', root), JSON.stringify(out, null, 1) + '\n');
console.log(groups.map(g => `${g.title}: ${g.entries.length}`).join('\n'));
