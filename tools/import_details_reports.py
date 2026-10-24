#!/usr/bin/env python3
"""Details card text from research reports written to data/details_prompt.md.

Each report (one .txt per space, named <record id>.txt or carrying an "ID: <record id>" line) is
read into the record's `details` field, which the Details card prints in this order: overview,
funding, red flags, not related, criticism in art media, wider context, bottom line. Nothing else
in the record is changed: funding, flags, tier and sources go through tools/import_research_reports.py,
which an editor reviews. The art critique frames, cases and personal accounts stay where they are
and are printed after this text.

Usage:
  python3 tools/import_details_reports.py --batches data/details_runs/<date>    # 12 records per batches/dNNN.json
  python3 tools/import_details_reports.py <file | dir>                          # dry run: review file, nothing written
  python3 tools/import_details_reports.py <file | dir> --apply [--only id1,id2] # writes details

The dry run writes review_details.md next to the input with each record's parsed sections and the
house-rule breaks the script can see (dashes, hedging and promotional words, empty or missing
sections, over length). A report with a hard break (no FUNDING, no BOTTOM LINE, no SOURCES, an
unknown id) is skipped on --apply; word-level breaks are listed for the slop checker, not blocked.
"""
import argparse
import datetime
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'institutions.json'

SECTIONS = ('OVERVIEW', 'FUNDING', 'CRITICISM IN ART MEDIA', 'WIDER CONTEXT', 'BOTTOM LINE', 'SOURCES')
SECTION = re.compile(r'^(%s)\s*:?\s*$' % '|'.join(SECTIONS))
RED_FLAG = re.compile(r'^Red flags?:\s*(.+?)\s*$', re.I)
NOT_RELATED = re.compile(r'^Not related:\s*(.+?)\s*$', re.I)
PRESS_ITEM = re.compile(r'^(\d+)[.)]\s+(.+?)\s*$')
URL = re.compile(r'https?://[^\s)>\]]+')
HEDGES = re.compile(r'\b(may|might|reportedly|allegedly|appears? to|seems?|arguably|is said to|believed to|likely|some say)\b')   # lower case: "May" is the month
PROMO = re.compile(r'\b(vibrant|renowned|prestigious|world-class|iconic|landmark|cutting-edge|dynamic|thriving|esteemed|pivotal|tapestry|testament to|nestled|boasts?|showcases?|fosters?|underscores?|delves?|ecosystem|plays a crucial role|it is worth noting|a diverse range of|among others|and more(?! than))\b')   # lower case: Foster is a name
INTERNAL = re.compile(r"\b(the editor|the map|the map's|atlas record|the record says|the checker|slop check)\b", re.I)
DASH = re.compile(r'\s[–—]\s|[–—]')


def bullet(t):
    return t[2:].strip() if t.startswith(('- ', '• ', '* ', '– ')) else t


def parse(text, stem, ids):
    lines = [l.rstrip() for l in text.splitlines() if l.strip()]
    if not lines:
        raise ValueError('empty report')
    rid = next((m.group(1) for l in lines[:4] for m in [re.match(r'^ID:\s*(\S+)', l.strip())] if m), None) or stem
    if rid not in ids:
        raise ValueError(f'id "{rid}" is not a record')
    d = {'overview': [], 'funding_verdict': '', 'funding': [], 'red_flags': [], 'not_related': [],
         'press': {'overall': '', 'items': []}, 'wider_context': [], 'bottom_line': '', 'sources': []}
    section, bottom = None, []
    for l in lines[1:]:
        t = l.strip()
        if t.startswith('ID:'):
            continue
        if t.startswith('Website:'):
            d['website'] = t[len('Website:'):].strip()
            continue
        m = SECTION.match(t)
        if m:
            section = m.group(1)
            continue
        m = RED_FLAG.match(t)
        if m and section in ('FUNDING', 'RED', 'NOT_RELATED', None):
            section = 'RED'
            h = m.group(1)
            d['red_flags'].append({'heading': h[:1].upper() + h[1:], 'points': []})
            continue
        m = NOT_RELATED.match(t)
        if m and section in ('FUNDING', 'RED', 'NOT_RELATED', None):
            section = 'NOT_RELATED'
            d['not_related'].append(m.group(1))
            continue
        item = bullet(t)
        if section == 'OVERVIEW':
            d['overview'].append(item)
        elif section == 'FUNDING':
            if not d['funding_verdict'] and not t.startswith(('- ', '• ', '* ')):
                d['funding_verdict'] = item
            else:
                d['funding'].append(item)
        elif section == 'RED':
            d['red_flags'][-1]['points'].append(item)
        elif section == 'NOT_RELATED':
            d['not_related'][-1] += ' ' + item
        elif section == 'CRITICISM IN ART MEDIA':
            p = d['press']
            if t.lower().startswith('overall:'):
                p['overall'] = t.split(':', 1)[1].strip()
                continue
            m = PRESS_ITEM.match(t)
            if m:
                head = m.group(2)
                hm = re.match(r'^(.+?):\s+(.+)$', head)
                p['items'].append({'outlet': hm.group(1) if hm else head, 'title': hm.group(2) if hm else '', 'url': '', 'points': []})
                continue
            if not p['items']:
                p['overall'] = (p['overall'] + ' ' + item).strip()
                continue
            if t.startswith('URL:'):
                u = URL.search(t)
                p['items'][-1]['url'] = u.group(0).rstrip('.,') if u else ''
                continue
            p['items'][-1]['points'].append(item)
        elif section == 'WIDER CONTEXT':
            d['wider_context'].append(item)
        elif section == 'BOTTOM LINE':
            bottom.append(item)
        elif section == 'SOURCES':
            u = URL.search(item)
            if u:
                note = item[u.end():].strip().strip('()').strip()
                d['sources'].append({'url': u.group(0).rstrip('.,'), **({'note': note} if note else {})})
    d['bottom_line'] = ' '.join(bottom)
    return rid, d


