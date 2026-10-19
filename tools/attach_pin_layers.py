#!/usr/bin/env python3
"""Attach the Sponsor Atlas's per-pin research layers to the records they are about. Run clean_data.py and embed_data.py afterwards.

The study (data/sponsor_atlas.json, set by tools/update_sponsor_atlas.py) carries four lines a pin can have beside its funding note:

  Records    what the institution publishes about its own money (accounts, annual reports, funder lists), or that it publishes nothing
  Finances   the figures from those accounts: fiscal year, income, shares of public, private and earned money, with the register read
  Affiliations   the networks, parent bodies and partners it belongs to
  Critique   paraphrased criticism of the institution from e-flux, BAK and others, each entry naming its source

They go on the record as the text fields records_note, finances_note, affiliations_note and critique_note. Re-running replaces the four fields, so it is safe
to repeat. A study entry that matches no record of that name in its city is listed, not guessed.
Usage: python3 tools/update_sponsor_atlas.py data/sponsor_atlas_<date>.json && python3 tools/attach_pin_layers.py && python3 tools/clean_data.py && python3 tools/embed_data.py
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIELD = {'Records': 'records_note', 'Finances': 'finances_note', 'Affiliations': 'affiliations_note', 'Critique': 'critique_note'}
# The study's Critique lines end by pointing at the Sponsor Atlas's "What the field says" case study, which this app does not carry.
POINTER = re.compile(r'\s*See the What the field says case study\.\s*$')


def norm(s):
    s = unicodedata.normalize('NFKD', (s or '').lower())
    return re.sub(r'[^a-z0-9]+', ' ', ''.join(c for c in s if not unicodedata.combining(c))).strip()


records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
by = {}
for r in records:
    r.pop('records_note', None)
    r.pop('finances_note', None)
    r.pop('affiliations_note', None)
    r.pop('critique_note', None)
    for k in {norm(r['name'])} | {norm(a) for a in r.get('aliases') or []}:
        by.setdefault(k, []).append(r)

placed = {v: 0 for v in FIELD.values()}
unplaced = []
for d in json.load(open(ROOT / 'data/sponsor_atlas.json', encoding='utf-8')):
    lines = {h: t for h, t in d.get('x') or [] if h in FIELD}
    if not lines:
        continue
    named = by.get(norm(d['n']), [])
    hits = [r for r in named if norm(r.get('city')) in norm(d['c'])]
    if not hits and len(named) == 1:   # the study spells the city another way (Frankfurt / Frankfurt am Main, Hanover / Hannover): one record of that name in the same country is the same space
        if norm(named[0].get('location')).split(' ')[-1:] == norm(d['c']).split(' ')[-1:]:
            hits = named
    if not hits:
        unplaced.append((d['n'], d['c'], 'no record of that name'))
        continue
    for r in hits:   # a twin pin (same city, the study's name as its name or alias) carries the same lines, as in attach_research.py
        for head, text in lines.items():
            text = POINTER.sub('', text.strip())
            r[FIELD[head]] = text
            placed[FIELD[head]] += 1

json.dump(records, open(ROOT / 'institutions.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
print('placed', placed)
for n, c, why in unplaced:
    print('  unplaced', n, '|', c, '|', why)
