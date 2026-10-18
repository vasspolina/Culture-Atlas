#!/usr/bin/env python3
"""Put the critical frames in data/research_attach/institutional_critiques.json on the records they apply to.

Each frame becomes an entry of kind "theory" in the record's visual_critiques list, beside the artists' critiques:
strategy, target, historical_impact and either a paraphrase (summary, no author or citation) or verbatim quotes
(each with text, author, source and url), with no artist or image. Re-running replaces every
"theory" entry. Then: python3 tools/clean_data.py && python3 tools/embed_data.py

A frame applies to a record when every rule under "applies" holds:
  name_or_focus  a regex matched against the name and curatorial_focus
  size           the record's size is one of these
  grade          the record's Clean Funding Grade is one of these
  cities         or: the record is in one of these cities (this rule alone is enough)
"""
import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
frames = json.load(open(ROOT / 'data' / 'research_attach' / 'institutional_critiques.json', encoding='utf-8'))['frames']
records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))


def applies(rule, r):
    text = ' '.join(filter(None, [r.get('name'), r.get('curatorial_focus'), r.get('highlight')]))
    if 'cities' in rule and (r.get('city') or '') in rule['cities']:
        return True
    if 'name_or_focus' in rule and not re.search(rule['name_or_focus'], text, re.I):
        return False
    if 'size' in rule and r.get('size') not in rule['size']:
        return False
    if 'grade' in rule and r.get('grade') not in rule['grade']:
        return False
    return any(k in rule for k in ('name_or_focus', 'size', 'grade'))


counts = collections.Counter()
for r in records:
    kept = [v for v in r.get('visual_critiques') or [] if v.get('kind') != 'theory']
    for f in frames:
        if applies(f['applies'], r):
            entry = {'kind': 'theory', 'strategy': f['strategy'], 'strategy_id': f['id'], 'target': f['target']}
            if f.get('quotes'):   # verbatim quotations, each with its author, source and url, all shown on the page
                entry['quotes'] = [dict(q) for q in f['quotes']]
            else:                 # a paraphrase, shown without author or citation
                entry['summary'] = f['summary']
            entry['historical_impact'] = f['impact']
            kept.append(entry)
            counts[f['strategy']] += 1
    if kept:
        r['visual_critiques'] = kept
    else:
        r.pop('visual_critiques', None)
json.dump(records, open(ROOT / 'institutions.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
for k, n in counts.items():
    print(f'{n:5d}  {k}')
print(sum(1 for r in records if any(v.get("kind") == "theory" for v in r.get("visual_critiques") or [])), 'records carry a frame')
