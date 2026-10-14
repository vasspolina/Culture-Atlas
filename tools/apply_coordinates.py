#!/usr/bin/env python3
"""Give the records that have no coordinates (0, 0: no pin, no building view) the coordinates a source states.

Input: rows from the coordinate-audit workflow (a list of {id, a, b, agreed}), one file per run, and
data/web_research/coordinate_audit_input.json (the records the workflow was given: id, name, city, country).
Each of the two search passes returned the coordinates a search result states, the URL and the text. A record gets them only when
  - both passes found them and they are within 0.01 degrees of each other, or one pass found them on Wikipedia or Wikidata and the
    other found nothing and did not contradict it; and
  - the place is within 60 km of the other records in the same city that already have coordinates (this catches a namesake and a
    dropped minus sign); a city with no other located record is accepted on the agreement alone.
A festival, biennial or organisation with no single building (fixed_venue false) never gets a pin.
The more precise of the two values is written. Sources and the quoted text go under field_sources.coordinates.
Usage: python3 tools/apply_coordinates.py rows.json [rows2.json ...] [--date 2026-10-14]
Then: python3 tools/clean_data.py && python3 tools/embed_data.py
"""
import json
import math
import statistics
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
args = sys.argv[1:]
date = '2026-10-14'
files = []
while args:
    a = args.pop(0)
    if a == '--date':
        date = args.pop(0)
    else:
        files.append(a)

records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
by_id = {}
for r in records:
    by_id.setdefault(r['id'], []).append(r)
rows = {}
for f in files:
    for r in json.load(open(f, encoding='utf-8')):
        rows[r['id']] = r


def located(r):
    return bool(r.get('lat')) or bool(r.get('lon'))


def km(a, b):
    p = math.pi / 180
    x = math.sin((b[0] - a[0]) * p / 2) ** 2 + math.cos(a[0] * p) * math.cos(b[0] * p) * math.sin((b[1] - a[1]) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(x))


def city_centre(rec):
    pts = [(o['lat'], o['lon']) for o in records if o.get('city') == rec.get('city') and o.get('country') == rec.get('country') and located(o)]
    if not pts:
        return None
    return (statistics.median(p[0] for p in pts), statistics.median(p[1] for p in pts))


def decimals(x):
    s = repr(float(x))
    return len(s.split('.')[1]) if '.' in s else 0


def wiki(urls):
    return any((urlparse(u).hostname or '').endswith(('wikipedia.org', 'wikidata.org')) for u in urls or [])


def has(p):
    return bool(p) and bool(p.get('lat') or p.get('lon'))


tally, decisions = {}, []
for rid, row in rows.items():
    if rid not in by_id or len(by_id[rid]) != 1:
        continue
    rec = by_id[rid][0]
    if located(rec):
        continue
    a, b = row.get('a') or {}, row.get('b') or {}
    pick, why = None, ''
    if has(a) and has(b):
        if abs(a['lat'] - b['lat']) <= 0.01 and abs(a['lon'] - b['lon']) <= 0.01 and a.get('fixed_venue') and b.get('fixed_venue'):
            pick = a if decimals(a['lat']) + decimals(a['lon']) >= decimals(b['lat']) + decimals(b['lon']) else b
            why = 'two passes agree'
        else:
            why = 'passes differ'
    elif has(a) or has(b):
        one = a if has(a) else b
        if wiki(one.get('coord_urls')) and one.get('fixed_venue'):
            pick, why = one, 'one pass on Wikipedia or Wikidata, the other found nothing'
        else:
            why = 'one pass, not Wikipedia'
    else:
        why = 'none found' if (a.get('fixed_venue', True) and b.get('fixed_venue', True)) else 'no single venue'
    if pick:
        ctr = city_centre(rec)
        if ctr and km(ctr, (pick['lat'], pick['lon'])) > 60:
            pick, why = None, f'{round(km(ctr, (a.get("lat") or b.get("lat"), a.get("lon") or b.get("lon"))))} km from the other records in {rec.get("city")}'
    if pick:
        rec['lat'], rec['lon'] = round(pick['lat'], 6), round(pick['lon'], 6)
        urls = []
        for p in (a, b):
            for u in p.get('coord_urls') or []:
                if u.startswith('http') and u not in urls and has(p):
                    urls.append(u)
        rec.setdefault('field_sources', {})['coordinates'] = {'urls': urls[:3], 'basis': pick.get('coord_statement', ''), 'retrieved': date}
        decisions.append({'id': rid, 'result': 'set', 'lat': rec['lat'], 'lon': rec['lon'], 'how': why})
        tally['set'] = tally.get('set', 0) + 1
    else:
        decisions.append({'id': rid, 'result': 'left', 'why': why})
        tally[why.split(' km ')[0] if 'km from' in why else why] = tally.get(why.split(' km ')[0] if 'km from' in why else why, 0) + 1

json.dump(records, open(ROOT / 'institutions.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
out = ROOT / 'data/web_research/coordinate_audit_decisions.json'
prev = json.load(open(out, encoding='utf-8')) if out.exists() else []
merged = {d['id']: d for d in prev}
merged.update({d['id']: d for d in decisions})
json.dump(list(merged.values()), open(out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(tally)
