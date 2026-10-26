#!/usr/bin/env python3
"""Read the agents' output for data/financing_scale_prompt.md into the records.

Each out/fNNN.json entry gives a record's `scale` block and, for a record with no accounts yet,
a `finance` block. Both are written only after the checks below; a figure that fails a check is
dropped and listed, never repaired. A record that already has a `finance` block keeps it.

Checks: figures are whole, positive and plausible; a block carries at least one source url that
is http(s); finance carries a currency, a url and at least one amount, and its public, private
and earned amounts do not exceed income, and a total income or expenditure is stated; years look like years.

Usage:
  python3 tools/import_financing_scale.py data/financing_scale_runs/<run>/out            # dry run
  python3 tools/import_financing_scale.py data/financing_scale_runs/<run>/out --apply
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'institutions.json'
YEAR = re.compile(r'^(19|20)\d{2}([-/](\d{2}|\d{4}))?$')
URL = re.compile(r'^https?://\S+$')
STAFF_KIND = {'employees', 'full-time equivalent', 'staff'}
AREA_KIND = {'gallery space', 'building', 'site'}
AMOUNTS = ('income', 'expenditure', 'public', 'private', 'earned', 'sponsorship', 'net_assets')
LIMITS = {'visitors': 30_000_000, 'staff': 20_000, 'area_m2': 1_000_000, 'site_m2': 50_000_000}
CURRENCY = re.compile(r'^[A-Z]{3}$')


def whole(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0 and float(v).is_integer()


def check_scale(s, problems):
    out = {}
    for key, yr in (('visitors', 'visitors_year'), ('staff', 'staff_year')):
        v = s.get(key)
        if v is None:
            continue
        if not whole(v) or v > LIMITS[key]:
            problems.append(f'{key} {v!r} is not a plausible whole number')
            continue
        out[key] = int(v)
        if s.get(yr):
            if YEAR.match(str(s[yr])):
                out[yr] = str(s[yr])
            else:
                problems.append(f'{yr} {s[yr]!r} is not a year')
    if 'staff' in out and s.get('staff_kind') in STAFF_KIND:
        out['staff_kind'] = s['staff_kind']
    v = s.get('area_m2')
    if v is not None:
        if whole(v) and v <= (LIMITS['site_m2'] if s.get('area_kind') == 'site' else LIMITS['area_m2']):
            out['area_m2'] = int(v)
            if s.get('area_kind') in AREA_KIND:
                out['area_kind'] = s['area_kind']
        else:
            problems.append(f'area_m2 {v!r} is not a plausible whole number')
    if not out:
        return None
    urls = [u for u in (s.get('sources') or []) if isinstance(u, str) and URL.match(u)]
    if not urls:
        problems.append('scale has figures but no source url; dropped')
        return None
    out['sources'] = urls[:4]
    return out


def check_finance(f, problems):
    if not f:
        return None
    out = {}
    if not CURRENCY.match(str(f.get('currency') or '')):
        problems.append('finance has no ISO currency; dropped')
        return None
    if not (isinstance(f.get('url'), str) and URL.match(f['url'])):
        problems.append('finance has no source url; dropped')
        return None
    if f.get('fy'):
        if not YEAR.match(str(f['fy'])):
            problems.append(f'fy {f["fy"]!r} is not a year; dropped')
            return None
        out['fy'] = str(f['fy'])
    out['currency'] = f['currency']
    amounts = {}
    for k in AMOUNTS:
        v = f.get(k)
        if v is None:
            continue
        if isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0:
            amounts[k] = v
        else:
            problems.append(f'finance {k} {v!r} is not an amount')
    if 'income' not in amounts and 'expenditure' not in amounts:
        problems.append('finance states neither income nor expenditure; dropped')
        return None
    inc = amounts.get('income')
    for k in ('public', 'private', 'earned', 'sponsorship'):
        if inc and amounts.get(k, 0) > inc * 1.0001:
            problems.append(f'finance {k} {amounts[k]} exceeds income {inc}; {k} dropped')
            del amounts[k]
    out.update(amounts)
    if f.get('source_kind'):
        out['source_kind'] = f['source_kind']
    out['url'] = f['url']
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out_dir')
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    records = json.load(open(DATA, encoding='utf-8'))
    by_id = {r['id']: r for r in records}
    n_scale = n_fin = n_rec = n_gone = 0
    report = []
    for path in sorted(Path(args.out_dir).glob('*.json')):
        for e in json.load(open(path, encoding='utf-8')):
            rec = by_id.get(e.get('id'))
            if not rec:
                report.append(f'{path.name}: unknown id {e.get("id")!r}')
                continue
            problems = []
            scale = check_scale(e.get('scale') or {}, problems)
            fin = None if rec.get('finance') else check_finance(e.get('finance'), problems)
            for p in problems:
                report.append(f'{path.name} {rec["id"]}: {p}')
            if not scale and rec.get('scale') and args.apply:
                del rec['scale']   # a figure dropped on review leaves no block behind
                n_gone += 1
            if not scale and not fin:
                continue
            n_rec += 1
            if scale:
                n_scale += 1
                if args.apply:
                    rec['scale'] = scale
            if fin:
                n_fin += 1
                if args.apply:
                    rec['finance'] = fin
    print(f'{n_rec} records: {n_scale} scale blocks, {n_fin} finance blocks; {len(report)} problems; {n_gone} stale scale blocks removed')
    for line in report:
        print(' ', line)
    if args.apply:
        with open(DATA, 'w', encoding='utf-8') as fh:
            json.dump(records, fh, indent=2, ensure_ascii=True)
        print('wrote', DATA.name)


if __name__ == '__main__':
    sys.exit(main())
