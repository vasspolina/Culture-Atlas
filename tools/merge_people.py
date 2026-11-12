#!/usr/bin/env python3
"""Fold one run of data/people_prompt.md into data/people.json and data/people.csv.

For each batch in data/people_runs/<run>/out/, a checker's file in check/ of the same name, when
there is one, overrides the researcher's record with its `corrected` object. A batch with no
check file is merged only with --unchecked, and its records are marked `"checked": false`.

Names lose honorifics and letters after them (Dr, Prof., Sir, Dame, OBE). Every record is validated against the brief before it is written: roles from the list, no field
outside the schema (so nothing from "What never goes in" can ride along), at least one source per
person, no Wikipedia or LinkedIn source, pay only with a url, no long dash in `basis`. A record
that fails is reported and left out; the rest are merged. A record already in people.json for the
same id is replaced.

Usage: python3 tools/merge_people.py <run> [--unchecked] [--dry-run]
"""
import argparse
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROLES = {'director', 'co-director', 'artistic director', 'chief curator', 'curator', 'founder',
         'chair of the board'}
LEFT = {'retired', 'term ended', 'moved to another post', 'resigned', 'dismissed', 'died', None}
PERSON_KEYS = {'name', 'role', 'title', 'current', 'since', 'until', 'left_because', 'next_post',
               'previously', 'pay', 'sources'}
PAY_KEYS = {'amount', 'amount_to', 'currency', 'year', 'what', 'url'}
HONORIFIC = re.compile(r'^(Dr|Prof|Professor|Sir|Dame|The Rt Hon|The Hon|Lord|Lady)\.?\s+'
                       r'|,?\s+(OBE|MBE|CBE|DBE|KBE|CH|FBA|FRS|FRSA|PhD|Hon\.? RA|RA)\b\.?')


def plain_name(name):
    """'Prof. Dr. Raphael Gross' -> 'Raphael Gross'; 'Dame Janet Vitmayer, DBE' -> 'Janet Vitmayer'."""
    prev = None
    while prev != name:
        prev, name = name, HONORIFIC.sub('', name).strip(' ,')
    return name
BANNED_HOSTS = re.compile(r'(wikipedia\.org|linkedin\.com|google\.[a-z.]+/search)', re.I)
DATE = re.compile(r'^\d{4}(-\d{2})?$')


def settle_predecessors(rec, note):
    """A predecessor with no leaving year stays only when a current head's start of 2023 or later
    shows they left inside the window the brief allows; otherwise that one person is dropped."""
    heads = ('director', 'co-director', 'artistic director', 'chief curator')
    people = rec.get('people') or []
    started = [str(p.get('since') or '')[:4] for p in people
               if p.get('current') and p.get('role') in heads and p.get('since')]
    keep = []
    for p in people:
        if p.get('current') is False and not p.get('until'):
            if any(y >= '2023' for y in started):
                keep.append(p)
                continue
            note(f'{rec["id"]}: dropped predecessor {p.get("name")} (no leaving year, no successor start since 2023)')
            continue
        keep.append(p)
    rec['people'] = keep


