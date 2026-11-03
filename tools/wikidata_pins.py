#!/usr/bin/env python3
"""Second pass for the pins tools/geocode_pins.py could not place: look the record up on Wikidata and keep its
coordinate location (P625).

Input: a JSON list of {id, name, city, lat, lon} (the records still on a rough pin). For each, Wikidata's entity
search is asked for the name, then the name without its bracket; the first result that has a P625 within 30 km of
the stored pin and whose label or alias shares a distinctive word with the name is written, with its QID.
tools/apply_geocode.py --wikidata reads the output.
Usage: python3 tools/wikidata_pins.py rough.json [--out data/web_research/wikidata_pins_2026-11-03.json]
"""
import json
import math
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = 'culture-atlas-geocode/1 (vasspolina.github.io/Culture-Atlas)'
args = sys.argv[1:]
out = ROOT / 'data' / 'web_research' / 'wikidata_pins_2026-11-03.json'
src = None
while args:
    a = args.pop(0)
    if a == '--out':
        out = Path(args.pop(0))
    else:
        src = a
rows = json.load(open(src, encoding='utf-8'))
done = json.load(open(out, encoding='utf-8')) if out.exists() else {}
STOP = {'the', 'of', 'and', 'for', 'de', 'del', 'della', 'di', 'du', 'des', 'la', 'le', 'el', 'museum', 'museo',
        'musee', 'musée', 'museu', 'art', 'arts', 'gallery', 'galerie', 'centre', 'center', 'contemporary', 'modern',
        'foundation', 'fondation', 'fundación', 'fundacion', 'kunst', 'national', 'institute', 'house', 'space',
        'state', 'fine', 'city', 'museums'}


def km(a, b, c, d):
    p = math.pi / 180
    x = 0.5 - math.cos((c - a) * p) / 2 + math.cos(a * p) * math.cos(c * p) * (1 - math.cos((d - b) * p)) / 2
    return 12742 * math.asin(math.sqrt(x))


class Failed(Exception):
    pass


def api(params):
    """One Wikidata request; backs off on 429 and raises Failed after five tries, so a record is not stored empty."""
    q = urllib.parse.urlencode({**params, 'format': 'json', 'maxlag': 5})
    req = urllib.request.Request('https://www.wikidata.org/w/api.php?' + q, headers={'User-Agent': UA})
    for wait in (5, 15, 30, 60, 120):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                time.sleep(1.5)
                return json.load(r)
        except Exception as e:
            print('  error', e, '- waiting', wait, file=sys.stderr)
            time.sleep(wait)
    raise Failed


def words(s):
    return {w for w in re.findall(r'\w{3,}', s.lower()) if w not in STOP}


def search(r, names, want):
    """The first Wikidata item for one of the names that has a P625 within 30 km and shares a word with the name."""
    for n in names:
        s = api({'action': 'wbsearchentities', 'search': n, 'language': 'en', 'limit': 7, 'type': 'item'})
        if not s.get('search'):
            continue
        ids = [h['id'] for h in s['search']]
        e = api({'action': 'wbgetentities', 'ids': '|'.join(ids), 'props': 'claims|labels|aliases|descriptions',
                 'languages': 'en'})
        for qid in ids:
            ent = e.get('entities', {}).get(qid, {})
            p625 = ent.get('claims', {}).get('P625')
            v = p625 and p625[0]['mainsnak'].get('datavalue', {}).get('value')
            if not v:
                continue
            lab = ent.get('labels', {}).get('en', {}).get('value', '')
            als = ' '.join(a['value'] for a in ent.get('aliases', {}).get('en', []))
            if want and not (want & words(lab + ' ' + als)):
                continue
            d = km(r['lat'], r['lon'], v['latitude'], v['longitude']) if (r.get('lat') or r.get('lon')) else 0
            if d > 30:
                continue
            return {'qid': qid, 'label': lab, 'desc': ent.get('descriptions', {}).get('en', {}).get('value', ''),
                    'lat': v['latitude'], 'lon': v['longitude'], 'km': round(d, 3)}
    return None


out.parent.mkdir(parents=True, exist_ok=True)
for r in rows:
    if r['id'] in done:
        continue
    names = [r['name']]
    short = re.sub(r'\s*\(.*?\)', '', r['name']).split(':')[0].strip()
    if short != r['name']:
        names.append(short)
    want = words(r['name'])
    try:
        found = search(r, names, want)
    except Failed:
        print(f"{r['id'][:45]:45} failed, left for the next run")
        continue
    done[r['id']] = {'name': r['name'], 'city': r.get('city'), 'stored': [r.get('lat'), r.get('lon')], **(found or {})}
    print(f"{r['id'][:45]:45} {found['qid'] + ' ' + str(found['km']) + ' km ' + found['label'] if found else 'nothing'}")
    json.dump(done, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('in file', len(done), 'with coordinates', sum(1 for v in done.values() if 'qid' in v))
