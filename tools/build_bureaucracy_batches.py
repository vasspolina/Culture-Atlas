#!/usr/bin/env python3
"""Cut institutions.json into research batches for data/bureaucracy_prompt.md.

Records are grouped by country so one agent reads one country's laws and registers, 12 to a
batch, in file data/bureaucracy_runs/<run>/batches/bNNN.json. A record that already has a
`bureaucracy` block is left out unless --all.

Usage: python3 tools/build_bureaucracy_batches.py <run> [--size 12] [--all]
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYS = ('id', 'name', 'city', 'country', 'website', 'size', 'year_founded')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run')
    ap.add_argument('--size', type=int, default=12)
    ap.add_argument('--all', action='store_true')
    args = ap.parse_args()
    records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
    todo = [r for r in records if args.all or not r.get('bureaucracy')]
    todo.sort(key=lambda r: ((r.get('country') or ''), (r.get('city') or ''), r['name']))
    out = ROOT / 'data' / 'bureaucracy_runs' / args.run / 'batches'
    out.mkdir(parents=True, exist_ok=True)
    for i in range(0, len(todo), args.size):
        batch = []
        for r in todo[i:i + args.size]:
            b = {k: r.get(k) for k in KEYS}
            b['funding'] = (r.get('funding') or '')[:300]
            b['sources'] = (r.get('sources') or [])[:3]
            batch.append(b)
        (out / f'b{i // args.size:03d}.json').write_text(json.dumps(batch, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    n = (len(todo) + args.size - 1) // args.size
    print(f'{len(todo)} records in {n} batches -> {out}')


if __name__ == '__main__':
    main()
