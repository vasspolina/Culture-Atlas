#!/usr/bin/env python3
"""Turn raw two-pass web-research rows into accepted claims for tools/import_web_research.py.

Input rows come from the research workflow: for each record two independent search passes (a, b), plus
`year` and `address`, which are set only where both passes agree (same four-digit year; same street number
and street name). This script picks one written form of each agreed address and the source URLs to keep:
the institution's own site first, then Wikipedia, then the rest, at most three, never a bare portal host.
Usage: python3 tools/accept_web_research.py rows.json input.json claims.json [retrieved-date]
  input.json is the record list the workflow was given (id, website).
"""
import json
import re
import sys
import unicodedata
from urllib.parse import urlparse

# Where the two agreed forms differ and the default (the longer one, else pass a) is not the better written one.
PREFER = {
    'bonnefanten': 'b',          # keeps the accent of "Céramique" as the museum writes it
    'bemis-center': 'a',         # pass b ends in a neighbourhood name, not a postcode
    'leopold-museum': 'b',       # pass b is from the museum's own contact page
    'cranbrook-art-museum': 'b', # pass b is from the museum's own site
    'national-gallery-of-australia': 'a',
    'institute-of-modern-art': 'a',
}


# Agreed by both passes but left out: the institution's own site gives two different events for the same word.
EXCLUDE = {
    ('henry-art-gallery', 'year'): "the museum's own site gives 1926 as founded and 1927 as opened to the public",
    ('museo-nacional-de-artes-visuales', 'address'): "one pass gives the address without a street number (s/n), the other gives 2283",
}


def norm(t):
    t = unicodedata.normalize('NFKD', t.lower())
    return re.sub(r'[^a-z0-9]+', ' ', ''.join(c for c in t if not unicodedata.combining(c))).strip()


def host(u):
    return (urlparse(u).hostname or '').lower().removeprefix('www.')


def keep_urls(urls, site):
    sd = host(site) if site else ''
    seen, out = set(), []
    for u in urls:
        if not u.startswith('http') or u in seen:
            continue
        seen.add(u)
        h = host(u)
        if h in ('wikipedia.org', 'wikipedia.com'):  # portal hosts with no language
            continue
        if h.split('.')[0] in ('dev', 'staging', 'test', 'stage'):  # a development copy of a site is not a source to send people to
            continue
        out.append(u)
    def rank(u):
        h = host(u)
        if sd and (h == sd or h.endswith('.' + sd) or sd.endswith('.' + h)):
            return 0
        return 1 if 'wikipedia.org' in h else 2
    out.sort(key=rank)
    if out and rank(out[0]) == 0:
        out = [u for u in out if rank(u) == 0] + [u for u in out if rank(u) == 1][:1]
    return out[:3]


def pick_address(row):
    a, b = row['a']['address'], row['b']['address']
    p = PREFER.get(row['id'])
    if p == 'a':
        return a, row['a']['address_urls'] + row['b']['address_urls']
    if p == 'b':
        return b, row['b']['address_urls'] + row['a']['address_urls']
    ta, tb = set(norm(a).split()), set(norm(b).split())
    if tb < ta:
        return a, row['a']['address_urls'] + row['b']['address_urls']
    if ta < tb:
        return b, row['b']['address_urls'] + row['a']['address_urls']
    return a, row['a']['address_urls'] + row['b']['address_urls']


rows = json.load(open(sys.argv[1], encoding='utf-8'))
inputs = {r['id']: r for r in json.load(open(sys.argv[2], encoding='utf-8'))}
date = sys.argv[4] if len(sys.argv) > 4 else '2026-10-13'
claims = []
for r in rows:
    site = inputs.get(r['id'], {}).get('website', '')
    c = {'id': r['id'], 'retrieved': date}
    if r.get('year') and (r['id'], 'year') not in EXCLUDE:
        c['year_founded'] = r['year']
        c['year_basis'] = r['a']['year_basis']
        c['year_urls'] = keep_urls(r['a']['year_urls'] + r['b']['year_urls'], site)
    if r.get('address') and (r['id'], 'address') not in EXCLUDE:
        c['address'], urls = pick_address(r)
        c['address_urls'] = keep_urls(urls, site)
    if c.get('year_founded') and not c['year_urls']:
        for k in ('year_founded', 'year_basis', 'year_urls'):
            c.pop(k)
    if c.get('address') and not c['address_urls']:
        for k in ('address', 'address_urls'):
            c.pop(k)
    if c.get('year_founded') or c.get('address'):
        claims.append(c)
json.dump(claims, open(sys.argv[3], 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(len(claims), 'claims,', sum(1 for c in claims if 'year_founded' in c), 'years,', sum(1 for c in claims if 'address' in c), 'addresses')