def lint(d):
    """House-rule breaks the script can see. Returns (hard, soft)."""
    hard, soft = [], []
    if not d['funding_verdict'] and not d['funding']:
        hard.append('no FUNDING')
    if not d['bottom_line']:
        hard.append('no BOTTOM LINE')
    if not d['sources']:
        hard.append('no SOURCES')
    if not d['overview']:
        soft.append('no OVERVIEW')
    if not d['press']['overall'] and not d['press']['items']:
        soft.append('no CRITICISM IN ART MEDIA')
    for f in d['red_flags']:
        if not f['points']:
            hard.append(f'empty red flag "{f["heading"]}"')
    for it in d['press']['items']:
        if not it['url']:
            soft.append(f'press item without URL: {it["outlet"]}')
    texts = d['overview'] + [d['funding_verdict']] + d['funding'] + [p for f in d['red_flags'] for p in [f['heading']] + f['points']] \
        + d['not_related'] + [d['press']['overall']] + [p for it in d['press']['items'] for p in [it['title']] + it['points']] \
        + d['wider_context'] + [d['bottom_line']]
    words = sum(len(t.split()) for t in texts)
    if words > 800:
        soft.append(f'{words} words (limit 800)')
    for t in texts:
        unq = re.sub(r'"[^"]*"|“[^”]*”', '', t)   # quoted source words are allowed
        for rx, name in ((DASH, 'dash'), (HEDGES, 'hedge'), (PROMO, 'promo'), (INTERNAL, 'internal wording')):
            m = rx.search(unq)
            if m:
                soft.append(f'{name}: "{m.group(0).strip()}" in "{t[:80]}"')
    return hard, soft


def make_batches(out, size=12):
    recs = json.loads(DATA.read_text())
    keep = ('id', 'name', 'location', 'website', 'funding', 'watch', 'flags', 'why_flagged', 'records_note', 'sources')
    rows = [{k: r[k] for k in keep if r.get(k)} for r in recs if r.get('tier') != 'COMMUNITY']
    # Flagged spaces first, then source-cited, then unverified: the order the editor reads them in.
    order = {'B': 0, 'A': 1, 'U': 2}
    rows.sort(key=lambda r: (order.get(next((x['tier'] for x in recs if x['id'] == r['id']), 'U'), 3), r['id']))
    b = out / 'batches'
    b.mkdir(parents=True, exist_ok=True)
    (out / 'reports').mkdir(exist_ok=True)
    (out / 'checks').mkdir(exist_ok=True)
    n = 0
    for i in range(0, len(rows), size):
        (b / f'd{n:03d}.json').write_text(json.dumps(rows[i:i + size], ensure_ascii=False, indent=1))
        n += 1
    print(f'{len(rows)} records in {n} batches under {b}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input', nargs='?')
    ap.add_argument('--batches', help='write batch files for a new run into this folder')
    ap.add_argument('--apply', action='store_true')
    ap.add_argument('--only', default='')
    ap.add_argument('--date', default=datetime.date.today().isoformat())
    a = ap.parse_args()
    if a.batches:
        return make_batches(Path(a.batches))
    src = Path(a.input)
    files = sorted(src.glob('*.txt')) if src.is_dir() else [src]
    recs = json.loads(DATA.read_text())
    by_id = {r['id']: r for r in recs}
    only = {x for x in a.only.split(',') if x}
    review, applied, skipped = [], 0, []
    for f in files:
        try:
            rid, d = parse(f.read_text(), f.stem, by_id)
        except ValueError as e:
            skipped.append(f'{f.name}: {e}')
            continue
        if only and rid not in only:
            continue
        hard, soft = lint(d)
        r = by_id[rid]
        review.append(f'## {r["name"]} (`{rid}`)\n\n'
                      f'Overview {len(d["overview"])} points; funding: {d["funding_verdict"] or "(no verdict)"}; '
                      f'red flags: {", ".join(f["heading"] for f in d["red_flags"]) or "none"}; '
                      f'press items: {len(d["press"]["items"])}; sources: {len(d["sources"])}\n\n'
                      + ''.join(f'- HARD: {x}\n' for x in hard) + ''.join(f'- {x}\n' for x in soft))
        if hard:
            skipped.append(f'{f.name}: {"; ".join(hard)}')
            continue
        if a.apply:
            d['retrieved'] = a.date
            r['details'] = d
            applied += 1
    out = (src if src.is_dir() else src.parent) / 'review_details.md'
    out.write_text(f'# Details reports ({"applied" if a.apply else "dry run, nothing written"})\n\n'
                   f'{len(review)} read, {applied} applied, {len(skipped)} skipped.\n\n'
                   + ''.join(f'- skipped {s}\n' for s in skipped) + '\n' + '\n'.join(review))
    if a.apply and applied:
        DATA.write_text(json.dumps(recs, ensure_ascii=True, indent=2))
    print(f'{len(review)} read, {applied} applied, {len(skipped)} skipped; review: {out}')
    for s in skipped:
        print('  skipped', s)


if __name__ == '__main__':
    main()
