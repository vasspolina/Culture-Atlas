#!/usr/bin/env python3
"""Attach the propaganda layer's findings to the records they are about.

A finding says that a state, ruling party or regime used the institution itself as an instrument of propaganda, now ("today") or in a
past period ("historical"). Research comes from the Sponsor Atlas batches (sponsor-atlas/work/ubatch/PROPAGANDA.md); the checked rows are
kept in data/propaganda.json so the record can be rebuilt from this repo alone. Each record gets a `propaganda` list:
  {kind: today|historical, period, mechanism, summary, sources: [urls]}
A row that fails a rule below is listed and skipped, never repaired. Re-running replaces the field on every record, so it is safe to repeat.
Usage: python3 tools/import_propaganda.py [out.json ...]   (with files: they are merged into data/propaganda.json first)
       then python3 tools/clean_data.py && python3 tools/embed_data.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STORE = ROOT / 'data/propaganda.json'
KINDS = {'today', 'historical'}
MECHANISMS = {'state-directed', 'founded to promote', 'repurposed'}
HEDGES = re.compile(r'\b(may|might|reportedly|allegedly|arguably|likely|appears?|seems?|believed to|said to)\b', re.I)
DASHES = re.compile('[–—]')


def problems(row, ids):
    out = []
    if row.get('id') not in ids:
        out.append('no record with that id')
    if row.get('kind') not in KINDS:
        out.append('kind')
    if row.get('mechanism') not in MECHANISMS:
        out.append('mechanism')
    if not re.fullmatch(r'\d{4}( to (\d{4}|present))?', row.get('period') or ''):
        out.append('period')
    summary = row.get('summary') or ''
    if not summary or len(summary.split()) > 35:
        out.append('summary length')
    if HEDGES.search(summary):
        out.append('hedge: ' + HEDGES.search(summary).group(0))
    if DASHES.search(summary):
        out.append('dash')
    urls = [u for u in row.get('sources') or [] if re.match(r'https?://', u or '')]
    if not urls:
        out.append('no source url')
    return out


records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
ids = {r['id'] for r in records}
rows = json.load(open(STORE, encoding='utf-8')) if STORE.exists() else []
for path in sys.argv[1:]:
    for row in json.load(open(path, encoding='utf-8')):
        rows = [q for q in rows if (q['id'], q['kind']) != (row.get('id'), row.get('kind'))] + [row]

kept, skipped = [], []
for row in rows:
    p = problems(row, ids)
    (skipped if p else kept).append((row, p))
STORE.write_text(json.dumps([r for r, _ in kept], ensure_ascii=False, indent=1) + '\n', encoding='utf-8')

by = {r['id']: r for r in records}
for r in records:
    r.pop('propaganda', None)
for row, _ in kept:
    by[row['id']].setdefault('propaganda', []).append({
        'kind': row['kind'], 'period': row['period'], 'mechanism': row['mechanism'],
        'summary': row['summary'].strip(), 'sources': [u for u in row['sources'] if re.match(r'https?://', u or '')][:3],
    })
json.dump(records, open(ROOT / 'institutions.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
print(f'{len(kept)} findings on {len({r["id"] for r, _ in kept})} records;', f'{len(skipped)} skipped')
for row, p in skipped:
    print('  skipped', row.get('id'), row.get('kind'), p)
