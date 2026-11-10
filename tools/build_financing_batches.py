#!/usr/bin/env python3
"""Cut institutions.json into research batches for data/financing_scale_prompt.md.

Records are grouped by country so one agent reads one country's registers, 12 to a batch, in
file data/financing_scale_runs/<run>/batches/fNNN.json. `needs_finance` marks records with no
`finance` block. A record that already has a `scale` block is left out unless --all; a record that
sits in a batch of an earlier run is left out with --skip-run <earlier run> (repeatable).

Usage: python3 tools/build_financing_batches.py <run> [--size 12] [--all] [--skip-run RUN]
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
    ap.add_argument('--skip-run', action='append', default=[])
    args = ap.parse_args()
    records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
    done = set()
    for run in args.skip_run:
        for f in (ROOT / 'data' / 'financing_scale_runs' / run / 'batches').glob('f*.json'):
            done.update(b['id'] for b in json.load(open(f, encoding='utf-8')))
    todo = [r for r in records if (args.all or not r.get('scale')) and r['id'] not in done]
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
