#!/usr/bin/env python3
"""Attach each space's own lobbying (data/space_lobbying.json) to its record as `lobbying`.

The record's Lobbying row reads it (index.html, proseLobbyingRow). Only lobbying filed by or for the space as the client
is attached; a funder's lobbying is not. US entries carry the years, the reported total and the latest full year's figure,
the outside firms (the space itself when it files in house), what the latest reports say it lobbied on, and the latest
report as the source. EU entries carry the register's own words and the LobbyFacts datacard.

Usage:
  python3 tools/attach_space_lobbying.py            # dry run: what would be attached
  python3 tools/attach_space_lobbying.py --apply    # writes institutions.json; then run tools/embed_data.py
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'institutions.json'
SRC = ROOT / 'data' / 'space_lobbying.json'

def tidy_firm(s):
    s = re.sub(r'\s*\(FKA [^)]*\)|\s+FKA .*$', '', s.strip(), flags=re.I)
    s = re.sub(r'^(MR|MS|MRS)\.\s+', '', s, flags=re.I)
    if s.isupper():
        keep = {'LLC', 'LLP', 'PC', 'PLLC', 'US', 'WOH', 'ACG', 'K&L', 'MARC', 'III'}
        s = ' '.join(w if w.strip(',.') in keep else w.capitalize() for w in s.split())
        s = re.sub(r'&(\w)', lambda m: '&' + m.group(1).upper(), s)
    return s

def tidy_desc(s):
    s = re.sub(r'\s+', ' ', s).strip()
    return s[0].upper() + s[1:] if s else s

def main():
    apply = '--apply' in sys.argv
    src = json.load(open(SRC, encoding='utf-8'))
    recs = json.load(open(DATA, encoding='utf-8'))
    by_id = {r.get('id'): r for r in recs}
    attached = {}
    for x in src['us']:
        last_full = max((int(y) for y in x['reported_usd_by_year'] if int(y) <= 2025), default=None)
        own = {n.upper() for n in x['filed_as']}
        firms = [tidy_firm(f) for f in x['lobbyists'] if f.upper() not in own]
        descs = []
        for d in x['latest_described']:
            d = tidy_desc(d)
            if d and d.lower().rstrip('.') not in {e.lower().rstrip('.') for e in descs}: descs.append(d)
        attached[x['space']] = {'register': 'us', 'years': x['years'], 'total_usd': round(x['reported_usd_total']),
            'last_year': last_full, 'last_year_usd': x['reported_usd_by_year'].get(str(last_full)) if last_full else None,
            'in_house': x['lobbyists'] and any(f.upper() in own for f in x['lobbyists']) or False,
            'firms': firms[:3], 'on': descs[:2], 'source': x['source']}
    for x in src['eu']:
        attached[x['space']] = {'register': 'eu', 'filed_as': x['filed_as'][0], 'registered': x['registered'],
            'declared': x['declared'], 'source': x['source']}
    missing = [k for k in attached if k not in by_id]
    if missing: sys.exit(f'not in institutions.json: {missing}')
    for r in recs:
        r.pop('lobbying', None)
        if r.get('id') in attached: r['lobbying'] = attached[r['id']]
    print(f"{len(attached)} records get a lobbying entry ({len(src['us'])} US, {len(src['eu'])} EU)")
    if apply:
        with open(DATA, 'w', encoding='utf-8') as fh:
            json.dump(recs, fh, indent=2, ensure_ascii=True)
    else:
        for k, v in list(attached.items())[:3]: print(k, json.dumps(v)[:300])

if __name__ == '__main__':
    main()
