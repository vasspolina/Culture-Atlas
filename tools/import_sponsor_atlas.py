#!/usr/bin/env python3
"""Add institutions from the Sponsor Atlas study (data/sponsor_atlas.json) that institutions.json does not have yet.

Existing records are left alone. Run tools/clean_data.py and tools/embed_data.py afterwards.
Tiers: A stays A; B, O (one name to note) and F (flags) become Flagged (B); U stays U.
A note that begins "Flags:" names the flags up to the first full stop; the sentences after it become the record's watch text.
"""
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def norm(s):
    s = unicodedata.normalize('NFKD', s.lower())
    return re.sub(r'[^a-z0-9]+', ' ', ''.join(c for c in s if not unicodedata.combining(c))).strip()


def slug(s):
    return norm(s).replace(' ', '-')


def split_flags(w):
    """'Flags: Fossil fuels, Gambling. Rest of the note.' -> (['Fossil fuels', 'Gambling'], 'Rest of the note.')
    The flag names end at the first full stop; what follows is the note."""
    body = w[len('Flags:'):].strip()
    head, dot, rest = body.partition('.')
    return [x.strip() for x in head.split(',') if x.strip()], rest.strip()


records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
have = {norm(r['name']) for r in records}
for r in records:
    have.update(norm(a) for a in r.get('aliases') or [])
ids = {r['id'] for r in records}
added = 0
for d in json.load(open(ROOT / 'data' / 'sponsor_atlas.json', encoding='utf-8')):
    if norm(d['n']) in have:
        continue
    city, _, country = d['c'].rpartition(', ')
    rec = {'name': d['n'], 'location': d['c'], 'city': city or d['c'], 'country': country or d['c'],
           'tier': 'B' if d['t'] in 'BOF' else d['t'], 'size': d.get('s') or 'S',
           'sources': d['u'], 'lat': d['la'], 'lon': d['lo'], 'id': slug(d['n'])}
    if rec['id'] in ids:
        rec['id'] += '-sa'
    if d.get('f'):
        rec['funding'] = d['f']
    w = d.get('w') or ''
    if w.startswith('Flags:'):
        rec['flags'], rest = split_flags(w)
        rec['why_flagged'] = d.get('f') or w
        if rest:
            rec['watch'] = rest
    elif w:
        rec['watch'] = w
        if d['t'] in 'BOF':
            rec['why_flagged'] = w
    if d.get('x'):
        rec['other_findings'] = ' | '.join(f'{src}: {text}' for src, text in d['x'])
    records.append(rec)
    ids.add(rec['id'])
    added += 1
json.dump(records, open(ROOT / 'institutions.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
print('added', added)
