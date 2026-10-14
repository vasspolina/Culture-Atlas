#!/usr/bin/env python3
"""Fold what the retired research library held into the museum records it is about. Run clean_data.py and embed_data.py afterwards.

The library window is gone. Its contents are archived under data/library/ and each piece goes where it belongs:

  study_notes   a line from a study's own abstract about this institution       (data/research_attach/study_findings.json)
  case_notes    a row of a case study table that the record did not already say  (data/research_attach/case_decisions.json)
  case_study    the two single-institution case studies, whole: MoMA and the Whitney
  funder_links  funders and trustees the map names at three or more institutions, only where the record's own text names them

Nothing is written in these tools: table rows are copied word for word, study lines were drafted from the abstract, checked twice
against it, and each keeps the quote it rests on in study_findings.json. Re-running replaces the four fields, so it is safe to repeat.
Usage: python3 tools/attach_research.py && python3 tools/clean_data.py && python3 tools/embed_data.py
"""
import collections
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ('study_notes', 'case_notes', 'case_study', 'funder_links')
GENERIC = set('foundation family philanthropies fonden of bank the and fund trust museums museum group'.split())


def norm(s):
    s = unicodedata.normalize('NFKD', (s or '').lower())
    return re.sub(r'[^a-z0-9]+', ' ', ''.join(c for c in s if not unicodedata.combining(c))).strip()


records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
studies = json.load(open(ROOT / 'data/library/academic_research.json', encoding='utf-8'))
cases = {c['key']: c for c in json.load(open(ROOT / 'data/library/case_studies.json', encoding='utf-8'))}
findings = json.load(open(ROOT / 'data/research_attach/study_findings.json', encoding='utf-8'))
decisions = json.load(open(ROOT / 'data/research_attach/case_decisions.json', encoding='utf-8'))

by_id = collections.defaultdict(list)
by_name = collections.defaultdict(list)
for r in records:
    for f in FIELDS:
        r.pop(f, None)
    by_id[r['id']].append(r)
    for k in {norm(r['name'])} | {norm(a) for a in r.get('aliases') or []}:
        by_name[k].append(r)


def keys(r):
    return {norm(r['name'])} | {norm(a) for a in r.get('aliases') or []}


def city_key(r):
    return re.sub(r'\bsaint\b', 'st', norm(r.get('city')))


def targets(rid):
    """Every record that is this institution: the id, a duplicate of the id, and a twin pin (same city, same name or alias)."""
    out = list(by_id[rid])
    seen = {id(r) for r in out}
    for r in list(out):
        for o in records:
            if id(o) in seen or city_key(o) != city_key(r) or o.get('country') != r.get('country'):
                continue
            if keys(r) & keys(o):
                out.append(o)
                seen.add(id(o))
    return out


def add(rid, field, value):
    for r in targets(rid):
        if value not in r.setdefault(field, []):
            r[field].append(value)


# ---- study lines
doi_of = {p.get('doi'): p for p in studies if p.get('doi')}
title_of = {p['title']: p for p in studies}
n_study = 0
for f in findings:
    p = doi_of.get(f.get('doi')) or title_of.get(f['title'])
    assert p, f['title']
    note = {'title': p['title'], 'authors': p.get('authors') or '', 'year': p.get('year') or '', 'journal': p.get('journal') or '',
            'doi': p.get('doi') or '', 'text': f['statement']}
    for rid in f['record_ids']:
        add(rid, 'study_notes', note)
        n_study += 1

# ---- case rows
# A row is shown as the research wrote it, minus what is about the app or about what was not found: a sentence that mentions the
# atlas, says a source "does not mention" something, or reports that nothing was found, is left out, and so is a sentence that only
# repeats an earlier one. A row that says nothing is left once those are gone is not shown.
LEFT_OUT = re.compile(r"\batlas\b|\bdoes not mention\b|\bmention(?:s)? neither\b|\bnames no\b|\bcarries no flag\b|\bcontains? no\b|"
                      r"^No\b[^.]*\b(found|published|incentive-law)\b|\bnot found\b|\bnone found\b", re.I)


def sentences(text):
    return [x for x in re.split(r'(?<=[.!?])\s+(?=[A-Z0-9(])', text.strip()) if x]


def clean_text(text):
    out, seen = [], ''
    for x in sentences(text):
        k = re.sub(r'^(he|she|it|they) ', '', norm(x))
        if k in seen or LEFT_OUT.search(x):
            continue
        seen += ' ' + k
        out.append(x)
    return ' '.join(out)


