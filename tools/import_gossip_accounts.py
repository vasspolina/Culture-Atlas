#!/usr/bin/env python3
"""Attach the individual accounts retained by data/gossip_research.md (rows R01…, RD01…) to the Atlas records they name.

Each row is kept as the research table holds it: the row id, the employer or scope text as written, every cell under its
own column heading, and the linked sources. Rows about unnamed employers, the sector, or organisations that are not in
the Atlas are left out. The research's own caveat applies and is shown with them: individual accounts, not verified findings.
Run: python3 tools/import_gossip_accounts.py && python3 tools/clean_data.py && python3 tools/embed_data.py
"""
import json, re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
md = (root / 'data/gossip_research.md').read_text(encoding='utf8')
inst = json.loads((root / 'institutions.json').read_text(encoding='utf8'))
by = {i['name'].lower(): i for i in inst}
for i in inst:
    for a in i.get('aliases') or []:
        by.setdefault(a.lower(), i)

# research name -> Atlas record, where the two are the same organisation under a different spelling.
MAP = {
    'the noguchi museum': 'Noguchi Museum', 'musée du louvre': 'Louvre', 'museum of modern art (moma)': 'MoMA',
    'the national gallery': 'National Gallery', 'institute of contemporary arts': 'Institute of Contemporary Arts (ICA)',
    'design museum london': 'Design Museum', "fondation cartier pour l'art contemporain": 'Fondation Cartier',
    'brooklyn academy of music': 'Brooklyn Academy of Music (BAM)', 'rmn–grand palais (profile name)': 'Grand Palais (Rmn–Grand Palais)',
    'paris musées': 'Paris Musées (Réseau des Musées de la Ville de Paris)',
    'kw institute for contemporary art – kunst-werke berlin e. v.': 'KW Institute for Contemporary Art',
    'haus der kulturen der welt': 'Haus der Kulturen der Welt (HKW)', 'science museum group': 'Science Museum',
    'staatliche museen zu berlin / preußischer kulturbesitz': 'Staatliche Museen zu Berlin', 'stedelijk museum': 'Stedelijk Museum Amsterdam',
    'tate': 'Tate Modern', 'tate modern': 'Tate Modern', 'hyundai tate research centre: transnational': 'Tate Modern',
    "musée de l'orangerie": None, "musée d'art moderne de paris": None,
}
SKIP = re.compile(r'unnamed|sector|unresolved', re.I)
SKIP_PART = re.compile(r'work location varies', re.I)

def clean(cell):
    cell = re.sub(r'\[(S\d+)\]\((https?://[^)\s]+)\)', r'\1', cell)
    return re.sub(r'\*\*', '', cell).strip()

lines = md.splitlines()
header = None
rows = []
for n, l in enumerate(lines):
    if l.startswith('|') and n + 1 < len(lines) and lines[n + 1].startswith('| ---'):
        header = [clean(c) for c in re.split(r'(?<!\\)\|', l.strip().strip('|'))]
        continue
    m = re.match(r'\| \*{0,2}((?:R|RD)\d+)\*{0,2} · ([^|]*)\|(.*)\|\s*$', l)
    if not m or not header:
        continue
    rid, scope = m.group(1), clean(m.group(2))
    cells = [c.strip() for c in re.split(r'(?<!\\)\|', m.group(3))]
    sources = [{'id': sid, 'url': url} for sid, url in re.findall(r'\[(S\d+)\]\((https?://[^)\s]+)\)', l)]
    fields = [[header[k + 1], clean(c)] for k, c in enumerate(cells) if k + 1 < len(header) and clean(c)]
    fields = [[h, v] for h, v in fields if not re.fullmatch(r'(S\d+[;, ]*)+', v)]   # a bare source list is already in sources
    rows.append({'id': rid, 'scope': scope, 'fields': fields, 'sources': sources})

attached, unmatched = 0, {}
for i in inst:
    if i.get('gossip_data', {}).get('accounts'):
        i['gossip_data']['accounts'] = []
for r in rows:
    if SKIP.search(r['scope']):
        continue
    targets = []
    for name in [s.strip() for s in r['scope'].split(';')]:
        if SKIP_PART.search(name): continue
        key = name.lower()
        if key in MAP:
            if MAP[key]: targets.append(by[MAP[key].lower()])
        elif key in by:
            targets.append(by[key])
        else:
            unmatched[name] = unmatched.get(name, 0) + 1
    for t in {id(x): x for x in targets}.values():
        g = t.setdefault('gossip_data', {})
        g.setdefault('accounts', []).append(r)
        attached += 1
json.dump(inst, open(root / 'institutions.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
print(len(rows), 'rows;', attached, 'attached;', 'not in the Atlas:', ', '.join(f'{k} ({v})' for k, v in sorted(unmatched.items())))
