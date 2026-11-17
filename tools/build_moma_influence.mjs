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

// MoMA's private funders as dots on the Influence map (user, 17 Nov 2026: "show moma funders as dots on the influence map").
// Only the entries the study says gave MoMA money: a company, foundation or person, with the head office or home city the
// study or the company's own site gives. A funder the map already draws (a ledger key in `keys`, or the same name in
// `names`) gains MoMA among its museums instead of a second dot. Public bodies are listed last; the funding maps' own
// public bodies stay off the mode, these are MoMA's alone. Study names are listed in `from`, so the record and the dot are traced to the study.
const NY = { c: 'New York', co: 'United States', lat: 40.7128, lon: -74.006 };
const DC = { c: 'Washington', co: 'United States', lat: 38.9072, lon: -77.0369 };
const FUNDERS = [
  { name: 'BlackRock', kind: 'corp', hq: NY, from: ['BlackRock', 'Laurence D. Fink'] },
  { name: 'Pfizer', kind: 'corp', hq: NY, from: ['Pfizer Inc.', 'Albert Bourla · David Rockefeller Award 2021'] },
  { name: 'Johnson & Johnson', kind: 'corp', hq: { c: 'New Brunswick', co: 'United States', lat: 40.4862, lon: -74.4518 }, from: ['Johnson & Johnson'] },
  { name: 'Axsome Therapeutics', kind: 'corp', hq: NY, from: ['Axsome Therapeutics'] },
  { name: 'Roche', kind: 'corp', names: ['F. Hoffmann-La Roche Ltd', 'Roche'], hq: { c: 'Basel', co: 'Switzerland', lat: 47.5596, lon: 7.5886 }, from: ['Roche Innovation Center NY', 'Roche (Hoffmann-La Roche)'] },
  { name: 'Maja Oeri', kind: 'family', hq: { c: 'Basel', co: 'Switzerland', lat: 47.5596, lon: 7.5886 }, from: ['Maja Oeri'] },
  { name: 'Ronald O. Perelman', kind: 'family', hq: NY, from: ['Ronald O. Perelman'] },
  { name: 'Sackler family', kind: 'family', keys: ['sacklerfamily'], from: ['Jillian Sackler'] },
  { name: 'Ronald S. Lauder', kind: 'family', hq: NY, from: ['Ronald S. Lauder'] },
  { name: 'Estée Lauder Companies', kind: 'corp', hq: NY, from: ['Estée Lauder Companies'] },
  { name: 'KKR and the Kravis family', kind: 'fund', keys: ['kkr'], from: ['Marie-Josée Kravis', 'Henry R. Kravis'] },
  { name: 'Steven Cohen (Point72)', kind: 'family', keys: ['right:cohen'], from: ['Steven A. Cohen'] },
  { name: 'Steven Tananbaum', kind: 'family', hq: NY, from: ['Steven Tananbaum'] },
  { name: 'Leon Black (Apollo)', kind: 'family', keys: ['leonblack'], from: ['Leon D. Black', 'Apollo Global Management'] },
  { name: 'Ken Griffin / Citadel', kind: 'family', keys: ['right:griffin'], from: ['Kenneth C. Griffin', 'Citadel'] },
  { name: 'Helen Zell', kind: 'family', hq: { c: 'Chicago', co: 'United States', lat: 41.8781, lon: -87.6298 }, from: ['Helen Zell'] },
  { name: 'Fox Corporation', kind: 'corp', hq: NY, from: ['Fox Corporation · 21st Century Fox', 'Murdoch family · News Corp'] },
  { name: 'The Wall Street Journal (Dow Jones)', kind: 'corp', hq: NY, from: ['The Wall Street Journal'] },
  { name: 'John Paulson (Paulson & Co.)', kind: 'family', keys: ['paulsonfamily'], from: ['Paulson & Co. (John Paulson)'] },
  { name: 'Stephen Schwarzman (Blackstone)', kind: 'family', keys: ['schwarzman'], from: ['Schwarzman · Langone · Blavatnik · Loeb · Tepper'] },
  { name: 'Blavatnik Family Foundation', kind: 'family', keys: ['blavatnikfamily'], from: ['Schwarzman · Langone · Blavatnik · Loeb · Tepper'] },
  { name: 'Glenn Dubin (Highbridge Capital)', kind: 'family', keys: ['glenndubin'], from: ['Glenn Dubin'] },
  { name: 'The Rockefeller University', kind: 'found', hq: NY, from: ['The Rockefeller University'] },
  { name: 'Rockefeller Brothers Fund', kind: 'found', names: ['Rockefeller Brothers Fund'], hq: NY, from: ['Rockefeller Brothers Fund'] },
  { name: 'David Rockefeller', kind: 'family', hq: NY, from: ['David Rockefeller'] },
  // Public money (user, 17 Nov 2026: "show government funders too"): the bodies the study says paid MoMA, gave it a tax or
  // bond advantage, or bought its work, each at its seat. A foreign government is set at its capital, since it is that
  // government's money, not its consulate's or mission's.
  { name: 'City of New York', kind: 'gov', hq: NY, from: ['City of New York'] },
  { name: 'Trust for Cultural Resources of the City of New York', kind: 'gov', hq: NY, from: ['Trust for Cultural Resources', 'Museum Tower TEPs'] },
  { name: 'NYC Department of Cultural Affairs', kind: 'gov', hq: NY, from: ['NYC Dept. of Cultural Affairs'] },
  { name: 'US Small Business Administration', kind: 'gov', hq: DC, from: ['US Small Business Administration'] },
  { name: 'National Endowment for the Arts', kind: 'gov', hq: DC, from: ['National Endowment for the Arts'] },
  { name: 'Office of the Coordinator of Inter-American Affairs', kind: 'gov', hq: DC, from: ['Office of the Coordinator of Inter-American Affairs', 'MoMA Film Library (Iris Barry)'] },
  { name: 'Government of Switzerland', kind: 'gov', hq: { c: 'Bern', co: 'Switzerland', lat: 46.948, lon: 7.4474 }, from: ['Consulate General of Switzerland'] },
  { name: 'State of Qatar', kind: 'gov', hq: { c: 'Doha', co: 'Qatar', lat: 25.2854, lon: 51.531 }, from: ['Permanent Mission of Qatar'] },
  // The study's other public bodies (user, 17 Nov 2026: "add the other public bodies too"): they did not pay MoMA, but the
  // study ties each to it: buyers of its members' products, the offices its leaders held, the Cold War agencies that used
  // its exhibitions, and the inquiries into a trustee. The CIA's fronts are drawn as the CIA, since the money was its.
  { name: 'Federal Reserve', kind: 'gov', notFunder: true, hq: DC, from: ['Federal Reserve'] },
  { name: 'US Department of Health and Human Services (BARDA)', kind: 'gov', notFunder: true, hq: DC, from: ['HHS · BARDA · Operation Warp Speed'] },
  { name: 'US State Department', kind: 'gov', notFunder: true, hq: DC, from: ['US State Department'] },
  { name: 'US Information Agency', kind: 'gov', notFunder: true, hq: DC, from: ['US Information Agency'] },
  { name: 'Office of Strategic Services', kind: 'gov', notFunder: true, hq: DC, from: ['Office of Strategic Services'] },
  { name: 'CIA', kind: 'gov', notFunder: true, hq: { c: 'Langley', co: 'United States', lat: 38.9517, lon: -77.1467 }, from: ['CIA International Organizations Division', 'Congress for Cultural Freedom', 'Farfield Foundation', 'Whitney Trust'] },
  { name: 'US Senate Finance Committee', kind: 'gov', notFunder: true, hq: DC, from: ['Senate Finance Committee (Sen. Wyden)'] },
  { name: 'US Department of Justice', kind: 'gov', notFunder: true, hq: DC, from: ['DOJ Epstein files (2025–26)'] },
  { name: 'US Virgin Islands Attorney General', kind: 'gov', notFunder: true, hq: { c: 'Charlotte Amalie', co: 'US Virgin Islands', lat: 18.3419, lon: -64.9307 }, from: ['US Virgin Islands Attorney General'] },
];
const allNames = new Set(N.map(n => n.label));
FUNDERS.forEach(f => f.from.forEach(n => { if (!allNames.has(n)) throw new Error(`${f.name}: "${n}" is not an entry of the study`); }));

const out = {
  about: 'Written by tools/build_moma_influence.mjs from the MoMA Influence Map study (moma-money-map.html). Text only; the network drawing is not copied.',
  space: 'moma-the-museum-of-modern-art',
  page: 'moma-money-map.html',
  museum: museum ? { role: museum.role || '', note: museum.note || '', sources: museum.src || [] } : null,
  groups,
  funders: FUNDERS,
};
writeFileSync(new URL('assets/moma-influence.json', root), JSON.stringify(out, null, 1) + '\n');
console.log(groups.map(g => `${g.title}: ${g.entries.length}`).join('\n') + `\nFunders on the map: ${FUNDERS.length}`);
