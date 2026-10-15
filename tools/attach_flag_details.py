#!/usr/bin/env python3
"""Add the further detail found for "Why it is flagged" to each flagged record as flag_details: [{text, url}].
Usage: python3 tools/attach_flag_details.py data/flag_details/accepted.json && python3 tools/clean_data.py && python3 tools/embed_data.py
accepted.json is a list of {id, details: [{text, url, quote}]} that two independent checks passed against the page they cite.
Re-running replaces the field. A record that is not flagged gets nothing.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = {r['id']: r['details'] for r in json.load(open(ROOT / sys.argv[1], encoding='utf-8'))}
records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
n = 0
for r in records:
    r.pop('flag_details', None)
    d = rows.get(r['id'])
    if d and r.get('why_flagged'):
        r['flag_details'] = [{'text': x['text'], 'url': x['url']} for x in d]
        n += 1
json.dump(records, open(ROOT / 'institutions.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
print('records with added detail:', n)
