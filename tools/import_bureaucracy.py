#!/usr/bin/env python3
"""Read the agents' output for data/bureaucracy_prompt.md into the records.

Each out/bNNN.json entry gives a record's `governance` facts and, where a source reports it, a
`red_tape` note. They land as record['bureaucracy'] (the facts, plus the level and the sentence
tools/grade_bureaucracy.py works out from them) and record['red_tape']. A fact that fails a check
is dropped and listed, never repaired.

Checks: every enumerated field holds one of its listed values; a block carries at least one
http(s) source url; the year looks like a year; the red-tape note is one sentence with a kind, a
date and a url, and carries no dash, hedging word or "not found" phrasing.

Usage:
  python3 tools/import_bureaucracy.py data/bureaucracy_runs/<run>/out            # dry run
  python3 tools/import_bureaucracy.py data/bureaucracy_runs/<run>/out --apply
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from grade_bureaucracy import LABELS, level  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'institutions.json'
URL = re.compile(r'^https?://\S+$')
YEAR = re.compile(r'^(19|20)\d{2}([-/](\d{2}|\d{4}))?$')
DATE = re.compile(r'^(19|20)\d{2}(-\d{2}(-\d{2})?)?$')
ENUMS = {
    'legal_form': {'national government body', 'municipal or regional body', 'statutory public body',
                   'university unit', 'public foundation', 'private nonprofit', 'private foundation',
                   'association', 'private company', 'religious body'},
    'director_appointed_by': {'government or ministry', 'city or region', 'parent institution', 'board', 'members', 'owner'},
    'staff_status': {'civil servants', 'public employees', 'employees of the institution', 'mixed'},
    'budget_set_by': {'legislature or ministry', 'city or regional council', 'parent institution', 'board', 'owner'},
}
CONTROLS = {'public procurement law', 'state audit office', 'freedom of information law', 'civil service rules',
            'approval of programme, loans or disposals by a ministry or council',
            'ministry or city seat on the governing board', 'charity or foundation regulator'}
KINDS = {'audit report', 'parliamentary report', 'press report', 'employee account', 'official review'}
BAD_TEXT = re.compile(r'[–—]|\b(?:no|nothing|none)\b[^.]{0,40}\b(?:found|reported|located)\b|\b(?:appears?|seems?|reportedly|allegedly|possibly|perhaps|likely)\b', re.I)


def check_governance(g, problems):
    if not g:
        return None
    out = {}
    for k, allowed in ENUMS.items():
        v = g.get(k)
        if v is None:
            continue
        if v in allowed:
            out[k] = v
        else:
            problems.append(f'{k} {v!r} is not a listed value; dropped')
    if 'legal_form' not in out:
        problems.append('governance has no legal form; dropped')
        return None
    if g.get('parent'):
        out['parent'] = str(g['parent']).strip()[:120]
    ctl = [c for c in (g.get('controls') or []) if c in CONTROLS]
    for c in (g.get('controls') or []):
        if c not in CONTROLS:
            problems.append(f'control {c!r} is not a listed value; dropped')
    out['controls'] = ctl
    if g.get('year'):
        if YEAR.match(str(g['year'])):
            out['year'] = str(g['year'])
        else:
            problems.append(f'year {g["year"]!r} is not a year')
    urls = [u for u in (g.get('sources') or []) if isinstance(u, str) and URL.match(u)]
    if not urls:
        problems.append('governance has no source url; dropped')
        return None
    out['sources'] = urls[:4]
    lv, why = level(out)
    out['level'] = lv
    out['level_basis'] = why
    return out


def check_red_tape(r, problems):
    if not r:
        return None
    note = re.sub(r'\s+', ' ', str(r.get('note') or '')).strip()
    if not note or r.get('kind') not in KINDS or not DATE.match(str(r.get('date') or '')) or not (isinstance(r.get('url'), str) and URL.match(r['url'])):
        problems.append('red_tape lacks a note, a listed kind, a date or a url; dropped')
        return None
    if BAD_TEXT.search(note):
        problems.append(f'red_tape note has a dash, hedge or not-found phrase; dropped: {note[:60]}')
        return None
    if not note.endswith(('.', '"', '”')):
        note += '.'
    return {'note': note, 'kind': r['kind'], 'date': str(r['date']), 'url': r['url']}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out_dir')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    records = json.load(open(DATA, encoding='utf-8'))
    by_id = {r['id']: r for r in records}
    n_gov = n_red = 0
    report = []
    spread = {}
    for path in sorted(Path(args.out_dir).glob('*.json')):
        for e in json.load(open(path, encoding='utf-8')):
            rec = by_id.get(e.get('id'))
            if not rec:
                report.append(f'{path.name}: unknown id {e.get("id")!r}')
                continue
            problems = []
            gov = check_governance(e.get('governance'), problems)
            red = check_red_tape(e.get('red_tape'), problems)
            for p in problems:
                report.append(f'{path.name} {rec["id"]}: {p}')
            if gov:
                n_gov += 1
                spread[gov['level']] = spread.get(gov['level'], 0) + 1
                if args.apply:
                    rec['bureaucracy'] = gov
            if red:
                n_red += 1
                if args.apply:
                    rec['red_tape'] = red
    print(f'{n_gov} governance blocks, {n_red} red-tape notes; {len(report)} problems')
    print('levels:', {f'{k} {LABELS.get(k, "none")}': v for k, v in sorted(spread.items())})
    for line in report:
        print(' ', line)
    if args.apply:
        with open(DATA, 'w', encoding='utf-8') as fh:
            json.dump(records, fh, indent=2, ensure_ascii=True)
        print('wrote', DATA.name)


if __name__ == '__main__':
    sys.exit(main())
