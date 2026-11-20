#!/usr/bin/env python3
"""Write checked funding lines onto the records that have none.

255 records lost their funding line to the first cleanup (lines such as "State-funded, no sponsors." assert an
absence nobody had checked) and nothing replaced it. Each of those records has a Details card whose funding points
were written from pages opened and cited. On 20 Nov 2026 a line of at most 30 words was written for each record from
those points alone (brief: sponsor-atlas/work/ubatch/FUNDLINES.md) and second-checked against the pages the points
cite (ubatch/FLCHECK.md, which applies CHECKER.md and SLOP.md). The checked rows are kept in
data/research_attach/funding_lines_<date>.json: id, funding, the pages the checker opened, and for a record that was
unverified the tier the checker gave it.

For each row this sets `funding` where the record still has none, records the pages under field_sources.funding,
adds them to `sources`, applies a tier the checker raised from U (with its flags), and takes a corrected `watch` line
where the check found the old one out of date (one record). A record whose funding has
been filled since, or whose row holds an empty line, is left alone. Then tools/clean_data.py (which grades) and
tools/embed_data.py run.
Usage: python3 tools/attach_funding_lines.py [data/research_attach/funding_lines_2026-11-20.json] [--dry]
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
args = [a for a in sys.argv[1:] if a != '--dry']
dry = '--dry' in sys.argv
src = Path(args[0]) if args else ROOT / 'data' / 'research_attach' / 'funding_lines_2026-11-20.json'
date = src.stem.rsplit('_', 1)[-1]
rows = json.load(open(src, encoding='utf-8'))
path = ROOT / 'institutions.json'
records = json.load(open(path, encoding='utf-8'))
by_id = {r['id']: r for r in records}

written, regraded, skipped = 0, 0, []
for row in rows:
    r = by_id.get(row['id'])
    if not r:
        skipped.append(f"{row['id']}: no such record")
        continue
    if r.get('funding'):
        skipped.append(f"{row['id']}: has a funding line already")
        continue
    if not (row.get('funding') or '').strip():
        skipped.append(f"{row['id']}: the checker left the line empty")
        continue
    r['funding'] = row['funding'].strip()
    urls = [u for u in row.get('sources') or [] if isinstance(u, str) and u.startswith('http')][:3]
    fs = r.get('field_sources')
    fs = dict(fs) if isinstance(fs, dict) else {}
    fs['funding'] = {'urls': urls, 'basis': 'written from the funding points of the Details card; checked against the pages cited'
                     if row.get('seen') == 'page' else 'written from the funding points of the Details card', 'retrieved': date}
    r['field_sources'] = fs
    r['sources'] = list(r.get('sources') or []) + [u for u in urls if u not in (r.get('sources') or [])]
    written += 1
    if row.get('watch'):                     # a watch line the check found to be out of date, corrected with it
        r['watch'] = row['watch'].strip()
    if r.get('tier') == 'U' and row.get('tier') in ('A', 'B'):
        # clean_data.py sends a B with no recorded reason, and an A with no source outside the space's own site, back
        # to U: a B row is applied only with its flags or its reason.
        if row['tier'] == 'B' and not (row.get('flags') or row.get('why_flagged')):
            skipped.append(f"{row['id']}: graded B with no flag and no reason; tier left at U")
            continue
        r['tier'] = row['tier']
        if row.get('flags'):
            r['flags'] = row['flags']
        if row.get('why_flagged'):
            r['why_flagged'] = row['why_flagged'].strip()
        r.pop('tier_note', None)             # the note said why it was unverified
        regraded += 1

print('funding lines written:', written, '| unverified records graded:', regraded, '| skipped:', len(skipped))
for s in skipped:
    print(' ', s)
if dry:
    sys.exit()
path.write_text(json.dumps(records, ensure_ascii=True, indent=2), encoding='utf-8')
subprocess.run([sys.executable, str(ROOT / 'tools' / 'clean_data.py')], check=True, stdout=subprocess.DEVNULL)
subprocess.run([sys.executable, str(ROOT / 'tools' / 'embed_data.py')], check=True)
