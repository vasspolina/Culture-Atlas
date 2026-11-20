#!/usr/bin/env python3
"""Add researched spaces that institutions.json does not hold yet.

Reads a file of checked pin rows (data/research_attach/new_spaces_<date>.json, written to
sponsor-atlas/work/ubatch/NEWSPACES.md and second-checked under CHECKER.md and SLOP.md) and appends each as a record.
A row is refused, and named, when the atlas already holds the space:
  - its id, or the id it would fold into (data/duplicates.json), is taken;
  - its name or an alias equals the name, an alias or a former id of a record within 30 km, accents and case set
    aside (a namesake further away is no duplicate, but the row loses an alias another record already answers to);
  - a record's pin is within 150 m and the two names share a distinctive word.
A row with no coordinates, no source or no name is refused too. Fields the pipeline does not keep on a record (the
checker's working fields) are left behind. Then tools/clean_data.py and tools/embed_data.py run.
With --reports <folder> the Details reports of the added records (<id>.txt, written to data/details_prompt.md) are
imported in the same run, and tools/absence.py's filter is applied to those records.
Usage: python3 tools/add_spaces.py data/research_attach/new_spaces_2026-11-20.json [--reports <folder>] [--dry]
"""
import json
import math
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
dry = '--dry' in sys.argv
argv = [a for a in sys.argv[1:] if a != '--dry']
reports = Path(argv[argv.index('--reports') + 1]) if '--reports' in argv else None
src = Path([a for a in argv if a != '--reports' and (not reports or Path(a) != reports)][0])
rows = json.load(open(src, encoding='utf-8'))
path = ROOT / 'institutions.json'
records = json.load(open(path, encoding='utf-8'))
dup = {k: v for k, v in json.load(open(ROOT / 'data' / 'duplicates.json', encoding='utf-8')).items() if k != '_about'}

KEEP = ('name', 'location', 'tier', 'size', 'funding', 'watch', 'flags', 'why_flagged', 'sources', 'lat', 'lon', 'country',
        'city', 'website', 'id', 'aliases', 'visit_url', 'address', 'year_founded', 'opening_hours', 'admission_fee',
        'field_sources')
STOP = {'the', 'of', 'and', 'for', 'de', 'del', 'della', 'di', 'du', 'des', 'la', 'le', 'el', 'museum', 'museo',
        'musee', 'museu', 'art', 'arts', 'gallery', 'galerie', 'centre', 'center', 'contemporary', 'modern',
        'foundation', 'national', 'institute', 'house', 'state', 'fine', 'city', 'in', 'at'}


def fold(s):
    s = unicodedata.normalize('NFKD', s or '')
    s = ''.join(c for c in s if not unicodedata.combining(c)).lower()
    return re.sub(r'[\W_]+', ' ', s).strip()        # letters of any script stay: a name in Greek or Arabic is still a name


def words(s):
    return {w for w in fold(s).split() if len(w) > 2 and w not in STOP}


def metres(a, b, c, d):
    p = math.pi / 180
    h = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 12742000 * math.asin(math.sqrt(h))


by_id = {r['id']: r for r in records}
known = {}
for r in records:
    for n in [r['name'], r['id'].replace('-', ' ')] + (r.get('aliases') or []) + [x.replace('-', ' ') for x in r.get('former_ids') or []]:
        if fold(n):
            known.setdefault(fold(n), []).append(r['id'])
for k, v in dup.items():
    known.setdefault(fold(k.replace('-', ' ')), []).append(v)
ids = {r['id'] for r in records} | set(dup)

added, refused, shared = [], [], []
for row in rows:
    why = None
    if not row.get('name') or not row.get('id'):
        why = 'no name or id'
    elif not isinstance(row.get('lat'), (int, float)) or not isinstance(row.get('lon'), (int, float)):
        why = 'no coordinates'
    elif not [u for u in row.get('sources') or [] if str(u).startswith('http')]:
        why = 'no source'
    elif row['id'] in ids:
        why = f"id is taken ({dup.get(row['id'], row['id'])})"
    else:
        # The same name within 30 km is the same space. Further away it is a namesake ("National Museum" is Prague's
        # name and an alias of New Delhi's): the row is added, without an alias another record already answers to.
        for n in [row['name']] + (row.get('aliases') or []):
            for rid in known.get(fold(n), []):
                r = by_id.get(rid)
                if r and metres(r['lat'], r['lon'], row['lat'], row['lon']) < 30000:
                    why = f'"{n}" is on the atlas as {rid}'
                elif n != row['name']:
                    row['aliases'] = [a for a in row['aliases'] if a != n]
                    shared.append(f"{row['id']}: alias \"{n}\" left out, {rid} answers to it")
            if why:
                break
    if not why:
        mine = set().union(*(words(n) for n in [row['name']] + (row.get('aliases') or [])))
        for r in records:
            if abs(r['lat'] - row['lat']) < 0.01 and metres(r['lat'], r['lon'], row['lat'], row['lon']) < 150:
                theirs = set().union(*(words(n) for n in [r['name']] + (r.get('aliases') or [])))
                if mine & theirs:
                    why = f"within 150 m of {r['id']} and shares {', '.join(sorted(mine & theirs)[:3])}"
                    break
    if why:
        refused.append(f"{row.get('id')}: {why}")
        continue
    rec = {k: row[k] for k in KEEP if row.get(k) not in (None, '', [], {})}
    # the pages the second checker opened stand beside the researcher's
    rec['sources'] = list(rec['sources']) + [u for u in row.get('check_sources') or [] if u not in rec['sources']]
    rec.setdefault('flags', None)
    rec['research_retrieved'] = src.stem.rsplit('_', 1)[-1]
    records.append(rec)
    ids.add(rec['id'])
    by_id[rec['id']] = rec
    for n in [rec['name']] + (rec.get('aliases') or []):
        known.setdefault(fold(n), []).append(rec['id'])
    added.append(rec['id'])

print('added:', len(added), '| refused:', len(refused))
for x in refused + shared:
    print(' ', x)
if dry or not added:
    sys.exit()
path.write_text(json.dumps(records, ensure_ascii=True, indent=2), encoding='utf-8')
if reports:
    # The Details reports of the new records, then the absence filter over those records alone (a report may say
    # "Paywalled; only excerpts were read", which the card does not print).
    subprocess.run([sys.executable, str(ROOT / 'tools' / 'import_details_reports.py'), str(reports), '--apply', '--only', ','.join(added),
                    '--date', src.stem.rsplit('_', 1)[-1]], check=True)
    sys.path.insert(0, str(ROOT / 'tools'))
    import absence
    records = json.load(open(path, encoding='utf-8'))
    for r in records:
        if r['id'] in added:
            absence.strip_record(r, [])
    path.write_text(json.dumps(records, ensure_ascii=True, indent=2), encoding='utf-8')
subprocess.run([sys.executable, str(ROOT / 'tools' / 'clean_data.py')], check=True, stdout=subprocess.DEVNULL)
subprocess.run([sys.executable, str(ROOT / 'tools' / 'embed_data.py')], check=True)
