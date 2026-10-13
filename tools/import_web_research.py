#!/usr/bin/env python3
"""Merge web-research findings into institutions.json, then run tools/clean_data.py and tools/embed_data.py.

Input: a JSON list of accepted claims, one entry per record:
  {"id": ..., "year_founded": 1966, "year_basis": "...", "year_urls": [...],
   "address": "...", "address_urls": [...], "retrieved": "2026-10-13"}
A value is written only where the record has none. Each written value gets its source URLs under
`field_sources`, which the record page shows next to the sources, with the words "not independently verified".
Usage: python3 tools/import_web_research.py data/web_research/<file>.json
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
claims = json.load(open(sys.argv[1], encoding='utf-8'))
path = ROOT / 'institutions.json'
records = json.load(open(path, encoding='utf-8'))
by_id = {r['id']: r for r in records}
wrote = {'year_founded': 0, 'address': 0}
for c in claims:
    r = by_id.get(c['id'])
    if r is None:
        print('unknown id', c['id'])
        continue
    fs = r.setdefault('field_sources', {})
    y = c.get('year_founded')
    if y and not r.get('year_founded') and isinstance(y, int) and 1000 <= y <= 2026 and c.get('year_urls'):
        r['year_founded'] = y
        fs['year_founded'] = {'urls': [u for u in c['year_urls'] if u.startswith('http')], 'basis': c.get('year_basis', ''), 'retrieved': c['retrieved']}
        wrote['year_founded'] += 1
    a = (c.get('address') or '').strip()
    if a and not r.get('address') and len(a) <= 200 and c.get('address_urls'):
        r['address'] = a
        fs['address'] = {'urls': [u for u in c['address_urls'] if u.startswith('http')], 'retrieved': c['retrieved']}
        wrote['address'] += 1
    if not fs:
        r.pop('field_sources')
json.dump(records, open(path, 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
print('written', wrote)
