#!/usr/bin/env python3
"""Build assets/studies.json, the data behind studies.html, from the Sponsor Atlas case studies.

The Sponsor Atlas page (sponsor-atlas/work/sponsor-atlas.html) is the research truth; its CASES list holds the
studies that cross many institutions (Epstein, Democracy Now!, Bellingcat, Rouanet, who connects the institutions,
community-led spaces, who publishes what, what the field says, WikiLeaks) and the two single-institution studies
(MoMA, the Tear Gas Biennial). This copies them as they are, links each institution they name to its record here
when the name matches a record name or alias, and points the MoMA study at moma-money-map.html.
Nothing is fetched and nothing in institutions.json is changed.

Usage: python3 tools/build_studies.py [path/to/sponsor-atlas.html]
"""
import json, os, re, sys, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, '..', 'sponsor-atlas', 'work', 'sponsor-atlas.html')
OUT = os.path.join(ROOT, 'assets', 'studies.json')


def norm(x):
    x = unicodedata.normalize('NFKD', (x or '').lower())
    x = ''.join(c for c in x if not unicodedata.combining(c))
    x = re.sub(r'\([^)]*\)', ' ', x)
    return re.sub(r'[^a-z0-9]+', ' ', x).strip()


s = open(SRC, encoding='utf-8').read()
i = s.index('const CASES = ') + len('const CASES = ')
CASES = json.loads(s[i:s.index('\n', i)].rstrip().rstrip(';'))

INST = json.load(open(os.path.join(ROOT, 'institutions.json'), encoding='utf-8'))
NAMES = {}
for r in INST:
    for n in [r.get('name')] + list(r.get('aliases') or []):
        k = norm(n)
        if k and len(k) >= 3 and not k.replace(" ", "").isdigit() and k not in NAMES:
            NAMES[k] = r['name']


def record(name):
    """The record name for a study's institution name, or None."""
    k = norm(name)
    if len(k) < 3 or re.fullmatch(r'[\d ]+', k):
        return None
    if k in NAMES:
        return NAMES[k]
    k2 = norm(re.split(r'\s+[|/]\s+|,\s', name)[0])          # "Mansudae Art Museum / ..." or "Name, City"
    return NAMES.get(k2)


MOMA_PAGE = 'moma-money-map.html'
out, unmatched = [], set()
for c in CASES:
    names = c.get('insts') or ([c['inst']] if c.get('inst') else [])
    recs = []
    for n in names:
        r = record(n)
        if r:
            if r not in recs:
                recs.append(r)
        else:
            unmatched.add(n)
    tables = c.get('tables') or ([c['table']] if c.get('table') else [])
    tabs = []
    for t in tables:
        rows = []
        for row in t.get('rows', []):
            cells = [str(x) for x in row]
            links = []                 # per cell: a record name, a list of [part, record or null], or null
            for cell in cells:
                r = record(cell) if len(cell) < 140 else None
                if r:
                    links.append(r); continue
                parts = [p.strip() for p in cell.split(', ')] if ', ' in cell and len(cell) > 40 else []
                hits = [[p, record(p)] for p in parts]
                links.append(hits if parts and sum(1 for _, h in hits if h) >= max(2, len(parts) // 2) else None)
            rows.append({'cells': cells, 'links': links})
        tabs.append({'title': t.get('title', ''), 'head': t.get('head', []), 'rows': rows})
    link = c.get('link')
    if link and 'TZtzbbCNYH8tNjEomKoyob' in str(link[1]):
        link = ['Open the interactive MoMA Money Map', MOMA_PAGE]
    out.append({
        'key': c['key'], 'title': c['title'], 'kick': c.get('kick', ''),
        'summary': c.get('summary', []), 'bullets': c.get('bullets', []), 'timeline': c.get('timeline', []),
        'stats': c.get('stats', []), 'tables': tabs, 'sources': c.get('sources', ''),
        'link': link, 'records': recs,
    })

json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('studies: %d, records linked: %d, study names with no record here: %d' % (
    len(out), sum(len(x['records']) for x in out), len(unmatched)))
if unmatched:
    print('  no record:', sorted(unmatched)[:40])
