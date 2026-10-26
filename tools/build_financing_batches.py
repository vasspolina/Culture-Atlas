#!/usr/bin/env python3
"""Cut institutions.json into research batches for data/financing_scale_prompt.md.

Records are grouped by country so one agent reads one country's registers, 12 to a batch, in
file data/financing_scale_runs/<run>/batches/fNNN.json. `needs_finance` marks records with no
`finance` block. A record that already has a `scale` block is left out unless --all.

Usage: python3 tools/build_financing_batches.py <run> [--size 12] [--all]
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYS = ('id', 'name', 'city', 'country', 'website', 'size', 'year_founded', 'sources')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run')
    ap.add_argument('--size', type=int, default=12)
    ap.add_argument('--all', action='store_true')
    args = ap.parse_args()
    records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
    todo = [r for r in records if args.all or not r.get('scale')]
    todo.sort(key=lambda r: ((r.get('country') or ''), (r.get('city') or ''), r['name']))
    out = ROOT / 'data' / 'financing_scale_runs' / args.run / 'batches'
    out.mkdir(parents=True, exist_ok=True)
    for i in range(0, len(todo), args.size):
        batch = []
        for r in todo[i:i + args.size]:
            b = {k: r.get(k) for k in KEYS if k != 'sources'}
            b['sources'] = (r.get('sources') or [])[:3]
            b['needs_finance'] = not r.get('finance')
            if r.get('finances_note'):
                b['finances_note'] = r['finances_note']
            batch.append(b)
        (out / f'f{i // args.size:03d}.json').write_text(json.dumps(batch, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    n = (len(todo) + args.size - 1) // args.size
    print(f'{len(todo)} records in {n} batches ({sum(1 for r in todo if not r.get("finance"))} need finance) -> {out}')


if __name__ == '__main__':
    main()
