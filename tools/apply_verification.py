#!/usr/bin/env python3
"""Copy results from data/verification.json into institutions.json.

A record gets `verification` = {status, checked_on} only when tools/verify_claims.py marked it verified or partial.
The page says "Not independently verified" for every record without it. Then run tools/embed_data.py.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
results = json.load(open(ROOT / 'data' / 'verification.json'))
n = 0
for r in records:
    v = results.get(r['id'])
    if v and v['status'] in ('verified', 'partial'):
        r['verification'] = {'status': v['status'], 'checked_on': v['checked_on']}
        n += 1
    else:
        r.pop('verification', None)
json.dump(records, open(ROOT / 'institutions.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
print(n, 'records carry a verification result')
