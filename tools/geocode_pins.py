#!/usr/bin/env python3
"""Look up every record's building on OpenStreetMap (Nominatim) and write what it finds to a review file.

Most pins were placed by hand from rounded coordinates: 852 records have three decimals (about 100 m) and 212
have one or two (1 to 10 km), so a pin sits on the wrong street, or on the city centre. This asks Nominatim for
the address when the record has one, and for the name in the city when it does not, and records the answer next
to the stored pin with the distance between them. Nothing in institutions.json changes here; tools/apply_geocode.py
reads the review file and decides what to move.

Usage: python3 tools/geocode_pins.py [--limit N] [--out data/web_research/geocode_2026-11-03.json]
Resumes from the output file, so it can be stopped and run again. One request a second, as Nominatim asks.
"""
import json
import math
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = 'culture-atlas-geocode/1 (vasspolina.github.io/Culture-Atlas)'
args = sys.argv[1:]
limit = None
out = ROOT / 'data' / 'web_research' / 'geocode_2026-11-03.json'
while args:
    a = args.pop(0)
    if a == '--limit':
        limit = int(args.pop(0))
    elif a == '--out':
        out = Path(args.pop(0))

records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
done = json.load(open(out, encoding='utf-8')) if out.exists() else {}


def km(a, b, c, d):
    p = math.pi / 180
    x = 0.5 - math.cos((c - a) * p) / 2 + math.cos(a * p) * math.cos(c * p) * (1 - math.cos((d - b) * p)) / 2
    return 12742 * math.asin(math.sqrt(x))


def nominatim(params):
    q = urllib.parse.urlencode({**params, 'format': 'jsonv2', 'limit': 3, 'addressdetails': 0})
    req = urllib.request.Request('https://nominatim.openstreetmap.org/search?' + q, headers={'User-Agent': UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except Exception as e:
        print('  error', e, file=sys.stderr)
        return None
    finally:
        time.sleep(1.1)


n = 0
for r in records:
    if r['id'] in done or r.get('fixed_venue') is False:
        continue
    if limit is not None and n >= limit:
        break
    n += 1
    lat, lon = r.get('lat') or 0, r.get('lon') or 0
    city, country = r.get('city') or '', r.get('country') or ''
    queries = []
    if r.get('address'):
        queries.append(('address', {'q': r['address']}))
    queries.append(('name', {'q': f"{r['name']}, {city}, {country}"}))
    queries.append(('name-short', {'q': f"{r['name'].split('(')[0].split(':')[0].strip()}, {city}"}))
    found = None
    for kind, params in queries:
        hits = nominatim(params)
        if hits is None:
            found = {'error': True}
            break
        hits = [h for h in hits if h.get('lat')]
        if hits:
            h = hits[0]
            found = {'how': kind, 'lat': float(h['lat']), 'lon': float(h['lon']), 'display': h.get('display_name'),
                     'type': h.get('type'), 'osm': f"{h.get('osm_type')}/{h.get('osm_id')}", 'n': len(hits)}
            break
    entry = {'name': r['name'], 'city': city, 'stored': [lat, lon], 'address': r.get('address')}
    if found and not found.get('error'):
        entry.update(found)
        entry['km'] = round(km(lat, lon, found['lat'], found['lon']), 3) if lat or lon else None
        print(f"{r['id']:40} {found['how']:10} {entry['km']} km  {found['display'][:70] if found['display'] else ''}")
    elif found:
        print(f"{r['id']:40} ERROR")
        continue
    else:
        print(f"{r['id']:40} nothing")
    done[r['id']] = entry
    if n % 10 == 0:
        out.parent.mkdir(parents=True, exist_ok=True)
        json.dump(done, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
out.parent.mkdir(parents=True, exist_ok=True)
json.dump(done, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('looked up', n, 'total in file', len(done))
