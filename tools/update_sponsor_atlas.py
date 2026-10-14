#!/usr/bin/env python3
"""Bring a newer Sponsor Atlas study into the records. Usage: python3 tools/update_sponsor_atlas.py data/sponsor_atlas_<date>.json
Run tools/clean_data.py and tools/embed_data.py afterwards.

1. Entries the old study (data/sponsor_atlas.json) did not have are added by tools/import_sponsor_atlas.py once the new study replaces it.
2. Entries the new study changed (funding, note, sources, tier) update their record, but only where the record still holds exactly what
   the old study produced. A record edited since (a source added, a sentence removed) keeps its edits and is listed instead.
The mapping from a study entry to record fields is the importer's: funding; watch, or flags and why_flagged when the note begins "Flags:";
sources; tier A stays A, B/O/F become B, U stays U.
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def norm(s):
    s = unicodedata.normalize('NFKD', (s or '').lower())
    return re.sub(r'[^a-z0-9]+', ' ', ''.join(c for c in s if not unicodedata.combining(c))).strip()


def mapped(d):
    out = {'funding': d.get('f') or '', 'sources': d.get('u') or [], 'tier': 'B' if d['t'] in 'BOF' else d['t']}
    w = d.get('w') or ''
    if w.startswith('Flags:'):
        out['flags'] = [x.strip() for x in w[len('Flags:'):].strip(' .').split(',') if x.strip()]
        out['why_flagged'] = d.get('f') or w
        out['watch'] = ''
    else:
        out['flags'] = None
        out['watch'] = w
        out['why_flagged'] = w if (w and d['t'] in 'BOF') else ''
    return out


new = json.load(open(ROOT / sys.argv[1], encoding='utf-8'))
old = json.load(open(ROOT / 'data/sponsor_atlas.json', encoding='utf-8'))
oldm = {(d['n'], d['c']): d for d in old}
for d in new:   # keep the cross-checks the old study carried
    o = oldm.get((d['n'], d['c']))
    if o and o.get('x') and not d.get('x'):
        d['x'] = o['x']
records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
by = {}
for r in records:
    for k in {norm(r['name'])} | {norm(a) for a in r.get('aliases') or []}:
        by.setdefault(k, []).append(r)

applied, kept = [], []
for d in new:
    o = oldm.get((d['n'], d['c']))
    if not o or all(d.get(f) == o.get(f) for f in ('t', 'f', 'w', 'u')):
        continue
    hits = [r for r in by.get(norm(d['n']), []) if norm(r.get('city')) in norm(d['c'])] or by.get(norm(d['n']), [])
    if len(hits) != 1:
        kept.append((d['n'], 'no single record'))
        continue
    r = hits[0]
    was, now = mapped(o), mapped(d)
    for field in ('funding', 'watch', 'why_flagged', 'sources', 'flags', 'tier'):
        if was[field] == now[field]:
            continue
        have = r.get(field) or ('' if field not in ('sources', 'flags') else None)
        if field == 'tier':
            same = r.get('tier') in (was['tier'], 'U')   # clean_data may already have set a verified record back to U
        elif field in ('sources', 'flags'):
            same = (have or None) == (was[field] or None)
        else:
            same = norm(have) == norm(was[field])
        if not same:
            kept.append((d['n'], field))
            continue
        if now[field] in ('', None, []):
            r.pop(field, None)
        else:
            r[field] = now[field]
        applied.append((d['n'], field))

json.dump(new, open(ROOT / 'data/sponsor_atlas.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(records, open(ROOT / 'institutions.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
print('applied', len(applied), 'fields; left as edited', len(kept))
for n, f in kept:
    print('  kept', n, f)
