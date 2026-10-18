#!/usr/bin/env python3
"""Put the critical frames in data/research_attach/institutional_critiques.json on the records they apply to.

Each frame becomes an entry of kind "theory" in the record's visual_critiques list, beside the artists' critiques:
strategy, target, quotes (word for word, each with author, title, publication, date and address) and historical_impact, with no artist or image. Re-running replaces every
"theory" entry. Then: python3 tools/clean_data.py && python3 tools/embed_data.py

A frame applies to a record when every rule under "applies" holds:
  type    the museum type read from the record's NAME (not its description: "I.M. Pei's modern exhibition hall" does not make a history
          museum a modern art museum); see TYPES below
  grade   the record's Clean Funding Grade is one of these
  size    the record's size is one of these (S, M, L)
  city    the record's city is one of these
  name    a regex on the record's name
  A "type" may be a list (any of them); "applies" may be a list of rules (any one of them holds).
A quotation with "only" (a regex on the name) is shown only on records it is about.
"""
import collections
import json
import re
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parent.parent
frames = json.load(open(ROOT / 'data' / 'research_attach' / 'institutional_critiques.json', encoding='utf-8'))['frames']
records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))


# Museum type, read from the name. A natural history museum is not also a history museum; the order below settles it.
TYPES = [
    ('natural', r'natural history|naturkunde|naturhistor|museum of natur'),
    ('ethno', r'ethnolog|ethnograph|etnograf|world cultures|weltkultur|quai branly|volkenkunde|museum der kulturen|humboldt|british museum|louvre'
              r'|pergamon|neues museum|altes museum|metropolitan museum of art|\bthe met\b|africa museum|afrika museum|pitt rivers'
              r'|tropenmuseum|rietberg|asian art museum|musee guimet|mus.e de l.homme'),
    ('history', r'histor(?!ic house)|historisch|histoire|storia|historia|war museum|memorial|holocaust|genocide|remembrance'),
    ('bien', r'biennale|biennial|bienal|\bdocumenta\b|triennale|triennial|manifesta'),
    ('contemp', r'contemporary|modern art|moderna|kunsthalle|kunstverein|kunsthaus|art cent(?:er|re)|arts cent(?:er|re)|\bmoma\b|\bmca\b'
                r'|moderne|zeitgen|mumok|macba|reina sof|serpentine|hayward|whitney|guggenheim|new museum|pompidou|kiasma|stedelijk|centre d.art'),
]
NOT_THE_TYPE = r'kunsthistor|art history|metropolitan museum of manila|museum of jurassic|cricoteka'


def plain(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', (s or '').lower()) if not unicodedata.combining(c))


def types_of(r):
    name = plain(r.get('name'))
    if re.search(NOT_THE_TYPE, name):
        return set()
    hit = {t for t, p in TYPES if re.search(p, name)}
    if 'natural' in hit:
        hit -= {'history'}
    return hit


def applies(rule, r):
    if isinstance(rule, list):
        return any(applies(x, r) for x in rule)
    if 'type' in rule and not ({rule['type']} if isinstance(rule['type'], str) else set(rule['type'])) & types_of(r):
        return False
    if 'grade' in rule and r.get('grade') not in rule['grade']:
        return False
    if 'size' in rule and r.get('size') not in rule['size']:
        return False
    if 'city' in rule and (r.get('city') or '') not in rule['city']:
        return False
    if 'name' in rule and not re.search(rule['name'], plain(r.get('name'))):
        return False
    return any(k in rule for k in ('type', 'grade', 'size', 'city', 'name'))


counts = collections.Counter()
for r in records:
    kept = [v for v in r.get('visual_critiques') or [] if v.get('kind') != 'theory']
    for f in frames:
        if applies(f['applies'], r):
            quotes = [{k: v for k, v in q.items() if k != 'only'} for q in f['quotes']
                      if not q.get('only') or re.search(q['only'], r['name'], re.I)]
            if not quotes:
                continue
            kept.append({'kind': 'theory', 'strategy': f['strategy'], 'strategy_id': f['id'], 'target': f['target'],
                         'quotes': quotes, 'historical_impact': f['impact']})
            counts[f['strategy']] += 1
    if kept:
        r['visual_critiques'] = kept
    else:
        r.pop('visual_critiques', None)
json.dump(records, open(ROOT / 'institutions.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
for k, n in counts.items():
    print(f'{n:5d}  {k}')
print(sum(1 for r in records if any(v.get("kind") == "theory" for v in r.get("visual_critiques") or [])), 'records carry a frame')
