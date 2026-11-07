#!/usr/bin/env python3
"""Fetch the street address OpenStreetMap holds for every record that has none, and write it to a review file.

The search-based address audit (tools/apply_address_audit.py, 14 Oct 2026) found nothing for 701 of the records it was
asked to fill. Most of those records have since been matched to their building on OpenStreetMap by the pin audit
(tools/geocode_pins.py and tools/apply_geocode.py, 3 Nov 2026): the object is named in field_sources.coordinates.
That object usually carries its own address, so this asks Nominatim for it, 50 objects a request, with the
address split into its parts (house number, road, postcode, city).

A record whose pin did not come from OpenStreetMap is searched by name in its city, and a hit is kept only on the
terms tools/apply_geocode.py uses for pins: a place, not an area; a distinctive word of the name in the hit's name;
within 15 km of the stored pin.

Nothing in institutions.json changes here; tools/apply_osm_addresses.py reads the review file and decides.
Usage: python3 tools/osm_addresses.py [--out data/web_research/osm_addresses_2026-11-04.json] [--limit N]
Resumes from the output file. One request every two seconds, under Nominatim's limit of one a second.
"""
import json
import math
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = 'culture-atlas-address/1 (vasspolina.github.io/Culture-Atlas)'
args = sys.argv[1:]
out = ROOT / 'data' / 'web_research' / 'osm_addresses_2026-11-04.json'
limit = None
while args:
    a = args.pop(0)
    if a == '--out':
        out = Path(args.pop(0))
    elif a == '--limit':
        limit = int(args.pop(0))
records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
done = json.load(open(out, encoding='utf-8')) if out.exists() else {}

# Areas and roads are not a building: a hit of these types is never taken from a name search.
AREA = {'city', 'town', 'village', 'hamlet', 'suburb', 'neighbourhood', 'quarter', 'borough', 'administrative',
        'county', 'state', 'country', 'postcode', 'region', 'district', 'municipality', 'island', 'locality',
        'residential', 'primary', 'secondary', 'tertiary', 'trunk', 'motorway', 'unclassified', 'service',
        'pedestrian', 'footway', 'living_street', 'road', 'track', 'path', 'bus_stop', 'station', 'stop_position',
        'platform', 'parking', 'park', 'square'}
STOP = {'the', 'of', 'and', 'for', 'de', 'del', 'della', 'di', 'du', 'des', 'la', 'le', 'el', 'museum', 'museo',
        'musee', 'museu', 'art', 'arts', 'gallery', 'galerie', 'centre', 'center', 'contemporary', 'modern',
        'foundation', 'fondation', 'fundacion', 'kunst', 'national', 'institute', 'house', 'space', 'state', 'fine',
        'city', 'museums', 'galleria', 'galeria', 'arte', 'van', 'von', 'der', 'und', 'et', 'y', 'e', 'at', 'in'}


def fold(s):
    s = unicodedata.normalize('NFKD', s or '')
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()


def words(s):
    return {w for w in re.findall(r'[^\W_]{3,}', fold(s)) if w not in STOP}


def km(a, b, c, d):
    p = math.pi / 180
    h = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


def get(path, params):
    url = 'https://nominatim.openstreetmap.org/' + path + '?' + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'en'})
            with urllib.request.urlopen(req, timeout=60) as r:
                body = json.load(r)
            time.sleep(2)
            return body
        except Exception as e:  # network trouble: wait and try again, then give up on this request
            print('  retry', attempt + 1, e, file=sys.stderr)
            time.sleep(30 * (attempt + 1))   # a 429 asks for a pause, not a quick retry
    return None


def save():
    out.write_text(json.dumps(done, ensure_ascii=False, indent=1), encoding='utf-8')


def osm_of(r):
    for u in (r.get('field_sources', {}).get('coordinates') or {}).get('urls') or []:
        m = re.match(r'https://www\.openstreetmap\.org/(node|way|relation)/(\d+)$', u)
        if m:
            return m.group(1)[0].upper() + m.group(2)
    return None


def row(hit, how):
    return {'how': how, 'osm': f"{hit.get('osm_type')}/{hit.get('osm_id')}", 'name': hit.get('name') or '',
            'type': hit.get('type'), 'category': hit.get('category') or hit.get('class'),
            'lat': float(hit['lat']), 'lon': float(hit['lon']), 'address': hit.get('address') or {}}


todo = [r for r in records if not r.get('address') and r['id'] not in done]
if limit:
    todo = todo[:limit]
by_osm = {}
for r in todo:
    o = osm_of(r)
    if o:
        by_osm.setdefault(o, []).append(r)
keys = list(by_osm)
print(len(todo), 'records to look up;', len(keys), 'by their OpenStreetMap object')
for i in range(0, len(keys), 50):
    batch = keys[i:i + 50]
    hits = get('lookup', {'osm_ids': ','.join(batch), 'format': 'jsonv2', 'addressdetails': 1}) or []
    seen = set()
    for h in hits:
        k = h['osm_type'][0].upper() + str(h['osm_id'])
        seen.add(k)
        for r in by_osm.get(k, []):
            done[r['id']] = row(h, 'pin object')
    for k in batch:
        if k not in seen:
            for r in by_osm[k]:
                done[r['id']] = {'how': 'pin object', 'osm': k, 'missing': True}
    save()
    print(' looked up', min(i + 50, len(keys)), 'of', len(keys))

rest = [r for r in todo if r['id'] not in done]
print(len(rest), 'records to search by name')
for n, r in enumerate(rest, 1):
    lat, lon = r.get('lat'), r.get('lon')
    names = [r['name']] + [a for a in (r.get('aliases') or []) if a != r['name']]
    short = re.sub(r'\s*\(.*?\)\s*', ' ', r['name']).strip()
    if short != r['name']:
        names.append(short)
    want = set().union(*(words(x) for x in names)) if names else set()
    found = None
    for q in names[:3]:
        hits = get('search', {'q': f"{q}, {r.get('city') or ''}, {r.get('country') or ''}", 'format': 'jsonv2',
                              'addressdetails': 1, 'limit': 5}) or []
        for h in hits:
            if h.get('type') in AREA or h.get('addresstype') in AREA:
                continue
            if not (words(h.get('name') or '') & want):
                continue
            if lat is not None and lon is not None and km(lat, lon, float(h['lat']), float(h['lon'])) > 15:
                continue
            found = row(h, 'name search')
            break
        if found:
            break
    done[r['id']] = found or {'how': 'name search', 'none': True}
    if n % 10 == 0 or n == len(rest):
        save()
        print(' searched', n, 'of', len(rest))
save()
print('wrote', out.relative_to(ROOT), 'with', len(done), 'rows')
