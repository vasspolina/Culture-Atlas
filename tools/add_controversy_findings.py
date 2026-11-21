#!/usr/bin/env python3
"""Add the findings of a controversy pass to the Details reports the records already hold.

A findings file (data/details_runs/<run>/findings/<record id>.txt) carries only what the pass found: Red flags sections,
WIDER CONTEXT points, CRITICISM IN ART MEDIA items and their SOURCES, in the layout of data/details_prompt.md. Nothing in
the existing report is replaced: sections, points, press items and sources are appended, and anything the report already
states (same heading, same point, same address) is skipped. The rules of the pass are in the run's RUN.md.

Usage: python3 tools/add_controversy_findings.py data/details_runs/<run>/findings            (dry run, lists what it would add)
       python3 tools/add_controversy_findings.py data/details_runs/<run>/findings --apply
Then:  python3 tools/clean_data.py && python3 tools/check_repetition.py --max 0 && python3 tools/embed_data.py
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from import_details_reports import DASH, DATA, HEDGES, INTERNAL, PROMO, parse   # noqa: E402

ABSENCE = re.compile(r'\b(no (?:reporting|criticism|dispute|record|evidence) (?:was )?found|not found|none found|could not be (?:found|opened|read)|in the sources read|is not known)\b', re.I)
VERDICT = re.compile(r'\b(controversial|problematic|troubling|concerning)\b', re.I)


def norm(t):
    return re.sub(r'\W+', ' ', (t or '').lower()).strip()


def lint(d):
    """House-rule breaks the script can see in a findings file."""
    out = []
    if not (d['red_flags'] or d['wider_context'] or d['press']['items']):
        out.append('nothing to add')
    if not d['sources']:
        out.append('no SOURCES')
    for f in d['red_flags']:
        if not f['points']:
            out.append(f'empty red flag "{f["heading"]}"')
    for it in d['press']['items']:
        if not it['url']:
            out.append(f'press item without URL: {it["outlet"]}')
        if not it['points']:
            out.append(f'press item without points: {it["outlet"]}')
    texts = [p for f in d['red_flags'] for p in [f['heading']] + f['points']] + d['wider_context'] \
        + [p for it in d['press']['items'] for p in [it['title']] + it['points']]
    for t in texts:
        unq = re.sub(r'"[^"]*"|“[^”]*”', '', t)   # quoted source words are allowed
        for rx, name in ((DASH, 'dash'), (HEDGES, 'hedge'), (PROMO, 'promo'), (INTERNAL, 'internal wording'),
                         (ABSENCE, 'absence line'), (VERDICT, 'verdict adjective')):
            m = rx.search(unq)
            if m:
                out.append(f'{name}: "{m.group(0).strip()}" in "{t[:80]}"')
    return out


def merge(det, d):
    """Append what `d` adds to the report `det`. Returns a count of each kind added."""
    n = {'red_flags': 0, 'wider_context': 0, 'press': 0, 'sources': 0}
    have_h = {norm(f.get('heading')) for f in det.get('red_flags') or []}
    have_p = {norm(p) for f in det.get('red_flags') or [] for p in f.get('points') or []} | {norm(p) for p in det.get('wider_context') or []}
    for f in d['red_flags']:
        pts = [p for p in f['points'] if norm(p) not in have_p]
        if norm(f['heading']) in have_h or not pts:
            continue
        det.setdefault('red_flags', []).append({'heading': f['heading'], 'points': pts})
        have_h.add(norm(f['heading']))
        have_p.update(norm(p) for p in pts)
        n['red_flags'] += 1
    for p in d['wider_context']:
        if norm(p) not in have_p:
            det.setdefault('wider_context', []).append(p)
            have_p.add(norm(p))
            n['wider_context'] += 1
    press = det.get('press')
    if not isinstance(press, dict):
        press = det['press'] = {'overall': '', 'items': []}
    have_u = {(it.get('url') or '').rstrip('/') for it in press.setdefault('items', [])}
    for it in d['press']['items']:
        if it['url'].rstrip('/') not in have_u:
            press['items'].append(it)
            have_u.add(it['url'].rstrip('/'))
            n['press'] += 1
    srcs = det.setdefault('sources', [])
    have_s = {(s.get('url') if isinstance(s, dict) else s or '').rstrip('/') for s in srcs}
    for s in d['sources']:
        if s['url'].rstrip('/') not in have_s:
            srcs.append(s)
            have_s.add(s['url'].rstrip('/'))
            n['sources'] += 1
    return n


# A bottom line written when the report held no dispute ("No controversy was found on the pages read") is false once one
# is added, and the atlas prints no "not found" lines anyway. The clause goes; what stands beside it stays.
NO_DISPUTE = re.compile(r'\b(?:no|nothing)\b[^.;]*\b(?:controvers\w*|disputes?|contested|protests?|criticism)\b', re.I)


TAIL = re.compile(r',\s+and\s+no\s+controvers[^.;]*', re.I)   # "..., and no controversy was found in the pages read."


def drop_no_dispute(text):
    text = text or ''
    if not NO_DISPUTE.search(text):
        return text
    out = []
    for sentence in re.split(r'(?<=[.!?])\s+(?=[A-Z"“])', TAIL.sub('', text)):
        parts = re.split(r';\s+', sentence)
        clauses = [c for c in parts if not NO_DISPUTE.search(c)]
        if not clauses:
            continue
        s = '; '.join(clauses)
        if clauses[0] is not parts[0]:
            s = s[:1].upper() + s[1:]   # the clause that opened the sentence went, so the next one opens it
        out.append(s if s[-1] in '.!?' else s + '.')
    return ' '.join(out)


def apply_replacements(by, folder):
    """`replace.json` beside the findings folder lists older lines a finding supersedes: a record's wider-context point that
    held the same event unconfirmed. Each entry: {"id", "drop_wider_context_starting": "<first words of the point>"}."""
    path = Path(folder).parent / 'replace.json'
    if not path.exists():
        return 0
    n = 0
    for e in json.loads(path.read_text(encoding='utf8')):
        det = by[e['id']]['details']
        keep = [p for p in det.get('wider_context') or [] if not p.startswith(e['drop_wider_context_starting'])]
        n += len(det.get('wider_context') or []) - len(keep)
        det['wider_context'] = keep
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('folder')
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()
    recs = json.loads(DATA.read_text(encoding='utf8'))
    by = {r['id']: r for r in recs}
    tot, bad, touched, bottoms = {'red_flags': 0, 'wider_context': 0, 'press': 0, 'sources': 0}, 0, [], 0
    for f in sorted(Path(a.folder).glob('*.txt')):
        try:
            rid, d = parse(f.read_text(encoding='utf8'), f.stem, by)
        except ValueError as e:
            print(f'REFUSED {f.name}: {e}')
            bad += 1
            continue
        problems = lint(d)
        if problems:
            print(f'{rid}:')
            for p in problems:
                print('   ', p)
        if any(p.startswith(('nothing', 'no SOURCES', 'empty red flag')) for p in problems):
            bad += 1
            continue
        det = by[rid].get('details')
        if not isinstance(det, dict):
            print(f'REFUSED {rid}: the record has no Details report to add to')
            bad += 1
            continue
        n = merge(det, d)
        if any(n.values()):
            touched.append(rid)
            before = det.get('bottom_line') or ''
            after = drop_no_dispute(before)
            if after != before:
                det['bottom_line'] = after
                bottoms += 1
                print(f'{rid}: bottom line\n    was: {before}\n    now: {after}')
        for k, v in n.items():
            tot[k] += v
    replaced = apply_replacements(by, a.folder)
    print(f'{bottoms} bottom lines lost a "no dispute" clause; {replaced} older wider-context points replaced')
    print(f'{len(touched)} records; {tot["red_flags"]} Red flags sections, {tot["wider_context"]} wider-context points, '
          f'{tot["press"]} press items, {tot["sources"]} sources; {bad} files refused')
    if a.apply:
        DATA.write_text(json.dumps(recs, ensure_ascii=True, indent=2))   # the file's own form, as import_details_reports writes it
        print('written', DATA.name)
    else:
        print('dry run: nothing written (add --apply)')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
