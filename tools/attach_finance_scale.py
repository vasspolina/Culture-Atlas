#!/usr/bin/env python3
"""Attach the structured accounts figures to records as `finance`.

data/finances_2026-10-18.json is the budget-extraction run (sponsor-atlas/work/finances.json,
brief in sponsor-atlas/work/ubatch/FINANCES.md): one entry per pin, keyed by the pin's name,
with full-currency-unit figures read from a filing and the filing's url. Each becomes a record's
`finance` object: fy, currency, income, expenditure, public, private, earned, sponsorship,
net_assets, source_kind, url. Figures a filing did not state are left out, never estimated, and
an entry with no figure at all attaches nothing. The one-line `finances_note` stays as it is.

Usage:
  python3 tools/attach_finance_scale.py            # dry run: counts and unmatched names
  python3 tools/attach_finance_scale.py --apply    # writes institutions.json
"""
import argparse
import json
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'institutions.json'
FIN = ROOT / 'data' / 'finances_2026-10-18.json'

# Names the run used that are not the record's name.
ALIAS = {
    'Muzeum Sztuki': 'muzeum-sztuki-lodz', 'Inhotim': 'instituto-inhotim',
    'WIELS': 'wiels-contemporary-art-centre', 'Guggenheim': 'solomon-r-guggenheim-museum',
    'MoMA': 'moma-the-museum-of-modern-art', 'The Met': 'the-metropolitan-museum-of-art-the-met',
    'Whitney Museum': 'whitney-museum-of-american-art', 'Fruitmarket': 'fruitmarket-gallery',
    'Serpentine': 'serpentine-galleries', 'MACBA': 'macba-museu-d-art-contemporani-de-barcelona',
    'MALBA': 'museo-de-arte-latinoamericano-de-buenos-aires-malba', 'Madre': 'madre-museum-naples',
    'Stedelijk Museum': 'stedelijk-museum-amsterdam', 'Vleeshal': 'vleeshal-middelburg',
    'Casco Art Institute': 'casco-art-institute', 'Auckland Art Gallery': 'auckland-art-gallery-toi-o-t-maki',
    'SALT': 'salt-galata-istanbul', 'Baltic': 'baltic-centre-for-contemporary-art',
    'Moderna galerija': 'moderna-galerija-ljubljana', 'Tabakalera': 'tabakalera-donostia',
    'Renaissance Society': 'the-renaissance-society', 'Beirut Art Center': 'beirut-art-center-bac',
    'Arab Image Foundation': 'arab-image-foundation-beirut',
}
FIGURES = (('income_total', 'income'), ('expenditure_total', 'expenditure'), ('public', 'public'),
           ('private', 'private'), ('earned', 'earned'), ('sponsorship', 'sponsorship'), ('net_assets', 'net_assets'))


def flat(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s.lower()) if c.isalnum())


def build(entry):
    out = {}
    for src, dst in FIGURES:
        v = entry.get(src)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            out[dst] = v
    if not out:
        return None
    if not entry.get('currency'):
        return None
    head = {k: entry[k] for k in ('fy', 'currency') if entry.get(k)}
    tail = {k: entry[k] for k in ('source_kind', 'url') if entry.get(k)}
    return {**head, **out, **tail}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    records = json.load(open(DATA, encoding='utf-8'))
    by_id = {r['id']: r for r in records}
    by_name = {r['name']: r for r in records}
    by_flat = {flat(r['name']): r for r in records}
    fin = json.load(open(FIN, encoding='utf-8'))
    attached, empty, unmatched = 0, [], []
    for name, entry in fin.items():
        rec = by_id.get(ALIAS.get(name, '')) or by_name.get(name) or by_flat.get(flat(name))
        if not rec:
            unmatched.append(name)
            continue
        f = build(entry)
        if not f:
            empty.append(name)
            continue
        if args.apply:
            rec['finance'] = f
        attached += 1
    print(f'{len(fin)} entries: {attached} with figures, {len(empty)} without, {len(unmatched)} unmatched')
    if unmatched:
        print('unmatched:', unmatched)
    if args.apply:
        with open(DATA, 'w', encoding='utf-8') as fh:
            json.dump(records, fh, indent=2, ensure_ascii=True)
        print('wrote', DATA.name)


if __name__ == '__main__':
    sys.exit(main())
