#!/usr/bin/env python3
"""Move the pins OpenStreetMap could not place to the coordinate location (P625) Wikidata gives them
(tools/wikidata_pins.py), then rerun clean and embed.

A pin moves when the item's label shares a word with the name (checked by tools/wikidata_pins.py), the item lies
within 15 km of the stored pin, and the record is not in REJECTED. A move of more than 2 km needs the record in
CHECKED. The QID goes under field_sources.coordinates.
Usage: python3 tools/apply_wikidata_pins.py [data/web_research/wikidata_pins_2026-11-03.json] [--date 2026-11-03] [--dry]
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
args = sys.argv[1:]
src = ROOT / 'data' / 'web_research' / 'wikidata_pins_2026-11-03.json'
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

# Checked by hand on 2026-11-03.
# Moves of more than 2 km that are right: the stored pin was a city or town placeholder.
CHECKED = {'pushkin-state-museum-of-fine-arts-moscow', 'mathaf-arab-museum-of-modern-art-doha',
           'skowhegan-school-of-painting-sculpture-skowhegan', 'magazzino-italian-art'}
# Another place with a similar name, an old site, a parish, or an event or network with no single building.
REJECTED = {'centro-león-santiago-de-los-caballeros', 'victoria-gallery-samara', 'metropolitan-museum-of-manila-taguig',
            'compton-verney-kineton', 'transmediale-berlin', 'fringe-world-perth', 'momus-thessaloniki'}

wd = json.load(open(src, encoding='utf-8'))
records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
moved, review = [], []
for r in records:
    w = wd.get(r['id'])
    if not w or 'qid' not in w:
        continue
    why = None
    if r['id'] in REJECTED:
        why = 'rejected on the hand check'
    elif [r.get('lat'), r.get('lon')] != w['stored']:
        why = 'pin changed since the lookup'
    elif w['km'] > 15:
        why = f"{w['km']:.1f} km from the stored pin"
    elif w['km'] > 2 and r['id'] not in CHECKED:
        why = f"{w['km']:.1f} km, not checked by hand"
    if why:
        review.append((r['id'], why))
        continue
    moved.append((r['id'], w))
    if dry:
        continue
    r['lat'], r['lon'] = round(w['lat'], 6), round(w['lon'], 6)
    r.setdefault('field_sources', {})['coordinates'] = {
        'urls': ['https://www.wikidata.org/wiki/' + w['qid']],
        'basis': f"Wikidata {w['qid']} coordinate location (P625): {w['label']}",
        'retrieved': date}

print(f'moved {len(moved)}, for review {len(review)}')
for id_, w in sorted(moved, key=lambda m: -m[1]['km']):
    print(f"  {w['km']:6.2f} km  {id_} <- {w['qid']} {w['label']}")
for id_, why in review:
    print(f'  {id_:45} {why}')
if dry:
    sys.exit()
json.dump(records, open(ROOT / 'institutions.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
subprocess.run([sys.executable, ROOT / 'tools' / 'clean_data.py'], check=True)
subprocess.run([sys.executable, ROOT / 'tools' / 'embed_data.py'], check=True)
