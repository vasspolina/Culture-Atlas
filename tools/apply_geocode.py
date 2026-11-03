#!/usr/bin/env python3
"""Move pins to the building OpenStreetMap found for them (tools/geocode_pins.py), then rerun clean and embed.

A pin moves only when the answer is the same place, found more precisely:
  - the hit is a place, not an area: a Nominatim type such as museum, gallery, arts_centre, building, house or yes,
    never a city, suburb, administrative unit or postcode; a bare road only when it came from the record's own
    address and the stored pin is rough (two decimals or fewer, or shared with another record);
  - a lookup by name, not address, must carry a distinctive word of the name (a namesake or a neighbour does not);
  - a move of more than 2 km from a precise pin needs a hand check (data/web_research/geocode_checked.json);
  - the hit lies within 15 km of the stored pin (a namesake in another town stays out), or the record had no pin
    at all and the hit's display name contains the record's city;
  - a pin that already carries a cited source (field_sources.coordinates) moves only when the hit is within 1 km of it.
The OSM object is recorded under field_sources.coordinates. Every other record is listed in the report for review.
Usage: python3 tools/apply_geocode.py [data/web_research/geocode_2026-11-03.json] [--date 2026-11-03] [--dry]
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
args = sys.argv[1:]
src = ROOT / 'data' / 'web_research' / 'geocode_2026-11-03.json'
date = '2026-11-03'
dry = False
while args:
    a = args.pop(0)
    if a == '--date':
        date = args.pop(0)
    elif a == '--dry':
        dry = True
    else:
        src = Path(a)

AREA = {'city', 'town', 'village', 'hamlet', 'suburb', 'quarter', 'neighbourhood', 'administrative', 'county',
        'state', 'region', 'country', 'postcode', 'island', 'municipality', 'borough', 'district', 'province',
        'city_district', 'locality', 'residential', 'road', 'pedestrian', 'primary', 'secondary', 'tertiary',
        'footway', 'path', 'cycleway', 'service', 'unclassified', 'living_street', 'trunk', 'motorway', 'square'}
# A street from the record's own address still beats a pin on the city centre.
ROAD = {'road', 'pedestrian', 'primary', 'secondary', 'tertiary', 'unclassified', 'living_street', 'residential',
        'service', 'square'}

geo = json.load(open(src, encoding='utf-8'))
records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))


def km(a, b, c, d):
    p = math.pi / 180
    x = 0.5 - math.cos((c - a) * p) / 2 + math.cos(a * p) * math.cos(c * p) * (1 - math.cos((d - b) * p)) / 2
    return 12742 * math.asin(math.sqrt(x))


STOP = {'the', 'of', 'and', 'for', 'de', 'del', 'della', 'di', 'du', 'des', 'la', 'le', 'el', 'museum', 'museo',
        'musee', 'musée', 'museu', 'art', 'arts', 'gallery', 'galerie', 'centre', 'center', 'contemporary', 'modern',
        'foundation', 'fondation', 'fundación', 'fundacion', 'kunst', 'national', 'institute', 'house', 'space'}
# Hits more than 2 km from a precise pin that were checked by hand against the institution's own address.
CHECKED = set(json.load(open(ROOT / 'data' / 'web_research' / 'geocode_checked.json', encoding='utf-8'))) \
    if (ROOT / 'data' / 'web_research' / 'geocode_checked.json').exists() else set()
# Hits that passed the rules but are another place with a similar name, found on the same hand check.
REJECTED = {'neon-athens', 'momus-thessaloniki', 'fondation-cartier', 'kingston-creative'}
shared = {}
for r in records:
    if r.get('lat') or r.get('lon'):
        shared.setdefault((round(r['lat'], 3), round(r['lon'], 3)), []).append(r['id'])


def decimals(x):
    s = repr(float(x))
    return len(s.split('.')[1].rstrip('0'))


page = (ROOT / 'index.html').read_text(encoding='utf-8')
CENTRES = [(c['lat'], c['lon']) for c in
           json.loads(page.split('const ALL_CITIES_REGISTRY = ')[1].split(';\n')[0]) if c.get('lat')]


def rough(r):
    """A pin placed on a city centre or a placeholder: two decimals or fewer, shared with another record, or within
    1 km of a city's centre point in ALL_CITIES_REGISTRY."""
    return min(decimals(r['lat']), decimals(r['lon'])) <= 2 or \
        len(shared.get((round(r['lat'], 3), round(r['lon'], 3)), [])) > 1 or \
        any(km(r['lat'], r['lon'], a, b) < 1 for a, b in CENTRES)


