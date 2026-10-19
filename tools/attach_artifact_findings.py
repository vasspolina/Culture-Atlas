#!/usr/bin/env python3
"""Carry what the Sponsor Atlas artifact of 19 Oct 2026 holds beyond the study lines into the records. Run clean_data.py and embed_data.py afterwards.

  case_notes    four reported items the records lacked, each with the sources research/dn-world.json, dn-us.json and rouanet-check.json
                give for it (data/research_attach/artifact_case_notes_2026-10-19.json). A note already on the record is not added twice.
  funder_links  recomputed from the artifact's network table (data/research_attach/network_funders_2026-10-19.json): 52 funders and
                trustees named at three or more institutions, up from 41, with the counts as the artifact gives them. A funder is linked
                to a record only where the record's own text names it, as tools/attach_research.py does.

  case wording  eight Bellingcat and WikiLeaks notes the records worded differently (data/research_attach/case_decisions.json had them
                say a source "does not report on" the museum) take the artifact's wording, on the user's instruction of 19 Oct 2026;
                the note keeps its sources and its title, and its date becomes the source's own date.
Usage: python3 tools/attach_artifact_findings.py && python3 tools/clean_data.py && python3 tools/embed_data.py
"""
import collections
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENERIC = set('foundation family philanthropies fonden of bank the and fund trust museums museum group'.split())


def norm(s):
    s = unicodedata.normalize('NFKD', (s or '').lower())
    return re.sub(r'[^a-z0-9]+', ' ', ''.join(c for c in s if not unicodedata.combining(c))).strip()


records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
by_id = {r['id']: r for r in records}
by_name = collections.defaultdict(list)
for r in records:
    for k in {norm(r['name'])} | {norm(a) for a in r.get('aliases') or []}:
        by_name[k].append(r)

n_note = 0
for d in json.load(open(ROOT / 'data/research_attach/artifact_case_notes_2026-10-19.json', encoding='utf-8')):
    r = by_id[d['record_id']]
    if d['note'] not in r.setdefault('case_notes', []):
        r['case_notes'].append(d['note'])
        n_note += 1


n_word = 0
for d in json.load(open(ROOT / 'data/research_attach/artifact_case_note_wording_2026-10-19.json', encoding='utf-8')):
    for note in by_id[d['record_id']].get('case_notes') or []:
        if note['text'].startswith(d['was']) or note['text'] == d['text']:
            if note['text'] != d['text']:
                n_word += 1
            note['text'], note['meta'] = d['text'], d['meta']


def variants(funder):
    out = set()
    for part in funder.split('/'):
        out.add(norm(part))
        out |= {w for w in norm(part).split() if w not in GENERIC and len(w) > 3}
    return out


def own_text(r):
    bits = [r.get(k) or '' for k in ('funding', 'watch', 'why_flagged', 'tier_note', 'highlight', 'other_findings')]
    for e in r.get('epstein_records') or []:
        bits += [e.get('summary') or '', e.get('tie') or '']
    for e in r.get('wikileaks_records') or []:
        bits.append(e.get('what_shows') or '')
    return norm(' '.join(bits))


for r in records:
    r.pop('funder_links', None)
net = json.load(open(ROOT / 'data/research_attach/network_funders_2026-10-19.json', encoding='utf-8'))
n_fund = skipped = 0
for funder, n, flagged, countries, which in net['rows']:
    toks = [x.strip() for x in which.split(', ')]
    i = 0
    while i < len(toks):
        for j in range(min(len(toks), i + 6), i, -1):
            cand = ', '.join(toks[i:j])
            if norm(cand) in by_name:
                hits = by_name[norm(cand)]
                exact = [r for r in hits if norm(r['name']) == norm(cand)] or hits
                i = j
                link = {'funder': funder, 'institutions': int(n)}
                done = False
                for r in exact:
                    if any(re.search(r'\b' + re.escape(v) + r'\b', own_text(r)) for v in variants(funder)):
                        if link not in r.setdefault('funder_links', []):
                            r['funder_links'].append(link)
                        done = True
                n_fund += done
                skipped += not done
                break
        else:
            print(f'  {funder}: {toks[i]} is not a record')
            i += 1
for r in records:
    if r.get('funder_links'):
        r['funder_links'].sort(key=lambda f: -f['institutions'])

json.dump(records, open(ROOT / 'institutions.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
print(f'case notes added {n_note}, reworded {n_word}; funder links {n_fund} (skipped {skipped}: the record does not name the funder);',
      'records with funder links:', sum(1 for r in records if r.get('funder_links')))