def problems(rec):
    out = []
    if set(rec) - {'id', 'people', 'basis'}:
        out.append(f'extra keys {sorted(set(rec) - {"id", "people", "basis"})}')
    people = rec.get('people')
    if not isinstance(people, list):
        return out + ['people is not a list']
    if len(people) > 6:
        out.append(f'{len(people)} people, the brief allows 6')
    if re.search('[–—]', rec.get('basis') or ''):
        out.append('long dash in basis')
    if people and not rec.get('basis'):
        out.append('people but no basis')
    for p in people:
        who = p.get('name', '?')
        extra = set(p) - PERSON_KEYS
        if extra:
            out.append(f'{who}: fields outside the schema {sorted(extra)}')
        if p.get('role') not in ROLES:
            out.append(f'{who}: role {p.get("role")!r}')
        if not isinstance(p.get('current'), bool):
            out.append(f'{who}: current is not true or false')
        for k in ('since', 'until'):
            if p.get(k) is not None and not DATE.match(str(p[k])):
                out.append(f'{who}: {k} {p[k]!r}')
        if p.get('current') and p.get('until'):
            out.append(f'{who}: current with an until date')
        if p.get('current') is False:
            if not p.get('until'):
                pass  # settled by settle_predecessors before validation
            elif str(p['until'])[:4] < '2023':
                out.append(f'{who}: predecessor left before 2023')
        if p.get('left_because') not in LEFT:
            out.append(f'{who}: left_because {p.get("left_because")!r}')
        srcs = p.get('sources') or []
        if not srcs:
            out.append(f'{who}: no source')
        for s in srcs:
            if BANNED_HOSTS.search(s):
                out.append(f'{who}: banned source {s}')
        pay = p.get('pay')
        if pay is not None:
            if not isinstance(pay, dict) or set(pay) - PAY_KEYS or not pay.get('url'):
                out.append(f'{who}: pay malformed or without a url')
            elif not all(isinstance(pay.get(k), (int, float)) for k in ('amount',)) or \
                    ('amount_to' in pay and not isinstance(pay['amount_to'], (int, float))):
                out.append(f'{who}: pay amount is not a number')

    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run')
    ap.add_argument('--unchecked', action='store_true')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    run = ROOT / 'data' / 'people_runs' / args.run
    names = {r['id']: r for r in json.load(open(ROOT / 'institutions.json', encoding='utf-8'))}
    store = ROOT / 'data' / 'people.json'
    merged = {r['id']: r for r in json.load(open(store, encoding='utf-8'))} if store.exists() else {}

    added = rejected = skipped = 0
    for f in sorted((run / 'out').glob('*.json')):
        recs = json.load(open(f, encoding='utf-8'))
        chk = run / 'check' / f.name
        corrected, checked = {}, chk.exists()
        if checked:
            for c in json.load(open(chk, encoding='utf-8')):
                if c.get('verdict') == 'fault' and c.get('corrected'):
                    corrected[c['id']] = c['corrected']
        elif not args.unchecked:
            print(f'{f.name}: no check file, skipped (pass --unchecked to merge it)')
            skipped += len(recs)
            continue
        for rec in recs:
            rec = corrected.get(rec['id'], rec)
            for p in rec.get('people') or []:
                if isinstance(p.get('name'), str):
                    p['name'] = plain_name(p['name'])
            if rec['id'] not in names:
                print(f'{f.name} {rec["id"]}: not in institutions.json')
                rejected += 1
                continue
            settle_predecessors(rec, print)
            bad = problems(rec)
            if bad:
                print(f'{f.name} {rec["id"]}: ' + '; '.join(bad))
                rejected += 1
                continue
            if not rec['people']:
                continue
            merged[rec['id']] = {'id': rec['id'], 'name': names[rec['id']]['name'],
                                 'city': names[rec['id']].get('city'),
                                 'country': names[rec['id']].get('country'),
                                 'people': rec['people'], 'basis': rec['basis'],
                                 'run': args.run, 'checked': checked}
            added += 1

    print(f'{added} records merged, {rejected} rejected, {skipped} waiting for a check; '
          f'{len(merged)} in people.json')
    if args.dry_run:
        return
    rows = sorted(merged.values(), key=lambda r: r['id'])
    store.write_text(json.dumps(rows, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    with open(ROOT / 'data' / 'people.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['space_id', 'space', 'city', 'country', 'name', 'role', 'title', 'current',
                    'since', 'until', 'left_because', 'next_post', 'previously', 'pay', 'sources',
                    'checked'])
        for r in rows:
            for p in r['people']:
                pay = p.get('pay')
                w.writerow([r['id'], r['name'], r['city'], r['country'], p['name'], p['role'],
                            p.get('title') or '', p['current'], p.get('since') or '',
                            p.get('until') or '', p.get('left_because') or '',
                            p.get('next_post') or '', ' | '.join(p.get('previously') or []),
                            (f'{pay["amount"]}' + (f' to {pay["amount_to"]}' if pay.get('amount_to') else '') + f' {pay["currency"]} {pay["year"]} {pay["what"]}') if pay else '',
                            ' '.join(p['sources']), r['checked']])


if __name__ == '__main__':
    main()