# Nominatim types that are a cultural building; a hit of this type whose name is in another script counts as the name.
CULTURE = {'museum', 'gallery', 'arts_centre', 'theatre', 'library', 'attraction', 'artwork', 'cinema', 'community_centre'}


def name_in(r, g):
    disp = (g.get('display') or '').lower()
    words = [w for w in re.findall(r'\w{3,}', (r['name'] + ' ' + ' '.join(r.get('aliases') or [])).lower())
             if w not in STOP]
    if any(w in disp for w in words):
        return True
    head = disp.split(',')[0]
    return g.get('type') in CULTURE and any(ord(ch) > 0x24f for ch in head)


moved, kept, review = [], [], []
for r in records:
    g = geo.get(r['id'])
    if not g or 'lat' not in g:
        if g:
            review.append((r['id'], 'nothing found', g))
        continue
    lat, lon = r.get('lat') or 0, r.get('lon') or 0
    had_pin = bool(lat or lon)
    d = km(lat, lon, g['lat'], g['lon']) if had_pin else None
    city = (r.get('city') or '').lower()
    why = None
    on_street = g['how'] == 'address' and g.get('type') in ROAD and had_pin and rough(r) and d <= 15
    if r['id'] in REJECTED:
        why = 'rejected on the hand check'
    elif g.get('type') in AREA and not on_street:
        why = f"area, not a place ({g.get('type')})"
    elif g['how'] != 'address' and not name_in(r, g):
        why = 'name lookup, and the hit does not carry the name'
    elif had_pin and d > 15:
        why = f'{d:.1f} km from the stored pin'
    elif had_pin and d > 2 and not rough(r) and r['id'] not in CHECKED:
        why = f'{d:.1f} km from a precise pin'
    elif not had_pin and city and city not in (g.get('display') or '').lower():
        why = 'no stored pin and the hit is not in the city'
    elif r.get('field_sources', {}).get('coordinates') and had_pin and d > 1:
        why = f'pin has a cited source and the hit is {d:.1f} km away'
    if why:
        review.append((r['id'], why, g))
        continue
    if had_pin and d < 0.005:
        kept.append(r['id'])
        continue
    moved.append((r['id'], r['name'], d, g))
    if dry:
        continue
    r['lat'], r['lon'] = round(g['lat'], 6), round(g['lon'], 6)
    r.setdefault('field_sources', {})['coordinates'] = {
        'urls': ['https://www.openstreetmap.org/' + g['osm']],
        'basis': f"OpenStreetMap, {g['how']} lookup: {g.get('display')}",
        'retrieved': date}

print(f'moved {len(moved)}, already exact {len(kept)}, for review {len(review)}')
far = sorted((m for m in moved if m[2]), key=lambda m: -m[2])
print('\nLargest moves:')
for id_, name, d, g in far[:25]:
    print(f'  {d:6.2f} km  {name} <- {(g.get("display") or "")[:80]}')
print('\nFor review:')
for id_, why, g in review:
    print(f'  {id_:40} {why}')
if dry:
    sys.exit()
json.dump(records, open(ROOT / 'institutions.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
subprocess.run([sys.executable, ROOT / 'tools' / 'clean_data.py'], check=True)
subprocess.run([sys.executable, ROOT / 'tools' / 'embed_data.py'], check=True)
