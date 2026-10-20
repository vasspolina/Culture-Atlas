#!/usr/bin/env python3
"""Merge funding research (data/research_prompt.md, part 2) into institutions.json.

Usage: python3 tools/import_research_reports.py data/research_runs/<date>/results
Then run tools/clean_data.py, tools/embed_data.py and tools/build_money_maps.py.

Unlike the other importers, this one updates records that already exist, but it never silently
throws away what a record says:
- sources, flags and other_findings are added to, never removed;
- funding is replaced only when the research cites a source, and the old text is kept under
  field_sources.funding.previous;
- tier: U becomes the research tier; A becomes B when the research found flags; B is never lowered;
- why_flagged, website and records_note are written only where the record has none.
Every change is listed in <results dir>/../import_log.json.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
results_dir = Path(sys.argv[1])
path = ROOT / 'institutions.json'
records = json.load(open(path, encoding='utf-8'))
by_id = {}
for r in records:
    by_id.setdefault(r['id'], []).append(r)

STATUS_NOTE = {
    'spam': 'Its website now serves spam, so its own statements about funding could not be checked.',
    'down': 'Its website could not be reached, so its own statements about funding could not be checked.',
    'parked': 'Its website address is parked, so its own statements about funding could not be checked.',
}


def urls(xs):
    return [u for u in xs or [] if isinstance(u, str) and u.startswith('http')]


def split_findings(s):
    return [x.strip() for x in (s or '').split(' | ') if x.strip()]


log, skipped = [], []
for f in sorted(results_dir.glob('*.json')):
    try:
        items = json.load(open(f, encoding='utf-8'))
    except json.JSONDecodeError as e:
        skipped.append({'file': f.name, 'reason': f'invalid JSON: {e}'})
        continue
    for c in items:
        rid = c.get('id')
        matches = by_id.get(rid, [])
        if len(matches) != 1:
            skipped.append({'id': rid, 'reason': f'{len(matches)} records with this id'})
            continue
        r = matches[0]
        src = urls(c.get('sources'))
        if not src:
            skipped.append({'id': rid, 'reason': 'no sources'})
            continue
        changed = []
        retrieved = c.get('retrieved') or ''

        old_sources = r.get('sources') or []
        new_sources = [u for u in src if u not in old_sources]
        if new_sources:
            r['sources'] = old_sources + new_sources
            changed.append(f'+{len(new_sources)} sources')

        fund = (c.get('funding') or '').strip()
        if fund and fund != (r.get('funding') or '').strip():
            fs = r.setdefault('field_sources', {})
            fs['funding'] = {'urls': src[:3], 'retrieved': retrieved, 'basis': 'funding research'}
            if r.get('funding'):
                fs['funding']['previous'] = r['funding']
            r['funding'] = fund
            changed.append('funding')

        new_flags = [x.strip() for x in c.get('flags') or [] if isinstance(x, str) and x.strip()]
        have = {x.lower() for x in r.get('flags') or []}
        add_flags = [x for x in new_flags if x.lower() not in have]
        if add_flags:
            r['flags'] = (r.get('flags') or []) + add_flags
            changed.append('flags: ' + ', '.join(add_flags))
        why = (c.get('why_flagged') or '').strip()
        if why and not r.get('why_flagged'):
            r['why_flagged'] = why
            changed.append('why_flagged')

        found = split_findings(r.get('other_findings') if isinstance(r.get('other_findings'), str) else '')
        extra = [x.strip() for x in c.get('other_findings') or [] if isinstance(x, str) and x.strip()]
        extra += ['Not related: ' + x.strip() for x in c.get('not_related') or [] if isinstance(x, str) and x.strip()]
        extra = [x for x in extra if x not in found]
        if extra:
            r['other_findings'] = ' | '.join(found + extra)
            changed.append(f'+{len(extra)} findings')

        t = c.get('tier')
        old_tier = r.get('tier')
        if old_tier == 'U' and t in ('A', 'B'):
            r['tier'] = t
        elif old_tier == 'A' and t == 'B':
            r['tier'] = 'B'
        if add_flags and r.get('tier') in ('A', 'U'):   # a new sourced flag makes the record Flagged
            r['tier'] = 'B'
        if r.get('tier') != old_tier:
            changed.append(f'tier {old_tier}→{r["tier"]}')

        status = c.get('website_status')
        if status == 'ok' and c.get('website') and not r.get('website'):
            r['website'] = c['website']
            changed.append('website')
        if status in STATUS_NOTE and not r.get('records_note'):
            r['records_note'] = STATUS_NOTE[status]
            changed.append('records_note')

        if changed:
            r['research_retrieved'] = retrieved
            log.append({'id': rid, 'changed': changed, 'research_changes': c.get('changes') or []})

json.dump(records, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
(results_dir.parent / 'import_log.json').write_text(
    json.dumps({'updated': log, 'skipped': skipped}, ensure_ascii=False, indent=1), encoding='utf-8')
print('updated', len(log), 'records; skipped', len(skipped))
