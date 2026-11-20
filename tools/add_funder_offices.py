#!/usr/bin/env python3
"""Give researched funders a head office on the money map.

tools/funder_profiles.py merges a researched batch (sponsor-atlas/work/ubatch/fpN-result.json, written to
ubatch/FUNDERS.md) into data/funder_profiles.json, but a profile shows only for a funder that has an office in
assets/hq.json, and tools/build_hq.py takes offices from its own table and tools/hq_extra.json. The first 28 batches
profiled offices that already existed. A batch of funders new to the atlas (named by funding lines written since)
needs the office too, and this adds it from the same researched row:

  - a row with `wrong_match` (the name is not a funder of the museums that name it), marked thin, with no seat city,
    or that the profile lint stops, gets no office;
  - a row whose official name is the name of an office already on the map gives its key to that office
    (tools/hq_aliases.json), so 'VTB' and 'VTB Bank' are one office;
  - every other row becomes an office in tools/hq_extra.json: official name, kind, seat city and country, the
    street address where the row has one, its first source, and the city's coordinates from OpenStreetMap
    (Nominatim, one request a second, kept in data/web_research/funder_city_coords.json).

Then run: tools/funder_profiles.py merge <the same files>, tools/build_hq.py, tools/funder_profiles.py build.
Usage: python3 tools/add_funder_offices.py <fpN-result.json> [...] [--dry]
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import funder_profiles  # noqa: E402

UA = 'culture-atlas-address/1 (vasspolina.github.io/Culture-Atlas)'
dry = '--dry' in sys.argv
paths = [a for a in sys.argv[1:] if a != '--dry']
extra_path, alias_path = ROOT / 'tools' / 'hq_extra.json', ROOT / 'tools' / 'hq_aliases.json'
coords_path = ROOT / 'data' / 'web_research' / 'funder_city_coords.json'
extra = json.load(open(extra_path, encoding='utf-8'))
aliases = json.load(open(alias_path, encoding='utf-8'))
coords = json.load(open(coords_path, encoding='utf-8')) if coords_path.exists() else {}
hq = json.load(open(ROOT / 'assets' / 'hq.json', encoding='utf-8'))['org']
by_name = {}
for k, o in list(hq.items()) + list(extra.items()):
    by_name.setdefault(o['n'].strip().lower(), k)
taken = set(hq) | set(extra) | {k for ks in aliases.values() for k in ks}


def city_point(city, country):
    key = f'{city}, {country}'
    if key not in coords:
        # The structured search first; a country OpenStreetMap names otherwise (Palestine) is searched as free text.
        hits = []
        for params in ({'city': city, 'country': country}, {'q': key}):
            url = 'https://nominatim.openstreetmap.org/search?' + urllib.parse.urlencode(dict(params, format='jsonv2', limit=1))
            try:
                req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'en'})
                with urllib.request.urlopen(req, timeout=60) as r:
                    hits = json.load(r)
            except Exception as e:
                print('  no answer for', key, e, file=sys.stderr)
                return None
            time.sleep(1.2)
            if hits:
                break
        coords[key] = {'lat': round(float(hits[0]['lat']), 4), 'lon': round(float(hits[0]['lon']), 4),
                       'osm': f"{hits[0].get('osm_type')}/{hits[0].get('osm_id')}"} if hits else None
    return coords[key]


new, joined, left = [], [], []
for p in paths:
    for r in json.load(open(p, encoding='utf-8')):
        k, name = r.get('key'), (r.get('name') or '').strip()
        if not k or k in taken:
            continue
        if r.get('wrong_match'):
            left.append(f'{k}: not a funder as named ({r["wrong_match"][:90]})')
            continue
        if r.get('status') == 'thin':
            left.append(f'{k}: thin, what it is rests on no confirmed source')
            continue
        probs = funder_profiles.lint(r)
        if probs:
            left.append(f'{k}: stopped by the profile lint ({"; ".join(probs)})')
            continue
        if not name or not (r.get('city') or '').strip() or not (r.get('country') or '').strip():
            left.append(f'{k}: no seat city')
            continue
        same = by_name.get(name.lower())
        if same:
            aliases.setdefault(same, []).append(k)    # build_hq.py reads the list as the office's other keys
            taken.add(k)
            joined.append(f'{k} -> {same} ({name})')
            continue
        pt = city_point(r['city'].strip(), r['country'].strip())
        if not pt:
            left.append(f'{k}: OpenStreetMap does not place {r["city"]}, {r["country"]}')
            continue
        o = {'n': name, 'k': {'person': 'found'}.get(r.get('kind'), r.get('kind') or 'corp'), 'c': r['city'].strip(),
             'co': r['country'].strip(), 'lat': pt['lat'], 'lon': pt['lon']}
        if (r.get('address') or '').strip():
            o['a'] = r['address'].strip()
        src = [s for s in r.get('sources') or [] if isinstance(s, str) and s.startswith('http')]
        o['s'] = src[0]
        extra[k] = o
        by_name[name.lower()] = k
        taken.add(k)
        new.append(k)

print('offices added:', len(new), '| keys given to an office already on the map:', len(joined), '| left without an office:', len(left))
for x in joined + left:
    print(' ', x)
if dry:
    sys.exit()
coords_path.write_text(json.dumps(coords, ensure_ascii=False, indent=1), encoding='utf-8')
extra_path.write_text(json.dumps(extra, ensure_ascii=False, indent=0), encoding='utf-8')
alias_path.write_text(json.dumps(aliases, ensure_ascii=False, indent=1), encoding='utf-8')
