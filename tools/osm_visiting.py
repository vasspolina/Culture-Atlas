#!/usr/bin/env python3
"""Fill opening hours and free admission from OpenStreetMap, for records whose building is already matched to an
OpenStreetMap object (named in field_sources, by the pin audit or tools/apply_osm_addresses.py).

Step 1 (default) asks Nominatim for each object's tags, 50 objects a request, and writes them to
data/web_research/osm_visiting_2026-11-04.json. Step 2 (--apply) writes into institutions.json, then runs
tools/clean_data.py and tools/embed_data.py.

What is written, and only where the record has nothing for that field:
  opening_hours  from the OSM opening_hours tag, set out as the records already write hours, with a semicolon
                 between groups of days so a list of days is not read as two groups
                 ("Tue, Wed, Fri 10:00–18:00; Thu 10:00–21:00; closed Mon"). Only the plain form is read: days, times and "off". A value
                 with months, dates, week numbers, holidays other than "PH off", sunrise or sunset, or a comment is left
                 out rather than half-read. "24/7" is not taken for a museum: on these objects it means the grounds.
                 Only hours a mapper has confirmed since 2024 (check_date or check_date:opening_hours) are taken.
  admission_fee  "Free" where the object is tagged fee=no, or the price where a charge tag states one.
                 fee=yes on its own says only that there is a charge, which is no help to a visitor, so it is skipped.
Each value records the OSM object under field_sources with the date it was read. OSM is kept by volunteers: the
visitor card links to the space's own visit page, which stays the authority.
Usage: python3 tools/osm_visiting.py [--apply] [--dry] [--date 2026-11-04]
"""
import json
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = 'culture-atlas-address/1 (vasspolina.github.io/Culture-Atlas)'
args = sys.argv[1:]
apply = '--apply' in args
dry = '--dry' in args
date = args[args.index('--date') + 1] if '--date' in args else '2026-11-04'
cache_path = ROOT / 'data' / 'web_research' / f'osm_visiting_{date}.json'
path = ROOT / 'institutions.json'
records = json.load(open(path, encoding='utf-8'))
OSM = re.compile(r'https://www\.openstreetmap\.org/(node|way|relation)/(\d+)$')


def osm_of(r):
    fs = r.get('field_sources') or {}
    for key in ('address', 'coordinates'):
        for u in (fs.get(key) or {}).get('urls') or []:
            m = OSM.match(u)
            if m:
                return m.group(1)[0].upper() + m.group(2), u
    return None, None


DAYS = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']
NAME = {'Mo': 'Mon', 'Tu': 'Tue', 'We': 'Wed', 'Th': 'Thu', 'Fr': 'Fri', 'Sa': 'Sat', 'Su': 'Sun'}
TIME = r'\d{1,2}:\d{2}-\d{1,2}:\d{2}\+?'


def day_set(spec):
    out = []
    for part in spec.split(','):
        if '-' in part:
            a, b = part.split('-')
            i, j = DAYS.index(a), DAYS.index(b)
            out += [DAYS[k % 7] for k in range(i, i + ((j - i) % 7) + 1)]
        else:
            out.append(part)
    return out


def runs(days):
    """Mo,Tu,We,Fr -> Mon–Wed, Fri (in week order, a run of three or more as a span)."""
    idx = sorted({DAYS.index(d) for d in days})
    groups, cur = [], [idx[0]]
    for k in idx[1:]:
        if k == cur[-1] + 1:
            cur.append(k)
        else:
            groups.append(cur)
            cur = [k]
    groups.append(cur)
    words = []
    for g in groups:
        if len(g) >= 3:
            words.append(f'{NAME[DAYS[g[0]]]}–{NAME[DAYS[g[-1]]]}')
        else:
            words += [NAME[DAYS[k]] for k in g]
    return ', '.join(words)


def hours(tag):
    """Read a plain OSM opening_hours value; None when it holds anything this does not read."""
    t = (tag or '').strip()
    if not t or re.search(r'[A-Za-z]{3,}|"|\|\||\[|week|\d{4}|sunrise|sunset|dawn|dusk|SH', t.replace('off', '').replace('closed', '')):
        return None
    open_on, closed, order = {}, set(), []
    D = r'(?:Mo|Tu|We|Th|Fr|Sa|Su|PH)'
    t = re.sub(r'(' + D + r'),\s+(?=' + D + r')', r'\1,', t)      # "Tu-We, Fr-Su" is one list of days
    t = re.sub(r',\s+(?=' + D + r')', '; ', t)                     # "Mo 10:00-17:30, We-Su ..." is two rules
    rules = [x.strip() for x in t.split(';') if x.strip()]
    holidays = False
    kept = []
    for x in rules:
        m = re.fullmatch(r'(.*?),?PH(?:,(.*?))?\s+(off|closed)', x)
        if x in ('PH off', 'PH closed') or m:
            holidays = True
            rest = ','.join(y for y in (m.groups()[:2] if m else ()) if y)
            if rest:
                kept.append(rest + ' off')
        elif re.fullmatch(r'PH\s+' + TIME, x):
            continue   # open on public holidays: the weekly hours already say enough
        else:
            kept.append(x)
    rules = kept
    for rule in rules:
        rule = rule.replace('closed', 'off')
        m = re.fullmatch(r'((?:(?:Mo|Tu|We|Th|Fr|Sa|Su)(?:-(?:Mo|Tu|We|Th|Fr|Sa|Su))?)(?:,(?:Mo|Tu|We|Th|Fr|Sa|Su)(?:-(?:Mo|Tu|We|Th|Fr|Sa|Su))?)*)?'
                         r'(?:,PH)?\s*(off|' + TIME + r'(?:,' + TIME + r')*)?', rule)
        if not m or not (m.group(1) or m.group(2)):
            return None
        days = day_set(m.group(1)) if m.group(1) else list(DAYS)
        what = m.group(2)
        if not what:
            return None
        if what == 'off':
            for d in days:
                closed.add(d)
                open_on.pop(d, None)
        else:
            for a, b in re.findall(r'(\d{1,2}):\d{2}-(\d{1,2}):\d{2}', what):
                if int(b) < int(a) and int(b) > 6:   # Th 23:00-19:00 is a typing slip, not a late night
                    return None
            span = what.replace('-', '–').replace(',', ', ')
            for d in days:
                open_on[d] = span
                closed.discard(d)
    if not open_on:
        return None
    by_span = {}
    for d in DAYS:
        if d in open_on:
            by_span.setdefault(open_on[d], []).append(d)
    parts = []
    for span, ds in sorted(by_span.items(), key=lambda kv: DAYS.index(kv[1][0])):
        parts.append(('Daily' if len(ds) == 7 else runs(ds)) + ' ' + span)
    shut = [d for d in DAYS if d not in open_on]
    if shut:
        parts.append('closed ' + runs(shut))
    if holidays:
        parts.append('closed on public holidays')
    return '; '.join(parts)


