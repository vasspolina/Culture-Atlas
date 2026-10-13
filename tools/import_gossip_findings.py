#!/usr/bin/env python3
"""Attach the OS01 findings (NS01 to NS14) from data/gossip_research.md to the Atlas records they name.

Only what the research table states is copied: the period, what the evidence adds, the response and its scope, and the
linked sources (titles and publishers come from the research's own source register). No status, topic or date is added.
Findings about organisations that are not in the Atlas (Sadler's Wells, Berlin district funds, Zitadelle Spandau) are skipped.
Run: python3 tools/import_gossip_findings.py && python3 tools/embed_data.py
"""
import json, re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
md = (root / 'data/gossip_research.md').read_text(encoding='utf8')

# finding id -> Atlas record name. Group-wide and absent organisations are decided here, in plain sight.
TARGET = {
    'NS01': 'Barbican Centre', 'NS02': 'Barbican Centre',
    'NS03': 'Science Museum', 'NS04': 'Science Museum',
    'NS07': 'Palais de Tokyo', 'NS08': 'Jeu de Paume',
    'NS09': 'De Appel', 'NS10': 'Het HEM', 'NS11': 'Framer Framed',
    'NS14': 'New Museum of Contemporary Art',
}

reg = {}
for m in re.finditer(r'^- \*\*(S\d+)\*\* — \[([^\]]+)\]\((https?://[^)\s]+)\)\. ([^.]*?)(?:; [^.]*)?\.', md, re.M):
    reg[m.group(1)] = {'id': m.group(1), 'title': m.group(2), 'url': m.group(3), 'publisher': m.group(4).strip(), 'published': None}
for m in re.finditer(r'^- \*\*(S\d+)\*\* — .*?Published: ([^.]*?)(?: \(|\.)', md, re.M):
    if m.group(1) in reg and re.match(r'\d{4}', m.group(2)):
        reg[m.group(1)]['published'] = m.group(2).strip()

rows = {}
for line in md.splitlines():
    m = re.match(r'\| \*\*(NS\d+)\*\* · ([^|]*)\|(.*)\|\s*$', line)
    if not m:
        continue
    cells = [c.strip() for c in m.group(3).split(' | ')] if False else [c.strip() for c in re.split(r'(?<!\\)\|', m.group(3))]
    org, (period, adds, resp, srcs) = m.group(2).strip(), (cells + [''] * 4)[:4]
    ids = re.findall(r'\[(S\d+)\]\((https?://[^)\s]+)\)', srcs)
    rows[m.group(1)] = {'org': org, 'period': period, 'adds': adds, 'resp': resp, 'srcs': ids}

inst = json.loads((root / 'institutions.json').read_text(encoding='utf8'))
by = {i['name']: i for i in inst}
n = 0
for fid, name in TARGET.items():
    r, rec = rows[fid], by[name]
    g = rec.setdefault('gossip_data', {})
    cases = [c for c in g.setdefault('real_cases', []) if c.get('case_id') != fid]
    sources = []
    for sid, url in r['srcs']:
        s = dict(reg.get(sid, {'id': sid, 'title': sid, 'publisher': None, 'published': None}))
        s['url'] = url
        sources.append(s)
    cases.append({
        'case_id': fid,
        'title': 'Other-source finding, ' + r['org'].replace(' · ', ', '),
        'event_date': r['period'],
        'facts': [r['adds']],
        'response': r['resp'],
        'sources': sources,
    })
    g['real_cases'] = cases
    n += 1
json.dump(inst, open(root / 'institutions.json', 'w', encoding='utf-8'), indent=2, ensure_ascii=True)
print(n, 'findings attached;', len(rows), 'in the research;', len(reg), 'sources parsed')
