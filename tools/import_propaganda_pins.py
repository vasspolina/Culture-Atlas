#!/usr/bin/env python3
"""Add the institutions that the propaganda layer needed and the atlas did not hold, then attach their findings.

data/propaganda_pins.json holds rows researched and checked in the Sponsor Atlas batches (ubatch/NEWPINS.md, NEWCHECK-PROP.md):
  n, c ("City, Country"), tier, flags, s (S|L), funding, note, sources, lat, lng, propaganda [{kind, period, mechanism, summary, sources}]
A record is added only if none of that name or id exists; the layer's findings go to data/propaganda.json (keyed by id) and are put on
the records by tools/import_propaganda.py, which this script runs last. Safe to repeat.
Usage: python3 tools/import_propaganda_pins.py && python3 tools/clean_data.py && python3 tools/embed_data.py
"""
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def norm(s):
    s = unicodedata.normalize('NFKD', s.lower())
    return re.sub(r'[^a-z0-9]+', ' ', ''.join(c for c in s if not unicodedata.combining(c))).strip()


def slug(s):
    return norm(s).replace(' ', '-')


records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
by_id = {r['id']: r for r in records}
have = {norm(r['name']) for r in records}
for r in records:
    have.update(norm(a) for a in r.get('aliases') or [])

rows = json.load(open(ROOT / 'data/propaganda_pins.json', encoding='utf-8'))
store = json.load(open(ROOT / 'data/propaganda.json', encoding='utf-8'))
added = 0
for d in rows:
    rid = slug(d['n'])
    if rid not in by_id:
        if norm(d['n']) in have:
            print('  already on the map under that name, skipped:', d['n'])
            continue
        city, _, country = d['c'].rpartition(', ')
        rec = {'name': d['n'], 'location': d['c'], 'city': city, 'country': country, 'tier': d['tier'], 'size': d['s'],
               'sources': d['sources'], 'lat': d['lat'], 'lon': d['lng'], 'id': rid, 'funding': d['funding'], 'watch': d['note']}
        if d['flags']:
            rec['flags'] = d['flags']
            rec['why_flagged'] = d['funding']
        records.append(rec)
        by_id[rid] = rec
        added += 1
    for p in d['propaganda']:
        store = [q for q in store if (q['id'], q['kind']) != (rid, p['kind'])]
        store.append({'id': rid, 'n': d['n'], 'kind': p['kind'], 'period': p['period'], 'mechanism': p['mechanism'],
                      'summary': p['summary'], 'sources': p['sources']})
json.dump(records, open(ROOT / 'institutions.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
(ROOT / 'data/propaganda.json').write_text(json.dumps(store, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print('added', added, 'records')
sys.exit(subprocess.call([sys.executable, str(ROOT / 'tools/import_propaganda.py')]))
