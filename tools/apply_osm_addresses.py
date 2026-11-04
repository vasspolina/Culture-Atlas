#!/usr/bin/env python3
"""Write the addresses tools/osm_addresses.py found into institutions.json, then run tools/clean_data.py and
tools/embed_data.py.

An address is written only when OpenStreetMap gives a house number and a street for the place itself, so a value
that names only a street, a district or a city is never written (the rule tools/apply_address_audit.py keeps).
It is set out the way each country writes it: the number before the street in the English-speaking countries and
France, after it elsewhere; the postcode after the city where that is the custom, before it elsewhere. The country
is the record's own.

A record matched by name search (no OpenStreetMap pin yet) also has its pin moved to the building, on the terms of
tools/apply_geocode.py: a move of more than 2 km from a precise pin (three decimals or more) is not made, and then
the address is not written either, because the hit may be a namesake. Those records are listed for a hand check.
The OpenStreetMap object is recorded under field_sources.address (and field_sources.coordinates when the pin moves).
Usage: python3 tools/apply_osm_addresses.py [data/web_research/osm_addresses_2026-11-04.json] [--date 2026-11-04] [--dry]
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
args = sys.argv[1:]
src = ROOT / 'data' / 'web_research' / 'osm_addresses_2026-11-04.json'
date = '2026-11-04'
dry = False
while args:
    a = args.pop(0)
    if a == '--date':
        date = args.pop(0)
    elif a == '--dry':
        dry = True
    else:
        src = Path(a)
found = json.load(open(src, encoding='utf-8'))
path = ROOT / 'institutions.json'
records = json.load(open(path, encoding='utf-8'))

NUMBER_FIRST = {'us', 'gb', 'ie', 'ca', 'au', 'nz', 'za', 'fr', 'lu', 'in', 'sg', 'my', 'ph', 'hk', 'il', 'ng', 'gh',
                'ke', 'jm', 'tt', 'bs', 'bb', 'lk', 'pk', 'bd', 'mt', 'cy', 'th', 'vn', 'kr', 'cn', 'tw'}
# Japan numbers blocks, not buildings on a street: an OpenStreetMap "road" there is a prefectural route
# (Miyano Otoshi Line), so a number beside it is not an address. Japanese records are left as they are.
NO_STREET_ADDRESSES = {'jp'}
POSTCODE_AFTER = {'us', 'ca', 'gb', 'au', 'nz', 'ie', 'za', 'in', 'sg', 'my', 'jp', 'kr', 'cn', 'hk', 'tw', 'th',
                  'ph', 'br', 'ru', 'ua', 'by', 'kz', 'ng', 'ke', 'gh', 'lk', 'pk', 'bd', 'id', 'vn', 'mt'}
STATE_CODE = {'us', 'ca', 'au'}   # Washington, DC 20009; Toronto, ON M5T 1G4; Melbourne, VIC 3004


def km(a, b, c, d):
    p = math.pi / 180
    h = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742 * math.asin(math.sqrt(h))


def decimals(x):
    s = repr(float(x))
    return len(s.split('.')[1].rstrip('0')) if '.' in s else 0


def compose(a, country, own_city):
    cc = (a.get('country_code') or '').lower()
    if cc in NO_STREET_ADDRESSES:
        return None
    num = (a.get('house_number') or '').split(';')[0].strip()
    num = re.sub(r'^(\d+)号$', r'\1', num)            # 200号 is "No. 200"
    road = (a.get('road') or a.get('pedestrian') or '').strip()
    # A street signed in two scripts ("Rue Tissa زنقة تيسة") keeps its Latin name; one in Chinese characters only, or
    # a house number that is still in them, is left out rather than set beside English words it cannot be read with.
    # Cyrillic and Greek street names stay: that is how the street is signed.
    if re.search(r'[A-Za-z]', road):
        road = re.sub(r'\s*[\u0600-\u06FF][\u0600-\u06FF\s]*', ' ', road).strip()
    if not num or not road or re.search(r'[\u3000-\u9FFF]', road + num):
        return None
    street = f'{num} {road}' if cc in NUMBER_FIRST else f'{road} {num}'
    city = a.get('city') or a.get('town') or a.get('village') or a.get('municipality') or a.get('hamlet') or ''
    # OpenStreetMap names a district where the city belongs (Greater London, Dongcheng District, Yongin-si stays):
    # the record's own city is used then.
    if not city or city.startswith('Greater ') or city.endswith(' District') or city.endswith(' Ward'):
        city = own_city or city
    if city.isupper():
        city = city.title()                                  # RABAT
    if city and country and city.lower() == country.lower():   # Hong Kong, Hong Kong; Singapore, Singapore
        country = ''
    pc = (a.get('postcode') or '').split(';')[0].strip()
    if cc in STATE_CODE:
        iso = a.get('ISO3166-2-lvl4') or ''
        state = iso.split('-', 1)[1] if '-' in iso else ''
        place = ', '.join(x for x in [city, ' '.join(x for x in [state, pc] if x)] if x)
    elif cc in POSTCODE_AFTER:
        place = ' '.join(x for x in [city, pc] if x)
    else:
        place = ' '.join(x for x in [pc, city] if x)
    return ', '.join(x for x in [street, place, country] if x)


# A name search can land on a namesake: NEON (Athens) found a travel agency, Kingston Creative a guest house,
# Anadolu Kültür a school. A name match is taken only when the object is a venue of the kind the atlas records.
PLACE_TYPES = {'museum', 'gallery', 'arts_centre', 'theatre', 'attraction', 'community_centre', 'civic', 'public',
               'yes', 'building', 'concert_hall', 'exhibition_centre', 'library'}
# Checked by hand on 4 Nov 2026 and wrong, though the type passes:
REJECTED = {
    'international-center-of-photography-new-york': '1133 Fifth Avenue is the old building; ICP moved to 79 Essex Street',
    'national-gallery-prague': 'the hit is one branch (Schwarzenberg Palace), not the institution',
    'long-museum-shanghai': 'the house number is in Chinese and reads as part of the street',
    'eyebeam-new-york': 'not confirmed that Eyebeam is still at 199 Cook Street',
}
written, moved, review, skipped = [], [], [], {'no house number or street': 0, 'not found': 0,
                                               'name match not a venue, or checked and wrong': 0}
for r in records:
    f = found.get(r['id'])
    if r.get('address') or not f:
        continue
    if not f.get('address'):
        skipped['not found'] += 1
        continue
    addr = compose(f['address'], r.get('country') or f['address'].get('country') or '', r.get('city') or '')
    if not addr:
        skipped['no house number or street'] += 1
        continue
    url = 'https://www.openstreetmap.org/' + f['osm']
    move = None
    if f['how'] == 'name search' and (f.get('type') not in PLACE_TYPES or r['id'] in REJECTED):
        skipped['name match not a venue, or checked and wrong'] += 1
        continue
    if f['how'] == 'name search':
        lat, lon = r.get('lat'), r.get('lon')
        if lat is not None and lon is not None:
            d = km(lat, lon, f['lat'], f['lon'])
            precise = min(decimals(lat), decimals(lon)) >= 3
            if d > 2 and precise:
                review.append({'id': r['id'], 'name': r['name'], 'osm': url, 'osm_name': f['name'], 'km': round(d, 2), 'address': addr})
                continue
            if d > 0.05:
                move = (round(f['lat'], 6), round(f['lon'], 6), round(d, 2))
        else:
            move = (round(f['lat'], 6), round(f['lon'], 6), None)
    r['address'] = addr
    fs = r.setdefault('field_sources', {})
    fs['address'] = {'urls': [url], 'basis': f"OpenStreetMap, {f['how']}: {f.get('name') or ''}".rstrip(': '), 'retrieved': date}
    written.append({'id': r['id'], 'address': addr, 'osm': url})
    if move:
        r['lat'], r['lon'] = move[0], move[1]
        fs['coordinates'] = {'urls': [url], 'basis': f"OpenStreetMap, name lookup: {f.get('name') or ''}", 'retrieved': date}
        moved.append({'id': r['id'], 'km': move[2]})

print('addresses written:', len(written), '| pins moved:', len(moved), '| held for a hand check:', len(review))
print('skipped:', skipped)
report = ROOT / 'data' / 'web_research' / f'osm_addresses_decisions_{date}.json'
if dry:
    for w in [w for w in written if found[w['id']]['how'] == 'name search']:
        print(' ', w['id'], '|', w['address'])
    print('review:', review)
    print('moved:', moved)
    sys.exit()
report.write_text(json.dumps({'written': written, 'moved': moved, 'review': review, 'skipped': skipped},
                             ensure_ascii=False, indent=1), encoding='utf-8')
path.write_text(json.dumps(records, ensure_ascii=False, indent=1), encoding='utf-8')
subprocess.run([sys.executable, str(ROOT / 'tools' / 'clean_data.py')], check=True, stdout=subprocess.DEVNULL)
subprocess.run([sys.executable, str(ROOT / 'tools' / 'embed_data.py')], check=True)
print('report:', report.relative_to(ROOT))
