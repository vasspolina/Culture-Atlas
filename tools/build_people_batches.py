#!/usr/bin/env python3
"""Cut institutions.json into research batches for data/people_prompt.md.

Records are grouped by country and city so one agent reads one place's press and registers, 12 to
a batch, in data/people_runs/<run>/batches/<prefix>NNN.json. Each record carries `known`: the
sentences the atlas record already holds that name a director, curator or founder, so the
researcher can confirm or replace them. They are a lead, never a source.

A record already in data/people.json is left out unless --all. --city and --country narrow the
cut (repeatable, exact match on the record's field); --ids takes a comma-separated list.

Usage: python3 tools/build_people_batches.py <run> [--size 12] [--all]
           [--city London] [--country Germany] [--ids a,b,c] [--prefix b]
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYS = ('id', 'name', 'city', 'country', 'website', 'size', 'year_founded')
ROLE = re.compile(
    r'\b(director(?!y)|directora|directrice|direktor|direktorin|intendant|curator|curated by|'
    r'conservat|founder|founded by|co-founded|ceo|chief executive|head of|chair)', re.I)
SPLIT = re.compile(r'(?<=[.;])\s+(?=[A-Z])')


def texts(r):
    """Every free-text string on a record that might name its people."""
    d = r.get('details') or {}
    for k in ('overview', 'funding'):
        for s in d.get(k) or []:
            if isinstance(s, str):
                yield s
    for k in ('affiliations_note', 'records_note', 'watch', 'curatorial_focus'):
        v = r.get(k)
        if isinstance(v, str):
            yield v
    b = r.get('bureaucracy')
    if isinstance(b, dict):
        for v in b.values():
            if isinstance(v, str):
                yield v


def known(r):
    seen, out = set(), []
    for t in texts(r):
        for s in SPLIT.split(t):
            s = s.strip()
            if ROLE.search(s) and s not in seen:
                seen.add(s)
                out.append(s[:300])
    return out[:6]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run')
    ap.add_argument('--size', type=int, default=12)
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--city', action='append', default=[])
    ap.add_argument('--country', action='append', default=[])
    ap.add_argument('--ids', default='')
    ap.add_argument('--prefix', default='b')
    args = ap.parse_args()
    records = json.load(open(ROOT / 'institutions.json', encoding='utf-8'))
    done = set()
    people = ROOT / 'data' / 'people.json'
    if people.exists() and not args.all:
        done = {p['id'] for p in json.load(open(people, encoding='utf-8'))}
    ids = {i.strip() for i in args.ids.split(',') if i.strip()}
    todo = [r for r in records
            if r['id'] not in done
            and (not ids or r['id'] in ids)
            and (not args.city or r.get('city') in args.city)
            and (not args.country or r.get('country') in args.country)]
    todo.sort(key=lambda r: ((r.get('country') or ''), (r.get('city') or ''), r['name']))
    out = ROOT / 'data' / 'people_runs' / args.run / 'batches'
    out.mkdir(parents=True, exist_ok=True)
    for i in range(0, len(todo), args.size):
        batch = []
        for r in todo[i:i + args.size]:
            b = {k: r.get(k) for k in KEYS}
            b['known'] = known(r)
            batch.append(b)
        name = f'{args.prefix}{i // args.size:03d}.json'
        (out / name).write_text(json.dumps(batch, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    n = (len(todo) + args.size - 1) // args.size
    print(f'{len(todo)} records in {n} batches -> {out}')


if __name__ == '__main__':
    main()