def compose(key, row_id, cols, inst=''):
    ci, ti, ri = row_id.split(':')
    sources = cols.get('Sources') or []
    if key == 'rouanet' and cols['Share through tax incentives'].lower().startswith('no incentive-law money'):
        return None
    if key == 'epstein':
        return {'title': cols['Person'], 'meta': f"{cols['Link']}, {cols['Status']}",
                'text': f"{cols['What the record shows']} {cols['What happened']}".strip(), 'sources': sources}
    if key == 'dn':
        return {'title': 'Democracy Now! report', 'meta': cols['Date'], 'text': cols['What Democracy Now! reported'], 'sources': sources}
    if key == 'bellingcat':
        return {'title': 'Bellingcat finding', 'meta': cols['Date'], 'text': cols['What Bellingcat found'], 'sources': sources}
    if key == 'wikileaks':
        return {'title': f"WikiLeaks, {cols['Document']}", 'meta': cols['Date'], 'text': cols['What the document shows'], 'sources': sources}
    if key == 'rouanet':
        return {'title': 'Rouanet Law and tax incentives', 'meta': '',
                'text': f"{cols['What the records show']} {cols['Share through tax incentives']}".strip(), 'sources': sources}
    raise KeyError(key)


# A few rows begin "The same cable ..." because the case study table read top to bottom. On a record the row stands alone, so the
# leading "same" goes. One row says "the same profile" where the row above it, same document and date, names it a New Yorker profile.
SAME_FIXES = {'wikileaks:0:45': ('The same profile', 'The New Yorker profile')}


def stand_alone(row_id, text):
    for old, new in [SAME_FIXES.get(row_id, ('', ''))]:
        if old and text.startswith(old):
            return new + text[len(old):]
    return re.sub(r'^The same ', 'The ', text)


n_case = 0
for d in decisions:
    if d['final'] != 'add':
        continue
    key, ti, ri = d['row_id'].split(':')
    c = cases[key]
    table = (c.get('tables') or [c['table']])[int(ti)]
    row = table['rows'][int(ri)]
    cols = dict(zip(table['head'][1:], row[1:]))
    note = compose(key, d['row_id'], cols, row[0])
    if note is None:
        continue
    text = clean_text(stand_alone(d['row_id'], note['text']))
    if re.match(r'^Lists\b', text):
        text = f'{row[0]} {text[0].lower()}{text[1:]}'
    if not text:
        continue
    note['text'] = text
    for t in targets(d['record_id']):
        sents = [norm(x) for x in sentences(text)]
        own = norm(json.dumps({k: t.get(k) for k in ('why_flagged', 'other_findings', 'epstein_records', 'wikileaks_records', 'watch')}, ensure_ascii=False))
        if sents and sum(1 for x in sents if x in own) / len(sents) >= 0.6:
            continue   # the record already says it
        if note not in t.setdefault('case_notes', []):
            t['case_notes'].append(note)
    n_case += 1

# ---- the two single-institution case studies
n_cs = 0
for key in ('moma', 'teargas'):
    c = cases[key]
    body = {k: c[k] for k in ('title', 'kick', 'summary', 'bullets', 'timeline', 'stats', 'sources') if c.get(k)}
    rid = [r['id'] for r in by_name[norm(c['inst'])] if norm(r['name']) == norm(c['inst'])][0]
    for t in targets(rid):
        t['case_study'] = body
    n_cs += 1

# ---- funders and trustees shared across institutions
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


net = cases['network']['tables'][0]
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
                        for t in targets(r['id']):
                            if link not in t.setdefault('funder_links', []):
                                t['funder_links'].append(link)
                        done = True
                n_fund += done
                skipped += not done
                break
        else:
            raise SystemExit(f'{funder}: {toks[i]} is not a record')
for r in records:
    if r.get('funder_links'):
        r['funder_links'].sort(key=lambda f: -f['institutions'])

json.dump(records, open(ROOT / 'institutions.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
print(f'study lines {n_study}, case rows {n_case}, case studies {n_cs}, funder links {n_fund} (skipped {skipped}: the record does not name the funder)')
print('records with a study line:', sum(1 for r in records if r.get('study_notes')),
      'case rows:', sum(1 for r in records if r.get('case_notes')),
      'funder links:', sum(1 for r in records if r.get('funder_links')))