def admission(tags):
    for k in ('charge', 'fee:amount', 'charge:adult'):
        v = (tags.get(k) or '').strip()
        m = re.fullmatch(r'(\d+(?:\.\d+)?)\s*([A-Z]{3})', v)   # "70 AED", "3.00 EUR"; anything looser is left out
        if m:
            amount = m.group(1)[:-3] if m.group(1).endswith('.00') else m.group(1)
            return f'{amount} {m.group(2)}'
    if (tags.get('fee') or '').strip().lower() == 'no':
        return 'Free'
    return None


if not apply:
    cache = json.load(open(cache_path, encoding='utf-8')) if cache_path.exists() else {}
    want = sorted({osm_of(r)[0] for r in records if osm_of(r)[0]} - set(cache))
    print(len(want), 'objects to look up')
    for i in range(0, len(want), 50):
        batch = want[i:i + 50]
        url = 'https://nominatim.openstreetmap.org/lookup?' + urllib.parse.urlencode(
            {'osm_ids': ','.join(batch), 'format': 'jsonv2', 'extratags': 1})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60) as resp:
                    hits = json.load(resp)
                break
            except Exception as e:
                print('  retry', attempt + 1, e, file=sys.stderr)
                time.sleep(30 * (attempt + 1))
        else:
            continue
        for h in hits:
            cache[h['osm_type'][0].upper() + str(h['osm_id'])] = h.get('extratags') or {}
        for k in batch:
            cache.setdefault(k, {})
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding='utf-8')
        print(' looked up', min(i + 50, len(want)), 'of', len(want))
        time.sleep(2)
    sys.exit()

cache = json.load(open(cache_path, encoding='utf-8'))
filled = {'opening_hours': [], 'admission_fee': []}
unread, stale = [], []
# Hours go out of date: of 462 objects with opening_hours, 294 had never been checked, and the Hermitage's read
# Tue–Sun 12:00–21:00 against its real 10:30 opening. Only hours a mapper confirmed (check_date) from 2024 on are taken.
RECENT = '2024-01-01'
for r in records:
    k, url = osm_of(r)
    tags = cache.get(k) if k else None
    if not tags:
        continue
    fs = r.setdefault('field_sources', {})
    checked = (tags.get('check_date:opening_hours') or tags.get('check_date') or '')[:10]
    if not r.get('opening_hours') and tags.get('opening_hours') and checked < RECENT:
        stale.append((r['id'], tags['opening_hours'], checked or 'never'))
    elif not r.get('opening_hours') and tags.get('opening_hours'):
        h = hours(tags['opening_hours'])
        if h:
            r['opening_hours'] = h
            fs['opening_hours'] = {'urls': [url], 'basis': f"OpenStreetMap opening_hours, checked by a mapper {checked}: " + tags['opening_hours'], 'retrieved': date}
            filled['opening_hours'].append((r['id'], tags['opening_hours'], h))
        else:
            unread.append((r['id'], tags['opening_hours']))
    if not (r.get('admission_fee') or r.get('admission_policy') or r.get('admission_details')):
        a = admission(tags)
        if a:
            r['admission_fee'] = a
            fs['admission_fee'] = {'urls': [url], 'basis': 'OpenStreetMap ' + ('fee=no' if a == 'Free' else 'charge tag'), 'retrieved': date}
            filled['admission_fee'].append((r['id'], a))
    if not fs:
        del r['field_sources']
print('opening hours written:', len(filled['opening_hours']), '| not checked since 2024:', len(stale), '| left unread:', len(unread),
      '| admission written:', len(filled['admission_fee']))
if dry:
    for x in filled['opening_hours'][:40]:
        print('  ', x[1], ' -> ', x[2])
    print('unread:', [u[1] for u in unread[:25]])
    print('admission:', [a[1] for a in filled['admission_fee'][:30]])
    sys.exit()
(ROOT / 'data' / 'web_research' / f'osm_visiting_decisions_{date}.json').write_text(
    json.dumps({'written': filled, 'unread': unread, 'stale': stale}, ensure_ascii=False, indent=1), encoding='utf-8')
path.write_text(json.dumps(records, ensure_ascii=False, indent=1), encoding='utf-8')
subprocess.run([sys.executable, str(ROOT / 'tools' / 'clean_data.py')], check=True, stdout=subprocess.DEVNULL)
subprocess.run([sys.executable, str(ROOT / 'tools' / 'embed_data.py')], check=True)
