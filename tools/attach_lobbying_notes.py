#!/usr/bin/env python3
"""Add the case notes on funders' lobbying through a space (data/research_attach/lobbying_case_notes_*.json) to the records.

Influence mode shows lobbying and political giving only where a record ties it to a space (user, 17 Nov 2026), so each
such tie needs its sentence in the space's own record first; tools/build_influence.py then finds it as a candidate and
data/influence_review.json keeps it with its `links`. A note already on the record is not added twice.
Usage: python3 tools/attach_lobbying_notes.py && python3 tools/embed_data.py && python3 -I tools/build_influence.py
"""
import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
path = ROOT / 'institutions.json'
records = json.load(open(path, encoding='utf-8'))
by_id = {r['id']: r for r in records}
n = 0
for f in sorted(glob.glob(str(ROOT / 'data/research_attach/lobbying_case_notes_*.json'))):
    for d in json.load(open(f, encoding='utf-8')):
        r = by_id[d['record_id']]
        notes = r.setdefault('case_notes', [])
        if all(x.get('text') != d['note']['text'] for x in notes):
            notes.append(d['note'])
            n += 1
json.dump(records, open(path, 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
print(f'{n} case notes added')
