#!/usr/bin/env python3
"""Merge funding research (data/research_prompt.md, part 2) into institutions.json, after review.

Usage:
  python3 tools/import_research_reports.py <results.json | results dir>            # dry run: writes nothing
  python3 tools/import_research_reports.py <results.json | results dir> --apply    # writes the records
  python3 tools/import_research_reports.py <...> --apply --only id1,id2            # writes only these records

The dry run writes a review file next to the input (review_<name>.md): for every record, each field
that would change, with its current text and its new text, and the research's own notes on what it
contradicts. Read it, then run again with --apply (all) or --apply --only (the records you approve).
After applying, run tools/clean_data.py, tools/embed_data.py and tools/build_money_maps.py.

Unlike the other importers, this one updates records that already exist, but it never silently
throws away what a record says:
- sources, flags and other_findings are added to, never removed (removing a flag is an editor's decision,
  made by hand; the research's suggestion to remove one is shown in the review);
- funding is replaced only when the research cites a source, and the old text is kept under
  field_sources.funding.previous;
- tier: U becomes the research tier; A becomes B when the research found flags; B is never lowered;
- why_flagged, website and records_note are written only where the record has none.
"""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STATUS_NOTE = {
    'spam': 'Its website now serves spam, so its own statements about funding could not be checked.',
    'down': 'Its website could not be reached, so its own statements about funding could not be checked.',
    'parked': 'Its website address is parked, so its own statements about funding could not be checked.',
}


def urls(xs):
    return [u for u in xs or [] if isinstance(u, str) and u.startswith('http')]


def split_findings(s):
    return [x.strip() for x in (s or '').split(' | ') if x.strip()]


def merge(r, c):
    """Apply one research entry to record r in place. Returns a list of (field, before, after)."""
    diff = []
    src = urls(c.get('sources'))
    retrieved = c.get('retrieved') or ''

    old_sources = r.get('sources') or []
    new_sources = [u for u in src if u not in old_sources]
    if new_sources:
        r['sources'] = old_sources + new_sources
        diff.append(('sources (added)', '', '\n'.join(new_sources)))

    fund = (c.get('funding') or '').strip()
    if fund and fund != (r.get('funding') or '').strip():
        before = r.get('funding') or ''
        fs = r.setdefault('field_sources', {})
        fs['funding'] = {'urls': src[:3], 'retrieved': retrieved, 'basis': 'funding research'}
        if before:
            fs['funding']['previous'] = before
        r['funding'] = fund
        diff.append(('funding (replaced; old text kept as previous)', before, fund))

    new_flags = [x.strip() for x in c.get('flags') or [] if isinstance(x, str) and x.strip()]
    have = {x.lower() for x in r.get('flags') or []}
    add_flags = [x for x in new_flags if x.lower() not in have]
    if add_flags:
        before = ', '.join(r.get('flags') or [])
        r['flags'] = (r.get('flags') or []) + add_flags
        diff.append(('flags (added)', before, ', '.join(r['flags'])))
    why = (c.get('why_flagged') or '').strip()
    if why and not r.get('why_flagged'):
        r['why_flagged'] = why
        diff.append(('why_flagged', '', why))

    found = split_findings(r.get('other_findings') if isinstance(r.get('other_findings'), str) else '')
    extra = [x.strip() for x in c.get('other_findings') or [] if isinstance(x, str) and x.strip()]
    extra += ['Not related: ' + x.strip() for x in c.get('not_related') or [] if isinstance(x, str) and x.strip()]
    extra = [x for x in extra if x not in found]
    if extra:
        r['other_findings'] = ' | '.join(found + extra)
        diff.append(('other_findings (added)', '', '\n'.join(extra)))

    t = c.get('tier')
    old_tier = r.get('tier')
    if old_tier == 'U' and t in ('A', 'B'):
        r['tier'] = t
    elif old_tier == 'A' and t == 'B':
        r['tier'] = 'B'
    if add_flags and r.get('tier') in ('A', 'U'):   # a new sourced flag makes the record Flagged
        r['tier'] = 'B'
    if r.get('tier') != old_tier:
        diff.append(('tier', old_tier, r['tier']))

    status = c.get('website_status')
    if status == 'ok' and c.get('website') and not r.get('website'):
        r['website'] = c['website']
        diff.append(('website', '', c['website']))
    if status in STATUS_NOTE and not r.get('records_note'):
        r['records_note'] = STATUS_NOTE[status]
        diff.append(('records_note', '', STATUS_NOTE[status]))

    if diff and retrieved:
        r['research_retrieved'] = retrieved
    return diff


def quote(text):
    return '\n'.join('> ' + line if line else '>' for line in str(text).split('\n')) if text else '> (empty)'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input', help='a results .json file, or a directory of them')
    ap.add_argument('--apply', action='store_true', help='write the changes to institutions.json')
    ap.add_argument('--only', default='', help='comma-separated record ids to apply (with --apply)')
    a = ap.parse_args()

    inp = Path(a.input)
    files = sorted(inp.glob('*.json')) if inp.is_dir() else [inp]
    only = {x.strip() for x in a.only.split(',') if x.strip()}

    path = ROOT / 'institutions.json'
    records = json.load(open(path, encoding='utf-8'))
    by_id = {}
    for r in records:
        by_id.setdefault(r['id'], []).append(r)

    out, skipped, n = [], [], 0
    for f in files:
        try:
            items = json.load(open(f, encoding='utf-8'))
        except json.JSONDecodeError as e:
            skipped.append(f'{f.name}: invalid JSON ({e})')
            continue
        if isinstance(items, dict):
            items = [items]
        for c in items:
            rid = c.get('id')
            if only and rid not in only:
                continue
            matches = by_id.get(rid, [])
            if len(matches) != 1:
                skipped.append(f'{rid}: {len(matches)} records with this id')
                continue
            if not urls(c.get('sources')):
                skipped.append(f'{rid}: no sources')
                continue
            target = matches[0] if a.apply else copy.deepcopy(matches[0])
            diff = merge(target, c)
            if not diff:
                continue
            n += 1
            out.append(f"## {matches[0].get('name')} (`{rid}`)\n")
            for field, before, after in diff:
                out.append(f'**{field}**\n\nNow:\n\n{quote(before)}\n\nWould become:\n\n{quote(after)}\n')
            notes = [x for x in c.get('changes') or [] if isinstance(x, str)]
            if notes:
                out.append('**Research notes (not written to the record):**\n\n' + '\n'.join(f'- {x}' for x in notes) + '\n')

    head = ('# Applied changes\n\n' if a.apply else
            '# Proposed changes (dry run: nothing was written)\n\n'
            'Approve with `--apply`, or `--apply --only id1,id2` for some records.\n\n')
    head += f'{n} records change. Skipped: {len(skipped)}.\n\n' + ''.join(f'- skipped {s}\n' for s in skipped) + '\n'
    name = inp.stem if inp.is_file() else inp.name
    review = (inp.parent if inp.is_file() else inp.parent) / f"{'applied' if a.apply else 'review'}_{name}.md"
    review.write_text(head + '\n'.join(out), encoding='utf-8')

    if a.apply:
        json.dump(records, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
        print(f'applied: {n} records written; log in {review}')
    else:
        print(f'dry run: {n} records would change; nothing written. Review: {review}')


if __name__ == '__main__':
    main()
