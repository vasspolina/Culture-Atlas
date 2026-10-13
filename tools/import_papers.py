#!/usr/bin/env python3
"""Merge the Consensus exports in data/papers/*.csv into the ACADEMIC_RESEARCH list embedded in index.html.

A paper is the same paper when its DOI or title matches. New papers are added with the CSV's own fields;
existing papers gain a study type when the CSV names one and the entry has none. Nothing else is changed.
"""
import csv, glob, json, re
from pathlib import Path

root = Path(__file__).resolve().parent.parent
idx = root / 'index.html'
html = idx.read_text(encoding='utf8')
m = re.search(r'(    const ACADEMIC_RESEARCH = )(\[.*?\]);\n', html, re.S)
papers = json.loads(m.group(2))
by_doi = {p.get('doi', '').lower(): p for p in papers if p.get('doi')}
by_title = {p['title'].strip().lower(): p for p in papers}
added = typed = 0
changed = []
for f in sorted(glob.glob(str(root / 'data/papers/*.csv'))):
    for r in csv.DictReader(open(f, encoding='utf-8-sig')):
        if not (r['DOI'] or r['Year'] or r['Authors']):
            continue                                   # a search-result stub, not a paper
        p = by_doi.get(r['DOI'].lower()) if r['DOI'] else None
        p = p or by_title.get(r['Title'].strip().lower())
        if p is not None:                              # the export is the record: its fields replace any edited copy
            for k, c in [('title', 'Title'), ('takeaway', 'Takeaway'), ('authors', 'Authors'), ('year', 'Year'), ('citations', 'Citations'),
                         ('abstract', 'Abstract'), ('journal', 'Journal'), ('doi', 'DOI'), ('link', 'Consensus Link')]:
                v = r[c].strip()
                if v and p.get(k) != v:
                    changed.append((p.get('title', '')[:40], k, (p.get(k) or '')[:50], v[:50]))
                    p[k] = v
        if p is None:
            p = {k: r[c].strip() for k, c in [('title', 'Title'), ('takeaway', 'Takeaway'), ('authors', 'Authors'), ('year', 'Year'),
                                               ('citations', 'Citations'), ('abstract', 'Abstract'), ('journal', 'Journal'), ('doi', 'DOI'), ('link', 'Consensus Link')]}
            p = {k: v for k, v in p.items() if v}
            papers.append(p)
            if p.get('doi'): by_doi[p['doi'].lower()] = p
            by_title[p['title'].lower()] = p
            added += 1
        if r.get('Study Type', '').strip() and not p.get('study_type'):
            p['study_type'] = r['Study Type'].strip()
            typed += 1
html = html[:m.start(2)] + json.dumps(papers, ensure_ascii=False).replace('</', '<\\/') + html[m.end(2):]
idx.write_text(html, encoding='utf8')
print(len(papers), 'papers;', added, 'added;', typed, 'given a study type;', len(changed), 'fields set from the export')
for c in changed: print('  ', c)
